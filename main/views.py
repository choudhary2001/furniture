from django.shortcuts import render
from django.shortcuts import render, redirect, get_object_or_404
from main.forms import SignupForm
from django.contrib.auth.models import User
import uuid
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.template import Context
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from .forms import SignupForm
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.core.validators import validate_email
from django.db import IntegrityError
import random
from main.models import crousel, User_verification, Category, Product, productreview, Cart, Address, Order, WarrantyRegistration, WarrantyClaim, Partner, Contact, Profile, Complainet, News, Faq, OrderData, Wish, Offer, Subscribe, Privacy_Policy, About, Return_Policy, Terms_Condition, Video
from django.db.models import Max, Min, Count, Avg
from django.core.paginator import Paginator
from django.http import JsonResponse, HttpResponse, request, response
from django.views.decorators.csrf import csrf_exempt
from django.db.models.query_utils import Q
import razorpay
from django.conf import settings
from django.http import HttpResponseBadRequest
from django.utils import timezone
from django.shortcuts import redirect, get_object_or_404
from django.http import JsonResponse
from .models import Cart, Product
from django.core.exceptions import ValidationError
from main.serializers import WarrantyRegistrationSerializer
from django.core.exceptions import ObjectDoesNotExist
import os
from twilio.rest import Client
# import track
import urllib.request
import urllib.parse

account_sid = settings.TWILIO_ACCOUNT_SID
auth_token = settings.TWILIO_AUTH_TOKEN
client = Client(account_sid, auth_token)


razorpay_client = razorpay.Client(auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))
 

# track.api_key =  settings.INTERKART_APII
test_local_api = settings.TEST_LOCAL_API

def on_error(error, queue_msg):
    print("An error occurred", error)
    print("Queue message", queue_msg)

# track.debug = True
# track.on_error = on_error



def index(request):
    if request.user.is_staff:
        return redirect('/admin')
    try:
        c = crousel.objects.all()
    except Exception as e:
        c = {}
    print(c)
    n = News.objects.filter(status=True)
    p = Product.objects.filter(is_featured = True).first()
    faq = Faq.objects.filter(status="Show").order_by('-date_added')
    products = Product.objects.all().order_by('-date_added')[:10]
    context = {
        'crousel' : c,
        'title':'Home',
        'news' : n,
        'featured' : p,
        'faq' : faq,
        'products' : products,
    }
    return render(request, 'main/index.html', context=context)

def signup(request):
    if request.method == 'POST':
        email = request.POST['username']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        password = request.POST['password']
        print(password)
        try:
            print(email)
            validate_email(email)
            try:
                # User.objects.create_user(username=email, email=email, first_name = first_name, last_name = last_name, password=password, is_active = False)
                user = User(first_name=first_name, last_name=last_name, username=email, email=email, is_active=False)
                user.set_password(password)
                user.save()
                user = User.objects.filter(username=email).first()
                p = Profile(user=user, is_active=False)
                p.save()
                request.session['user'] = email
                fixed_digits = 6 
                otp = random.randrange(111111, 999999, fixed_digits)
                print(otp)
                v = User_verification(username=email, otp=otp)
                v.save()
                try:
                    subject = 'Account Verification'
                    message = f"""Thank you for creating an account on our website! Your OTP for account verification is: {otp}. Please enter this code in the verification field on our website to confirm your account and gain access to all our features. If you did not create an account, please ignore this message. Thank you!"""
                    from_email = 'contact@swastik.ai'
                    recipient_list = [email,]
                    send_mail(subject, message, from_email, recipient_list)
                except Exception as e:
                    print(e)
                return redirect('/user-verification')
            except IntegrityError:
                messages.error(request, f'Email or phone number is already exists, so please try another email or phone number.')
                return redirect('signup')

        except:
            if email.isdigit() == True:
                try:
                    # User.objects.create_user(username=email, first_name = first_name, last_name = last_name, password=password, is_active = False)
                    user = User(first_name=first_name, last_name=last_name, username=email, email=email, is_active=False)
                    user.set_password(password)
                    user.save()
                    request.session['user'] = email
                    user = User.objects.filter(username=email).first()
                    p = Profile(user=user, phone_number=email, is_active=False)
                    p.save()
                    fixed_digits = 6
                    otp = random.randrange(111111, 999999, fixed_digits)
                    print(otp)
                    v = User_verification(username=email, otp=otp)
                    v.save()
                    number = email
                    msg_body = f"""Thank you for creating an account on our website! Your OTP for account verification is: {otp}. Please enter this code in the verification field on our website to confirm your account and gain access to all our features. If you did not create an account, please ignore this message. Thank you!"""
                    
                    # try:
                    #     track.user(
                    #         user_id=number,
                    #         country_code="+91",
                    #         phone_number=number,
                    #         traits={
                    #             "name": user.first_name,
                    #             "phone": number
                    #         },
                    #     )

                    #     track.event(
                    #         user_id=number,
                    #         event="Account Verification",
                    #         country_code="+91",
                    #         phone_number=number,
                    #         traits={
                    #             "subject": "Account Verification",
                    #             "message": f"""Thank you for creating an account on our website! Your OTP for account verification is: {otp}. Please enter this code in the verification field on our website to confirm your account and gain access to all our features. If you did not create an account, please ignore this message. Thank you!"""
                    #         },
                    #     )  
                    #     resp =  sendSMS(test_local_api, number,
                    #         'FURNITURE', f'Verify your account by entering One Time Password.Your OTP is {otp}.Thanks FURNITURE')
                    #     print (resp)
                    # except Exception as e:
                    #     print(e)
                    return redirect('/user-verification')
                except IntegrityError:
                    print("error")
                    messages.error(request, f'Email or phone number is already exists, so please try another email or phone number.')
                    return redirect('signup')
            else:
                messages.error(request, f'Please Fill all the field correctly.')
                return redirect('signup')

        messages.success(request, f'Your account has been created ! You are now able to log in')
        return redirect('login')
    else:
        return render(request, 'main/signup.html', { 'title':'Register'})
 
def sendSMS(apikey, numbers, sender, message):
    data =  urllib.parse.urlencode({'apikey': apikey, 'numbers': numbers,
        'message' : message, 'sender': sender})
    data = data.encode('utf-8')
    request = urllib.request.Request("https://api.textlocal.in/send/?")
    f = urllib.request.urlopen(request, data)
    print(f)
    fr = f.read()
    return(fr)

def signin(request):
    if request.user.is_active:
        return redirect('index')
    next = request.GET.get('next')
    
    if request.method == 'POST':
        # AuthenticationForm_can_also_be_used__
        username = request.POST['username']
        password = request.POST['password']
        if username != None and password != None:
            user = authenticate(request, username = username, password = password)
            print(user)
            if user is not None:        
                print(user.is_active)
                if user.is_active == True:
                    login(request, user)
                    
                    if request.user.is_staff == True:
                        return redirect('admin-index')
                    print('authenticated')
                else:
                    print('not authenticated')
                    request.session['user'] = username
                    fixed_digits = 6 
                    otp = random.randrange(111111, 999999, fixed_digits)
                    print(otp)
                    v = User_verification(username=username, otp=otp)
                    v.save()
                    try:
                        validate_email(username)
                        try:
                            subject = 'Account Verification'
                            message = f"""Your verification code is {otp}. Please enter this code to verify your account and complete the registration process. If you did not request this code, please ignore this message. Thank you!"""
                            from_email = 'contact@swastik.ai'
                            recipient_list = [username,]
                            send_mail(subject, message, from_email, recipient_list)
                        except Exception as e:
                            print(e)
                        #####################
                    except:
                        if username.isdigit() == True:
                            number = username
                            msg_body = f"""Your verification code is {otp}. Please enter this code to verify your account and complete the registration process. If you did not request this code, please ignore this message. Thank you!"""

                            # track.user(
                            #     user_id=number,
                            #     country_code="+91",
                            #     phone_number=number,
                            #     traits={
                            #         "name": user.first_name,
                            #         "phone": number
                            #     }
                            # )

                            # track.event(
                            #     user_id=number,
                            #     event="Account Verification",
                            #     country_code="+91",
                            #     phone_number=number,
                            #     traits={
                            #         "subject": "Account Verification",
                            #         "message": f"""Thank you for creating an account on our website! Your OTP for account verification is: {otp}. Please enter this code in the verification field on our website to confirm your account and gain access to all our features. If you did not create an account, please ignore this message. Thank you!"""
                            #     },
                            # )

                            # resp =  sendSMS(test_local_api, username,
                            #     'FURNITURE', f'Verify your account by entering One Time Password.Your OTP is {otp}.Thanks FURNITURE')
                            # print (resp)

                    return redirect('/user-verification')
                
                if next:
                    return redirect(next)
                    
                return redirect('index')
            else:
                messages.info(request, f'Account does not exit please sign up.')
                return render(request, 'main/signin.html', {'title':'log in'})
        else:
            messages.error(request, 'Account does not exist')
            return render(request, 'main/signin.html', {'title':'log in'})
    else:
        return render(request, 'main/signin.html', {'title':'log in', 'next' : next})

