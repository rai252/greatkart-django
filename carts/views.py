from django.shortcuts import render, redirect
from store.models import Product, Variation
from .models import Cart, CartItem
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse

def _cart_id(request):
    cart_id = request.session.session_key
    if not cart_id:
        request.session.create()
        cart_id = request.session.session_key
    return cart_id

def add_cart(request, product_id):
    product = Product.objects.get(id=product_id)
    product_variations = []

    if request.method == 'POST':
        for item in request.POST:
            key = item
            value = request.POST[key]
            try:
                variation = Variation.objects.get(product=product, variation_category__iexact=key, variation_value__iexact=value)
                product_variations.append(variation)
            except Variation.DoesNotExist:
                pass
    
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
    except Cart.DoesNotExist:
        cart = Cart.objects.create(cart_id=_cart_id(request))
    
    is_cart_item_exists = CartItem.objects.filter(product=product, cart=cart).exists()
    
    if is_cart_item_exists:
        try:
            cart_item = CartItem.objects.get(product=product, cart=cart)
            existing_variations = cart_item.variations.all()
            
            if set(product_variations) == set(existing_variations):
                cart_item.quantity += 1
                cart_item.save()
            else:
                new_cart_item = CartItem.objects.create(product=product, quantity=1, cart=cart)
                new_cart_item.variations.set(product_variations)
        except CartItem.DoesNotExist:
            pass
    else:
        new_cart_item = CartItem.objects.create(product=product, quantity=1, cart=cart)
        new_cart_item.variations.set(product_variations)
    
    return redirect('cart')

def remove_cart_item(request, product_id):
    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = Product.objects.get(id=product_id)
    cart_item = CartItem.objects.filter(product=product, cart=cart)
    cart_item.delete()
    return redirect('cart')
    
def subtract_cart(request, product_id):
    product = Product.objects.get(id=product_id)
    
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
    except Cart.DoesNotExist:
        cart = Cart.objects.create(cart_id=_cart_id(request))
    
    try:
        cart_item = CartItem.objects.get(product=product, cart=cart)
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
    except CartItem.DoesNotExist:
        pass
    
    return redirect('cart')

def cart(request, total=0, quantity=0, cart_items=None):
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        tax = (2 * total) / 100
        grand_total = total + tax 
    except ObjectDoesNotExist:
        pass
    
    context ={
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'tax': tax if 'tax' in locals() else 0,
        'grand_total': grand_total if 'grand_total' in locals() else 0,
    }
    return render(request, 'store/cart.html', context)
