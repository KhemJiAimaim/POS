from django.shortcuts import render, get_object_or_404, redirect
from store.models import Category, Product, Cart, CartItem, Order, OrderItem , Debtor , ProfitProduct
from django.urls import reverse
from django.template import loader
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth import login , authenticate,logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
from .forms import ProductForm, CategoryForm , DebtorForm , OrderSearcForm
from datetime import date, datetime
from django.template.loader import get_template
from io import StringIO, BytesIO
from dateutil.relativedelta import relativedelta
from django.db.models import Q

# Import PDF Stuff
from django.http import FileResponse
from reportlab.lib.units import cm , inch
from reportlab.lib.pagesizes import A4 , letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate
from reportlab.platypus import Table , Image , TableStyle , SimpleDocTemplate




# Create your views here.
@login_required(login_url='signIn')
def pos(request, category_slug=None):
    product = None
    category_page = None

    if category_slug != None:
        category_page = get_object_or_404(Category, slug=category_slug)
        product = Product.objects.all().filter(category=category_page , active = 1)
    else:
        product = Product.objects.all().filter(active = 1 )

    total = 0  # ยอดชำระ
    cost = 0  # ยอดต้นทุน
    counter = 0  # ยอดจำนวนสินค้าที่ซื้อ
    profit = 0  # ยอดกำไรในการขาย
    cart_items = None

    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))  # ดึงตะกร้าสินค้ามา
        cart_items = CartItem.objects.filter(cart=cart, active=1)  # ดึงข้อมูลสินต้าในตะกร้า

        for item in cart_items:
            total += (item.product.price*item.quantity)
            cost += (item.product.cost*item.quantity)
            profit += total-cost
            counter += item.quantity

        product = Product.objects.filter(name__icontains=request.GET['title']) | Product.objects.filter(
            barcode__icontains=request.GET['title'])
    except Exception as e:
        pass

    paginator = Paginator(product, 1)
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
    money = 0  # รับเงิน
    amount = 0  # เงินถอน
    total = 0  # ยอดชำระ
    cost = 0  # ยอดต้นทุน
    counter = 0  # ยอดจำนวนสินค้าที่ซื้อ
    profit = 0  # ยอดกำไรในการขาย
    cart_items = None
    print(request)
    if request.method == "POST":
        data = request.POST.copy()
        print(data)
        print("============POST=============")
        try:
            money = int(data.get('amount'))
            total = int(float(data.get('total')))
            print(money)
            print(total)
            amount = money - total
            print(amount)

            # บันทึกข้อมูลใบสั่งซื้อ
            cart = Cart.objects.get(cart_id=_cart_id(request))  # ดึงตะกร้าสินค้ามา
            cart_items = CartItem.objects.filter(cart=cart, active=1)  # ดึงข้อมูลสินต้าในตะกร้า
            for item in cart_items:
                print("item",item.product)
                totalProfit = (item.product.price - item.product.cost)*item.quantity
                try:
                    print("data" , item.product.barcode)
                    profitDataItem = ProfitProduct.objects.get(barcode=item.product.barcode)
                    profitDataItem.profitTotal += totalProfit
                    profitDataItem.save()
                except ProfitProduct.DoesNotExist:
                    profitDataItem = None
                    print("Data DoesNotExist")
                    pass
                if profitDataItem is None:
                        profitData = ProfitProduct.objects.create(
                        barcode=item.product.barcode,
                        profitTotal=totalProfit,
                        nameProduct = item.product.name
                         )
                        profitData.save()
                cost += (item.product.cost*item.quantity)
                counter += item.quantity
            profit = total-cost
            order = Order.objects.create(
                money=money,
                total=total,
                cost=cost,
                profit=profit,
                quantity=counter,
                amount = amount
            )
            order.save()
            
            # บันทึกรายการสั่งซื้อ
            for item in cart_items:
                order_item = OrderItem.objects.create(
                product=item.product.name,
                quantity=item.quantity,
                price=item.product.price,
                order=order
                )
                order_item.save()
                # ลดจำนวน Stock
                product = Product.objects.get(id=item.product.id)
                product.stock = int(item.product.stock-order_item.quantity)
                product.save()
                item.delete()
            return render(request, 'ch.html', {
                'amount': amount
            })
        except Exception as e:
            print("Error Post Method" , e)
    else:
        print("============GET=============")
        try:
            cart = Cart.objects.get(cart_id=_cart_id(request))  # ดึงตะกร้าสินค้ามา
            cart_items = CartItem.objects.filter(
            cart=cart, active=1)  # ดึงข้อมูลสินต้าในตะกร้า

            for item in cart_items:
                total += (item.product.price*item.quantity)
            return render(request, 'checkout_add.html', {
            'total': total,
        })
        except Exception as e:
            print("Exception Get" , e)