def twoverificationmobile(request):
    if request.session['user']:
        try:
            mobile = request.session['user']
            print(mobile)
            username = request.GET.get('username')
            if username:
                try:
                    validate_email(username)
                    try:
                        fixed_digits = 6 
                        otp = random.randrange(111111, 999999, fixed_digits)
                        print(otp)
                        v = User_verification(username=username, otp=otp)
                        v.save()
                        subject = 'Account Verification'
                        message = f"""Your verification code is {otp}. Please enter this code to verify your account and complete the registration process. If you did not request this code, please ignore this message. Thank you!"""
                        from_email = 'contact@swastik.ai'
                        recipient_list = [username,]
                        send_mail(subject, message, from_email, recipient_list)
                    except Exception as e:
                        print(e)
                        #####################
                except:
                    if username.isdigit() == True:
                        fixed_digits = 6 
                        otp = random.randrange(111111, 999999, fixed_digits)
                        print(otp)
                        v = User_verification(username=username, otp=otp)
                        v.save()
                        number = str(username)
                        user = User.objects.filter(username = number).first()
                        msg_body = f"""Your verification code is {otp}. Please enter this code to verify your account and complete the registration process. If you did not request this code, please ignore this message. Thank you!"""
                        # track.user(
                        #     user_id=number,
                        #     country_code="+91",
                        #     phone_number=number,
                        #     traits={
                        #         "name": user.first_name,
                        #         "phone": number,
                        #     },
                            
                        # )

                        # track.event(
                        #     user_id=number,
                        #     event="Account Verification",
                        #     country_code="+91",
                        #     phone_number=number,
                        #     traits={
                        #         "subject": "Account Verification",
                        #         "message": msg_body
                        #     },
                        # )
                        # resp =  sendSMS(test_local_api, number,
                        #         'FURNITURE', f'Verify your account by entering One Time Password.Your OTP is {otp}.Thanks FURNITURE')
                        # print (resp)
                        pass
            if mobile:
                context = {
                    'number' : mobile,
                    'title':'Two Step Verification',
                }
                print(context)
                if request.method == 'POST':
                    otp = request.POST['otp']
                    print(otp)
                    try:
                        d = User_verification.objects.filter(username=mobile).latest('date_added')
                        print(d.otp)

                        if otp == d.otp:
                            user = User.objects.filter(username = mobile).first()
                            print(user)
                            user.is_active = True
                            user.save()
                            p = Profile.objects.filter(user = user).first()
                            p.is_active = True
                            p.save()
                            return redirect('login')
                        else:
                            messages.error(request, 'Account does not exist')
                            return render(request, 'main/twostepv.html',  context = context)
                    except Exception as e:
                        messages.error(request, f'{e}')
                        return render(request, 'main/twostepv.html',  context = context)
                else:
                    return render(request, 'main/twostepv.html', context = context)
        except Exception as e:
            print(e)
            return redirect('signup')
    else:
        return redirect('signup')

def forgot_password(request):
    if request.method=="POST":
        username = request.POST['username']
        u = User.objects.filter(username = username).first()
        print(u)
        if u:
            try:
                validate_email(username)
                try:
                    fixed_digits = 6 
                    otp = random.randrange(111111, 999999, fixed_digits)
                    print(otp)
                    v = User_verification(username=username, otp=otp)
                    v.save()
                    subject = 'OTP verification for password change'
                    message = f"""Your verification code is {otp}. Please enter this code to verify your account and complete the process. If you did not request this code, please ignore this message. Thank you!"""
                    from_email = 'contact@swastik.ai'
                    recipient_list = [username,]
                    try:
                        send_mail(subject, message, from_email, recipient_list,fail_silently=False,)
                    except Exception as e:
                        print(e)
                    request.session['user'] = username
                    return redirect('verify')
                except Exception as e:
                    print(e)
                    messages.error(request, f"Error at the time of sending mail.")
            except:
                if username.isdigit() == True:
                    fixed_digits = 6 
                    otp = random.randrange(111111, 999999, fixed_digits)
                    print(otp)
                    v = User_verification(username=username, otp=otp)
                    v.save()

                    number = username
                    msg_body = f"""Your verification code is {otp}. Please enter this code to verify your account and complete the registration process. If you did not request this code, please ignore this message. Thank you!"""
                    user = User.objects.filter(username = number).first()
                    print(msg_body, user)
                    # track.user(
                    #     user_id=number,
                    #     country_code="+91",
                    #     phone_number=number,
                    #     traits={
                    #         "name": user.first_name,
                    #         "phone": number,
                    #     },
                        
                    # )
                    # track.event(
                    #     user_id=number,
                    #     event="Account Verification",
                    #     country_code="+91",
                    #     phone_number=number,
                    #     traits={
                    #         "subject": "Account Verification",
                    #         "message": msg_body
                    #     },
                    # )
                    # resp =  sendSMS(test_local_api, number,
                    #             'FURNITURE', f'Verify your account by entering One Time Password.Your OTP is {otp}.Thanks FURNITURE')
                    # print (resp)
                    request.session['user'] = username
                    return redirect('verify')
        else:
            messages.error(request, f"Account not found.")
    return render(request, 'main/forgot_password.html')
    
def verify(request):
    if request.session['user']:
        try:
            mobile = request.session['user']
            print(mobile)

            if mobile:
                context = {
                    'number' : mobile,
                    'title':'Two Step Verification',
                }
                print(context)
                if request.method == 'POST':
                    otp = request.POST['otp']
                    print(otp)
                    d = User_verification.objects.filter(username=username).latest('date_added')
                    print(d.otp)
                    if otp == d.otp:
                        request.session['change_password'] = 'change'
                        request.session['user'] = mobile
                        return redirect('change_password')
                    else:
                        messages.error(request, f"Please Enter Correct OTP")
                    return render(request, 'main/verify.html',  context = context)
                else:
                    username = request.GET.get('username')
                    if username is not None:
                        try:
                            validate_email(username)
                            try:
                                fixed_digits = 6 
                                otp = random.randrange(111111, 999999, fixed_digits)
                                print(otp)
                                v = User_verification(username=username, otp=otp)
                                v.save()
                                subject = 'OTP verification for password change'
                                message = f"""Your verification code is {otp}. Please enter this code to verify your account and complete the process. If you did not request this code, please ignore this message. Thank you!"""
                                from_email = 'contact@swastik.ai'
                                recipient_list = [username,]
                                send_mail(subject, message, from_email, recipient_list)
                            except:
                                print(e)
                        except:
                            if username.isdigit() == True:
                                fixed_digits = 6 
                                otp = random.randrange(111111, 999999, fixed_digits)
                                print(otp)
                                v = User_verification(username=username, otp=otp)
                                v.save()

                                number = username
                                msg_body = f"""Your verification code is {otp}. Please enter this code to verify your account and complete the  process. If you did not request this code, please ignore this message. Thank you!"""
                                
                                user = User.objects.filter(username = number).first()
                                # track.user(
                                #     user_id=number,
                                #     country_code="+91",
                                #     phone_number=number,
                                #     traits={
                                #         "name": user.first_name,
                                #         "phone": number,
                                #     },
                                    
                                # )

                                # track.event(
                                #     user_id=number,
                                #     event="Account Verification",
                                #     country_code="+91",
                                #     phone_number=number,
                                #     traits={
                                #         "subject": "Account Verification",
                                #         "message": msg_body
                                #     },
                                # )
                                # resp =  sendSMS(test_local_api, number,
                                # 'FURNITURE', f'Verify your account by entering One Time Password.Your OTP is {otp}.Thanks FURNITURE')
                                # print (resp)
                    return render(request, 'main/verify.html', context = context)
        except Exception as e:
            print(e)
            return redirect('forgot_password')
    else:
        return redirect('forgot_password')

def change_password(request):
    try:
        if 'user' in request.session:
            if 'change_password' in request.session:
                username = request.session['user']
                if request.method == "POST":
                    user = User.objects.filter(username=username).first()
                    password = request.POST['password']
                    c_password = request.POST['c_password']
                    if password == c_password:
                        user.set_password(password)
                        user.save()
                    del request.session['change_password']
                    del request.session['user']
                    return redirect('login')
                return render(request, 'main/change_password.html')
            else:
                return redirect('signup')
        else:
            return redirect('signup')
    except KeyError:
        messages.error(request, "User not found")
        return redirect('signup')

