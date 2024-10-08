from django.shortcuts import render, redirect
from main.models import crousel, User_verification, Category, Product, productreview, Cart, Address, Order, WarrantyRegistration, WarrantyClaim, Partner, Contact, Profile, Complainet, News, Faq, OrderData, Offer, Subscribe, About, Terms_Condition, Privacy_Policy, Return_Policy, Video
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Max, Min, Count, Avg, Sum
from django.core.paginator import Paginator
from django.http import JsonResponse, HttpResponse, request, response
from django.views.decorators.csrf import csrf_exempt
from django.db.models.query_utils import Q
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.paginator import Paginator
from django.core.validators import validate_email
from django.db import IntegrityError
from django.conf import settings
from django.db.models import CharField
from django.db.models.functions import Cast
from django.core.mail import send_mail
import json
import os
from twilio.rest import Client

test_local_api = settings.TEST_LOCAL_API

# Find your Account SID and Auth Token at twilio.com/console
# and set the environment variables. See http://twil.io/secure
account_sid = settings.TWILIO_ACCOUNT_SID
auth_token = settings.TWILIO_AUTH_TOKEN
client = Client(account_sid, auth_token)


# import track

# track.api_key =  settings.INTERKART_APII
test_local_api = settings.TEST_LOCAL_API

def on_error(error, queue_msg):
    print("An error occurred", error)
    print("Queue message", queue_msg)

# track.debug = True
# track.on_error = on_error



import urllib.request
import urllib.parse
 
def sendSMS(apikey, numbers, sender, message):
    data =  urllib.parse.urlencode({'apikey': apikey, 'numbers': numbers,
        'message' : message, 'sender': sender})
    data = data.encode('utf-8')
    request = urllib.request.Request("https://api.textlocal.in/send/?")
    f = urllib.request.urlopen(request, data)
    print(f)
    fr = f.read()
    return(fr)

def home(request):
    if request.user.is_authenticated:
        if request.user.is_staff == True:
            if request.method == "POST":
                email = request.POST['username']
                first_name = request.POST['first_name']
                last_name = request.POST['last_name']
                password = request.POST['password']
                try:
                    try:
                        validate_email(email)
                        User.objects.create_user(username=email, email=email, first_name = first_name, last_name = last_name, password=password, is_active = True)
                        user = User.objects.filter(username=email).first()
                        p = Profile(user=user, is_active=True)
                        p.save()
                        messages.success(request, f'Account has been created successfully.')
                    except IntegrityError as e:
                        print(e)
                        messages.error(request, f'Email or phone number is already exists, so please try another email or phone number.')
                        return redirect('admin-index')
                except Exception as e:
                    print(e)
                    if email.isdigit() == True:
                        try:
                            User.objects.create_user(username=email, first_name = first_name, last_name = last_name, password=password, is_active = True)
                            request.session['user'] = email
                            user = User.objects.filter(username=email).first()
                            p = Profile(user=user, phone_number=email, is_active=True)
                            p.save()
                            messages.success(request, f'Account has been created successfully.')
                        except IntegrityError as e:
                            print(e)
                            messages.error(request, f'Email or phone number is already exists, so please try another email or phone number.')
                            return redirect('admin-index')
                    else:
                        messages.error(request, f'Please Fill all the field correctly.')
                        return redirect('admin-index')
            
            user  = Profile.objects.all().order_by('-date_added')
            search = request.GET.get('search')
            if search:
                userr = []
                userr_c = User.objects.filter(Q(first_name__icontains=search) | Q(last_name__icontains=search) | Q(username__icontains=search))
                for c in userr_c:
                    p = user.filter(user=c)
                    userr.extend(p)
                user = userr
                if isinstance(user, list):
                    user = Profile.objects.filter(id__in=[u.id for u in user])
            else:
                search = None
            aut = request.GET.get('authenticate')
            if aut == '1':
                user = user.filter(is_active = True)
            elif aut == '0':
                user = user.filter(is_active = False)
            else:
                aut = None
            paginator = Paginator(user, 15)
            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)
            context = {
                'users' : page_obj,
                'authenticate' : aut,
                'search' : search,
            }
            return render(request, 'adminestration/home.html', context=context)
    return redirect('login')

def user_status(request, username):
    if request.user.is_authenticated:
        if request.user.is_staff == True:
            status = request.GET['active']
            user = User.objects.filter(username=username).first()
            p = Profile.objects.filter(user = user).first()
            if status == '1':
                user.is_active = True
                p.is_active = True
                
                messages.success(request, f"User '{username}' Authenticated successfully.")
                try:
                    validate_email(username)
                    try:
                        subject = 'Account Activation'
                        message = f"Congretulations, Your account is activated."
                        from_email = 'contact@swastik.ai'
                        recipient_list = [username,]
                        send_mail(subject, message, from_email, recipient_list)
                    except Exception as e:
                        print(e)
                except:
                    if username.isdigit() == True:
                        subject = 'Account Activation'
                        number = username
                        msg_body = f"Congretulations, Your account is activated."
                        
                        # track.user(
                        #     user_id=number,
                        #     country_code="+91",
                        #     phone_number=number,
                        #     traits={
                        #         "name": user.first_name,
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
                        #         "message": msg_body
                        #     },
                        # )

            else:
                user.is_active = False
                p.is_active = False
                messages.success(request, f"User '{username}' Status changed successfully.")
            user.save()
            p.save()
            return redirect('admin_user')
    return redirect('login')

def delete_user(request, username):
    if request.user.is_authenticated:
        if request.user.is_staff == True:
            user = User.objects.filter(username=username).first()
            user.delete()
            messages.success(request, f"User '{username}' deleted successfully.")
            return redirect('admin_user')
    return redirect('login')