def ch(request):
    return render(request, 'ch.html')


def product(request, category_slug=None):
    product = None
    category_page = None
    currentdate = datetime.today()
    formatDate = currentdate.strftime("%d-%m-%Y")

    if category_slug != None:
        category_page = get_object_or_404(Category, slug=category_slug)
        product = Product.objects.all().filter(category=category_page  , active = 1)
    else:
        product = Product.objects.all().filter()

    try:
        product = Product.objects.filter(name__icontains=request.GET['title']) | Product.objects.filter(
            barcode__icontains=request.GET['title'])
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
        'formatDate': formatDate
    })


def add_product(request):
    submitted = False
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "บันทึกข้อมูลสำเสร็จ")
            return HttpResponseRedirect('/product?submitted=True')
    else:
        form = ProductForm
        if 'submitted' in request.GET:
            submitted = True
    return render(request, 'add_product.html', {'form': form, 'submitted': submitted})


def edit_product(request, product_id):
    product = Product.objects.get(id=product_id)
    form = ProductForm(request.POST or None,
                       request.FILES or None, instance=product)
    if form.is_valid():
        form.save()
        messages.success(request, "แก้ไขข้อมูลสำเสร็จ")
        return redirect('product')

    return render(request, 'edit_product.html', {
        'product': product,
        'form': form
    })


def deleteProduct(request, product_id):
    product = Product.objects.get(id=product_id)
    product.delete()
    return redirect('product')


def index(request):
    now = datetime.now()
    formatDate = now.strftime("%d-%m-%Y")
    current_year = now.strftime("%Y")
    current_month = now.strftime("%m")
    current_day = now.strftime("%d")
    products = len(Product.objects.all())
    transaction = len(Order.objects.filter(
        created__year=current_year,
        created__month = current_month,
        created__day = current_day
    ))
    order = Order.objects.filter(
        created__year=current_year,
        created__month = current_month,
        created__day = current_day
    )
    today_sales = Order.objects.filter(
        created__year=current_year,
        created__month = current_month,
        created__day = current_day
    ).all()
    total_sales = sum(today_sales.values_list('total',flat=True))
    total_cost = sum(today_sales.values_list('cost',flat=True))
    total_profit = sum(today_sales.values_list('profit',flat=True))

    profit = ProfitProduct.objects.all().filter()

    context = {
        'page_title':'Home',
        'products' : products,
        'transaction' : transaction,
        'total_sales' : total_sales,
        'total_cost': total_cost,
        'total_profit':total_profit,
        'order':order,
        'profit':profit,
        'formatDate':formatDate
    }
    return render(request, 'index.html',context)
    


def category(request):
    category = Category.objects.all().filter()
    return render(request, 'category.html', {
        'category': category
    })


def add_category(request):
    submitted = False
    if request.method == "POST":
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "บันทึกข้อมูลสำเสร็จ")
            return HttpResponseRedirect('/category?submitted=True')
    else:
        form = CategoryForm
        if 'submitted' in request.GET:
            submitted = True
    return render(request, 'add_category.html', {'form': form, 'submitted': submitted})


def deleteCategory(request, category_id):
    category = Category.objects.get(id=category_id)
    category.delete()
    return redirect('category')