def all_product(request, category_slug=None):
    products = Product.objects.all().order_by('-date_added')
    print(products)
    search = None
    search = request.GET.get('search')
    if search:
        products = products.filter(Q(title__icontains=search) | Q(details__icontains=search))

    categoryy = None
    category_ss = None
    categoryy = request.GET.get('category')
    if categoryy:
        category_ss = get_object_or_404(Category, slug=categoryy)
        print(category_ss)
        print("###")
        productss = []
        if category_ss.children.all():
            parent_category = category_ss.parent
            print(parent_category)
            products = Product.objects.filter(category__in=[category_ss, parent_category])
        else:
            products = products.filter(category = category_ss)
        
    if request.method == "POST":
        try:
            price_range = request.POST['price_range']
            min_price, max_price = price_range.split(' - ')
            min_p = int(min_price)
            max_p = int(max_price)
            products = products.filter(price__range=(min_p, max_p))
            pass
        except:
            pass

    slug = category_slug
    low_to_high = request.GET.get('low_to_high')
    print(low_to_high)

    if low_to_high == '0':
        products = products.order_by('price')
    elif low_to_high == '1':
        products = products.order_by('-price')
    else:
        low_to_high = None

    category_s = None
    if slug:
        category_s = get_object_or_404(Category, slug=slug)
        print(category_s)
        print("###")
        productss = []
        if category_s.children.all():
            subcategories = [category_s] + list(category_s.children.all())
            print(subcategories)
            products = Product.objects.filter(category__in=subcategories)
        else:
            products = products.filter(category = category_s)
    print(products)
    productss = Product.objects.all().order_by('-date_added')
    min_price = productss.aggregate(Min('price'))
    max_price = productss.aggregate(Max('price'))
    p = productss.aggregate(Min('price'),Max('price'))
    print(productss)

    paginator = Paginator(products, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    print(low_to_high)
    if category_slug:
        capitalized_string = category_slug.title().replace("-", " ")
    else:
        capitalized_string = None
    context = {
        'products' : page_obj,
        'category' : category_s,
        'low_to_high' : low_to_high,
        'min_price' : min_price,
        'max_price' : max_price,
        'minMaxPrice' : p,
        'search' : search,
        'categoryy' : categoryy,
        'title' : 'Products',
        'cat' :  capitalized_string,
        'cats' : category_slug
    }
    return render(request, 'main/shop.html', context = context)

def product_details(request,category_slug, product_slug):
    product = get_object_or_404(Product, slug = product_slug)
    related_products = Product.objects.filter(
        category=product.category).exclude(slug=product_slug)
    reviews = productreview.objects.filter(product=product)
    avg_reviews = productreview.objects.filter(
        product=product).aggregate(avg_rating=Avg('review_rating'))
    if avg_reviews['avg_rating'] is not None:
        avg_rating = int(avg_reviews['avg_rating'])
    else:
        avg_rating = 0
    Context = {
        'product_detail' : product,
        'related_product' : related_products,
        'reviews' : reviews,
        'avg_rating' : avg_rating,
    }
    return render(request, 'main/shop-details.html', context=Context)

def cart_add(request, product_slug):
    increase = request.GET.get('increase')
    decrease = request.GET.get('decrease')
    quantity = request.GET.get('quantity')
    print(increase, decrease, quantity)
    cart_data = {}
    cart_data_len = 0
    total_price = 0
    total_not_price = 0

    if increase == '1':
        quantity = 1
    elif decrease == '0':
        quantity = -1
    elif quantity:
        quantity = int(quantity)

    product = get_object_or_404(Product, slug=product_slug)
    cart_p = {
        str(product_slug): {
            'product': product_slug,
            'quantity': quantity,
        }
    }
    o_quantity = None

    if request.method == "POST":
        quantity_p = request.POST.get('quantity_p')
        if quantity_p:
            o_quantity = int(quantity_p)
            cart_p = {
                str(product_slug): {
                    'product': product_slug,
                    'quantity': o_quantity,
                }
            }

    l = None

    if request.user.is_authenticated:
        if request.user.is_active:
            try:
                d = Cart.objects.filter(product=product, user=request.user).first()
                if d:
                    if d.quantity == 1 and decrease == '0':
                        d.delete()
                        l = '/cart'
                    else:
                        if o_quantity:
                            qty = d.quantity + o_quantity
                        else:
                            qty = d.quantity + quantity
                        d.quantity = qty
                        d.save()
                else:
                    if not increase or not decrease:
                        for key, value in cart_p.items():
                            obj, created = Cart.objects.get_or_create(user=request.user, product=product,
                                                                      defaults={'quantity': value['quantity']})
            except Exception as e:
                if not increase or not decrease:
                    for key, value in cart_p.items():
                        obj = Cart(user=request.user, product=product, quantity=value['quantity'])
                        obj.save()
            cart_data = Cart.objects.filter(user=request.user).values('product__slug', 'quantity')
            cart_data_len = len(cart_data)
    else:
        if 'cartdata' in request.session:
            cart_data = request.session['cartdata']
            if str(product_slug) in cart_data:
                if cart_data[product_slug]['quantity'] == 1 and decrease == '0':
                    del cart_data[product_slug]
                    l = '/cart'
                else:
                    if o_quantity is not None:
                        cart_data[product_slug]['quantity'] += o_quantity
                    else:
                        cart_data[product_slug]['quantity'] += cart_p[str(product_slug)]['quantity']
                
            else:
                cart_data.update(cart_p)
            request.session['cartdata'] = cart_data
        else:
            request.session['cartdata'] = cart_p
        cart_data_len = len(request.session['cartdata'])

    if 'cartdata' in request.session:
        cart_data = request.session['cartdata']
        cart_pp = {}
        for key, value in cart_data.items():
            slug = cart_data[key]['product']
            product = get_object_or_404(Product, slug=slug)
            cart_pp[str(slug)] = {
                'product': product,
                'quantity': int(cart_data[key]['quantity']),
            }
            productt = cart_pp[slug]['product']
            quantityy = cart_pp[slug]['quantity']
            price = productt.price
            total_price += price * quantityy
            not_price = productt.not_price
            total_not_price += not_price * quantityy
        cart_data = cart_pp
        if request.user.is_authenticated and request.user.is_active:
            for key, value in cart_data.items():
                obj, created = Cart.objects.get_or_create(user=request.user, product=value['product'],
                                                            defaults={'quantity': value['quantity']})
                if not created:
                    obj.quantity += value['quantity']
                    obj.save()
            request.session.pop('cartdata')  # Remove the cart data from the session

    if request.user.is_authenticated and request.user.is_active:
        cart_data = Cart.objects.filter(user=request.user).all()
        for cart_item in cart_data:
            total_price += cart_item.product.price * cart_item.quantity
            total_not_price += cart_item.product.not_price * cart_item.quantity
        cart_data = Cart.objects.filter(user=request.user).values('product__slug', 'quantity')


    response = {
        'cart_data': list(cart_data),
        'totalitems': cart_data_len,
        'location': l,
        'total_price' : total_price,
        'total_not_price' : total_not_price
    }
    return JsonResponse(response)

def cart(request):
    total_price = 0
    total_not_price = 0
    cart_data = {}
    try:
        if 'cartdata' in request.session:
            cart_data = request.session['cartdata']
            cart_p = {}
            for key, value in cart_data.items():
                slug = cart_data[key]['product']
                product = get_object_or_404(Product, slug=slug)
                cart_p[str(slug)] = {
                    'product': product,
                    'quantity': int(cart_data[key]['quantity']),
                }
                productt = cart_p[slug]['product']
                quantityy = cart_p[slug]['quantity']
                price = productt.price
                total_price += price * quantityy
                not_price = productt.not_price
                total_not_price += not_price * quantityy
            cart_data = cart_p
            if request.user.is_authenticated and request.user.is_active:
                for key, value in cart_data.items():
                    obj, created = Cart.objects.get_or_create(user=request.user, product=value['product'],
                                                              defaults={'quantity': value['quantity']})
                    if not created:
                        obj.quantity += value['quantity']
                        obj.save()
                request.session.pop('cartdata')  # Remove the cart data from the session

        if request.user.is_authenticated and request.user.is_active:
            cart_data = Cart.objects.filter(user=request.user).all()
            total_price = 0
            total_not_price = 0
            for cart_item in cart_data:
                total_price += cart_item.product.price * cart_item.quantity
                total_not_price += cart_item.product.not_price * cart_item.quantity

    except Exception as e:
        print(e)
        cart_data = {}
        total_price = 0
        total_not_price = 0

    context = {
        'cart_data': cart_data,
        'total_price': total_price,
        'total_not_price': total_not_price
    }
    return render(request, 'main/shopping-cart.html', context=context)

def cart_remove(request, product_slug):
    print(product_slug)
    if request.user.is_authenticated:
        if request.user.is_active == True:
            product = get_object_or_404(Product, slug = product_slug)
            print(product)
            cart_data = Cart.objects.filter(user = request.user, product = product)
            cart_data.delete()

    if 'cartdata' in request.session:
        cart_data = request.session['cartdata']
        del cart_data[product_slug]
        request.session['cartdata'] = cart_data
    else:
        cart_data = {}
    print(cart_data)
    return redirect('cart')

def clear_cart(request):
    if request.user.is_authenticated:
        if request.user.is_active:
            Cart.objects.filter(user=request.user).delete()
    if 'cartdata' in request.session:
        del request.session['cartdata']
    return redirect('cart')

def wishlist(request):
    if request.user.is_authenticated:
        if request.user.is_active == True:   
            wishlist = Wish.objects.filter(user = request.user)
            print(wishlist)
            context = {
                'wishlist' : wishlist,
                'title' : "wishlist"
            }
            return render(request, 'main/wishlist.html', context = context)
    return redirect('login')

def add_wishlist(request, product_slug):
    if request.user.is_authenticated:
        if request.user.is_active == True:
            product = get_object_or_404(Product, slug=product_slug)
            existing_wish = Wish.objects.filter(user=request.user, product=product).exists()

            if not existing_wish:
                w = Wish(user=request.user, product=product)
                w.save()
                response = {'data': 'success'}
                return JsonResponse(response)

    return redirect('login')
    
def remove_wishlist(request, w_id):
    if request.user.is_authenticated:
        if request.user.is_active == True:
            w = Wish.objects.filter(w_id = w_id, user = request.user).first()
            w.delete()
            return redirect('wishlist')
    return redirect('login')

@csrf_exempt
def add_product_review(request):
    if request.user.is_authenticated:
        if request.user.is_active == True:
            if request.method == 'POST':
                product_slug = request.POST['product']
                product = get_object_or_404(Product, slug = product_slug)
                rating = request.POST['rating']
                message = request.POST['message']
                print(rating, message)
                review = productreview(product = product, user = request.user, review_rating = rating, review_text = message )
                review.save()
                r = {
                    'success': True,
                    'message' : 'Done'
                    }
                return JsonResponse(r)
            else:
                messages.success(request, f"Somthing went wrong. Try again.")
                r = {
                    'message' : 'Somthing went wrong. Try again.'
                }
                return JsonResponse(r)
        else:
            messages.success(request, f"Please Login first then try again.")
            r = {
                'success': False, 
                'message' : 'Please Login first then try again.'
                }
            return JsonResponse(r)
    else:
        messages.success(request, f"Please Login first then try again.")
        r = {
            'success': False, 
            'message' : 'Please Login first then try again.'
        }
        return JsonResponse(r)

def add_address(request):
    if request.user.is_authenticated:
        if request.user.is_active == True:
            if request.method == 'POST':
                first_name = request.POST['first_name']
                last_name = request.POST['last_name']
                country = request.POST['country']
                street_address= request.POST['street_address']
                appartment = request.POST['appartment']
                town = request.POST['town']
                state = request.POST['state']
                postcode = request.POST['postcode']
                phone = request.POST['phone']
                email = request.POST['email']
                address = Address(user = request.user, first_name = first_name, last_name = last_name, country = country, address = street_address, local_address = appartment, town = town, state = state, postalcode =postcode, phone = phone, email = email)
                print(address)
                address.save()
                if request.GET.get('profile'):
                    return redirect('profile')
                return redirect('checkout_page')
    return redirect('login')

def change_address(request, address_id):
    if request.user.is_authenticated:
        if request.user.is_active == True:
            addres = Address.objects.filter(address_id = address_id).first()
            print(addres)
            if request.method == 'POST':
                first_name = request.POST['first_name']
                last_name = request.POST['last_name']
                country = request.POST['country']
                street_address= request.POST['street_address']
                appartment = request.POST['appartment']
                town = request.POST['town']
                state = request.POST['state']
                postcode = request.POST['postcode']
                phone = request.POST['phone']
                email = request.POST['email']
                addres.first_name = first_name
                addres.last_name = last_name
                addres.country = country
                addres.address = street_address
                addres.local_address = appartment
                addres.town = town
                addres.state = state
                addres.postalcode = postcode
                addres.phone = phone
                addres.email = email
                addres.save()
                if request.GET.get('profile'):
                    return redirect('profile')
                return redirect('checkout_page')

            context = {
                'address' : addres
            }
            return render(request, 'main/address_change.html', context=context)
    return redirect('login')

def delete_address(request, address_id):
    if request.user.is_authenticated:
        if request.user.is_active == True:
            addres = Address.objects.filter(address_id = address_id).first()
            addres.delete()
            if request.GET.get('profile'):
                return redirect('profile')
            return redirect('checkout_page')
    return redirect('login')

def checkout_page(request):
    if request.user.is_authenticated:
        if request.user.is_active == True:
            total_price = 0
            total_cart_p = 0
            total_cart_q = 0
            total_not_price = 0
            taxx = 0
            cart_data = Cart.objects.filter(user = request.user)
            print(cart_data)
            if len(cart_data) > 0:
                taxx = 0
                for c in cart_data:
                    total_am = int(c.quantity) * c.product.price
                    total_not_price_am = int(c.quantity) * c.product.not_price
                    total_cart_p = int(total_cart_p)  +  int(total_am)
                    total_not_price = int(total_not_price)  +  int(total_not_price_am)
                    total_cart_q = int(total_cart_q)  + int(c.quantity)
                    taxx = taxx + round(int(total_am) * c.product.tax / 100, 2)
                tp = total_cart_p + taxx
                if request.method == 'POST':
                    adr = request.POST.get('address')
                    print(adr)          
                    if adr:
                        addres = Address.objects.filter(user = request.user, address_id = adr).first()
                        if 'cod' in request.POST:
                            order = Order.objects.create(user=request.user, address=addres, order_status = "None", total_price = 0 )
                            order_id = order.order_id
                            return redirect(f'checkout/payment/{order_id}')
                        elif 'payment' in request.POST:
                            order = Order.objects.create(user=request.user, address=addres, order_status = 'Placed', payment_status= "Unpaid", payment_method = 'Online Payment', total_price = 0)
                            total_cart_p = 0
                            total_not_price = 0
                            total_cart_q = 0
                            tax = 0
                            for c in cart_data:
                                total_am = int(c.quantity) * c.product.price
                                total_cart_p = int(total_cart_p)  +  int(total_am)
                                total_cart_q = int(total_cart_q)  + int(c.quantity)
                                total_not_price_am = int(c.quantity) * c.product.not_price
                                total_not_price = int(total_not_price)  +  int(total_not_price_am)
                                tax = tax + round(int(total_am) * c.product.tax / 100, 2)
                                order_data = OrderData(user = request.user, product = c.product, total_price = total_am,
                                            quantity = c.quantity )
                                order_data.save()
                                order.product.add(order_data)
                            order.quantity = total_cart_q
                            total_price = total_cart_p + tax
                            order.total_price = int(total_price)
                            currency = 'INR'
                            amount = int(total_price) * 100  # Rs. 200
                            # Create a Razorpay Order
                            razorpay_order = razorpay_client.order.create(dict(amount=amount,
                                                                            currency=currency,
                                                                            payment_capture='0'))
                            print(razorpay_order)
                            # order id of newly created order.
                            razorpay_order_id = razorpay_order['id']
                            callback_url = 'paymenthandler/'
                            order.payment_id = razorpay_order_id
                            order.save()

                            o = Order.objects.filter(user = request.user, payment_id = razorpay_order_id).first()
                            print(o)
                            c = o.product.all()
                            print(c)
                            # we need to pass these details to frontend.
                            context = {}
                            context['address'] = addres
                            context['order'] = o
                            context['cart_data'] = cart_data
                            context['total_price'] = total_price
                            context['total_cart_price'] = total_cart_p
                            context['total_not_price'] = total_not_price
                            context['tax'] = tax
                            context['total_not_price'] = total_not_price
                            context['razorpay_order_id'] = razorpay_order_id
                            context['razorpay_merchant_key'] = settings.RAZOR_KEY_ID
                            context['razorpay_amount'] = amount
                            context['currency'] = currency
                            context['callback_url'] = callback_url
                            context['store_name'] = 'Gluoen Electrical'

                        return render(request, 'main/payment.html', context = context)
                            
                    messages.success(request, f"Please add shipping details.")
                    return redirect('checkout_page')

                addr = Address.objects.filter(user = request.user).order_by('-date_added')
                context = {
                    'cart_data' : cart_data,
                    'total_price' : tp,
                    'total_cart_price' : total_cart_p,
                    'total_not_price' : total_not_price,
                    'address' : addr,
                    'tax' : taxx
                }
                return render(request, 'main/checkout.html', context = context)
            else:
                return redirect('products')
    else:
        return redirect('login')

def payment_process(request, order_id):
    if request.user.is_authenticated:
        if request.user.is_active == True:
            total_cart_p = 0
            total_cart_q = 0
            tax = 0
            total_not_price = 0
            coupon_p = 0
            cart_data = Cart.objects.filter(user = request.user)
            order = Order.objects.filter(order_id = order_id, user = request.user).first()
            if request.method == "POST":
                coupon_code = request.POST['code']
                print(coupon_code)
                coupon = Offer.objects.filter(code=coupon_code, status=True).first()
                print(coupon)
                for c in cart_data:
                    total_am = c.quantity * c.product.price
                    total_not_price_am = int(c.quantity) * c.product.not_price
                    total_not_price = int(total_not_price)  +  int(total_not_price_am)
                    total_cart_p += total_am
                    total_cart_q += c.quantity
                    tax += round((total_am * c.product.tax) / 100, 2)
                    if coupon and coupon.status and coupon.start_date <= timezone.now() <= coupon.end_date:
                        if c.product == coupon.product:
                            coupon_p += round((total_am * coupon.discount) / 100, 2)
                            order_data = OrderData(
                                user=request.user,
                                product=c.product,
                                total_price=total_am,
                                quantity=c.quantity,
                                coupon=coupon
                            )
                            order_data.save()
                            order.product.add(order_data)
                            
                    else:
                        order_data = OrderData(
                            user=request.user,
                            product=c.product,
                            total_price=total_am,
                            quantity=c.quantity
                        )
                        order_data.save()
                        order.product.add(order_data)
                order.quantity = total_cart_q
                if coupon_p:
                    total_price = total_cart_p + tax - coupon_p
                    order.total_price = int(total_cart_p + tax - coupon_p)
                else:
                    total_price = total_cart_p + tax
                    order.total_price = int(total_cart_p + tax)
                order.save()
                currency = 'INR'
                amount = int(total_price) * 100 # Rs. 200
                # Create a Razorpay Order
                razorpay_order = razorpay_client.order.create(dict(amount=amount,
                                                                currency=currency,
                                                                payment_capture='0'))
                print(razorpay_order)
                # order id of newly created order.
                razorpay_order_id = razorpay_order['id']
                callback_url = 'paymenthandler/'
                order.payment_id = razorpay_order_id
                order.save()

                o = Order.objects.filter(user = request.user, payment_id = razorpay_order_id).first()
                print(o)
                c = o.product.all()
                print(c)
                # we need to pass these details to frontend.
                user = request.user
                login(request, request.user)
                context = {}
                context['address'] = o.address
                context['order'] = o
                context['coupon'] = coupon_p
                context['cart_data'] = cart_data
                context['total_price'] = total_price
                context['total_cart_price'] = total_cart_p
                context['tax'] = tax
                context['total_not_price'] = total_not_price
                context['razorpay_order_id'] = razorpay_order_id
                context['razorpay_merchant_key'] = settings.RAZOR_KEY_ID
                context['razorpay_amount'] = amount
                context['currency'] = currency
                context['callback_url'] = callback_url
                context['store_name'] = 'Gluoen Electrical'
                return render(request, 'main/payment.html', context = context)
            else:
                return redirect('checkout_page')
    return redirect('login')

@csrf_exempt
def paymenthandler(request):
    try:
        user = request.user
        login(request, request.user)
    except Exception as e:
        print(e)
    # only accept POST request.
    if request.method == "POST":
        try:
            # get the required parameters from post request.
            payment_id = request.POST.get('razorpay_payment_id', '')
            razorpay_order_id = request.POST.get('razorpay_order_id', '')
            signature = request.POST.get('razorpay_signature', '')
            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature
            }
            print(params_dict)
            # verify the payment signature.
            result = razorpay_client.utility.verify_payment_signature(params_dict)
            print(result)
            if result == True:
                oop = Order.objects.filter(payment_id = razorpay_order_id).first()
                print(oop)
                print(oop.total_price)
                price = int(oop.total_price)
                print(price)
                amount = int(price) * 100  # Rs. 200
                try:
                    # capture the payemt
                    oop.payment_status = "Paid"
                    oop.save()
                    number = str(oop.address.phone)

                    try:
                        user = oop.user
                        login(request, user)
                    except Exception as e:
                        print(e)

                    
                    try:
                        subject = 'Order Confirmation'
                        message = f"""Dear {oop.address.first_name}, Thank you for your recent order from our online store. We are delighted to inform you that your order has been successfully processed.Your order details are as follows:
                                Order ID: {oop.order_id}
                                Total Amount: {oop.total_price}.
                                Shop with us again. For more details login to https://gluoenelectrical.com.
                                The FURNITURE
                                """
                        from_email = 'contact@swastik.ai'
                        recipient_list = [oop.address.email,]
                        send_mail(subject, message, from_email, recipient_list)
                    except Exception as e:
                        print(e)
                    msg_body = f"""Dear {oop.address.first_name}, Thank you for your recent order from our online store. We are delighted to inform you that your order has been successfully processed.Your order details are as follows: Order ID: {oop.order_id} Total Amount: {oop.total_price}. Shop with us again. For more details login to https://gluoenelectrical.com. The FURNITURE"""
                    # track.user(
                    #     user_id=number,
                    #     country_code="+91",
                    #     phone_number=number,
                    #     traits={
                    #         "name": oop.address.first_name,
                    #         "phone": number,
                    #     },   
                    # )
                    # track.event(
                    #     user_id=number,
                    #     event="Order",
                    #     country_code="+91",
                    #     phone_number=number,
                    #     traits={
                    #         "subject": subject,
                    #         "message": msg_body
                    #     },
                    # )
                    # resp =  sendSMS(test_local_api, number,
                    #     'FURNITURE', f'Dear {oop.address.first_name} Your order id {oop.order_id} has been {oop.order_status} Thanks Furniture')
                    # print (resp)
                    # render success page on successful caputre of payment
                    return redirect('payment_success')
                except Exception as e:
                    print(e)
                    # if there is an error while capturing payment.
                    return redirect('payment_failed')

            else:
                # if signature verification fails.
                oop.payment_status = "Failed"
                oop.order_status = "Failed"
                oop.save()
                return redirect('payment_failed')
        except Exception as e:
            print(e)
 
            # if we don't find the required parameters in POST data
            return HttpResponseBadRequest()
    else:
       # if other than POST request is made.
        return HttpResponseBadRequest()

