from django.shortcuts import render, get_object_or_404, redirect
from store.models import Category, Product, Cart, CartItem , Order , OrderItem
from django.urls import reverse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth import login , authenticate,logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
from .forms import ProductForm , CategoryForm
from datetime import date
from django.template.loader import get_template
from xhtml2pdf import pisa
from io import StringIO, BytesIO

# Import PDF Stuff
from django.http import FileResponse
import io
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate
from reportlab.platypus import Table



# Create your views here.
@login_required (login_url='signIn')
def pos(request, category_slug=None):
    product = None
    category_page = None

    if category_slug != None:
        category_page = get_object_or_404(Category, slug=category_slug)
        product = Product.objects.all().filter(category=category_page)
    else:
        product = Product.objects.all().filter()

   

    total = 0 #ยอดชำระ
    cost = 0 #ยอดต้นทุน
    counter = 0 #ยอดจำนวนสินค้าที่ซื้อ
    profit = 0 #ยอดกำไรในการขาย
    cart_items = None

    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))  # ดึงตะกร้าสินค้ามา
        cart_items = CartItem.objects.filter(
            cart=cart, active=True)  # ดึงข้อมูลสินต้าในตะกร้า
        
        for item in cart_items:
            total += (item.product.price*item.quantity)
            cost += (item.product.cost*item.quantity)
            profit += total-cost
            counter += item.quantity

        product = Product.objects.filter(name__icontains=request.GET ['title']) | Product.objects.filter(barcode__icontains=request.GET ['title'])
    except Exception as e:
        pass
    
    paginator = Paginator(product, 12)
    page = request.GET.get('page')
    try:
        product = paginator.page(page)
    except PageNotAnInteger:
        product = paginator.page(1)
    except EmptyPage:
        product = paginator.page(paginator.num_pages)
    
    return render(request, 'pos.html', {
        'product':  product,
        'category': category_page,
        'cart_items': cart_items,
        'total': total,
        'cost': cost,
        'counter': counter
    })


def checkout_add(request):
    
    money = 0 #รับเงิน 
    amount = 0#เงินถอน
    total = 0 #ยอดชำระ
    cost = 0 #ยอดต้นทุน
    counter = 0 #ยอดจำนวนสินค้าที่ซื้อ
    profit = 0 #ยอดกำไรในการขาย
    cart_items = None

    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))  # ดึงตะกร้าสินค้ามา
        cart_items = CartItem.objects.filter(
            cart=cart, active=True)  # ดึงข้อมูลสินต้าในตะกร้า
        
        for item in cart_items:
            total += (item.product.price*item.quantity)
            cost += (item.product.cost*item.quantity)
            profit += total-cost
            counter += item.quantity

            
        money = (int(request.GET["amount"])) 
        amount = money - total

       
    except Exception as e:
        pass

        if request.method=="POST":
            try:
                #บันทึกข้อมูลใบสั่งซื้อ
                order=Order.objects.create(
                    total=total,
                    cost=cost,
                    profit=profit,
                    quantity=counter
                )
                order.save()

                #บันทึกรายการสั่งซื้อ
                for item in cart_items :
                    order_item=OrderItem.objects.create(
                        product=item.product.name,
                        quantity=item.quantity,
                        price=item.product.price,
                        order=order
                    )
                    order_item.save()
                    #ลดจำนวน Stock
                    product=Product.objects.get(id=item.product.id)
                    product.stock=int(item.product.stock-order_item.quantity)
                    product.save()
                    item.delete()
                return redirect('/')
                
            except Exception as e:
                pass

        return render(request, 'checkout_add.html',{
        'cart_items': cart_items,
        'total': total,
        'profit': profit,
        'cost': cost,
        'counter': counter
    }) 
    return render(request, 'ch.html',{
        'amount' : amount    
    })


def ch(request):
    return render(request, 'ch.html')


def product(request , category_slug=None):
    product = None
    category_page = None
    today = date.today()

    if category_slug != None:
        category_page = get_object_or_404(Category, slug=category_slug)
        product = Product.objects.all().filter(category=category_page)
    else:
        product = Product.objects.all().filter()


    try:
        product = Product.objects.filter(name__icontains=request.GET ['title']) | Product.objects.filter(barcode__icontains=request.GET ['title']) 
    except Exception as e:
        pass

    
    paginator = Paginator(product, 12)
    page = request.GET.get('page')
    try:
        product = paginator.page(page)
    except PageNotAnInteger:
        product = paginator.page(1)
    except EmptyPage:
        product = paginator.page(paginator.num_pages)
    

    return render(request, 'product.html', {
        'product':  product,
        'category': category_page,
        'today':today
    })