def admin_product(request, category_slug=None):
    if request.user.is_authenticated:
        if request.user.is_staff == True:
            products = Product.objects.all().order_by('-date_added')
            print(products)
            search = None
            search = request.GET.get('search')
            if search:
                products = products.filter(Q(title__icontains=search) | Q(
                details__icontains=search))

            categoryy = None
            category_ss = None
            categoryy = request.GET.get('category')
            if categoryy:
                category_ss = get_object_or_404(Category, slug=categoryy)
                print(category_ss)
                print("###")
                productss = []
                if category_ss.children.all():
                    subcategories = [category_ss] + list(category_ss.children.all())
                    print(subcategories)
                    products = Product.objects.filter(category__in=subcategories)
                else:
                    products = products.filter(category = category_ss)
                
            if request.method == "POST":
                min_p = request.POST['min_price']
                max_p = request.POST['max_price']
                products = products.filter(price__range=(min_p, max_p))
                pass

            slug = category_slug
            low_to_high = request.GET.get('low_to_high')
            print(low_to_high)

            if low_to_high == '1':
                products = products.order_by('price')
            elif low_to_high == '0':
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

            productss = Product.objects.all().order_by('-date_added')
            min_price = productss.aggregate(Min('price'))
            max_price = productss.aggregate(Max('price'))
            p = productss.aggregate(Min('price'),Max('price'))
            print(productss)

            paginator = Paginator(products, 15)
            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)
            print(low_to_high)
            context = {
                'products' : page_obj,
                'category' : category_s,
                'low_to_high' : low_to_high,
                'min_price' : min_price,
                'max_price' : max_price,
                'minMaxPrice' : p,
                'search' : search,
                'categoryy' : categoryy,
                'page' : 'Products',
                'title' : 'Products',
                'cats' : category_slug
            }
            return render(request, 'adminestration/products.html', context = context)
    return redirect('login')

def admin_product_details(request,category_slug, product_slug):
    if request.user.is_authenticated:
        if request.user.is_staff == True:
            if request.method =="POST":
                title = request.POST['title']
                category = request.POST['category']
                details = request.POST['details']
                features = request.POST['features']
                specifications = request.POST['specifications']
                image1 = request.FILES.get('image1')
                image2 = request.FILES.get('image2')
                image3 = request.FILES.get('image3')
                image4 = request.FILES.get('image4')
                image5 = request.FILES.get('image5')
                quantity = request.POST['quantity']
                not_price = request.POST['not_price']
                price = request.POST['price']
                status = request.POST.get('status')
                tax = request.POST.get('tax')
                featured = request.POST.get('is_featured')
                print(status)
                print(featured)
                p = product = Product.objects.filter(slug=product_slug).first()
                p.title = title
                p.category = Category.objects.filter(slug=category).first()
                p.details = details
                p.features = features
                p.tax = tax
                p.specifications = specifications
                if image1:
                    p.image1 = image1
                if image2:
                    p.image2 = image2
                if image3:
                    p.image3 = image3
                if image4:
                    p.image4 = image4
                if image5:
                    p.image5 = image5
                p.quantity = quantity
                p.not_price = not_price
                print(status)
                p.price = price
                if status:
                    p.status = status
                if featured:
                    p.is_featured = featured
                p.save()
                messages.success(request, 'Product edited successfully')
                pass
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
            return render(request, 'adminestration/product-details.html', context=Context)
    return redirect('login')

def admin_product_add(request):
    if request.user.is_authenticated:
        if request.user.is_staff == True:
            if request.method =="POST":
                title = request.POST['title']
                category = request.POST['category']
                details = request.POST['details']
                features = request.POST['features']
                specifications = request.POST['specifications']
                image1 = request.FILES.get('image1', None)
                image2 = request.FILES.get('image2', None)
                image3 = request.FILES.get('image3', None)
                image4 = request.FILES.get('image4', None)
                image5 = request.FILES.get('image5', None)
                quantity = request.POST['quantity']
                not_price = request.POST['not_price']
                price = request.POST['price']
                tax = request.POST['tax']
                status = request.POST.get('status')
                featured = request.POST.get('is_featured')
                if not status:
                    status = False
                else:
                    status = True
                if not featured:
                    featured = False
                else:
                    featured = True
                # check which images were uploaded by the user
                images = [image1, image2, image3, image4, image5]

                # filter out the None values
                images = [image for image in images if image is not None]

                # create a dictionary to save the data to the database
                data = {
                    'title': title,
                    'category': Category.objects.filter(slug=category).first(),
                    'details': details,
                    'features': features,
                    'specifications': specifications,
                    'quantity': quantity,
                    'not_price': not_price,
                    'price': price,
                    'tax' : tax,
                    'status': status,
                    'is_featured': featured,
                }

                # set the image fields in the dictionary
                for i, image in enumerate(images):
                    data[f'image{i+1}'] = image

                # create a new model instance and save it to the database
                product = Product(**data)
                product.save()
                messages.success(request, f"Product added Successfully.")
            return redirect('admin_products')
    return redirect('login')
    
def admin_product_delete(request, product_slug):
    if request.user.is_authenticated:
        if request.user.is_staff == True:
            product = get_object_or_404(Product, slug = product_slug)
            product.delete()
            return redirect('admin_products')
    return redirect('login')

def admin_product_review_delete(request, product_slug, review_id):
    if request.user.is_authenticated:
        if request.user.is_staff == True:
            productreview = get_object_or_404(Product, slug = product_slug)
            review = productreview.objects.filter(review_id = review_id)
            review.delete()
            return redirect(f'/admin/products/{product.category.slug}/{product.slug}')
    return redirect('login')

