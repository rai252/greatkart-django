from django.shortcuts import render, redirect, get_object_or_404
from store.models import Product, Variation
from .models import Cart, CartItem
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required

def _cart_id(request):
    cart_id = request.session.session_key
    if not cart_id:
        request.session.create()
        cart_id = request.session.session_key
    return cart_id

def add_cart(request, product_id):
    current_user = request.user
    product = get_object_or_404(Product, id=product_id)
    
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

    if current_user.is_authenticated:
        is_cart_item_exists = CartItem.objects.filter(product=product, user=current_user).exists()
        if is_cart_item_exists:
            cart_items = CartItem.objects.filter(product=product, user=current_user)
            for cart_item in cart_items:
                existing_variations = list(cart_item.variations.all())
                if product_variations == existing_variations:
                    cart_item.quantity += 1
                    cart_item.save()
                    break
            else:
                cart_item = CartItem.objects.create(product=product, quantity=1, user=current_user)
                cart_item.variations.set(product_variations)
                cart_item.save()
        else:
            cart_item = CartItem.objects.create(product=product, quantity=1, user=current_user)
            cart_item.variations.set(product_variations)
            cart_item.save()
    else:
        cart = Cart.objects.get_or_create(cart_id=_cart_id(request))[0]
        is_cart_item_exists = CartItem.objects.filter(product=product, cart=cart).exists()
        if is_cart_item_exists:
            cart_items = CartItem.objects.filter(product=product, cart=cart)
            for cart_item in cart_items:
                existing_variations = list(cart_item.variations.all())
                if product_variations == existing_variations:
                    cart_item.quantity += 1
                    cart_item.save()
                    break
            else:
                cart_item = CartItem.objects.create(product=product, quantity=1, cart=cart)
                cart_item.variations.set(product_variations)
                cart_item.save()
        else:
            cart_item = CartItem.objects.create(product=product, quantity=1, cart=cart)
            cart_item.variations.set(product_variations)
            cart_item.save()

    return redirect('cart')

def remove_cart_item(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.user.is_authenticated:
        cart_item = get_object_or_404(CartItem, product=product, user=request.user)
    else:
        cart = get_object_or_404(Cart, cart_id=_cart_id(request))
        cart_item = get_object_or_404(CartItem, product=product, cart=cart)
    cart_item.delete()
    return redirect('cart')

def subtract_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.user.is_authenticated:
        cart_item = get_object_or_404(CartItem, product=product, user=request.user)
    else:
        cart = get_object_or_404(Cart, cart_id=_cart_id(request))
        cart_item = get_object_or_404(CartItem, product=product, cart=cart)

    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()
    
    return redirect('cart')

def cart(request, total=0, quantity=0, cart_items=None):
    try:
        tax = 0
        grand_total = 0
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        
        tax = (2 * total) / 100
        grand_total = total + tax
    except ObjectDoesNotExist:
        pass

    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'tax': tax,
        'grand_total': grand_total,
    }
    return render(request, 'store/cart.html', context)

@login_required(login_url='login')
def checkout(request, total=0, quantity=0, cart_items=None):
    try:
        tax = 0
        grand_total = 0
        cart_items = CartItem.objects.filter(user=request.user, is_active=True)
        
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        
        tax = (2 * total) / 100
        grand_total = total + tax
    except ObjectDoesNotExist:
        pass

    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'tax': tax,
        'grand_total': grand_total,
    }
    return render(request, 'store/checkout.html', context)
