from django.contrib.auth.models import User
from django import forms
from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from .models import Product , Category , Debtor

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
        fields = ('active','barcode','name','category','description','price','cost','stock','image','EXP')
        labels = {
            'active':'สถานะ พิมพ์ 1 แสดงสินค้า 0 ไม่แสดงสินค้า ',
            'barcode':'',
            'name':'',
            'category':'หมวดหมู่สินค้า ',
            'description':'',
            'price':'',
            'cost':'',
            'stock':'',
            'image':'รูปสินค้า ',
            'EXP':'วันหมดอายุ ',
            
        }
        widgets = {

            'active': forms.TextInput(attrs={'class':'form-control', 'placeholder':''}),
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

class DebtorForm(ModelForm):
    class Meta:
        model = Debtor
        fields = ('name','phone','total','cash_limit')
        labels = {
            'name':'ชื่อ',
            'phone':'เบอร์โทรศัพท์',
            'total':'ยอดหนี้ทั้งหมด',
            'cash_limit':'วงเงิน',
        }
        widgets = {
            'name': forms.TextInput(attrs={'class':'form-control', 'placeholder':'ชื่อจริง นามสกุล'}),
            'phone': forms.TextInput(attrs={'class':'form-control', 'placeholder':'เบอ์โทรศัพท์'}),
            'total': forms.NumberInput(attrs={'class':'form-control', 'placeholder':'ยอดหนี้'}),
            'cash_limit': forms.NumberInput(attrs={'class':'form-control', 'placeholder':'กำหนดวงเงิน'}),
        }




        