def admin_order(request, category_slug=None):
    if request.user.is_authenticated:
        if request.user.is_staff == True:
            order = Order.objects.all().order_by('-date_added')
            print(order)
            search = None
            search = request.GET.get('search')
            if search:
                order = order.filter(Q(order_id__icontains=search))

            categoryy = None
            category_ss = None
            categoryy = request.GET.get('category')
            if categoryy:
                category_ss = get_object_or_404(Category, slug=categoryy)
                print(category_ss)
                print("###")
                if category_ss.children.all():
                    # parent_category = category_ss.parent
                    # products = Product.objects.filter(category__in=[category_ss, parent_category])
                    subcategories = [category_ss] + list(category_ss.children.all())
                    print(subcategories)
                    products = Product.objects.filter(category__in=subcategories)
                    order_data = OrderData.objects.filter(product__in=products)

                    # get all orders that contain the above order data objects
                    order = Order.objects.filter(product__in=order_data)
                else:
                    products = Product.objects.filter(category=category_ss)
                    order_data = OrderData.objects.filter(product__in=products)

                    # get all orders that contain the above order data objects
                    order = Order.objects.filter(product__in=order_data)
            low_to_high = request.GET.get('low_to_high')
            print(low_to_high)

            if low_to_high == '1':
                order = order.order_by('total_price')
            elif low_to_high == '0':
                order = order.order_by('-total_price')
            else:
                low_to_high = None

            slug = category_slug
            category_s = None

            if slug:
                category_s = get_object_or_404(Category, slug=slug)
                print(category_s)
                print("###")
                if category_s.children.all():
                    # parent_category = category_s.parent
                    # products = Product.objects.filter(category__in=[category_s, parent_category])
                    subcategories = [category_s] + list(category_s.children.all())
                    print(subcategories)
                    products = Product.objects.filter(category__in=subcategories)
                    order_data = OrderData.objects.filter(product__in=products)

                    # get all orders that contain the above order data objects
                    order = Order.objects.filter(product__in=order_data)
                else:
                    products = Product.objects.filter(category=category_s)
                    print(products)
                    order_data = OrderData.objects.filter(product__in=products)
                    print(order_data)
                    # get all orders that contain the above order data objects
                    order = Order.objects.filter(product__in=order_data)

            if request.method == "POST":
                min_p = request.POST['min_price']
                max_p = request.POST['max_price']
                order = Order.objects.filter(total_price__range=(min_p, max_p))
                pass

            # order_pincode_list = order.values_list('address__postalcode', flat=True).distinct()
            order_pincode_list = order.values_list('address__postalcode', flat=True).distinct().values_list(Cast('address__postalcode', output_field=CharField()))
            print(order_pincode_list)
            # Query the Partner model to find all partners with matching pincode
            matching_partners = Partner.objects.filter(pin_code__in=order_pincode_list, status="Approved")
            print(matching_partners)

            min_price = Order.objects.aggregate(Min('total_price'))
            max_price = Order.objects.aggregate(Max('total_price'))
            ppp = Order.objects.aggregate(Min('total_price'),Max('total_price'))
            print(order)

            paginator = Paginator(order, 15)
            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)
            print(low_to_high)
            context = {
                'order' : page_obj,
                'category' : category_s,
                'low_to_high' : low_to_high,
                'min_price' : min_price,
                'max_price' : max_price,
                'minMaxPrice' : ppp,
                'search' : search,
                'categoryy' : categoryy,
                'page' :'Order',
                'title' : 'Orders',
                'matching_partners': matching_partners,

            }
            return render(request, 'adminestration/orders.html', context=context)
    return redirect('login')

def admin_order_detail(request, order_id):
    if request.user.is_authenticated:
        if request.user.is_staff == True:
            order = Order.objects.filter(order_id = order_id).first()
            
            context = {
                'invoice' : order,
            }
            return render(request, 'adminestration/order_deetails.html', context=context)
    return redirect('login')
    
def admin_change_order(request, order_id):
    if request.user.is_authenticated:
        if request.user.is_staff == True:
            order = Order.objects.filter(order_id = order_id).first()
            status = request.GET.get('order_status')
            payment_status = request.GET.get('payment_status')
            if status:
                order.order_status = status
                number = str(order.address.phone)
                msg_body = f"""Dear {order.address.first_name}, Your Order ID: {order.order_id} is {status}. Shop with us again. For more details login to https://gluoenelectrical.com. The FURNITURE"""

                try:
                    subject = 'Order Confirmation'
                    message = f"""Dear {order.address.first_name}, Your Order ID: {order.order_id} is {status}.
                            Shop with us again. For more details login to https://gluoenelectrical.com.
                            The FURNITURE
                            """
                    from_email = 'contact@swastik.ai'
                    recipient_list = [order.address.email,]
                    send_mail(subject, message, from_email, recipient_list)
                    # track.user(
                    #     user_id=number,
                    #     country_code="+91",
                    #     phone_number=number,
                    #     traits={
                    #         "name": order.user.first_name,
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
                    #         "message": msg_body
                    #     },
                    # )
                    # resp =  sendSMS(test_local_api, number,
                    #     'FURNITURE', f'Dear {order.address.first_name} Your order id {order.order_id} has been {order.order_status} Thanks Furniture')
                    # print (resp)
                except Exception as e:
                    print(e)
            if payment_status is not None:
                order.payment_status = payment_status
                number = order.address.phone
                msg_body = f"""Dear {order.address.first_name}, Your Order ID: {order.order_id} payment is {payment_status}.
                            Shop with us again. For more details login to https://gluoenelectrical.com.
                            The FURNITURE
                            """
                # track.user(
                #     user_id=number,
                #     country_code="+91",
                #     phone_number=number,
                #     traits={
                #         "name": order.user.first_name,
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
                #         "message": msg_body
                #     },
                # )
                # resp =  sendSMS(test_local_api, number,
                #     'FURNITURE', f'Dear {order.address.first_name} Your order id {order.order_id} has been {order.order_status} Thanks Furniture')
                # print (resp)
                try:
                    subject = f'{order.order_id} payment status'
                    message = f"""Dear {order.address.first_name}, Your Order ID: {order.order_id} payment is {payment_status}.
                            Shop with us again. For more details login to https://gluoenelectrical.com.
                            The FURNITURE
                            """
                    from_email = 'contact@swastik.ai'
                    recipient_list = [order.address.email,]
                    send_mail(subject, message, from_email, recipient_list)
                except Exception as e:
                    print(e)
            order.save()
            invoice = request.GET.get('invoice')
            if invoice == '1':
                return redirect(f"/admin/user/details/order/{order_id}")
            return redirect('admin_order')
    return redirect('login')