def payment_success(request):
    try:
        user = request.user
        login(request, request.user)
    except Exception as e:
        print(e)
    if request.user.is_authenticated:
        if request.user.is_active == True:
            cart_data = Cart.objects.filter(user = request.user)
            print(cart_data)
            for cart_item in cart_data:
                # Decrease the quantity of the product in the cart
                cart_item.product.quantity -= cart_item.quantity
                cart_item.product.save()
            cart_data.delete()
            if 'cartdata' in request.session:
                del request.session['cartdata']
            oop = Order.objects.filter(user = request.user).first()
            number = str(oop.address.phone)
            oop.payment_status = "Paid"
            oop.save()
            msg_body = f"""Dear {oop.address.first_name}, Thank you for your recent order from our online store. We are delighted to inform you that your order has been successfully processed.Your order details are as follows: Order ID: {oop.order_id} Total Amount: {oop.total_price}. Shop with us again. For more details login to https://gluoenelectrical.com. The FURNITURE"""
            try:
                subject = 'Order Confirmation'
                # message = f"""Dear {oop.address.first_name}, Thank you for your recent order from our online store. We are delighted to inform you that your order has been successfully processed.Your order details are as follows:
                #         Order ID: {oop.order_id}
                #         Total Amount: {oop.total_price}.
                #         Shop with us again. For more details login to https://gluoenelectrical.com.
                #         The FURNITURE
                #         """
                # from_email = 'contact@swastik.ai'
                # recipient_list = [oop.address.email,]
                # try:
                #     # send_mail(subject, message, from_email, recipient_list)
                # except Exception as e:
                #     print(e)
                user = request.user
                # track.user(
                #     user_id=number,
                #     country_code="+91",
                #     phone_number=number,
                #     traits={
                #         "name": user.first_name,
                #         "phone": number,
                #     },
                    
                # )
                # track.event(
                #     user_id=number,
                #     event="Order",
                #     country_code="+91",
                #     phone_number=number,
                #     traits={
                #         "subject": subject,
                #         "message": msg_body
                #     },
                # )
                # resp =  sendSMS(test_local_api, number,
                #     'FURNITURE', f'Dear {oop.address.first_name} Your order id {oop.order_id} has been {oop.order_status} Thanks Furniture')
                # print (resp)
            except Exception as e:
                print(e)
            return render(request, 'main/ordercomplete.html')
    return redirect('login')

