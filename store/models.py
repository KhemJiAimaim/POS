from django.urls import reverse
from django.db import models
from django.utils.html import format_html
from django.utils import timezone

# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)

    class Meta:
        ordering = ['id'] #เรียงจากน้อยไปมาก ถ้า -id จะเป็นจากมากไปน้อย
        verbose_name = 'หมวดหมู่สินค้า'
        verbose_name_plural = 'ข้อมูลหมวดหมู่สินค้า'

    def get_url(self):
        return reverse('product_by_category' , args=[self.slug])

    def __str__(self):
        return self.name
    

class Product(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, blank=True)
    category = models.ForeignKey(Category, null=True , blank=True , on_delete=models.CASCADE)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField()
    image = models.ImageField(upload_to='product' )
    active = models.IntegerField(default=1)
    barcode = models.CharField(max_length=255)
    EXP = models.DateField() #วันหมดอายุ
    created = models.DateTimeField(auto_now_add=True) #วัน-เวลาเพิ่มสินค้า
    updated = models.DateTimeField(auto_now = True) #วัน-เวลาที่แก้ไขสินค้า

    class Meta: 
        ordering = ['EXP','stock'] #เรียงจากน้อยไปมาก ถ้า -id จะเป็นจากมากไปน้อย
        verbose_name = 'คลังสินค้า'
        verbose_name_plural = 'ข้อมูลสินค้า'

    def show_image(self):
        if self.image:
            return format_html('<img src= '+self.image.url+' height= "80px" >' )
        return ''
    show_image.allow_tags = True

    def __str__(self) :
        return self.name

class Cart(models.Model):
    cart_id = models.CharField(max_length=255,blank=True,null=True)
    date_added = models.DateTimeField(auto_now_add=True) #วัน-เวลาเพิ่มขุ้อมูลสินค้า

    def __str__(self):
        return str(self.cart_id)
    
    class Meta:
        db_table = 'cart'
        ordering = ['date_added']
        verbose_name = 'ตะกร้าสินค้า'
        verbose_name_plural = 'ข้อมูลตะกร้าสินค้า'

class CartItem(models.Model):
    product = models.ForeignKey(Product , on_delete=models.CASCADE)
    cart = models.ForeignKey(Cart , on_delete=models.CASCADE)
    quantity = models.IntegerField()
    active = models.BooleanField(default=True)

    class Meta:
        db_table = 'cartItem'
        verbose_name = 'รายการสินค้า'
        verbose_name_plural = 'ข้อมูลรายการสินค้า'
        
    #ผลรวมราคาขาย
    def sub_total(self):
        return self.product.price * self.quantity
    
    #ผลรวมต้นทุน
    def sub_cost(self):   
        return self.product.cost * self.quantity

    def __str__(self):
        return str(self.product.name)


class Order(models.Model):
    money=models.IntegerField() #รับเงิน
    amount=models.DecimalField(max_digits=10,decimal_places=2 ,null=True) #เงินถอน
    total=models.DecimalField(max_digits=10,decimal_places=2,null=True) #ราคาสินค้า
    cost=models.DecimalField(max_digits=10,decimal_places=2,null=True) #ต้นทุนของสินค้า
    profit=models.DecimalField(max_digits=10,decimal_places=2,null=True) #กำไรที่ได้
    quantity = models.IntegerField()    
    created=models.DateTimeField(auto_now_add=True)
    updated=models.DateTimeField(auto_now=True)

    class Meta :
        db_table='Order'
        ordering=('-created',)
        verbose_name = 'การซื้อสินค้า'
        verbose_name_plural = 'ข้อมูลการซื้อสินค้า'



class OrderItem(models.Model):
    product=models.CharField(max_length=250)
    quantity=models.IntegerField()
    price=models.DecimalField(max_digits=10,decimal_places=2)
    # cost = models.FloatField() #ต้นทุนของสินค้า
    cost=models.DecimalField(max_digits=10,decimal_places=2,null=True) #ต้นทุนของสินค้า
    order=models.ForeignKey(Order,on_delete=models.CASCADE ,null=True)
    created=models.DateTimeField(auto_now_add=True)
    updated=models.DateTimeField(auto_now=True)
    

    class Meta :
        db_table='OrderItem'
        ordering=('-created',)
        verbose_name = 'รายการสินค้าที่ขาย'
        verbose_name_plural = 'ข้อมูลรายการสินค้าที่ขาย'

    def sub_total(self):
        return self.quantity*self.price
    
    def __str__(self):
        return self.product
        

class Debtor(models.Model):
    name = models.CharField(max_length=100)
    phone = models.TextField()
    total = models.DecimalField(max_digits=10, decimal_places=2, null=True)  # ยอดหนี้
    balance = models.DecimalField(max_digits=10 , decimal_places=2 , null=True) # วงเงินคงเหลิอ
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    cash_limit = models.DecimalField(max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        self.balance = self.cash_limit - self.total 
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name
    
    class Meta:
        db_table = 'Debtor'
        ordering = ['-updated_at']
        verbose_name = 'ลูกหนี้'
        verbose_name_plural = 'ข้อมูลลูกหนี้'

class ProfitProduct(models.Model):
    barcode = models.CharField(max_length=255 , null=True)
    profitTotal = models.DecimalField(max_digits=10, decimal_places=2 , null=True)
    nameProduct = models.CharField(max_length=100 ,  null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'ProfitProduct'
        verbose_name = 'กำไร'
        ordering = ['-profitTotal']
        verbose_name_plural = 'ข้อมูลกำไร'
    
    def __str__(self):
        return self.barcode