def admin_change_order_partner(request, order_id, partner_id):
    if request.user.is_authenticated:
        if request.user.is_staff == True:
            order = Order.objects.filter(order_id = order_id).first()
            partner = Partner.objects.filter(partner_id = partner_id).first()
            print(order, partner)
            if partner:
                order.partner = partner
                number = str(order.address.phone)
                website_url = "https://gluoenelectrical.com"
                msg_body = f"""Dear {order.address.first_name}, We hope this message finds you well! We are excited to inform you that FURNITURE is providing an electrician to assist you with the installation of a fan in your home. For your Order ID: {order.order_id}, our dedicated team at {partner.name} will ensure a smooth and efficient installation process. Partner Contact Details : {partner.mob_number} {partner.email}. At FURNITURE, we pride ourselves on delivering top-notch service and quality products for all your electrical needs. We are confident that our skilled electrician will leave you fully satisfied with the installation. you have any specific preferences or requirements for the fan installation, please do not hesitate to let our electrician know. Once the installation is complete, we welcome you to shop with us again for any other electrical solutions you may need in the future. Our website {website_url} is always at your service.  you for choosing FURNITURE. We look forward to enhancing the comfort and convenience of your home with this fan installation. Best regards, The FURNITURE Team """

                try:
                    subject = 'Electrician allocation for installation'
                    # message = f"""Dear {order.address.first_name}, Your Order ID: {order.order_id} is {status}.
                    #         Shop with us again. For more details login to https://gluoenelectrical.com.
                    #         The FURNITURE
                    #         """
                    message = msg_body
                    from_email = 'contact@swastik.ai'
                    recipient_list = [order.address.email,]
                    send_mail(subject, message, from_email, recipient_list)
                    # track.user(
                    #     user_id=number,
                    #     country_code="+91",
                    #     phone_number=number,
                    #     traits={
                    #         "name": order.user.first_name,
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
                    #         "message": msg_body
                    #     },
                    # )
                    # resp =  sendSMS(test_local_api, number,
                    #     'FURNITURE', f'Dear {order.address.first_name} Your order id {order.order_id} has been {order.order_status} Thanks Furniture')
                    # print (resp)
                except Exception as e:
                    print(e)

            order.save()
            invoice = request.GET.get('invoice')
            if invoice == '1':
                return redirect(f"/admin/user/details/order/{order_id}")
            return redirect('admin_order')
    return redirect('login')


def admin_delete_order(request, order_id):
    if request.user.is_authenticated:
        if request.user.is_staff == True:
            order = Order.objects.filter(order_id = order_id).first()
            order.delete()
            return redirect('admin_order')
    return redirect('login')

def admin_partner_locetor(request):
    if request.user.is_authenticated:
        if request.user.is_staff == True:
            partner = Partner.objects.all().order_by('-date_added')

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
                messages.success(request, f'Partner registered successfully.')
                pass

            search = request.GET.get('search')
            if search:
                partner = partner.filter(Q(name__icontains=search) | Q(father_name__icontains=search) | Q(email__icontains=search) | Q(mob_number__icontains=search)) | Q(partner_id__icontains=search)
            else:
                search = None
            aut = request.GET.get('authenticate')
            if aut == 'Progress':
                partner = partner.filter(status = aut)
            elif aut == 'Approved':
                partner = partner.filter(status = aut)
            elif aut == "Rejected":
                partner = partner.filter(status = aut)
            else:
                aut = None
            paginator = Paginator(partner, 15)
            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)
            context = {
                'partner' : page_obj,
                'authenticate' : aut,
                'search' : search,
                'title': 'Partner Locator',
                'page' : 'Partner'
            }
            return render(request, 'adminestration/partner.html', context = context)
    return redirect('login')

def admin_partner_detail(request, partner_id):
    if request.user.is_authenticated:
        if request.user.is_staff == True:    
            partner = Partner.objects.filter(partner_id = partner_id).first()
            context = {
                'partner' : partner
            }
            return render(request, 'adminestration/partner_details.html', context = context)
    return redirect('login')

def admin_change_partner(request, partner_id):
    if request.user.is_authenticated:
        if request.user.is_staff == True:
            partner = Partner.objects.filter(partner_id = partner_id).first()
            status = request.GET.get('active')
            if status:
                partner.status = status
                nuber = str(partner.mob_number)
               
                try:
                    subject = 'Warranty Claim'
                    message = f"""Dear Customer, Your partner account is {status}. Shop with us again. For more details login to https://gluoenelectrical.com. The FURNITURE"""
                    from_email = 'contact@swastik.ai'
                    recipient_list = [partner.email,]
                    send_mail(subject, message, from_email, recipient_list)
                    # track.user(
                    #     user_id=number,
                    #     country_code="+91",
                    #     phone_number=number,
                    #     traits={
                    #         "name": partner.name,
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
                except Exception as e:
                    print(e)
            partner.save()
            invoice = request.GET.get('details')
            if invoice == '1':
                return redirect(f"/admin/partner/details/{partner_id}")
            return redirect('admin_partner_locetor')
    return redirect('login')

def admin_delete_partner(request, partner_id):
    if request.user.is_authenticated:
        if request.user.is_staff == True:
            partner = Partner.objects.filter(partner_id = partner_id).first()
            nuber = str(partner.mob_number)

            try:
                subject = 'Warranty Claim'
                message = f"""Dear Customer, Your partner account is deactivated. Shop with us again. For more details login to https://gluoenelectrical.com. The FURNITURE """
                from_email = 'contact@swastik.ai'
                recipient_list = [partner.email,]
                send_mail(subject, message, from_email, recipient_list)
                # track.user(
                #     user_id=number,
                #     country_code="+91",
                #     phone_number=number,
                #     traits={
                #         "name": partner.name,
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
            except Exception as e:
                print(e)
            partner.delete()
            return redirect('admin_partner_locetor')
    return redirect('login')

def admin_wr_locetor(request):
    if request.user.is_authenticated:
        if request.user.is_staff == True:
            wr = WarrantyRegistration.objects.all().order_by('-date_added')

            search = request.GET.get('search')
            if search:
                wr = wr.filter(Q(name__icontains=search) | Q(email__icontains=search) | Q(reg_id__icontains=search) | Q(mob_number__icontains=search) | Q(product_icontains = search) | Q(product_batch_no_icontains=search))
            else:
                search = None
            aut = request.GET.get('authenticate')
            if aut == 'Processing':
                wr = wr.filter(status = aut)
            elif aut == 'Approved':
                wr = wr.filter(status = aut)
            elif aut == "Rejected":
                wr = wr.filter(status = aut)
            else:
                aut = None
            paginator = Paginator(wr, 15)
            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)
            context = {
                'wr' : page_obj,
                'authenticate' : aut,
                'search' : search,
                'page' : 'Registration',
                'title' : 'Warranty Registration'
            }
            return render(request, 'adminestration/wr.html', context = context)
    return redirect('login')