def payment_failed(request):
    if request.user.is_authenticated:
        if request.user.is_active == True:
            oop = Order.objects.filter(user = request.user).first()
            number = str(oop.address.phone)
            
            msg_body = f"""We regret to inform you that there was an issue processing your payment for the order placed on {oop.date_added}. Unfortunately, the payment transaction was declined by your bank. Please note that your order has not been completed and will not be processed until payment has been successfully received. Shop with us again. For more details login to https://gluoenelectrical.com. The FURNITURE"""

            try:
                subject = 'Payment Failed'
                message = msg_body
                from_email = 'contact@swastik.ai'
                recipient_list = [oop.address.email,]
                try:
                    send_mail(subject, message, from_email, recipient_list)
                except Exception as e:
                    print(e)
                u = request.user
                # track.user(
                #     user_id=number,
                #     country_code="+91",
                #     phone_number=number,
                #     traits={
                #         "name": u.first_name,
                #         "phone": number,
                #     },
                    
                # )
                # track.event(
                #     user_id=number,
                #     event="Order",
                #     country_code="+91",
                #     phone_number=number,
                #     traits={
                #         "subject": subject,
                #         "message": msg_body
                #     },
                # )
                # resp =  sendSMS(test_local_api, number,
                #     'FURNITURE', f'Dear {oop.address.first_name} Your order id {oop.order_id} has been {oop.order_status} Thanks Furniture')
                # print (resp)
            except Exception as e:
                print(e)
            return render(request, 'main/orderfailed.html')
    return redirect('login')

