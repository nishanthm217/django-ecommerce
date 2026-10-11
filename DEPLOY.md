# Deploying ecomProject to AWS EC2

Stack on the server: **Ubuntu 24.04 → Nginx → Gunicorn → Django (ecomProject) → MySQL**

- Nginx serves `/static/` (admin + DRF CSS) and `/media/` (product images) directly.
- Gunicorn runs Django on `127.0.0.1:8000`.
- MySQL runs on the same EC2 instance.
- Secrets live in `/home/ubuntu/app/.env`, never in git.

Replace `YOUR_ELASTIC_IP` and `yourdomain.com` everywhere below.

---

## 0. Before you start (on your Windows laptop)

1. **Revoke the old Gmail app password.** It was committed to GitHub inside `settings.py`.
   Go to Google Account → Security → 2-Step Verification → App passwords, delete the old one, and create a new one.
   Put the new one in your local `.env` and in the server `.env` (step 5).
2. Make sure the project still runs locally:
   ```powershell
   pip install -r requirements.txt
   python manage.py runserver
   ```
3. Commit and push:
   ```powershell
   git add .
   git commit -m "Production settings via .env, add requirements"
   git push
   ```
   Check that `git status` does **not** list `.env`. It is in `.gitignore`.

---

## 1. EC2 instance

- **AMI:** Ubuntu Server 24.04 LTS. **Type:** t2.micro or t3.micro.
- **Storage:** 20 GB gp3.
- **Security group inbound:** SSH 22 (My IP), HTTP 80 (Anywhere), HTTPS 443 (Anywhere). Do **not** open 3306 or 8000.
- **Elastic IP:** allocate one and associate it with the instance.

Connect from PowerShell:

```powershell
# One-time fix for "UNPROTECTED PRIVATE KEY FILE" on Windows
icacls .\my-key.pem /inheritance:r
icacls .\my-key.pem /grant:r "$($env:USERNAME):(R)"

ssh -i .\my-key.pem ubuntu@YOUR_ELASTIC_IP
```

---

## 2. Server packages and swap

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3-venv python3-dev git nginx mysql-server

# 2 GB swap: a 1 GB micro instance running MySQL needs it
sudo fallocate -l 2G /swapfile && sudo chmod 600 /swapfile
sudo mkswap /swapfile && sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

---

## 3. MySQL database and user

```bash
sudo mysql
```

```sql
CREATE DATABASE ECOMMERCE_DB CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'ecomuser'@'localhost' IDENTIFIED BY 'PUT-A-STRONG-PASSWORD-HERE';
GRANT ALL PRIVILEGES ON ECOMMERCE_DB.* TO 'ecomuser'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

---

## 4. Code and virtual environment

```bash
cd ~
git clone https://github.com/nishanthm217/django-ecommerce.git app
cd app
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

If the repo is private, git asks for a username and password. Use your GitHub username and a **personal access token** as the password (GitHub → Settings → Developer settings → Tokens).

---

## 5. Server `.env`

Generate a new secret key:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

```bash
nano ~/app/.env
```

```
DJANGO_SECRET_KEY=<paste the generated key>
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=YOUR_ELASTIC_IP,yourdomain.com,www.yourdomain.com
DJANGO_CSRF_TRUSTED_ORIGINS=http://YOUR_ELASTIC_IP,http://yourdomain.com,https://yourdomain.com,https://www.yourdomain.com
DJANGO_USE_HTTPS=False

DB_NAME=ECOMMERCE_DB
DB_USER=ecomuser
DB_PASSWORD=<the MySQL password from step 3>
DB_HOST=localhost
DB_PORT=3306

EMAIL_HOST_USER=paradox.internationals2026@gmail.com
EMAIL_HOST_PASSWORD=<NEW gmail app password>
```

```bash
chmod 600 ~/app/.env
```

---

## 6. Database tables and data

**Option A: start fresh** (simplest). You re-add products through `/admin` later.

```bash
cd ~/app && source venv/bin/activate
python manage.py migrate
python manage.py createsuperuser
```

**Option B: copy your local products, users and orders.**

On Windows, use `--result-file`. PowerShell's `>` writes UTF-16 and the import will fail.