def admin_wr_detail(request, reg_id):
    if request.user.is_authenticated:
        if request.user.is_staff == True:    
            wr = WarrantyRegistration.objects.filter(reg_id = reg_id).first()
            context = {
                'wr' : wr
            }
            return render(request, 'adminestration/wr_details.html', context = context)
    return redirect('login')

def admin_change_wr(request, reg_id):
    if request.user.is_authenticated:
        if request.user.is_staff == True:
            wr = WarrantyRegistration.objects.filter(reg_id = reg_id).first()
            status = request.GET.get('active')
            if status:
                wr.status = status
                nuber = str(wr.mob_number)
                
                try:
                    subject = 'Warranty Registration'
                    message = f"""Dear Customer, Your waranty registration for {wr.batch_no} is {status}. Your registration id is {wr.claim_id}. Shop with us again. For more details login to https://gluoenelectrical.com. The FURNITURE"""
                    from_email = 'contact@swastik.ai'
                    recipient_list = [wr.email,]
                    send_mail(subject, message, from_email, recipient_list)
                    # track.user(
                    #     user_id=number,
                    #     country_code="+91",
                    #     phone_number=number,
                    #     traits={
                    #         "name": wr.name,
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
                    #     'FURNITURE', f'Dear {wr.name} Your product {wr.product} for warranty registration has been submitted and e-warranty id is {wr.reg_id} Thanks Support Team FURNITURE')
                    # print (resp)
                except Exception as e:
                    print(e)
            wr.save()
            invoice = request.GET.get('details')
            if invoice == '1':
                return redirect(f"/admin/warranty_registration/details/{reg_id}")
            return redirect('admin_wr_locetor')
    return redirect('login')

def admin_delete_wr(request, reg_id):
    if request.user.is_authenticated:
        if request.user.is_staff == True:
            er = WarrantyRegistration.objects.filter(reg_id = reg_id).first()
            er.delete()
            return redirect('admin_wr_locetor')
    return redirect('login')

def admin_wc_locetor(request):
    if request.user.is_authenticated:
        if request.user.is_staff == True:
            wc = WarrantyClaim.objects.all().order_by('-date_added')

            search = request.GET.get('search')
            if search:
                wc = wc.filter(Q(name__icontains=search) | Q(email__icontains=search) | Q(claim_id__icontains=search) | Q(mob_number__icontains=search) | Q(product_batch_no_icontains=search))
            else:
                search = None
            aut = request.GET.get('authenticate')
            if aut == 'Processing':
                wc = wc.filter(status = aut)
            elif aut == 'Approved':
                wc = wc.filter(status = aut)
            elif aut == "Rejected":
                wc = wc.filter(status = aut)
            else:
                aut = None
            paginator = Paginator(wc, 15)
            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)
            context = {
                'wc' : page_obj,
                'authenticate' : aut,
                'search' : search,
                'page' : 'Claim',
                'title' : 'Warranty Claim'
            }
            return render(request, 'adminestration/wc.html', context = context)
    return redirect('login')

def admin_wc_detail(request, claim_id):
    if request.user.is_authenticated:
        if request.user.is_staff == True:    
            wc = WarrantyClaim.objects.filter(claim_id = claim_id).first()
            context = {
                'wc' : wc
            }
            return render(request, 'adminestration/wc_details.html', context = context)
    return redirect('login')

def admin_change_wc(request, claim_id):
    if request.user.is_authenticated:
        if request.user.is_staff == True:
            wc = WarrantyClaim.objects.filter(claim_id = claim_id).first()
            status = request.GET.get('active')
            if status:
                wc.status = status
                nuber = str(wc.mob_number)
                
                try:
                    subject = 'Warranty Claim'
                    message = f"""Dear Customer, Your registration for waranty claim for {wc.warranty_registration} is {status}. Your registration id is {wc.claim_id}. Shop with us again. For more details login to https://gluoenelectrical.com. The FURNITURE"""
                    from_email = 'contact@swastik.ai'
                    recipient_list = [wc.email,]
                    send_mail(subject, message, from_email, recipient_list)
                    # track.user(
                    #     user_id=number,
                    #     country_code="+91",
                    #     phone_number=number,
                    #     traits={
                    #         "name": wc.name,
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
                    #     'FURNITURE', f'Dear {wc.name} Your warranty request of product {wc.batch_no} has been submitted Thanks Support Team FURNITURE')
                    # print (resp)
                except Exception as e:
                    print(e)
            wc.save()
            invoice = request.GET.get('details')
            if invoice == '1':
                return redirect(f"/admin/warranty_claim/details/{claim_id}")
            return redirect('admin_wc_locetor')
    return redirect('login')

def admin_delete_wc(request, claim_id):
    if request.user.is_authenticated:
        if request.user.is_staff == True:
            wc = WarrantyClaim.objects.filter(claim_id = claim_id).first()
            wc.delete()
            return redirect('admin_wc_locetor')
    return redirect('login')

def admin_contact(request):
    if request.user.is_authenticated:
        if request.user.is_staff == True:    
            contact = Contact.objects.all().order_by('-date_added')
            search = None
            search = request.GET.get('search')
            if search:
                contact = Contact.objects.filter(Q(first_name__icontains=search) | Q(last_name__icontains = search) | Q(email__icontains=search) | Q(phone_no__icontains = search) | Q(message__icontains=search))
            
            aut = request.GET.get('time')
            if aut == '1':
                contact = contact.order_by('-date_added')
            elif aut == '0':
                contact = contact.order_by('date_added')
            else:
                aut = None
            paginator = Paginator(contact, 15)
            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)
            context = {
                'contact' : page_obj,
                'aut' : aut,
                'search' : search,
                'page' : 'Contact',
                'title' : 'Contact'
            }
            return render(request, 'adminestration/contact.html', context = context)
    return redirect('login')