def cod_payment(request, order_id):
    if request.user.is_authenticated:
        if request.user.is_active == True:
            total_price = 0
            total_cart_p = 0
            total_cart_q = 0
            total_not_price = 0
            cart_data = Cart.objects.filter(user = request.user)
            print(cart_data)
            taxx = 0
            for c in cart_data:
                total_am = int(c.quantity) * c.product.price
                total_not_price_am = int(c.quantity) * c.product.not_price
                total_cart_p = int(total_cart_p)  +  int(total_am)
                total_not_price = int(total_not_price)  +  int(total_not_price_am)
                total_cart_q = int(total_cart_q)  + int(c.quantity)
                taxx = taxx + round(int(total_am) * c.product.tax / 100, 2)
            total_tax = total_cart_p + taxx
            request.session['order'] = 'order'
            order = Order.objects.filter(order_id = order_id, user = request.user).first()
            print(order)
            context = {
                'cart_data' : cart_data,
                'total_cart_price' : total_cart_p,
                'total_not_price' : total_not_price,
                'address' : order.address,
                'order' : order,
                'tax' : taxx,
                'total_price' : total_tax
            }

            return render(request, 'main/payment_cod.html', context = context)
    else:
        return redirect('login')

def complete_order(request, order_id):
    if request.user.is_authenticated and request.user.is_active:
        if 'order' in request.session:
            if request.method == "POST":
                # order_id = request.session['order']
                order = Order.objects.filter(order_id=order_id, user=request.user).first()

                cart_data = Cart.objects.filter(user=request.user)
                if 'payment' in request.POST:
                    total_cart_p = 0
                    total_cart_q = 0
                    total_tax = 0
                    coupon_p = 0
                    coupon_code = request.session.get('coupon')
                    print(coupon_code)
                    coupon = None
                    if coupon_code:
                        coupon = Offer.objects.filter(code=coupon_code, status=True).first()
                    print(coupon)
                    for c in cart_data:
                        total_am = c.quantity * c.product.price
                        total_cart_p += total_am
                        total_cart_q += c.quantity
                        total_tax += round((total_am * c.product.tax) / 100, 2)
                        if coupon and c.product == coupon.product:
                            coupon_p += round((total_am * coupon.discount) / 100, 2)
                            order_data = OrderData(
                                user=request.user,
                                product=c.product,
                                total_price=total_am,
                                quantity=c.quantity,
                                coupon=coupon
                            )
                            order_data.save()
                            
                            order.product.add(order_data)
                        else:
                            order_data = OrderData(
                                user=request.user,
                                product=c.product,
                                total_price=total_am,
                                quantity=c.quantity
                            )
                            order_data.save()
                            order.product.add(order_data)
                    
                    order.order_status = "Placed"
                    order.payment_status = "Unpaid"
                    order.payment_method = "Cash On Delivery"
                    order.quantity = total_cart_q
                    if coupon_p:
                        order.total_price = total_cart_p + total_tax - coupon_p
                    else:
                        order.total_price = total_cart_p + total_tax
                    
                    order.save()
                    for cart_item in cart_data:
                        # Decrease the quantity of the product in the cart
                        cart_item.product.quantity -= cart_item.quantity
                        cart_item.product.save()
                    cart_data.delete()
                    if 'order' in request.session:
                        del request.session['order']
                    if 'coupon' in request.session:
                        del request.session['coupon']
                    if 'cartdata' in request.session:
                        del request.session['cartdata']
                    
                    # Sending SMS using Twilio
                    number = str(order.address.phone)
 
                    # Sending email
                    subject = 'Order Confirmation'
                    message = f"Dear {order.address.first_name}, Thank you for your recent order from our online store. We are delighted to inform you that your order has been successfully processed. Your order details are as follows:\n\nOrder ID: {order.order_id}\nTotal Amount: {order.total_price}.\n\nShop with us again. For more details, please visit our website.\n\nThe FURNITURE"
                    from_email = 'contact@swastik.ai'
                    recipient_list = [order.address.email]
                    try:
                        send_mail(subject, message, from_email, recipient_list)
                    except Exception as e:
                        print(e)
                    user = request.user
                    # track.user(
                    #     user_id=number,
                    #     country_code="+91",
                    #     phone_number=number,
                    #     traits={
                    #         "name": user.first_name,
                    #         "phone": number,
                    #     },
                        
                    # )

                    # track.event(
                    #     user_id=number,
                    #     event="Order",
                    #     country_code="+91",
                    #     phone_number=number,
                    #     traits={
                    #         "subject": subject,
                    #         "message": message
                    #     },
                    # )

                    # resp =  sendSMS(test_local_api, number,
                    # 'FURNITURE', f'Dear {order.address.first_name} Your order id {order.order_id} has been {order.order_status} Thanks Furniture')
                    # print (resp)

                    return render(request, 'main/ordercomplete.html')
                
                elif 'coupon' in request.POST:
                    coupon_code = request.POST['code']
                    print(coupon_code)
                    coupon = Offer.objects.filter(code=coupon_code, status=True).first()
                    print(coupon)
                    if coupon and coupon.start_date <= timezone.now() <= coupon.end_date:
                        request.session['coupon'] = coupon.code
                    else:
                        request.session.pop('coupon', None)
                    
                    total_price = 0
                    total_not_price = 0
                    tax = 0
                    total_cart_p = 0
                    total_cart_q = 0
                    if 'coupon' in request.session:
                        coupon_code = request.session['coupon']
                        coupon = Offer.objects.filter(code=coupon_code, status=True).first()
                    for c in cart_data:
                        total_am = c.quantity * c.product.price
                        total_not_price_am = int(c.quantity) * c.product.not_price
                        total_not_price += int(total_not_price_am)
                        total_cart_p += total_am
                        total_cart_q += c.quantity
                        tax += round((total_am * c.product.tax) / 100, 2)
                        if coupon and c.product == coupon.product:
                            total_price = round((total_am) * coupon.discount / 100, 2)
                    
                    total_ = total_cart_p + tax - total_price
                    order.quantity = total_cart_q
                    order.total_price = total_
                    order.save()
                    request.session['order'] = order_id
                    cart_data = Cart.objects.filter(user=request.user)

                    context = {
                        'cart_data': cart_data,
                        'total_cart_price': total_cart_p,
                        'total_not_price': total_not_price,
                        'address': order.address,
                        'tax': tax,
                        'order': order,
                        'coupon': total_price,
                        'total_price': total_
                    }

                    return render(request, 'main/payment_cod.html', context)
                
                else:
                    request.session['order'] = order_id
                    return redirect('cart')
            
            else:
                return redirect('cart')
        
        else:
            return redirect('profile')
    
    else:
        return redirect('login')

