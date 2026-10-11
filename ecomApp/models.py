from django.db import models
from django.utils.text import slugify
from django.urls import reverse
# Create your models here.
class ProductModel(models.Model):
    def get_absolute_url(self):
        return reverse('detail',args=[self.slug])
    name = models.CharField(max_length=200)
    price = models.FloatField()
    description = models.TextField()
    image = models.ImageField(upload_to='images/',blank=True,null=True)
    slug = models.SlugField(unique=True, blank=True)
    stock = models.IntegerField()
    active = models.BooleanField(default=True)
    
    def save(self,*args,**kwargs):
        base_slug = slugify(self.name)
        slug = base_slug
        counter = 1
        while ProductModel.objects.filter(slug=slug).exists():
            slug = f"{slug}-{counter}"
            counter+=1
        self.slug = slug
        super().save(*args,**kwargs)
             
    def __str__(self):
        return self.name
            
    