def admin_delete_contact(request, contact_id):
    if request.user.is_authenticated:
        if request.user.is_staff == True:
            contact = Contact.objects.filter(contact_id = contact_id).first()
            contact.delete()
            return redirect('admin_contact')
    return redirect('login')

def admin_complainet(request):
    if request.user.is_authenticated:
        if request.user.is_staff == True:    
            complainet = Complainet.objects.all().order_by('-date_added')
            search = None
            search = request.GET.get('search')
            if search is not None:
                complainet = Complainet.objects.filter(Q(complaint_id__icontains=search) | Q(subject__icontains = search) | Q(complaint__icontains=search) )
            else:
                search = None
            aut = request.GET.get('time')
            if aut == '1':
                complainet = complainet.order_by('-date_added')
            elif aut == '0':
                complainet = complainet.order_by('date_added')
            else:
                aut = None
            paginator = Paginator(complainet, 15)
            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)
            context = {
                'complainet' : page_obj,
                'aut' : aut,
                'search' : search,
                'page' : 'Complainet',
                'title' : 'Complainet'
            }
            return render(request, 'adminestration/complainet.html', context = context)
    return redirect('login')

def admin_delete_complainet(request, complaint_id):
    if request.user.is_authenticated:
        if request.user.is_staff == True:
            wc = Complainet.objects.filter(complaint_id = complaint_id).first()
            wc.delete()
            return redirect('admin_complainet')
    return redirect('login')


def admin_news(request):
    if request.user.is_authenticated:
        if request.user.is_staff == True:    
            if request.method == "POST":
                title = request.POST['title']
                image = request.FILES['image']
                date_added = request.POST['date_added']
                slug = request.POST['slug']
                status = True
                n = News(title = title, image = image, date_added = date_added ,slug = slug, status = status)
                n.save()
                pass
            news = News.objects.all().order_by('-date_added')
            search = None
            search = request.GET.get('search')
            if search:
                news = News.objects.filter(Q(news_id__icontains=search) | Q(title__icontains = search) | Q(slug__icontains=search) )

            aut = request.GET.get('status')
            if aut == '1':
                s = True
                news = news.filter(status = s)
            elif aut == '0':
                s = False
                news = news.filter(status = s)
            else:
                aut = None
            paginator = Paginator(news, 15)
            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)
            context = {
                'news' : page_obj,
                'aut' : aut,
                'search' : search,
                'page' : 'News',
                'title' : 'News'
            }
            return render(request, 'adminestration/news.html', context = context)
    return redirect('login')

def admin_change_news(request, news_id):
    if request.user.is_authenticated:
        if request.user.is_staff == True:
            news = News.objects.filter(news_id = news_id).first()
            status = request.GET.get('active')
            if status == '1':
                status = True
                news.status = status
            else:
                status = False
                news.status = status
            news.save()
            invoice = request.GET.get('details')
            return redirect('admin_news')
    return redirect('login')

def admin_delete_news(request, news_id):
    if request.user.is_authenticated:
        if request.user.is_staff == True:
            news = News.objects.filter(news_id = news_id).first()
            news.delete()
            return redirect('admin_news')
    return redirect('login')


def admin_category(request):
    if request.user.is_authenticated:
        if request.user.is_staff == True:    
            if request.method == "POST":
                parent = request.POST.get('parent')
                print(parent)
                print("##")
                title = request.POST['title']
                image = request.FILES['image']
                if parent:
                    category = Category.objects.filter(slug = parent).first()
                    n = Category(parent = category, title =title, image = image)
                else:
                    n = Category( title =title, image = image)
                n.save()
                pass
            category = Category.objects.filter(parent=None)
            search = None
            search = request.GET.get('search')
            if search:
                category = category.filter(Q(title__icontains=search) | Q(slug__icontains = search) )
            paginator = Paginator(category, 15)
            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)
            context = {
                'category' :  page_obj,
                'search' : search,
            }
            return render(request, 'adminestration/category.html', context = context)
    return redirect('login')

def admin_change_category(request, category_slug):
    if request.user.is_authenticated:
        if request.user.is_staff == True:
            category = Category.objects.filter(slug = category_slug).first()
            if request.method=="POST":
                parent = request.POST.get('parent')
                title = request.POST['title']
                image = request.FILES.get('image')
                print(parent)
                if parent:
                    pp = Category.objects.filter(slug = parent).first()
                    category.parent = pp
                category.title = title
                if image:
                    category.image = image
                category.save()
                return redirect('admin_category')
            context = {
                'category' : category,
            }
            return render(request, 'adminestration/category_change.html', context = context)
    return redirect('login')

def admin_delete_category(request, category_slug):
    if request.user.is_authenticated:
        if request.user.is_staff == True:
            category = Category.objects.filter(slug = category_slug).first()
            category.delete()
            return redirect('admin_category')
    return redirect('login')


def admin_crousel(request):
    if request.user.is_authenticated:
        if request.user.is_staff == True:    
            if request.method == "POST":
                name = request.POST['title']
                description = request.POST['description']
                image = request.FILES['image']
                link = request.POST['link']
                n = crousel(name = name, description =description, image = image, link = link)
                n.save()
                pass
            c = crousel.objects.all()
            context = {
                'crousel' : c
            }
            return render(request, 'adminestration/crousel.html', context = context)
    return redirect('login')

def admin_change_crousel(request, c_id):
    if request.user.is_authenticated:
        if request.user.is_staff == True:
            c = crousel.objects.filter(c_id = c_id).first()
            if request.method=="POST":
                name = request.POST['title']
                description = request.POST['description']
                image = request.FILES.get('image')
                link = request.POST['link']
                c.name = name
                c.description = description
                if image:
                    c.image = image
                c.link = link
                c.save()
                return redirect('admin_crousel')
            context = {
                'crousel' : c
            }
            return render(request, 'adminestration/crousel_edit.html', context = context)
    return redirect('login')

def admin_delete_crousel(request, c_id):
    if request.user.is_authenticated:
        if request.user.is_staff == True:
            c = crousel.objects.filter(c_id = c_id).first()
            c.delete()
            return redirect('admin_crousel')
    return redirect('login')


