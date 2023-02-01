from store.models import Category 
#from store.views import _cart_id

def menu_links(request):
    links = Category.objects.all()
    return dict(links=links)

#def counter(request):
#    item_count = 0

#    try:
        #query Cart 
 #       cart = Cart.objects.filter(cart_id = _cart_id(request))
        #query CartItem
#        cart_item = CartItem.objects.all().filfilter(cart = cart[:1])
        
#        for item in cart_item:
 #           item_count += item.quantity

 #   except Cart.DoesNotExist:
 #       item_count = 0

 #   return dict(item_count=item_count)