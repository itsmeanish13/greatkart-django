from django.shortcuts import render, redirect
from .models import Cart, CartItem
from store.models import Product, Variation
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist




# Create your views here.
def _cart_id(request):
    cart = request.session.session_key #get the session key
    if not cart:
        cart = request.session.create() #create a new session if not present
    return cart

def add_cart(request, product_id):
    product = Product.objects.get(id=product_id) #get the product
    product_variation = [] #initialize an empty list to store product variations
    if request.method == 'POST':
        for item in request.POST:
            key = item
            value = request.POST[key]
            try:
                variation = Variation.objects.get(product=product,variation_category__iexact=key, variation_value__iexact=value)
                product_variation.append(variation) #add the variation to the list of product variations 
            except:
                pass
            
            
            
         
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request)) #get the cart using the cart_id present in the session
    except Cart.DoesNotExist:
        cart = Cart.objects.create(
            cart_id = _cart_id(request) #create a new cart using the cart_id present in the session
        )
        cart.save()
    
    is_cart_item_exists = CartItem.objects.filter(product=product, cart=cart).exists() #check if the cart item exists in the cart    
    
    if is_cart_item_exists:
        cart_item = CartItem.objects.filter(product=product, cart=cart) #get the cart items associated with the product and cart
        ex_var_list = [] #initialize an empty list to store existing variations
        id = [] #initialize an empty list to store cart item ids
        for item in cart_item:
            existing_variation = item.variations.all() #get all variations associated with the cart item
            ex_var_list.append(list(existing_variation)) #add the existing variations to the list
            id.append(item.id) #add the cart item id to the list
        if product_variation in ex_var_list:
            #increase the cart item quantity
            index = ex_var_list.index(product_variation) #get the index of the existing variation
            item_id = id[index] #get the cart item id using the index
            cart_item = CartItem.objects.get(product=product, id=item_id) #get the cart item using the product and id
            cart_item.quantity += 1  #increase the cart item quantity
            cart_item.save() #save the cart item
        else:
            cart_item = CartItem.objects.create(    #create a new cart item
                product = product, #associate the product
                quantity = 1,     #set the quantity to 1
                cart = cart
            )
                
            if len(product_variation) > 0:
                cart_item.variations.clear() #clear existing variations
                
                cart_item.variations.add(*product_variation) #add the variation to the cart item
                    
            cart_item.save() #save the cart item
    else:
        
        cart_item = CartItem.objects.create(    #create a new cart item
            product = product, #associate the product
            quantity = 1,     #set the quantity to 1
            cart = cart
        )
        if len(product_variation) > 0:
            cart_item.variations.clear() #clear existing variations
            
            cart_item.variations.add(*product_variation) #add the variation to the cart item
        cart_item.save()
    return redirect('cart')  #redirect to cart page

def remove_cart(request, product_id,cart_item_id):
    
    cart = Cart.objects.get(cart_id=_cart_id(request)) #get the cart using the cart_id present in the session
    product = Product.objects.get(id=product_id) #get the product
    try:
        cart_item = CartItem.objects.get(product=product, cart=cart,id=cart_item_id) #get the cart item associated with the product and cart
        
        if cart_item.quantity > 1:
            cart_item.quantity -= 1  #decrease the cart item quantity
            cart_item.save() #save the cart item
        else:
            cart_item.delete()    #delete the cart item if quantity is 0
    except:
        pass
    return redirect('cart')  #redirect to cart page

def remove_cart_item(request, product_id,cart_item_id):
    cart = Cart.objects.get(cart_id=_cart_id(request)) #get the cart using the cart_id present in the session
    product = Product.objects.get(id=product_id) #get the product
    cart_item = CartItem.objects.get(product=product, cart=cart,id=cart_item_id) #get the cart item associated with the product and cart
    cart_item.delete()    #delete the cart item
    return redirect('cart')  #redirect to cart page


            
def cart(request, total=0, quantity=0, cart_items=None):
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request)) #get the cart using the cart_id present in the session
        cart_items = CartItem.objects.filter(cart=cart, is_active=True) #get the cart items associated with the cart
        
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity) #calculate the total price
            quantity += cart_item.quantity #calculate the total quantity
            
        tax= (2 * total)/100  #calculate tax as 2% of total
        grand_total= total + tax  #calculate grand total
        
            
    except Cart.DoesNotExist:
        pass  #ignore if the cart does not exist
    context={   #context to be passed to the template
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,   #cart items associated with the cart
        'tax': tax,
        'grand_total': grand_total
    }
    return render(request, 'store/cart.html',context)   #render the cart page with the context