def admin_faq(request):
    if request.user.is_authenticated:
        if request.user.is_staff == True:    
            if request.method == "POST":
                title = request.POST['title']
                description = request.POST['description']
                status = "Show"
                n = Faq(title = title, description =description, status=status)
                n.save()
                pass
            faq = Faq.objects.all()
            search = None
            search = request.GET.get('search')
            if search:
                faq = Faq.objects.filter(Q(faq_id__icontains=search) | Q(title__icontains = search) | Q(description__icontains=search) )

            aut = request.GET.get('status')
            if aut == 'Show':
                faq = faq.filter(status = aut)
            elif aut == 'Hide':
                faq = faq.filter(status = aut)
            else:
                aut = None
            paginator = Paginator(faq, 15)
            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)
            context = {
                'faq' :  page_obj,
                'aut' : aut,
                'search' : search,
                'page' : 'Faq',
                'title' : 'Faq'
            }
            return render(request, 'adminestration/faq.html', context = context)
    return redirect('login')


def admin_change_faq(request, faq_id):
    if request.user.is_authenticated:
        if request.user.is_staff == True:
            c = Faq.objects.filter(faq_id = faq_id).first()
            if request.method == "POST":
                title = request.POST['title']
                description = request.POST['description']
                status = request.POST['status']
                c.title = title
                c.description = description
                c.status = status
                c.save()
                return redirect('admin_faq')
                
            if request.GET.get('active'):
                status = request.GET.get('active')
                c.status = status
                c.save()
                
            return redirect('admin_faq')
        
    return redirect('login')


def admin_delete_faq(request, faq_id):
    if request.user.is_authenticated:
        if request.user.is_staff == True:
            c = Faq.objects.filter(faq_id = faq_id).first()
            c.delete()
            return redirect('admin_faq')
    return redirect('login')


from django.core.serializers.json import DjangoJSONEncoder
import json
from datetime import datetime, date, timedelta
from django.utils import timezone
from django.utils.timezone import now
from django.db.models.functions import TruncMonth


class DateTimeEncoder(DjangoJSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.strftime("%Y-%m-%d %H:%M:%S")
        return super().default(o)


def index(request):
    if request.user.is_authenticated:
        if request.user.is_staff == True:
            orders = Order.objects.values('date_added').annotate(total_sales=Sum('total_price'))
            print(orders)
            orders_json = json.dumps(list(orders), cls=DateTimeEncoder)  # Convert queryset to list and serialize to JSON
            today = timezone.now().date()
            total_price = Order.objects.filter(date_added__date=today).aggregate(total=Sum('total_price'))['total']
            print(total_price)
            yesterday = timezone.now() - timedelta(days=1)
            total_price_yesterday = Order.objects.filter(date_added__date=yesterday.date()).aggregate(total_price_yesterday=Sum('total_price'))['total_price_yesterday']
            print(total_price_yesterday)
            try:
                current_month_total = Order.objects.filter(
                    date_added__month=now().month
                ).annotate(
                    month=TruncMonth('date_added')
                ).values(
                    'month'
                ).annotate(
                    total_sales=Sum('total_price')
                ).values(
                    'month',
                    'total_sales'
                )[0]['total_sales']
            except Exception as e:
                current_month_total = 0
            # Calculate the first day of the current month
            first_day_of_month = date(today.year, today.month, 1)

            # Calculate the last day of the current month
            last_day_of_month = date(today.year, today.month, 28) + timedelta(days=4)

            # Get the number of users registered this month
            users_this_month = User.objects.filter(date_joined__gte=first_day_of_month, date_joined__lte=last_day_of_month).count()
            print(users_this_month)
            orders_count = Order.objects.filter(date_added__date=today).count()
            orders = Order.objects.order_by('-date_added')[:15]
            top_products = Product.objects.annotate(total_sold=Sum('orderdata__quantity')).order_by('-total_sold')[:10]
            print(orders)
            print(top_products)
            context = {
                'sales': orders_json,
                'total_price' : total_price,
                'users_this_month' : users_this_month,
                'total_price_yesterday' : total_price_yesterday,
                'current_month_total' : current_month_total,
                'orders_count' : orders_count,
                'orders' : orders,
                'top_products' : top_products,
                'title' : 'Home',
                'page' : 'Home'
            }
            return render(request, 'adminestration/index.html', context = context)
    return redirect('login')

def admin_coupon(request):
    if request.user.is_authenticated:
        if request.user.is_staff == True:    
            if request.method == "POST":
                code = request.POST['code']
                product = request.POST['product']
                product = Product.objects.filter(slug = product).first()
                discount = request.POST['discount']
                start_date = request.POST['start_date']
                end_date = request.POST['last_date']
                status = True
                n = Offer(code = code, product = product, discount = discount ,start_date = start_date, end_date = end_date, status = status)
                n.save()
                messages.success(request, 'Coupon is added succesfully.')
                pass
            coupon = Offer.objects.all()
            print(coupon)
            search = None
            search = request.GET.get('search')
            if search:
                coupon = Offer.objects.filter(Q(coupon__icontains=search) )

            aut = request.GET.get('status')
            if aut == '1':
                s = True
                coupon = coupon.filter(status = s)
            elif aut == '0':
                s = False
                coupon = coupon.filter(status = s)
            else:
                aut = None
            paginator = Paginator(coupon, 15)
            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)
            product = Product.objects.all()
            context = {
                'coupon' : page_obj,
                'aut' : aut,
                'product' : product,
                'search' : search,
            }
            return render(request, 'adminestration/coupon.html', context = context)
    return redirect('login')

def admin_change_coupon(request, code):
    if request.user.is_authenticated:
        if request.user.is_staff == True:
            coupon = Offer.objects.filter(code = code).first()
            status = request.GET.get('active')
            if status == '1':
                status = True
                coupon.status = status
            else:
                status = False
                coupon.status = status
            coupon.save()
            return redirect('admin_coupon')
    return redirect('login')

def admin_delete_coupon(request, codde):
    if request.user.is_authenticated:
        if request.user.is_staff == True:
            coupon = Offer.objects.filter(code = code).first()
            coupon.delete()
            return redirect('admin_coupon')
    return redirect('login')




