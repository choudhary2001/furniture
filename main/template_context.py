from .models import Category, Cart, Product
from django.shortcuts import render, redirect, get_object_or_404

def categories(request):
    categories = Category.objects.filter(parent=None)
    print(categories)
    return {'categories': categories}

def cart_len(request):
    if request.user.is_authenticated:
        if request.user.is_active == True:
            if 'cartdata' in request.session:
                cart_p = request.session['cartdata']
                for key, value in cart_p.items():
                    # Use get_or_create to avoid creating duplicates
                    slug = cart_p[key]['product']
                    product = get_object_or_404(Product, slug = slug)
                    obj, created = Cart.objects.get_or_create(user= request.user, product = product, defaults={'quantity': int(cart_p[key]['quantity'])})
            cart_len = Cart.objects.filter(user = request.user)
    else:
        if 'cartdata' in request.session:
            try:
                cart_len = request.session['cartdata']
            except:
                cart_len = 0
        else:
            cart_len = 0
    return {'cart_len': cart_len}