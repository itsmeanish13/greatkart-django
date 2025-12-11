from .models import CartItem,Cart
from carts.views import _cart_id

def counter(request):
    if 'admin' in request.path: #do not show counter in admin page
        return {}
    else:
        cart_count = 0
        try:
            cart = Cart.objects.filter(cart_id=_cart_id(request))   #get the cart using the cart_id present in the session
            if cart.exists():   #if cart exists
                cart_items = CartItem.objects.filter(cart__cart_id=_cart_id(request))
                for cart_item in cart_items:
                    cart_count += cart_item.quantity    #counting the quantity of items in the cart
        except Cart.DoesNotExist:
            cart_count = 0
    return dict(cart_count=cart_count)