```powershell
mysqldump -u root -p --databases ECOMMERCE_DB --result-file=ecommerce.sql
scp -i .\my-key.pem ecommerce.sql ubuntu@YOUR_ELASTIC_IP:~
```

If `mysqldump` isn't found, it's usually in `C:\Program Files\MySQL\MySQL Server 8.0\bin\`.

On the server:

```bash
sudo mysql ECOMMERCE_DB < ~/ecommerce.sql
cd ~/app && source venv/bin/activate
python manage.py migrate
```

Product images are already in the repo under `media/images/`, so they come along with `git clone`.

---

## 7. Static files and a deployment check

```bash
python manage.py collectstatic --noinput
python manage.py check --deploy      # warnings about HTTPS are expected until step 11
gunicorn --bind 127.0.0.1:8000 ecomProject.wsgi:application   # quick test, then Ctrl+C
```

---

## 8. Gunicorn as a service

```bash
sudo nano /etc/systemd/system/ecom.service
```

```ini
[Unit]
Description=Gunicorn for ecomProject
After=network.target mysql.service

[Service]
User=ubuntu
Group=www-data
WorkingDirectory=/home/ubuntu/app
ExecStart=/home/ubuntu/app/venv/bin/gunicorn --workers 2 --timeout 60 --bind 127.0.0.1:8000 ecomProject.wsgi:application
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now ecom
sudo systemctl status ecom
```

---

## 9. Nginx

```bash
sudo nano /etc/nginx/sites-available/ecom
```

```nginx
server {
    listen 80;
    server_name YOUR_ELASTIC_IP yourdomain.com www.yourdomain.com;

    client_max_body_size 10M;   # product image uploads

    location /static/ {
        alias /home/ubuntu/app/staticfiles/;
    }

    location /media/ {
        alias /home/ubuntu/app/media/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/ecom /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo chmod 755 /home/ubuntu           # lets Nginx read static + media
sudo nginx -t && sudo systemctl reload nginx
```

---

## 10. Test everything at http://YOUR_ELASTIC_IP

- [ ] Home page lists products with images (`/media/` works)
- [ ] Product detail → **Add to cart** updates the cart count (jQuery AJAX + CSRF)
- [ ] Cart page: update quantity and delete work
- [ ] Register → verification email arrives. The link should start with `http://YOUR_ELASTIC_IP/users/...`, not 127.0.0.1
- [ ] Login, logout, profile, password reset email
- [ ] Address form → checkout → place order
- [ ] `/admin` is styled (`/static/` works)
- [ ] `/api/products/` returns JSON

---

## 11. Domain and HTTPS (when you have a domain)

1. At your registrar, add **A records** for `yourdomain.com` and `www` pointing to the Elastic IP.
2. Run:
   ```bash
   sudo apt install -y certbot python3-certbot-nginx
   sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
   ```
3. In `~/app/.env`, set `DJANGO_USE_HTTPS=True`, then run `sudo systemctl restart ecom`.

---

## Deploying updates later

On Windows: `git push`. Then on the server:

```bash
cd ~/app && git pull
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart ecom
```

---

## Troubleshooting

| Symptom | Fix |
|---|---|
| `KeyError: 'DJANGO_SECRET_KEY'` | `.env` is missing or not in `~/app` next to `manage.py` |
| **400 Bad Request** | Add the IP/domain to `DJANGO_ALLOWED_HOSTS`, then restart `ecom` |
| **403 CSRF verification failed** | Add the exact origin (with `http://` or `https://`) to `DJANGO_CSRF_TRUSTED_ORIGINS` |
| **502 Bad Gateway** | Gunicorn is down. Run `journalctl -u ecom -n 50` |
| Admin has no styling | Run `collectstatic`, then `chmod 755 /home/ubuntu` |
| Product images 404 | Check that `media/images/` exists on the server and the Nginx `/media/` alias is correct |
| `Access denied for user` (MySQL) | `DB_USER`/`DB_PASSWORD` in `.env` don't match step 3 |
| `SMTPAuthenticationError` | Wrong Gmail app password, or 2-Step Verification is off |
| Logs | `journalctl -u ecom -f` (Django) · `sudo tail -f /var/log/nginx/error.log` |