def admin_user_subscribe(request):
    if request.user.is_authenticated:
        if request.user.is_staff == True:    
            subscribe = Subscribe.objects.all().order_by('-date_added')
            search = None
            search = request.GET.get('search')
            if search is not None:
                subscribe = Subscribe.objects.filter(Q(email__icontains=search))
            else:
                search = None
            
            paginator = Paginator(subscribe, 15)
            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)
            context = {
                'subscribe' : page_obj,
                'search' : search,
                'page' : 'Subscribe',
                'title' : 'Subscribe'
            }
            return render(request, 'adminestration/subscribe.html', context = context)
    return redirect('login')

def admin_delete_user_subscribe(request, email):
    if request.user.is_authenticated:
        if request.user.is_staff == True:
            wc = Subscribe.objects.filter(email = email).first()
            wc.delete()
            return redirect('admin_subscribe')
    return redirect('login')


def partner_locator(request):
    if request.user.is_authenticated:
        if request.user.is_staff == True:
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
                    'title' : 'Partner Locator',
                    'page' : 'locator'
                }
                return render (request, 'adminestration/partner_locator.html', context = context)
            return render (request, 'adminestration/partner_locator.html',{'title':'Partner Locator', 'page' : 'locator'})
    return redirect('login')
        

def privacy_policy(request):
    if request.user.is_authenticated:
        if request.user.is_staff == True:
            
            if request.method == "POST":
                privacy_policy = request.POST['privacy_policy']
                c = Privacy_Policy(privacy = privacy_policy)
                c.save()
                messages.success(request, f"Added Successfully.")
            privacy = Privacy_Policy.objects.first()
            context = {
                'privacy' : privacy,
                'page' : "Privacy",
                'title': "Privacy Policy"
            }
            return render(request, 'adminestration/privacy_policy.html', context = context)
    return redirect('login')

def about(request):
    if request.user.is_authenticated:
        if request.user.is_staff == True:
            if request.method == "POST":
                about = request.POST['about']
                c = About(about = about)
                c.save()
                messages.success(request, f"Added Successfully.")
            about = About.objects.first()
            context = {
                'about' : about,
                'page' : "About",
                'title': "About"
            }
            return render(request, 'adminestration/about.html', context = context)
    return redirect('login')

def return_policy(request):
    if request.user.is_authenticated:
        if request.user.is_staff == True:
            if request.method == "POST":
                return_policy = request.POST['return_policy']
                c = Return_Policy(return_policy = return_policy)
                c.save()
                messages.success(request, f"Added Successfully.")
            return_policy = Return_Policy.objects.first()
            context = {
                'return_policy' : return_policy,
                'page' : "Return",
                'title': "Return Policy"
            }
            return render(request, 'adminestration/return_policy.html', context = context)
    return redirect('login')

def terms_condition(request):
    if request.user.is_authenticated:
        if request.user.is_staff == True:
            if request.method == "POST":
                terms_condition = request.POST['terms_condition']
                c = Terms_Condition(terms = terms_condition)
                c.save()
                messages.success(request, f"Added Successfully.")
            terms = Terms_Condition.objects.first()
            context = {
                'terms' : terms,
                'page' : "Terms",
                'title': "Terms & Condition"
            }
            return render(request, 'adminestration/terms_condition.html', context = context)
    return redirect('login')

    
def edit_privacy_policy(request, privacy_id):
    if request.user.is_authenticated:
        if request.user.is_staff == True:
            if request.method == "POST":
                privacy_policy = request.POST['privacy_policy']
                c = Privacy_Policy.objects.filter(privacy_id = privacy_id).first()
                c.privacy = privacy_policy
                c.save()
                messages.success(request, f"Updated Successfully.")
            privacy = Privacy_Policy.objects.first()
            context = {
                'privacy' : privacy,
                'page' : "Privacy",
                'title': "Privacy Policy"
            }
            return render(request, 'adminestration/privacy_policy.html', context = context)
    return redirect('login')

def edit_about(request, about_id):
    if request.user.is_authenticated:
        if request.user.is_staff == True:
            if request.method == "POST":
                about = request.POST['about']
                c = About.objects.filter(about_id = about_id).first()
                c.about = about
                c.save()
                messages.success(request, f"Updated Successfully.")
            about = About.objects.first()
            context = {
                'about' : about,
                'page' : "About",
                'title': "About"
            }
            return render(request, 'adminestration/about.html', context = context)
    return redirect('login')

def edit_return_policy(request, return_id):
    if request.user.is_authenticated:
        if request.user.is_staff == True:
            if request.method == "POST":
                return_policy = request.POST['return_policy']
                c = Return_Policy.objects.filter(return_id = return_id).first()
                c.return_policy = return_policy
                c.save()
                messages.success(request, f"Updated Successfully.")
            return_policy = Return_Policy.objects.first()
            context = {
                'return_policy' : return_policy,
                'page' : "Return",
                'title': "Return Policy"
            }
            return render(request, 'adminestration/return_policy.html', context = context)
    return redirect('login')

def edit_terms_condition(request, terms_id):
    if request.user.is_authenticated:
        if request.user.is_staff == True:
            if request.method == "POST":
                terms_condition = request.POST['terms_condition']
                c = Terms_Condition.objects.filter(terms_id = terms_id).first()
                c.terms = terms_condition
                c.save()
                messages.success(request, f"Updated Successfully.")
            
            return redirect('admin_terms_condition')
    return redirect('login')

def admin_video(request):
    if request.user.is_authenticated:
        if request.user.is_staff == True:    
            if request.method == "POST":
                video = request.FILES['video']
                n = Video(video = video)
                n.save()
                pass
            video = Video.objects.all().order_by('-date_added')
            search = None
            search = request.GET.get('search')
            
            
            paginator = Paginator(video, 15)
            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)
            context = {
                'video' : page_obj,
                'page' : 'Video',
                'title' : 'Video'
            }
            return render(request, 'adminestration/video.html', context = context)
    return redirect('login')


def admin_delete_video(request, video_id):
    if request.user.is_authenticated:
        if request.user.is_staff == True:
            video = Video.objects.filter(video_id = video_id).first()
            video.delete()
            return redirect('admin_video')
    return redirect('login')
