from django.contrib.auth.models import User
from django import forms
from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from .models import Product , Category

class CategoryForm(ModelForm):
    class Meta:
        model = Category
        fields = ('name',)
        labels = {
            'name':'',
        }
        widgets = {
             'name': forms.TextInput(attrs={'class':'form-control', 'placeholder':'ชื่อหมวดหมู่สินค้า'})
             }
             
class ProductForm(ModelForm):
    class Meta:
        model = Product
        fields = ('barcode','name','category','description','price','cost','stock','image','EXP')
        labels = {
            'barcode':'',
            'name':'',
            'category':'หมวดหมู่สินค้า',
            'description':'',
            'price':'',
            'cost':'',
            'stock':'',
            'image':'รูปสินค้า',
            'EXP':'วันหมดอายุ',
        }
        widgets = {
            'barcode': forms.TextInput(attrs={'class':'form-control', 'placeholder':'รหัสสินค้า'}),
            'name': forms.TextInput(attrs={'class':'form-control', 'placeholder':'ชื่อสินค้า'}),
            'category': forms.Select(attrs={'class':'form-control', 'placeholder':''}),
            'description': forms.Textarea(attrs={'class':'form-control', 'placeholder':'รายละเอียดสินค้า'}),
            'price': forms.NumberInput(attrs={'class':'form-control', 'placeholder':'ราคาขายสินค้า'}),
            'cost': forms.NumberInput(attrs={'class':'form-control', 'placeholder':'ต้นทุนสินค้า'}),
            'stock': forms.NumberInput(attrs={'class':'form-control', 'placeholder':'จำนวนสินค้า'}),
            'image': forms.FileInput(attrs={'class':'form-control', 'placeholder':''}),
            'EXP': forms.DateInput(attrs={'class':'form-control', 'placeholder':'วัน/เดือน/ปี'}),
        }




        