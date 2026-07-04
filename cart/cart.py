from ecomApp.models import ProductModel
from decimal  import Decimal
class Cart():
    def __init__(self,request):
        self.session = request.session
        cart = request.session.get('cart')
        if 'cart' not in request.session:
            cart = self.session['cart'] = {}
        self.cart = cart # This cart is stored inside the iter
#Have to make this code available anywhere througout the application

    def __len__(self):
        return sum(int(item['qty']) for item in self.cart.values())
    
    def __iter__(self):
        product_keys = self.cart.keys() #Fetching list of product ID's
        products = ProductModel.objects.filter(id__in=product_keys)
        #id__in searches the id in the list of "product_keys"
        cart = self.cart.copy()
        
        for product in products:
            cart[str(product.id)]['product'] = product
        
        for item in cart.values():
            item['price'] = Decimal(item['price'])
            item['total'] = item['price'] * item['qty']
            yield item
    
    def get_total_price(self):
        return sum(Decimal(item['price'])* Decimal(item['qty']) for item in self.cart.values())

    def add(self,product, product_qty):
        product_id = str(product.id)
        if product_id in self.cart:
            self.cart[product_id]['qty'] += int(product_qty)
            #It means if the product is available already, then update product_qty
        else:
            self.cart[product_id] = {'price':str(product.price), 'qty':int(product_qty)}
            #If product is not available then we are creating new product
        self.session.modified = True
        
    def delete(self,product_id):
        product_id = str(product_id)
        if product_id in self.cart:
            del(self.cart[product_id])
        self.session.modified = True
        
    def update(self,product_id,selected_qty):
        product_id = str(product_id)
        selected_qty = int(selected_qty)
        if product_id in self.cart:
            self.cart[product_id]['qty'] = selected_qty
        self.session.modified = True