def invoice(request, invoice_id=None):
    if request.user.is_authenticated:
        if request.user.is_active == True:
            if invoice_id != None:
                i = Order.objects.filter(user = request.user,order_id = invoice_id).first()
                context = {
                    'invoice' : i,
                }
                return render(request, 'main/invoice.html', context = context)
            else:
               return redirect('profile') 
    else:
        return redirect('login')

def customer_service(request):
    faq = Faq.objects.filter(status="Show").order_by('-date_added')
    context = {
        'faq' : faq,
        'title': 'Customer Services'
    }
    return render(request, 'main/customer_service.html', context = context)

def warranty_registration(request):
    if request.method == "POST":
        name = request.POST['name']
        email = request.POST['email']
        mobile = request.POST['number']
        product = request.POST['product']
        manufacturing_date = request.POST['manufacturing_date']
        batch_no = request.POST['batch_no']
        serial_no = request.POST['serial_no']
        color = request.POST['color']
        order_date = request.POST['order_date']
        invoice_no = request.POST['invoice_no']
        invoice = request.FILES['invoice']
        price = request.POST['price']
        state = request.POST['state']
        district = request.POST['district']
        city = request.POST['city']
        postoffice = request.POST['postoffice']
        zipcode = request.POST['zipcode']
        landmark = request.POST['landmark']
        purchasse_source = request.POST['category']
        address = request.POST['address']

        wrr_reg = WarrantyRegistration.objects.filter(invoice_no = invoice_no, product_serial_no = serial_no).all()
        if wrr_reg:
            messages.error(request, f"Your Warranty registration is allready completed.")
            return redirect('customer_service')

        if request.user.is_authenticated:
            warranty = WarrantyRegistration(user= request.user, name = name, email = email, 
            mob_number = mobile, product = product, product_manufacturing_date = manufacturing_date,
            product_batch_no = batch_no, product_serial_no = serial_no, product_color = color, 
            order_date = order_date, invoice_no = invoice_no, invoice = invoice, price = price,
            state = state, district = district, city = city, post_office = postoffice, zipcode = zipcode,
            land_mark = landmark, purchase_source = purchasse_source, address = address)
            warranty.save()
        else:
            warranty = WarrantyRegistration(name = name, email = email, 
            mob_number = mobile, product = product, product_manufacturing_date = manufacturing_date,
            product_batch_no = batch_no, product_serial_no = serial_no, product_color = color, 
            order_date = order_date, invoice_no = invoice_no, invoice = invoice, price = price,
            state = state, district = district, city = city, post_office = postoffice, zipcode = zipcode,
            land_mark = landmark, purchase_source = purchasse_source, address = address)
            warranty.save()

        wrr = WarrantyRegistration.objects.filter(name = name, product_batch_no = batch_no).first()
        number = str(mobile)
        
        try:
            subject = 'Warranty Registration'
            message = f"""Dear Customer, Your registration for {product} is successfully processed. Your registration id is {wrr.reg_id}. Shop with us again. For more details login to https://gluoenelectrical.com. The FURNITURE"""
            from_email = 'contact@swastik.ai'
            recipient_list = [wrr.email,]
            try:
                send_mail(subject, message, from_email, recipient_list)
            except Exception as e:
                print(e)
            # track.user(
            #     user_id=mobile,
            #     country_code="+91",
            #     phone_number=mobile,
            #     traits={
            #         "name": name,
            #         "phone": mobile,
            #         "email" :email,
            #     },
                
            # )

            # track.event(
            #     user_id=number,
            #     event="Order",
            #     country_code="+91",
            #     phone_number=number,
            #     traits={
            #         "subject": subject,
            #         "message": message
            #     },
            # )
            # resp =  sendSMS(test_local_api, number,
            #     'FURNITURE', f'Dear {name} Your product {product} for warranty registration has been submitted and e-warranty id is {wrr.reg_id} Thanks Support Team FURNITURE')
            # print (resp)
        except Exception as e:
            print(e)
        messages.success(request, f"Your Warranty registration is successfully completed.")
        return redirect('customer_service')
    return redirect('customer_service')


@csrf_exempt
def warranty_registration_verify(request):
    if request.method == "POST":
        reg_num = request.POST.get('reg_number')
        print(reg_num)
        try:
            wrr = WarrantyRegistration.objects.filter(reg_id=reg_num, status="Approved").first()
            print(wrr)
            if wrr is not None:
                w_registration_serializer = WarrantyRegistrationSerializer(wrr)
                print(w_registration_serializer.data)
                data = {
                    'warranty_registration': w_registration_serializer.data
                }
                return JsonResponse(data, status=200)
            else:
                return JsonResponse({'error': 'Registration not found or not approved.'})
        except ObjectDoesNotExist:
            return JsonResponse({'error': 'Registration not found or not approved.'})

    return JsonResponse({'error': 'Invalid Method.'}, status=401)

def claim_warranty(request):
    if request.method == "POST":
        reg_number = request.POST['reg_number']
        wrr = WarrantyRegistration.objects.filter(reg_id=reg_number, status="Approved").first()
        print(wrr)
        name = wrr.name
        email = wrr.email
        mobile = wrr.mob_number
        manufacturing_date = wrr.product_manufacturing_date
        batch_no = wrr.product_batch_no
        serial_no = wrr.product_serial_no
        color = wrr.product_color
        warranty_registration_date = wrr.date_added
        product_image = request.POST['product_image']
        warranty_card = request.POST['warranty_card']
        state = request.POST['state']
        district = request.POST['district']
        city = request.POST['city']
        postoffice = request.POST['postoffice']
        zipcode = request.POST['zipcode']
        landmark = request.POST['landmark']
        purchasse_source = request.POST['category']
        address = request.POST['address']

        wrr_reg = WarrantyRegistration.objects.filter(reg_id = reg_number, product_batch_no = batch_no).first()

        if wrr_reg:
            wrr = WarrantyClaim.objects.filter(product_serial_no = serial_no, product_batch_no = batch_no).first()
            if wrr:
                messages.error(request, f"Your Warranty registration is allready completed.")
                return redirect('customer_service')
            if request.user.is_authenticated:
                warranty = WarrantyClaim(user= request.user, name = name, email = email, 
                mob_number = mobile, warranty_registration = reg_number, product_manufacturing_date = manufacturing_date,
                product_batch_no = batch_no, product_serial_no = serial_no, product_color = color, 
                registration_date = warranty_registration_date, product_image = product_image, waranty_card = warranty_card,
                state = state, district = district, city = city, post_office = postoffice, zipcode = zipcode,
                land_mark = landmark, purchase_source = landmark, address = address)
                warranty.save()
            else:
                warranty = WarrantyClaim(name = name, email = email, 
                mob_number = mobile, warranty_registration = reg_number, product_manufacturing_date = manufacturing_date,
                product_batch_no = batch_no, product_serial_no = serial_no, product_color = color, 
                registration_date = warranty_registration_date, product_image = product_image, waranty_card = warranty_card,
                state = state, district = district, city = city, post_office = postoffice, zipcode = zipcode,
                land_mark = landmark, purchase_source = purchasse_source, address = address)
                warranty.save()

            number = str(mobile)

            try:
                subject = 'Warranty Claim'
                message = f"""Dear Customer, Your registration for waranty claim for {batch_no} is successfully processed. Your registration id is {wrr.claim_id}. Shop with us again. For more details login to https://gluoenelectrical.com. The FURNITURE"""
                from_email = 'contact@swastik.ai'
                recipient_list = [wrr.email,]
                try:
                    send_mail(subject, message, from_email, recipient_list)
                except Exception as e:
                    print(e)
                # track.user(
                #     user_id=mobile,
                #     country_code="+91",
                #     phone_number=mobile,
                #     traits={
                #         "name": name,
                #         "phone": mobile,
                #         "email" :email,
                #     },
                    
                # )

                # track.event(
                #     user_id=mobile,
                #     event="Order",
                #     country_code="+91",
                #     phone_number=mobile,
                #     traits={
                #         "subject": subject,
                #         "message": message
                #     },
                # )

                # resp =  sendSMS(test_local_api, number,
                #     'FURNITURE', f'Dear {name} Your warranty request of product {batch_no} has been submitted Thanks Support Team FURNITURE')
                # print (resp)
                
            except Exception as e:
                print(e)
            messages.success(request, f"Your Warranty Claim is registered.")
        else:
            messages.success(request, f"Please register your product.")

        return redirect('customer_service')
    return redirect('customer_service')

