from django.contrib import admin
from .models import Category , Product , Cart ,Order,OrderItem,Debtor , ProfitProduct

# Register your models here.

class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id' , 'name' ]
    prepopulated_fields = {'slug' : ['name']}
    search_fields = ['name']

class ProductAdmin(admin.ModelAdmin):
    list_display = ['active','barcode' , 'name' , 'category' , 'price' , 'stock' , 'show_image']
    search_fields = ['barcode' , 'name' ]
    prepopulated_fields = {'slug' : ['name']}
    list_editable=['price' , 'stock']
    list_per_page = 20

class OrderAdmin(admin.ModelAdmin):
    list_display=['id','quantity','total','money','amount' ,'cost' ,'profit','created','updated']
    list_per_page=20

class OrderItemAdmin(admin.ModelAdmin):
    list_display=['order','product','quantity','price','cost','created','updated']
    list_per_page=20

class DebtorItemAdmin(admin.ModelAdmin):
    list_display=['name','phone','total','cash_limit','balance','created_at','updated_at']
    list_per_page=20

class ProfitProductAdmin(admin.ModelAdmin):
    list_display=['barcode','nameProduct','description','profitTotal','created_at','updated_at']
    #list_per_page=20

admin.site.register(Category,CategoryAdmin)
admin.site.register(Product,ProductAdmin)
admin.site.register(Cart)
admin.site.register(Order,OrderAdmin)
admin.site.register(OrderItem,OrderItemAdmin)
admin.site.register(Debtor,DebtorItemAdmin)
admin.site.register(ProfitProduct,ProfitProductAdmin)