def add_product(request):
    submitted = False
    if request.method == "POST" :
        form = ProductForm(request.POST , request.FILES)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/product?submitted=True')
    else:
        form = ProductForm
        if 'submitted' in request.GET:
            submitted = True
    return render(request, 'add_product.html', {'form':form ,'submitted':submitted})

def edit_product(request, product_id):
    product = Product.objects.get(id = product_id) 
    form = ProductForm(request.POST or None, request.FILES or None , instance=product)
    if form.is_valid():
            form.save()
            return redirect('product')
    
    return render(request, 'edit_product.html', {
        'product':product,
        'form':form
    })

def deleteProduct (request , product_id):
    product = Product.objects.get(id = product_id)
    product.delete()
    return redirect('product')


def pdfProduct (template_src):
    product = Product.objects.all()
    pdfmetrics.registerFont(TTFont('THSarabunNew', 'store/THSarabunNew.ttf' , 'utf-8'))
    pdfmetrics.registerFont(TTFont('THSarabunNewB', 'store/THSarabunNew Bold.ttf' , 'utf-8'))

    pdf = canvas.Canvas("mypdf.pdf", pagesize=A4)

    pdf.setFont("THSarabunNewB",30)
    pdf.setTitle("Product Report")
   
    pdf.drawCentredString(300,770,"รายการสินค้า")
   
    data = []

    pdf.save()

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] =  'filename="products_report.pdf"' #attachment; ดาวห์โหลดไฟล์
    with open('mypdf.pdf' , 'rb') as f :
        response.write(f.read())
    return response
def index(request):
    return render(request, 'index.html')


def category(request):
    category = Category.objects.all().filter()
    return render(request, 'category.html',{
        'category' : category
    })

def add_category(request):
    submitted = False
    if request.method == "POST" :
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/category?submitted=True')
    else:
        form = CategoryForm
        if 'submitted' in request.GET:
            submitted = True
    return render(request, 'add_category.html', {'form':form ,'submitted':submitted})


def deleteCategory (request , category_id):
    category = Category.objects.get(id = category_id)
    category.delete()
    return redirect('category')

def edit_category(request, category_id):
    category = Category.objects.get(id = category_id) 
    form = CategoryForm(request.POST or None, instance=category)
    if form.is_valid():
            form.save()
            return redirect('category')
    
    return render(request, 'edit_category.html', {
        'category': category,
        'form':form
    })




# สร้าง Session
def _cart_id(request):
   cart = request.session.session_key
   if not cart:
       cart = request.session.create()
       return cart


def addCart(request, product_id):
    # มันส่งจะไอดีมาจากนั้น ไอดีจะเป็นตังดึงสินค้าออกมาตามรหัส
    product = Product.objects.get(id=product_id) 
    
    # สร้างตะกร้าสินค้า
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
    except Cart.DoesNotExist:   
        cart = Cart.objects.create(cart_id=_cart_id(request))
        cart.save()
        # บันทึกเข้าฐานข้อมูล

    try:
        
        # ซื้อรายการสินค้าซ้ำ
        cart_item = CartItem.objects.get(product=product, cart=cart , )
        if cart_item.quantity < cart_item.product.stock:
            # เปลี่ยนจำนวนรายการสินค้า
            cart_item.quantity += 1
            # บันทึก / อัพเดทค่า
            cart_item.save()
    except CartItem.DoesNotExist:
        # ซื้อรายการสินค้าครั้งแรก
        cart_item = CartItem.objects.create(
            product=product,
            cart=cart,
            quantity=1
        )
        cart_item.save()
    return redirect('/')


def removeCart(request, product_id):
    # ทำงานกับตะกร้าสินค้า
    cart = Cart.objects.get(cart_id=_cart_id(request))  # ดึงตะกร้าสินค้ามา
    # ทำงานกับสินค้าที่จะลบ
    product = get_object_or_404(Product, id=product_id)
    cartItem = CartItem.objects.get(product=product, cart=cart)
    # ลบรายการสินค้า 1 ออกจากตะกร้า A โดยลบจาก รายการสินค้าในตะกร้า (CartItem)
    cartItem.delete()
    return redirect('/')

def deleteCart (request):
    cart = Cart.objects.get(cart_id=_cart_id(request))  # ดึงตะกร้าสินค้ามา
    cart.delete()

    
    return redirect('/')

def signInView(request):
    if request.method=='POST':
        form=AuthenticationForm(data=request.POST)
        if form.is_valid():
            username=request.POST['username']
            password=request.POST['password']
            user=authenticate(username=username,password=password)
            if user is not None :
                login(request,user)
                return redirect('pos')
            else :
                messages.error(request,"Invalid username or password.")
    else:
        messages.error(request,"Invalid username or password.")
        form=AuthenticationForm()
    return render(request,'signIn.html',{'form':form})

def signOutView(request):
    logout(request)
    return redirect('signIn')


