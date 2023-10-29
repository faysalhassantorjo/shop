from django import forms
from .models import *

class AddProduct(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name','category','description',
                  'image','price','instock'
                  ]
class CustomerOrderForm(forms.ModelForm):
    class Meta:
        model = CustomerOrder
        fields = ['order_by', 'customer_name', 'shipping', 'orderItem', 'total_tk', 'date_added']