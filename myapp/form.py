from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from .models import Product,Category

class AddProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'category','description','image','image2','hot_product','price','instock','discount_percent','discount']


class AddCategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'image','special_collection']