def edit_category(request, category_id):
    category = Category.objects.get(id=category_id)
    form = CategoryForm(request.POST or None, instance=category)
    if form.is_valid():
        form.save()
        messages.success(request, "แก้ไขข้อมูลสำเสร็จ")
        return redirect('category')

    return render(request, 'edit_category.html', {
        'category': category,
        'form': form
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
        cart_item = CartItem.objects.get(product=product, cart=cart, )
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


def addCartSearch(request):
    if request.method == "POST":
        barcodesearch = request.POST.get('barcodesearch')
        # มันส่งจะไอดีมาจากนั้น ไอดีจะเป็นตังดึงสินค้าออกมาตามรหัส
        product = Product.objects.get(barcode=barcodesearch)
        if product.stock != 0:
            # สร้างตะกร้าสินค้า
            try:
                cart = Cart.objects.get(cart_id=_cart_id(request))
            except Cart.DoesNotExist:
                cart = Cart.objects.create(cart_id=_cart_id(request))
                cart.save()
                # บันทึกเข้าฐานข้อมูล

            try:
                # ซื้อรายการสินค้าซ้ำ
                cart_item = CartItem.objects.get(product=product, cart=cart, )
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


def deleteCart(request):
    cart = Cart.objects.get(cart_id=_cart_id(request))  # ดึงตะกร้าสินค้ามา
    cart.delete() 
    return redirect('/')


def signInView(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('pos')
            else:
               form = AuthenticationForm()
    else:
        form = AuthenticationForm()
    return render(request, 'signIn.html', {'form': form})


def signOutView(request):
    logout(request)
    return redirect('signIn')



def debtor(request):
    return render(request, 'debtor.html')


def debtorCaseNew(request):
    submitted = False
    currentdate = datetime.today()
    formatDate = currentdate.strftime("%d-%m-%Y")
    if request.method == "POST":
        counter = 0
        cost = 0
        total = 0
        profit = 0
        print("===============POST==============")
        form = DebtorForm(request.POST)
        if form.is_valid():
            form.save()
            cart = Cart.objects.get(cart_id=_cart_id(request))  # ดึงตะกร้าสินค้ามา
            cart_items = CartItem.objects.filter(
            cart=cart, active=True)  # ดึงข้อมูลสินต้าในตะกร้า
            for item in cart_items:
                print("item",item.product)
                totalProfit = (item.product.price - item.product.cost)*item.quantity
                try:
                    print("data" , item.product.barcode)
                    profitDataItem = ProfitProduct.objects.get(barcode=item.product.barcode)
                    profitDataItem.profitTotal += totalProfit
                    profitDataItem.save()
                except ProfitProduct.DoesNotExist:
                    profitDataItem = None
                    print("Data DoesNotExist")
                    pass
                if profitDataItem is None:
                        profitData = ProfitProduct.objects.create(
                        barcode=item.product.barcode,
                        profitTotal=totalProfit,
                        nameProduct = item.product.name
                         )
                        profitData.save()
                total = (item.product.price*item.quantity)
                cost += (item.product.cost*item.quantity)
                counter += item.quantity
                profit = total-cost
            order = Order.objects.create(
                money=0,
                total=total,
                cost=cost,
                profit=profit,
                quantity=counter,
                amount = 0
            )
            order.save()
            # บันทึกรายการสั่งซื้อ
            for item in cart_items:
                order_item = OrderItem.objects.create(
                product=item.product.name,
                quantity=item.quantity,
                price=item.product.price,
                order=order
                )
                order_item.save()
                # ลดจำนวน Stock
                product = Product.objects.get(id=item.product.id)
                product.stock = int(item.product.stock-order_item.quantity)
                product.save()
                item.delete()
            messages.success(request, "บันทึกข้อมูลสำเร็จ")
            return redirect('debtor_old')
            
    else:
        form = DebtorForm
        return render(request, 'debtor_new.html' , {'form': form , 'submitted':submitted , 'formatDate':formatDate})

def debtorCaseOld(request):
    currentdate = datetime.today()
    formatDate = currentdate.strftime("%d-%m-%Y")
    debtors = Debtor.objects.all()
    try:
        debtors = Debtor.objects.filter(name__icontains=request.GET['title']) | Debtor.objects.filter(
            phone__icontains=request.GET['title'])
    except Exception as e:
        pass
    return render(request , 'debtor_old.html' , {'debtors': debtors , 'formatDate':formatDate})

def debtorCaseOldEdit(request , debtor_id):
    debtor = Debtor.objects.get(id=debtor_id)
    currentdate = datetime.today()
    formatDate = currentdate.strftime("%d-%m-%Y")
    form = DebtorForm(request.POST or None, instance=debtor)
    if form.is_valid():
        form.save()
        messages.success(request, "แก้ไขข้อมูลสำเร็จ")
        return redirect('debtor_old')

    return render(request, 'edit_debtor.html', {
        'debtor': debtor,
        'form': form,
        'formatDate':formatDate
    })

def deleteDebtorCaseOld(request, debtor_id):
    debtor = Debtor.objects.get(id=debtor_id)
    debtor.delete()
    return redirect('debtor_old')


def plusDebtor(request, debtor_id):
    debtor = Debtor.objects.get(id=debtor_id)
    currentdate = datetime.today()
    formatDate = currentdate.strftime("%d-%m-%Y")
    if request.method == 'POST':
        print("========== PLUS-POST===========")
        data = request.POST.copy()
        money = int(data.get('amount'))
        balance = int(float(data.get('balance')))
        if money > balance :
            return render(request , 'debtor_plus.html' ,  {"balance" : debtor.balance , "statusFail" : True ,
        'formatDate':formatDate})
        else:
            counter = 0
            cost = 0
            total = 0
            profit = 0
            debtor.balance = debtor.balance - money
            debtor.total = debtor.total + money
            debtor.save()
            cart = Cart.objects.get(cart_id=_cart_id(request))  # ดึงตะกร้าสินค้ามา
            cart_items = CartItem.objects.filter(
            cart=cart, active=1)  # ดึงข้อมูลสินต้าในตะกร้า
            for item in cart_items:
                print("item",item.product)
                totalProfit = (item.product.price - item.product.cost)*item.quantity
                try:
                    print("data" , item.product.barcode)
                    profitDataItem = ProfitProduct.objects.get(barcode=item.product.barcode)
                    profitDataItem.profitTotal += totalProfit
                    profitDataItem.save()
                except ProfitProduct.DoesNotExist:
                    profitDataItem = None
                    print("Data DoesNotExist")
                    pass
                if profitDataItem is None:
                        profitData = ProfitProduct.objects.create(
                        barcode=item.product.barcode,
                        profitTotal=totalProfit,
                        nameProduct = item.product.name
                         )
                        profitData.save()
                total += (item.product.price*item.quantity)
                cost += (item.product.cost*item.quantity)
                counter += item.quantity
                profit = total-cost
                money = 0
                amount = 0
            order = Order.objects.create(
                money=0,
                total=total,
                cost=cost,
                profit=profit,
                quantity=counter,
                amount = 0
            )
            order.save()
            # บันทึกรายการสั่งซื้อ
            for item in cart_items:
                order_item = OrderItem.objects.create(
                product=item.product.name,
                quantity=item.quantity,
                price=item.product.price,
                cost=item.product.cost,
                order=order
                )
                order_item.save()
                # ลดจำนวน Stock
                product = Product.objects.get(id=item.product.id)
                product.stock = int(item.product.stock-order_item.quantity)
                product.save()
                item.delete()
            return render(request, 'debtor_plus.html', {"balance": debtor.balance,
        'formatDate':formatDate ,"statusSuccess": True}) 
    else: 
        print("========== PLUS-GET============")
        return render(request,'debtor_plus.html' , {"balance" : debtor.balance})
    


def payOffDebtor(request, debtor_id):
    debtor = Debtor.objects.get(id=debtor_id)
    currentdate = datetime.today()
    formatDate = currentdate.strftime("%d-%m-%Y")
    if request.method == 'POST':
        print("========== PAYOFF-POST===========")
        data = request.POST.copy()
        money = int(data.get('amount'))
        total = int(float(data.get('total')))

        if money > total :
            return render(request , 'debtor_payoff.html' ,  {"total" : debtor.total ,
        'formatDate':formatDate , "statusFail" : True})
        else:
            debtor.total = debtor.total - money
            debtor.balance = money
            debtor.save()
            return render(request, 'debtor_payoff.html', {"total": debtor.total,
        'formatDate':formatDate , "statusSuccess": True}) 
            
    else: 
        print("========== PAYOFF-GET============")
        return render(request,'debtor_payoff.html' , {"total" : debtor.total,
        'formatDate':formatDate})


def pdfProduct (datas):
    currentdate = datetime.today()+ relativedelta(years=543)
    formatDate = currentdate.strftime("%d-%m-%Y")
    pdfmetrics.registerFont(TTFont('THSarabunNew', 'store/THSarabunNew.ttf' , 'utf-8'))
    pdfmetrics.registerFont(TTFont('THSarabunNewB', 'store/THSarabunNew Bold.ttf' , 'utf-8'))
    buffer = BytesIO()
    doc = SimpleDocTemplate( buffer, pagesize=letter,title='รายการสินค้า {}'.format(formatDate))
    # container for the 'Flowable' objects
    elements = []

    data=  [
        ['รายการสินค้าเหลือน้อย หรือ หมดสต๊อก', ' ', ' ', ''],
        [' ', '', '', ''],
        ['ประจำวันที่ {}'.format(formatDate), ' ', ' ', ' '],
        [' ', '', '', '', ' '],
        [' ', '', '', '', ' '],
        ['วันหมดอายุ', 'รหัสสินค้า', 'ชื่อ', 'จำนวนสินค้า'],
        [' ', '', '', '', ' '],
        
    ]

    product = Product.objects.all().filter()
     
    for products in product:
        if products.stock <= 3:
            data += [
                [
                products.EXP,
                products.barcode,
                products.name,
                products.stock]
            ]
        else: 0


    t=Table(data) 
    t.setStyle(TableStyle
            ([
               
                ('BOX', (0, 5), (-1, 4), 1, (0, 0, 0)),
                ('FONT', (0, 0), (-1, 0), 'THSarabunNewB'),#หัวเรื่อง
                ('FONTSIZE', (0, 0), (-1, 0), 25),  #หัวเรื่อง
                ('FONT', (0, 2), (-1, 2), 'THSarabunNewB'),#วันที่
                ('FONTSIZE', (0, 2), (-1, 2), 16),  #วันที่
                ('FONT', (0, 5), (-1, 5), 'THSarabunNewB'),#หัวตาราง
                ('FONTSIZE', (0, 5), (-1,5), 18), 
                ('FONT', (0, 7), (-1, -1), 'THSarabunNew'),#เนื้อหาตาราง
                ('FONTSIZE', (0, 7), (-1,-1), 18),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('ALIGN', (0, 2), (-1, 2), 'CENTER'),
                ('ALIGN', (0, 5), (-1, 5), 'CENTER'), 
                ('ALIGN', (0, 7), (-1, -1), 'CENTER'), 
                ('SPAN', (0, 0), (-1, 0)),
                ('SPAN', (0, 2), (-1, 2)),
            ]))

                
    elements.append(t)
    # write the document to disk
    doc.build(elements)
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] =  ' attachment; filename="products_report.pdf"' #attachment; ดาวห์โหลดไฟล์
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    return response

def reportSale(request, ):
    currentdate = datetime.today()
    formatDate = currentdate.strftime("%d-%m-%Y")
    orders = Order.objects.all().filter().values()
    
    total = 0
    cost = 0
    profit = 0
    try: 
        order = Order.objects.filter()
        for item in order:
                total += item.total
                cost += item.cost
                profit += item.total-item.cost
                
    except Exception as e:
        pass

        
    return render(request, 'report_sale.html',
    {'orders':orders,
    'formatDate':formatDate,
    'total':total,
    'cost':cost,
    'profit':profit,
    })

def detailOrderItem(request, order_id ):
    currentdate = datetime.today()
    formatDate = currentdate.strftime("%d-%m-%Y")
    order = Order.objects.get(id=order_id)
    orderitem=OrderItem.objects.filter(order=order)
    return render(request, 'orderItem.html',
    {'order':order,'formatDate':formatDate ,'orderitem':orderitem})



def deleteReportSale(request, order_id):
    order = Order.objects.get(id=order_id)
    order.delete()
    return redirect('reportSale')


def dateReport(request):
    currentdate = datetime.today()
    formatDate = currentdate.strftime("%d-%m-%Y")
    error = ""
    total = 0
    cost = 0
    profit = 0
    if request.method == 'POST':
        fd = request.POST['fromDate']
        td = request.POST['toDate']
        orders = Order.objects.filter(Q(created__gte=fd) & Q(created__lte=td))
           
        try: 
            for item in orders:
                    total += item.total
                    cost += item.cost
                    profit += item.total-item.cost
                
        except Exception as e:
            pass
        return render(request, 'between_date_report.html', locals() )
    return render(request, 'dateReport.html', locals())