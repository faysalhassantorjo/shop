from django.db import models
from datetime import datetime
from django.contrib.auth.models import User
import json

class Category(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(null=True, blank=True)
    special_collection=models.BooleanField(default=False,null=True, blank=False)
    any_special_discount=models.BooleanField(default=False, null=True,blank=False)

    hero_slide=models.BooleanField(default=False,null=True,blank=False)

    special_discount=models.IntegerField(default=0, null=True,blank=False)


    def __str__(self):
        return str(self.name)

    @property
    def imageURL(self):
        try:
            url = self.image.url
        except:
            url = ''
        return url


class Product(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    description=models.CharField(default="",max_length=200)
    image = models.ImageField(null=True, blank=True)
    image2 = models.ImageField(null=True, blank=True)
    hot_product=models.BooleanField(default=False,null=True, blank=False)
    discount_percent=models.IntegerField(default=0)
    discount=models.BooleanField(default=True,null=True,blank=False)

    price = models.IntegerField(default=0)
    instock=models.IntegerField(default=0)
    def __str__(self):
       
        return str(self.name)


    

    @property
    def imageURL(self):
        try:
            url = self.image.url
        except:
            url = ''
        return url
    @property
    def imageURL2(self):
        try:
            url = self.image2.url
        except:
            url = ''
        return url


class Customer(models.Model):
    user = models.OneToOneField(User, null=True, blank=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=200, null=True)
    email = models.CharField(max_length=200, null=True)

    def __str__(self):
        return str(self.name)

class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, blank=True, null=True)
    date_order = models.DateTimeField(default=datetime.now, db_index=True)
    complete = models.BooleanField(default=False, null=True, blank=False)
    transaction_id = models.CharField(max_length=200, null=True)
    any_coupon=models.BooleanField(default=False,null=True,blank=False)
    after_using_coupn=models.IntegerField(default=0)

    def __str__(self):
        return str(self.customer.name)

    @property
    def shipping(self):
        shipping = False
        return shipping

    @property
    def get_cart_total(self):
     
        orederitems = self.orderitem_set.all()
        total = sum(item.get_total for item in orederitems)
        return total
    def coupon_uses_total(self):
            if self.after_using_coupn and self.any_coupon:
                return self.after_using_coupn

    @property
    def get_cart_items(self):
        orederitems = self.orderitem_set.all()
        total = sum(item.quantity for item in orederitems)
        return total

    


class OrderItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, blank=True, null=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, blank=True, null=True)
    quantity = models.IntegerField(default=0, null=True, blank=True)

    date_added=models.DateTimeField(default=datetime.now)
    size=models.CharField(max_length=10)
    transaction_id = models.CharField(max_length=200, null=True)


    def __str__(self):
        return str(self.product)

    @property
    def get_total(self):
        total = self.product.price * self.quantity
        return total

    def productnameandquantity(self):
        name = self.product.name
        qty = str(self.quantity)
        return 'ProductName:' + name + ' Quntity:' + qty + '   '


class ShippingAddress(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, blank=True, null=True)
    oder = models.ForeignKey(Order, on_delete=models.SET_NULL, blank=True, null=True)
    address = models.CharField(max_length=100)
    email=models.EmailField(null=True)
    phonNumber = models.CharField(max_length=100)
    date_added = models.DateTimeField(default=datetime.now)

    def __str__(self):
        return self.address


class CustomerOrder(models.Model):
    order_by = models.ForeignKey(Order, on_delete=models.SET_NULL, blank=True, null=True)
    orderItems = models.ManyToManyField(OrderItem,  blank=True)
    customer_name=models.CharField(max_length=100)
    shipping = models.ForeignKey(ShippingAddress, on_delete=models.SET_NULL, blank=True, null=True)
    # orderItem = models.CharField(max_length=500) 
    total_tk=models.CharField(max_length=100)
    date_added = models.DateTimeField(default=datetime.now)
    twoDAr=models.CharField(default=None,blank=True,max_length=500)
    def __str__(self):
        return f'Order No: {self.id}'
    def set_two_d_array(self, array):
        self.twoDAr = json.dumps(array)

    def get_two_d_array(self):
        return json.loads(self.twoDAr)


class Cuppon(models.Model):
    cuppon_name=models.CharField(max_length=10)
    percent=models.PositiveIntegerField(default=0)