def partner_registration(request):
    if request.method == "POST":
        name = request.POST['name']
        father_name = request.POST['father_name']
        email = request.POST['email']
        number = request.POST['number']
        image = request.FILES['image']
        identity_proof = request.FILES['identity_proof']
        partner_type = request.POST['partner_type']
        state = request.POST['state']
        pincode = request.POST['pincode']
        bankname = request.POST['bankname']
        account_holder_name = request.POST['account_holder_name']
        account_no = request.POST['account_no']
        ifsc_code = request.POST['ifsc_code']
        bank_details = request.FILES['bank_details']
        payment_method = request.POST['payment_method']
        pay_method_no = request.POST['pay_method_no']
        if Partner.objects.filter(mob_number=number).exists():
            messages.error(request, f"Mobile number {number} already exists.")
            return render(request, 'main/partner_registration.html')

        if Partner.objects.filter(email=email).exists():
            messages.error(request, f"Email {email} already exists.")
            return render(request, 'main/partner_registration.html')
        p = Partner(name = name, father_name = father_name, email = email, mob_number = number, image = image,
                    identity_proof = identity_proof, partner_type = partner_type, state = state, 
                    pin_code = pincode, bank_name = bankname, account_holder_name = account_holder_name,
                    bank_account_no = account_no, bank_ifsc_code = ifsc_code, bank_details = bank_details,
                    pay_method = payment_method, pay_method_no = pay_method_no
                    )
        p.save()
        wrr = Partner.objects.filter(name = name, email = email, mob_number = number).first()
        number = str(number)

        try:
            subject = 'Partner Registration'
            message = f"""Dear Customer, Your registration for {partner_type} is under processing. Your registration id is {wrr.partner_id}. Shop with us again. For more details login to https://gluoenelectrical.com. The FURNITURE"""
            from_email = 'contact@swastik.ai'
            recipient_list = [wrr.email,]
            try:
                send_mail(subject, message, from_email, recipient_list)
            except Exception as e:
                print(e)
            # track.user(
            #     user_id=number,
            #     country_code="+91",
            #     phone_number=number,
            #     traits={
            #         "name": name,
            #         "phone": number
            #     },
                
            # )

            # track.event(
            #     user_id=number,
            #     event="Order",
            #     country_code="+91",
            #     phone_number=number,
            #     traits={
            #         "subject": subject,
            #         "message": message
            #     },
            # )
            # resp =  sendSMS(test_local_api, number,
            #     'FURNITURE', f'Dear {name} Thanks for showing interest in doing business with us Our Team will you soon FURNITURE Team')
            # print (resp)
        except Exception as e:
            print(e)
        messages.success(request, f"Your registration for {partner_type} is completed.")
        return render(request, 'main/partner_registration.html')
    return render(request, 'main/partner_registration.html')

def partner_locator(request):
    if request.method == "POST":
        state = request.POST.get('state')
        pincode = request.POST.get('pincode')
        if state:
            partner = Partner.objects.filter(state=state, status="Approved")
            if not partner:
                messages.success(request, f"No any partner found at you location.")
        elif pincode:
            partner = Partner.objects.filter(pin_code=pincode, status = "Approved")
            if not partner:
                messages.success(request, f"No any partner found at you location.")
        else: 
            messages.success(request, f"Please Enter State/City or Zipcode.")
            partner = None
        print(partner)
        context = {
            'partner' : partner,
            'title' : 'Partner Locator'
        }
        return render (request, 'main/partner_locator.html', context = context)
    return render (request, 'main/partner_locator.html',{'title':'Partner Locator', 'page' : 'partner'})

def contact(request):
    context = {
        'page' : "Contact",
        'title': "Contact"
    }
    if request.method == "POST":
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email = request.POST['email']
        phone_no = request.POST['phone_no']
        message = request.POST['message']
        c = Contact(first_name = first_name, last_name = last_name, email = email, phone_no = phone_no, message = message)
        c.save()
        messages.success(request, f"Our team reached at you shortely.")
        return render(request, 'main/contact.html', context = context)
    return render(request, 'main/contact.html', context = context)

def profile(request):
    if request.user.is_authenticated:
        if request.user.is_active == True:
            if request.method == "POST":
                first_name = request.POST['first_name']
                last_name = request.POST['last_name']
                email = request.POST['email']
                phone_no = request.POST['phone_no']
                try:
                    image = request.FILES['profile_picture']
                except :
                    image = None
                password = request.POST['password']
                p = Profile.objects.filter(user = request.user).first()
                if p:
                    if image:
                        p.profile_image = image
                    p.phone_number = phone_no
                    p.save()
                else:
                    if image:
                        pp = Profile(user = request.user, profile_image = image, phone_number = phone_no)
                    else:
                        pp = Profile(user = request.user, phone_number = phone_no)
                    pp.save()

                u = User.objects.filter(username = request.user).first()
                u.first_name = first_name
                u.last_name = last_name
                u.email = email
                if password:
                    u.set_password(password)
                u.save()
                login(request, u)
                messages.success(request, f"Profile updated successfully.")
                return redirect('profile')
            # order = Order.objects.filter(user=request.user).order_by('-date_added')
            # order = Order.objects.filter(user=request.user, product__isnull=False).order_by('-date_added')
            # order = Order.objects.filter(user=request.user, total_price__isnull=False).order_by('-date_added')
            order = Order.objects.filter(user=request.user).exclude(order_status__isnull=True).order_by('-date_added')
            user = request.user
            profile = Profile.objects.filter(user=user).first()

            w_reg = WarrantyRegistration.objects.filter(user = request.user)
            w_claim = WarrantyClaim.objects.filter(user = request.user)
            addr = Address.objects.filter(user = request.user)
            context = {
                'user' : user,
                'profile' : profile,
                'order' : order,
                'w_reg' : w_reg,
                'w_claim' : w_claim,
                'address' : addr
            }
            return render(request, 'main/profile.html', context = context)
    else:
        return redirect('login')
                
def complaint(request):
    if request.user.is_authenticated:
        if request.user.is_active == True:
            if request.method == "POST":
                sub = request.POST['subject']
                com = request.POST['complaint']
                c = Complainet(user = request.user, subject = sub, complaint = com)
                c.save()
                messages.success(request, f"Your complaint registered, we try our best to resolve immediately.")
                return redirect('profile')
            else:
                return redirect('profile')
    else:
        return redirect('login')

@csrf_exempt
def subscribe(request):
    if request.method == 'POST':
        email = request.POST.get('email')

        # Process the email subscription logic here
        # ...
        # Check if the email already exists in the database
        if Subscribe.objects.filter(email=email).exists():
            # Email already exists
            response_data = {
                'message': 'The email is already saved.'
            }
        else:
            # Email doesn't exist, save it
            s = Subscribe(email=email)
            s.save()

            response_data = {
                'message': 'Thank you for subscribing!'
            }
        return JsonResponse(response_data)
    else:
        return JsonResponse({'message': 'Invalid request'})


def privacy_policy(request):
    privacy = Privacy_Policy.objects.first()
    context = {
        'privacy' : privacy,
        'page' : "Privacy",
        'title': "Privacy Policy"
    }
    return render(request, 'main/privacy_policy.html', context = context)

def about(request):
    about = About.objects.first()
    context = {
        'about' : about,
        'page' : "About",
        'title': "About"
    }
    return render(request, 'main/about.html', context = context)

def return_policy(request):
    return_policy = Return_Policy.objects.first()
    context = {
        'return_policy' : return_policy,
        'page' : "Return",
        'title': "Return Policy"
    }
    return render(request, 'main/return_policy.html', context = context)

def terms_condition(request):
    terms = Terms_Condition.objects.first()
    context = {
        'terms' : terms,
        'page' : "Terms",
        'title': "Terms & Condition"
    }
    return render(request, 'main/terms_condition.html', context = context)

def video_news(request):
    video = Video.objects.all().order_by('-date_added')
    context = {
        'video' : video,
        'page' : "About",
        'title': "About"
    }
    return render(request, 'main/video.html', context = context)

def logoutuser(request):
    if request.user.is_authenticated:
        if request.user.is_active == True:
            logout(request)
            return redirect('index')
    return redirect('login')


