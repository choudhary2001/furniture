from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
import random
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.authtoken.models import Token
from django.contrib.auth import logout
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from rest_framework.renderers import JSONRenderer
import jwt
from django.conf import settings    
from django.views.decorators.http import require_POST
from django.shortcuts import render
from django.shortcuts import render, redirect, get_object_or_404
from main.forms import SignupForm
from django.contrib.auth.models import User
import uuid
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.template import Context
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.core.validators import validate_email
from django.db import IntegrityError
import random
from main.models import crousel, User_verification, Category, Product, productreview, Cart, Address, Order, WarrantyRegistration, WarrantyClaim, Partner, Contact, Profile, Complainet, News, Faq, OrderData, Wish, Offer, Privacy_Policy, About, Return_Policy, Terms_Condition
from django.db.models import Max, Min, Count, Avg
from django.core.paginator import Paginator
from django.http import JsonResponse, HttpResponse, request, response
from django.views.decorators.csrf import csrf_exempt
from django.db.models.query_utils import Q
import razorpay
from django.conf import settings
from django.http import HttpResponseBadRequest
from .serializers import CrouselSerializer, NewsSerializer, ProductSerializer, FaqSerializer, ProductSerializer, CategorySerializer, ProductReviewSerializer, AddressSerializer,  ProfileSerializer, OrderSerializer, WarrantyRegistrationSerializer, WarrantyClaimSerializer, PartnerSerializer, WishSerializer, UserSerializer, CartSerializer
from rest_framework.views import APIView
from django.utils import timezone
from rest_framework.permissions import AllowAny
from rest_framework.decorators import permission_classes
import os
from twilio.rest import Client
# import track
import urllib.request
import urllib.parse
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework_simplejwt.tokens import AccessToken

from django.db.models import Sum

import razorpay

account_sid = settings.TWILIO_ACCOUNT_SID
auth_token = settings.TWILIO_AUTH_TOKEN
client = Client(account_sid, auth_token)


# track.api_key =  settings.INTERKART_APII
test_local_api = settings.TEST_LOCAL_API

def on_error(error, queue_msg):
    print("An error occurred", error)
    print("Queue message", queue_msg)

# track.debug = True
# track.on_error = on_error


def sendSMS(apikey, numbers, sender, message):
    data =  urllib.parse.urlencode({'apikey': apikey, 'numbers': numbers,
        'message' : message, 'sender': sender})
    data = data.encode('utf-8')
    request = urllib.request.Request("https://api.textlocal.in/send/?")
    f = urllib.request.urlopen(request, data)
    print(f)
    fr = f.read()
    return(fr)

@swagger_auto_schema(
    method='post',
    operation_description="User signup endpoint. Creates a new user and sends an OTP for verification.",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'first_name': openapi.Schema(type=openapi.TYPE_STRING, description="First name of the user"),
            'last_name': openapi.Schema(type=openapi.TYPE_STRING, description="Last name of the user"),
            'username': openapi.Schema(type=openapi.TYPE_STRING, description="Email or phone number of the user"),
            'password': openapi.Schema(type=openapi.TYPE_STRING, description="Password for the account"),
        },
        required=['first_name', 'last_name', 'username', 'password']
    ),
    responses={
        200: openapi.Response(description="OTP sent successfully."),
        400: openapi.Response(description="Error occurred during signup.")
    }
)
@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
@csrf_exempt
def api_signup(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        print(data)
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        email = data.get('username')
        password = data.get('password')

        # Perform input validation
        if not first_name or not last_name or not email or not password:
            return JsonResponse({'error': 'Missing required fields.'}, status=400)

        # Check if user with the given email already exists
        if User.objects.filter(username=email).exists():
            return JsonResponse({'error': 'User with this email already exists.'}, status=400)

        # Create a new user instance
        try:
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
                User_verification.objects.filter(username=email).delete()
                v = User_verification(username = email, otp = otp)
                print(v)
                v.save()
                try:
                    subject = 'Account Verification'
                    message = f"""Thank you for creating an account on our website! Your OTP for account verification is: {otp}. Please enter this code in the verification field on our website to confirm your account and gain access to all our features. If you did not create an account, please ignore this message. Thank you!"""
                    from_email = 'contact@swastik.ai'
                    recipient_list = [email,]
                    send_mail(subject, message, from_email, recipient_list)
                    return JsonResponse({'success': 'OTP sent successfully. Please verify your account.'})
                except Exception as e:
                    print(e)
                    return JsonResponse({'error': f'{e}'})
            except Exception as e:
                messages.error(request, f'Email or phone number is already exists, so please try another email or phone number.')
                return JsonResponse({'error': 'Email or phone number is already exists, so please try another email or phone number.'}, status=400)

        except Exception as e:
            print(e)
            if email.isdigit() == True:
                try:
                    # User.objects.create_user(username=email, first_name = first_name, last_name = last_name, password=password, is_active = False)
                    user = User(first_name=first_name, last_name=last_name, username=email,  is_active=False)
                    user.set_password(password)
                    user.save()
                    request.session['user'] = email
                    user = User.objects.filter(username=email).first()
                    p = Profile(user=user, phone_number=email, is_active=False)
                    p.save()
                    fixed_digits = 6 
                    otp = random.randrange(111111, 999999, fixed_digits)
                    print(otp)
                    v = User_verification(username = email, otp = otp)
                    print(v)
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
                    return JsonResponse({'success': 'OTP sent successfully. Please verify your account.'})
                except IntegrityError:
                    messages.error(request, f'Email or phone number is already exists, so please try another email or phone number.')
                    return JsonResponse({'error': 'Email or phone number is already exists, so please try another email or phone number.'}, status=400)
                except Exception as e:
                    print(e)
            else:
                messages.error(request, f'Please Fill all the field correctly.')
                return JsonResponse({'error': 'Please Fill all the field correctly.'}, status=400)

        return JsonResponse({'success': 'OTP sent successfully. Please verify your account.'})
    else:
        return JsonResponse({'error': 'Invalid request method.'}, status=400)

@swagger_auto_schema(
    method='post',
    operation_description="User sign-in endpoint. Authenticate user and send OTP if account is inactive.",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'username': openapi.Schema(type=openapi.TYPE_STRING, description="Username or email of the user"),
            'password': openapi.Schema(type=openapi.TYPE_STRING, description="Password of the user"),
        },
        required=['username', 'password']
    ),
    responses={
        200: openapi.Response(description="Authentication successful and access tokens returned."),
        400: openapi.Response(description="Error occurred during authentication.")
    }
)
@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
@require_POST
@csrf_exempt
def api_signin(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        email = data.get('username')
        password = data.get('password')
        # Perform input validation
        if not email or not password:
            return JsonResponse({'error': 'Missing required fields.'}, status=400)
        try:
            # Authenticate the user
            user = authenticate(request, username=email, password=password)
            # print(user.password)
            print(password)
            if user is not None:
                
                print(user.is_active)
                if user.is_active == True:
                    login(request, user)
                    if user.is_staff == True:
                        return JsonResponse({'error': 'Please login with another account.'}, status=400)
                    refresh = RefreshToken.for_user(user)
                    access = str(refresh.access_token)
                    return JsonResponse({ 'access': access, 'refresh': str(refresh)}, status=200)
                    print('authenticated')
                else:
                    print('not authenticated')
                    request.session['user'] = username
                    fixed_digits = 6 
                    otp = random.randrange(111111, 999999, fixed_digits)
                    print(otp)
                    User_verification.objects.filter(username=username).delete()
                    v = User_verification(username = username, otp = otp)
                    print(v)
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
                    return JsonResponse({'success': 'OTP sent successfully. Please verify your account.', 'otp': 'otp'})
                
            else:
                print('error')
                return JsonResponse({'error': 'Incorrect password.'}, status=400)
        except Exception as e:
            print(e)
            return JsonResponse({'error': f'{e}'}, status=400)
    else:
        return JsonResponse({'error': 'Invalid request method.'}, status=400)

@swagger_auto_schema(
    method='post',
    operation_description="Verify OTP for user account login or password reset.",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'username': openapi.Schema(type=openapi.TYPE_STRING, description="Email or username of the user"),
            'otp': openapi.Schema(type=openapi.TYPE_STRING, description="One Time Password sent to the user"),
            'm': openapi.Schema(type=openapi.TYPE_STRING, description="Operation type: 'login' or 'forget'")
        },
        required=['username', 'otp', 'm']
    ),
    responses={
        200: openapi.Response(description="OTP verification successful."),
        400: openapi.Response(description="Error occurred during OTP verification.")
    }
)
@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
@require_POST
@csrf_exempt
def otp_verification(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        print(data)
        email = data.get('username')
        otp = data.get('otp')
        m = data.get('m')
        print(email, otp)
        # Retrieve the user with the given email
        user = User.objects.filter(username=email).first()
        print(user)
        if user:
            o = OTP.objects.filter(user=user).latest('created_at')
            print(o.user)
            print(o.otp_code)
            # Compare the entered OTP with the stored OTP
            if int(otp) == int(o.otp_code):
                if m == 'forget':
                    print(otp, o.otp_code, m)
                    return JsonResponse({'success': 'OTP verification successful.'}, status = 200)
                user.is_active = True
                user.save()
                if m == 'login':
                    login(request, user)
                    refresh = RefreshToken.for_user(user)
                    access = str(refresh.access_token)
                    return JsonResponse({ 'access': access, 'refresh': str(refresh)}, status=200)
                return JsonResponse({'success': 'OTP verification successful.'}, status = 200)
            else:
                return JsonResponse({'error': 'Invalid OTP.'}, status=400)
        return JsonResponse({'error': "User doesn't exist."}, status=400)
    else:
        return JsonResponse({'error': 'Invalid request method.'}, status=400)

@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
@csrf_exempt
def custom_token(request):
    authorization_header = request.META.get('HTTP_AUTHORIZATION')
    print(authorization_header)
    try:
        token = authorization_header.split(" ")[1]
    except IndexError:
        return JsonResponse({"success": False, "error": "login"}, status = 201)
    # Decode the token and get the user ID
    try:
        decoded_token = jwt.decode(token, options={"verify_signature": False})
        print(decoded_token)
        user_id = decoded_token["user_id"]
        print(user_id)
        user = User.objects.filter(id=user_id).first()
        if user is None:
            return JsonResponse({"success": False, "error": "login"}, status = 201)
        login(request, user)
        refresh = RefreshToken.for_user(user)
        access = str(refresh.access_token)
        print(refresh, access)
        # return JsonResponse({"success": False, "error": "login"}, status = 201)
        return JsonResponse({'access': access, 'refresh': str(refresh)}, status=200)
    except jwt.InvalidTokenError:
        print("Invalid token")
        print(authorization_header)
    return JsonResponse({"success": False, }, status = 201)

@swagger_auto_schema(
    method='post',
    operation_description="Verify OTP for user account registration or login.",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'username': openapi.Schema(type=openapi.TYPE_STRING, description="Username or email of the user"),
            'otp': openapi.Schema(type=openapi.TYPE_STRING, description="One Time Password sent to the user"),
            'm': openapi.Schema(type=openapi.TYPE_STRING, description="Operation type: 'login' or 'forget'")
        },
        required=['username', 'otp', 'm']
    ),
    responses={
        200: openapi.Response(description="OTP verification successful."),
        400: openapi.Response(description="Error occurred during OTP verification.")
    }
)
@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
@require_POST
@csrf_exempt
def api_twoverificationmobile(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        print(data)
        username = data.get('username')
        mobile = data.get('otp')
        m = data.get('m')
        if mobile:
            if request.method == 'POST':
                otp = mobile
                print(otp)
                d = User_verification.objects.filter(username = username).first()

                print(d.otp)
                if otp == d.otp:
                    user = User.objects.filter(username = username).first()
                    print(user)
                    if user.is_active:
                        if m == 'forget':
                            print(otp, d.otp, m)
                            refresh = RefreshToken.for_user(user)
                            access = str(refresh.access_token)
                            return JsonResponse({'success': 'OTP verification successful.', 'refresh': str(refresh)}, status = 200)
                    user.is_active = True
                    user.save()
                    p = Profile.objects.filter(user = user).first()
                    p.is_active = True
                    p.save()
                    if m == 'login':
                        login(request, user)
                        refresh = RefreshToken.for_user(user)
                        access = str(refresh.access_token)
                        return JsonResponse({ 'access': access, 'refresh': str(refresh)}, status=200)
                    return JsonResponse({'success': 'OTP verification successful.'}, status = 200)
            else:
                return JsonResponse({'error': 'Invalid OTP.'}, status=400)
    
        if username:
            try:
                user = User.objects.filter(username = username).first()
                if user is None:
                    return JsonResponse({'error': "User doesn't exist."}, status=400)
                validate_email(username)
                try:
                    fixed_digits = 6 
                    otp = random.randrange(111111, 999999, fixed_digits)
                    print(otp)
                    User_verification.objects.filter(username=username).delete()
                    v = User_verification(username = username, otp = otp)
                    print(v)
                    v.save()
                    subject = 'Account Verification'
                    message = f"""Your verification code is {otp}. Please enter this code to verify your account and complete the registration process. If you did not request this code, please ignore this message. Thank you!"""
                    from_email = 'contact@swastik.ai'
                    recipient_list = [username,]
                    send_mail(subject, message, from_email, recipient_list)
                    return JsonResponse({'success': 'OTP sent successfully. Please verify your account.'}, status = 200)
                except Exception as e:
                    print(e)
                    #####################
            except:
                if username.isdigit() == True:
                    fixed_digits = 6 
                    otp = random.randrange(111111, 999999, fixed_digits)
                    print(otp)
                    User_verification.objects.filter(username=username).delete()
                    v = User_verification(username = username, otp = otp)
                    print(v)
                    v.save()
                    number = username
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
                    return JsonResponse({'success': 'OTP sent successfully. Please verify your account.'}, status = 200)

        return JsonResponse({'error': "User doesn't exist."}, status=400)
    else:
        return JsonResponse({'error': 'Invalid request method.'}, status=400)

@swagger_auto_schema(
    method='post',
    operation_description="Change the password of a user using a JWT token.",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'username': openapi.Schema(type=openapi.TYPE_STRING, description="JWT token containing the user ID"),
            'password': openapi.Schema(type=openapi.TYPE_STRING, description="New password for the user")
        },
        required=['username', 'password']
    ),
    responses={
        200: openapi.Response(description="Password changed successfully."),
        400: openapi.Response(description="Error occurred while changing password.")
    }
)
@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
@require_POST
@csrf_exempt
def api_forget_password_change(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        print(data)
        try:
            token = data.get('username')
            decoded_token = jwt.decode(token, options={"verify_signature": False})
            print(decoded_token)
            user_id = decoded_token["user_id"]
            print(user_id)
            user = User.objects.filter(id = user_id).first()
            print(user)
            password = data.get('password')
            # user = User.objects.filter(username=email).first()
            print(user)
        except Exception as e:
            return JsonResponse({'error': "User doesn't exist."}, status=400)
        if user:
            if user.is_active:
                user.set_password(password)
                user.save()
                return JsonResponse({'success': 'Password Changed Successfully.'}, status = 200)
            else:
                return JsonResponse({'error': "User account doesn't activated."}, status=400)
        return JsonResponse({'error': "User doesn't exist."}, status=400)
    else:
        return JsonResponse({'error': 'Invalid request method.'}, status=400)

   
@csrf_exempt
def api_logout_view(request):
    authorization_header = request.META.get('HTTP_AUTHORIZATION')

    # Decode the token and get the user ID
    print(authorization_header)
    if authorization_header is None:
        return JsonResponse({"success": False, "error": "login"}, status = 201)
    try:
        token = authorization_header.split(" ")[1]
        decoded_token = jwt.decode(token, options={"verify_signature": False})
        print(decoded_token)
        user_id = decoded_token["user_id"]
        print(user_id)
        user = User.objects.filter(id = user_id).first()
        if user is None:
            return JsonResponse({"success": False, "error": "login"}, status = 201)
        
    except jwt.InvalidTokenError:
        print("Invalid token")
        print(authorization_header)

    access_token = authorization_header.split(" ")[1]

    # Invalidate the token - in case of server-side tracking of blacklisted tokens
    # For example, store invalidated access tokens in a blacklist database (optional)
    # Depending on your setup, this may involve logging the user out, removing their session, etc.
    token = AccessToken(access_token)
    user_id = token['user_id']

    # Perform user-specific logout operations, such as ending a session
    # If using Django session:
    if hasattr(user, 'auth_token'):
        user.auth_token.delete()  # If you're using Django Token Auth

    # Alternatively, manually delete the session (if session-based auth)
    request.session.flush()
    return JsonResponse({"success": True, "message": "Logout successful"}, status=200)


@swagger_auto_schema(
    method='get',
    operation_description="Retrieve index data including carousels, featured products, news, FAQs, and categories.",
    responses={
        200: openapi.Response(
            description="Successful response with index data.",
            examples={
                "application/json": {
                    "crousel": [
                        {
                            "id": 1,
                            "image": "url_to_image.jpg",
                            "link": "http://example.com"
                        }
                    ],
                    "title": "Index",
                    "products": [
                        {
                            "id": 1,
                            "title": "Featured Product",
                            "price": 99.99,
                            "is_featured": "true"
                        }
                    ],
                    "faq": [
                        {
                            "id": 1,
                            "question": "What is the return policy?",
                            "answer": "You can return any item within 30 days."
                        }
                    ],
                    "category": [
                        {
                            "id": 1,
                            "name": "Category Name",
                            "slug": "category-name"
                        }
                    ]
                }
            }
        )
    }
)
@api_view(['GET'])
@permission_classes([AllowAny])
@csrf_exempt
def api_index(request):
    try:
        c = crousel.objects.all()
    except Exception as e:
        c = {}
    n = News.objects.filter(status=True)
    p = Product.objects.filter(is_featured=True).first()
    faq = Faq.objects.filter(status="Show").order_by('-date_added')

    cat= Category.objects.all()

    top_products = Product.objects.annotate(total_sold=Sum('orderdata__quantity')).order_by('-total_sold')[:10]

    crousel_serializer = CrouselSerializer(c, many=True)
    news_serializer = NewsSerializer(n, many=True)
    product_serializer = ProductSerializer(top_products, many=True)
    faq_serializer = FaqSerializer(faq, many=True)
    category_serializer = CategorySerializer(cat, many = True)

    data = {
        'crousel': crousel_serializer.data,
        'title': 'Index',
        # 'news': news_serializer.data,
        'products': product_serializer.data,
        'faq': faq_serializer.data,
        'category' : category_serializer.data
    }

    return JsonResponse(data, status=200)



@swagger_auto_schema(
    method='get',
    operation_description="Retrieve a list of products, with optional filtering by category, search term, and price range.",
    manual_parameters=[
        openapi.Parameter('search', openapi.IN_QUERY, description="Search term to filter products by title or details", type=openapi.TYPE_STRING),
        openapi.Parameter('category', openapi.IN_QUERY, description="Slug of the category to filter products", type=openapi.TYPE_STRING),
        openapi.Parameter('low_to_high', openapi.IN_QUERY, description="Sort products by price. '0' for low to high, '1' for high to low", type=openapi.TYPE_STRING),
        openapi.Parameter('page', openapi.IN_QUERY, description="Page number for pagination", type=openapi.TYPE_INTEGER),
    ],
    responses={
        200: openapi.Response(
            description="List of products retrieved successfully.",
            examples={
                "application/json": {
                    "products": [
                        {
                            "id": 1,
                            "title": "Sample Product",
                            "price": 29.99,
                            "slug": "sample-product"
                        }
                    ],
                    "category": {
                        "id": 1,
                        "name": "Sample Category",
                        "slug": "sample-category"
                    },
                    "low_to_high": "0",
                    "min_price": 10,
                    "max_price": 100,
                    "minMaxPrice": {
                        "min": 10,
                        "max": 100
                    },
                    "search": "example",
                    "categoryy": "sample-category",
                    "title": "Products",
                    "cat": "Sample Category",
                    "cats": "sample-category"
                }
            }
        )
    }
)
@api_view(['GET'])
@permission_classes([AllowAny])
@csrf_exempt
def api_products(request, category_slug=None):
    products = Product.objects.all().order_by('-date_added')
    search = None
    search = request.GET.get('search')
    if search:
        products = products.filter(Q(title__icontains=search) | Q(details__icontains=search))
    categoryy = None
    category_ss = None
    categoryy = request.GET.get('category')
    if categoryy:
        category_ss = get_object_or_404(Category, slug=categoryy)
        if category_ss.children.all():
            subcategories = [category_s] + list(category_s.children.all())
            print(subcategories)
            products = Product.objects.filter(category__in=subcategories)
        else:
            products = products.filter(category=category_ss)
    
    low_to_high = request.GET.get('low_to_high')
    if low_to_high == '0':
        products = products.order_by('price')
    elif low_to_high == '1':
        products = products.order_by('-price')
    else:
        low_to_high = None

    slug = category_slug
    category_s = None
    if slug:
        category_s = get_object_or_404(Category, slug=slug)
        if category_s.children.all():
            parent_category = category_s.parent
            products = Product.objects.filter(category__in=[category_s, parent_category])
        else:
            products = products.filter(category=category_s)

    min_price = products.aggregate(Min('price'))
    max_price = products.aggregate(Max('price'))
    p = products.aggregate(Min('price'), Max('price'))

    paginator = Paginator(products, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    if category_slug:
        capitalized_string = category_slug.title().replace("-", " ")
    else:
        capitalized_string = None

    product_serializer = ProductSerializer(page_obj, many=True)
    category_serializer = CategorySerializer(category_s)

    data = {
        'products': product_serializer.data,
        'category': category_serializer.data,
        'low_to_high': low_to_high,
        'min_price': min_price,
        'max_price': max_price,
        'minMaxPrice': p,
        'search': search,
        'categoryy': categoryy,
        'title': 'Products',
        'cat': capitalized_string,
        'cats': category_slug
    }

    return JsonResponse(data, status=200)


@swagger_auto_schema(
    method='get',
    operation_description="Retrieve product details along with related products and reviews.",
    manual_parameters=[
        openapi.Parameter('category_slug', openapi.IN_PATH, description="Slug of the product category", type=openapi.TYPE_STRING),
        openapi.Parameter('product_slug', openapi.IN_PATH, description="Slug of the product", type=openapi.TYPE_STRING),
    ],
    responses={
        200: openapi.Response(
            description="Product details retrieved successfully.",
            examples={
                "application/json": {
                    "product_detail": {
                        "id": 1,
                        "name": "Sample Product",
                        "description": "Product description here",
                        "price": 29.99,
                        "slug": "sample-product"
                    },
                    "related_product": [
                        {
                            "id": 2,
                            "name": "Related Product",
                            "price": 19.99,
                            "slug": "related-product"
                        }
                    ],
                    "reviews": [
                        {
                            "id": 1,
                            "review_rating": 4,
                            "review_text": "Great product!"
                        }
                    ],
                    "avg_rating": 4
                }
            }
        ),
        404: openapi.Response(
            description="Product not found.",
            examples={
                "application/json": {
                    "error": "Product not found."
                }
            }
        )
    }
)
@api_view(['GET'])
@permission_classes([AllowAny])
@csrf_exempt
def api_product_details(request, category_slug, product_slug):
    product = get_object_or_404(Product, slug=product_slug)
    related_products = Product.objects.filter(category=product.category).exclude(slug=product_slug)
    reviews = productreview.objects.filter(product=product)
    avg_reviews = productreview.objects.filter(product=product).aggregate(avg_rating=Avg('review_rating'))
    avg_rating = int(avg_reviews['avg_rating']) if avg_reviews['avg_rating'] is not None else 0

    product_serializer = ProductSerializer(product)
    related_products_serializer = ProductSerializer(related_products, many=True)
    reviews_serializer = ProductReviewSerializer(reviews, many=True)

    data = {
        'product_detail': product_serializer.data,
        'related_product': related_products_serializer.data,
        'reviews': reviews_serializer.data,
        'avg_rating': avg_rating
    }
    return JsonResponse(data, status=200)


@swagger_auto_schema(
    method='post',
    operation_description="Add a product review",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'product': openapi.Schema(type=openapi.TYPE_STRING, description='Product slug'),
            'rating': openapi.Schema(type=openapi.TYPE_NUMBER, description='Rating for the product'),
            'message': openapi.Schema(type=openapi.TYPE_STRING, description='Review message'),
        },
        required=['product', 'rating', 'message'],
    ),
    responses={
        200: openapi.Response(
            description="Review added successfully",
            examples={
                "application/json": {
                    "success": True,
                    "message": "Done"
                }
            }
        ),
        201: openapi.Response(
            description="User not logged in or token is invalid",
            examples={
                "application/json": {
                    "success": False,
                    "error": "login"
                }
            }
        ),
        400: openapi.Response(
            description="Bad request, invalid data",
            examples={
                "application/json": {
                    "success": False,
                    "message": "Something went wrong. Try again."
                }
            }
        ),
    },
    security=[{'Bearer': []}],
)
@csrf_exempt
@permission_classes([AllowAny])
@api_view(['POST'])
def api_add_product_review(request):
    authorization_header = request.META.get('HTTP_AUTHORIZATION')

    # Decode the token and get the user ID
    print(authorization_header)
    if authorization_header is None:
        return JsonResponse({"success": False, "error": "login"}, status = 201)
    try:
        token = authorization_header.split(" ")[1]
        decoded_token = jwt.decode(token, options={"verify_signature": False})
        print(decoded_token)
        user_id = decoded_token["user_id"]
        print(user_id)
        user = User.objects.filter(id = user_id).first()
        if user is None:
            return JsonResponse({"success": False, "error": "login"}, status = 201)
        
    except jwt.InvalidTokenError:
        print("Invalid token")
        print(authorization_header)
    if user.is_authenticated:
        if user.is_active == True:
            if request.method == 'POST':
                data = json.loads(request.body.decode('utf-8'))
                product_slug = data.get('product_slug')
                product = get_object_or_404(Product, slug = product_slug)
                rating = data.get('rating')
                message = data.get('message')
                print(rating, message)
                review = productreview(product = product, user = user, review_rating = rating, review_text = message )
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


@swagger_auto_schema(
    method='post',
    operation_description="Add a new address for the authenticated user.",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'first_name': openapi.Schema(type=openapi.TYPE_STRING, description='First name of the user'),
            'last_name': openapi.Schema(type=openapi.TYPE_STRING, description='Last name of the user'),
            'country': openapi.Schema(type=openapi.TYPE_STRING, description='Country of the address'),
            'street_address': openapi.Schema(type=openapi.TYPE_STRING, description='Street address'),
            'apartment': openapi.Schema(type=openapi.TYPE_STRING, description='Apartment or local address (optional)'),
            'town': openapi.Schema(type=openapi.TYPE_STRING, description='Town or city'),
            'state': openapi.Schema(type=openapi.TYPE_STRING, description='State of the address'),
            'postcode': openapi.Schema(type=openapi.TYPE_STRING, description='Postal code'),
            'phone': openapi.Schema(type=openapi.TYPE_STRING, description='Phone number'),
            'email': openapi.Schema(type=openapi.TYPE_STRING, description='Email address'),
        },
        required=['first_name', 'last_name', 'country', 'street_address', 'town', 'state'],
    ),
    responses={
        200: openapi.Response(
            description="Address added successfully",
            examples={
                "application/json": {
                    "success": True
                }
            }
        ),
        401: openapi.Response(
            description="Authentication required",
            examples={
                "application/json": {
                    "error": "Authentication required."
                }
            }
        ),
    },
    security=[{'Bearer': []}],
)
@swagger_auto_schema(
    method='get',
    operation_description="Retrieve all addresses for the authenticated user.",
    responses={
        200: openapi.Response(
            description="Addresses retrieved successfully",
            examples={
                "application/json": {
                    "address": [
                        {
                            "first_name": "John",
                            "last_name": "Doe",
                            "country": "USA",
                            "address": "123 Main St",
                            "local_address": "Apt 4B",
                            "town": "Springfield",
                            "state": "IL",
                            "postalcode": "62701",
                            "phone": "555-1234",
                            "email": "john.doe@example.com"
                        }
                    ]
                }
            }
        ),
        401: openapi.Response(
            description="Authentication required",
            examples={
                "application/json": {
                    "error": "Authentication required."
                }
            }
        ),
    },
)
@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
@csrf_exempt
def api_add_address(request):
    authorization_header = request.META.get('HTTP_AUTHORIZATION')
    print(authorization_header)
    if authorization_header is None:
        return JsonResponse({"success": False, "error": "login"}, status = 201)
    try:
        token = authorization_header.split(" ")[1]
        decoded_token = jwt.decode(token, options={"verify_signature": False})
        print(decoded_token)
        user_id = decoded_token["user_id"]
        print(user_id)
        user = User.objects.filter(id = user_id).first()
        if user is None:
            return JsonResponse({"success": False, "error": "login"}, status = 201)
        
    except jwt.InvalidTokenError:
        print("Invalid token")
        print(authorization_header)
    if user.is_authenticated:
        if user.is_active == True:
            if request.method == "POST":
                data = json.loads(request.body.decode('utf-8'))
                first_name = data.get('first_name')
                last_name = data.get('last_name')
                country = data.get('country')
                street_address = data.get('street_address')
                apartment = data.get('apartment')
                town = data.get('town')
                state = data.get('state')
                postcode = data.get('postcode')
                phone = data.get('phone')
                email = data.get('email')

                address = Address(
                    user=user,
                    first_name=first_name,
                    last_name=last_name,
                    country=country,
                    address=street_address,
                    local_address=apartment,
                    town=town,
                    state=state,
                    postalcode=postcode,
                    phone=phone,
                    email=email
                )
                address.save()
                return JsonResponse(
                    {
                        'success' : True
                    }
                )
            if request.method == "GET":
                addresses = Address.objects.filter(user=user)
                address_serializer = AddressSerializer(addresses, many=True)
                data = {
                    'address': address_serializer.data
                }
                return JsonResponse(data)
    return JsonResponse({'error': 'Authentication required.'}, status=401)


@swagger_auto_schema(
    method='post',
    operation_description="Update an existing address for the authenticated user.",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'first_name': openapi.Schema(type=openapi.TYPE_STRING, description='First name of the user'),
            'last_name': openapi.Schema(type=openapi.TYPE_STRING, description='Last name of the user'),
            'country': openapi.Schema(type=openapi.TYPE_STRING, description='Country of the address'),
            'street_address': openapi.Schema(type=openapi.TYPE_STRING, description='Street address'),
            'apartment': openapi.Schema(type=openapi.TYPE_STRING, description='Apartment or local address (optional)'),
            'town': openapi.Schema(type=openapi.TYPE_STRING, description='Town or city'),
            'state': openapi.Schema(type=openapi.TYPE_STRING, description='State of the address'),
            'postcode': openapi.Schema(type=openapi.TYPE_STRING, description='Postal code'),
            'phone': openapi.Schema(type=openapi.TYPE_STRING, description='Phone number'),
            'email': openapi.Schema(type=openapi.TYPE_STRING, description='Email address'),
        },
        required=['first_name', 'last_name', 'country', 'street_address', 'town', 'state'],
    ),
    responses={
        200: openapi.Response(
            description="Address updated successfully",
            examples={
                "application/json": {
                    "success": True
                }
            }
        ),
        401: openapi.Response(
            description="Authentication required",
            examples={
                "application/json": {
                    "error": "Authentication required."
                }
            }
        ),
        404: openapi.Response(
            description="Address not found",
            examples={
                "application/json": {
                    "error": "Address not found."
                }
            }
        ),
    },
    security=[{'Bearer': []}],
)
@swagger_auto_schema(
    method='get',
    operation_description="Retrieve the specified address for the authenticated user.",
    responses={
        200: openapi.Response(
            description="Address retrieved successfully",
            examples={
                "application/json": {
                    "first_name": "John",
                    "last_name": "Doe",
                    "country": "USA",
                    "address": "123 Main St",
                    "local_address": "Apt 4B",
                    "town": "Springfield",
                    "state": "IL",
                    "postalcode": "62701",
                    "phone": "555-1234",
                    "email": "john.doe@example.com"
                }
            }
        ),
        401: openapi.Response(
            description="Authentication required",
            examples={
                "application/json": {
                    "error": "Authentication required."
                }
            }
        ),
        404: openapi.Response(
            description="Address not found",
            examples={
                "application/json": {
                    "error": "Address not found."
                }
            }
        ),
    },
)
@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
@csrf_exempt
def api_change_address(request, address_id):
    authorization_header = request.META.get('HTTP_AUTHORIZATION')

    # Decode the token and get the user ID
    print(authorization_header)
    if authorization_header is None:
        return JsonResponse({"success": False, "error": "login"}, status = 201)
    try:
        token = authorization_header.split(" ")[1]
        decoded_token = jwt.decode(token, options={"verify_signature": False})
        print(decoded_token)
        user_id = decoded_token["user_id"]
        print(user_id)
        user = User.objects.filter(id = user_id).first()
        if user is None:
            return JsonResponse({"success": False, "error": "login"}, status = 201)
        
    except jwt.InvalidTokenError:
        print("Invalid token")
        print(authorization_header)
    if user.is_authenticated and user.is_active:
        address = Address.objects.filter(id=address_id, user=user).first()
        if address:
            if request.method == "POST":
                data = json.loads(request.body.decode('utf-8'))
                first_name = data.get('first_name')
                last_name = data.get('last_name')
                country = data.get('country')
                street_address = data.get('street_address')
                apartment = data.get('apartment')
                town = data.get('town')
                state = data.get('state')
                postcode = data.get('postcode')
                phone = data.get('phone')
                email = data.get('email')

                address.first_name = first_name
                address.last_name = last_name
                address.country = country
                address.address = street_address
                address.local_address = apartment
                address.town = town
                address.state = state
                address.postalcode = postcode
                address.phone = phone
                address.email = email
                address.save()

                return JsonResponse(
                    {
                        'success' : True
                    }
                )
            serializer = AddressSerializer(address)
            return JsonResponse(serializer.data)
        return JsonResponse({'error': 'Address not found.'}, status=404)
    return JsonResponse({'error': 'Authentication required.'}, status=401)


@swagger_auto_schema(
    method='post',
    operation_description="Delete an address for the authenticated user.",
    responses={
        200: openapi.Response(
            description="Address deleted successfully",
            examples={
                "application/json": {
                    "success": True
                }
            }
        ),
        401: openapi.Response(
            description="Authentication required",
            examples={
                "application/json": {
                    "error": "Authentication required."
                }
            }
        ),
        404: openapi.Response(
            description="Address not found",
            examples={
                "application/json": {
                    "error": "Address not found."
                }
            }
        ),
    },
    security=[{'Bearer': []}],
)
@api_view(['POST'])
@csrf_exempt
def api_delete_address(request, address_id):
    authorization_header = request.META.get('HTTP_AUTHORIZATION')

    # Decode the token and get the user ID
    print(authorization_header)
    if authorization_header is None:
        return JsonResponse({"success": False, "error": "login"}, status = 201)
    try:
        token = authorization_header.split(" ")[1]
        decoded_token = jwt.decode(token, options={"verify_signature": False})
        print(decoded_token)
        user_id = decoded_token["user_id"]
        print(user_id)
        user = User.objects.filter(id = user_id).first()
        if user is None:
            return JsonResponse({"success": False, "error": "login"}, status = 201)
        
    except jwt.InvalidTokenError:
        print("Invalid token")
        print(authorization_header)
    if user.is_authenticated and user.is_active:
        address = Address.objects.filter(id=address_id, user=user).first()
        if address:
            address.delete()
            return JsonResponse({'success': True})
        return JsonResponse({'error': 'Address not found.'}, status=404)
    return JsonResponse({'error': 'Authentication required.'}, status=401)


@api_view(['POST'])
@csrf_exempt
def api_complaint(request):
    authorization_header = request.META.get('HTTP_AUTHORIZATION')

    # Decode the token and get the user ID
    print(authorization_header)
    if authorization_header is None:
        return JsonResponse({"success": False, "error": "login"}, status = 201)
    try:
        token = authorization_header.split(" ")[1]
        decoded_token = jwt.decode(token, options={"verify_signature": False})
        print(decoded_token)
        user_id = decoded_token["user_id"]
        print(user_id)
        user = User.objects.filter(id = user_id).first()
        if user is None:
            return JsonResponse({"success": False, "error": "login"}, status = 201)
        
    except jwt.InvalidTokenError:
        print("Invalid token")
        print(authorization_header)
    if user.is_authenticated and user.is_active:
        if request.method == "POST":
            data = json.loads(request.body.decode('utf-8'))
            sub = data.get('subject')
            com = data.get('complaint')
            c = Complainet(user=user, subject=sub, complaint=com)
            c.save()
            return JsonResponse({'success': True, 'message': 'Your complaint has been registered.'})
        return JsonResponse({'error': 'Invalid request method.'}, status=400)
    return JsonResponse({'error': 'Authentication required.'}, status=401)




@swagger_auto_schema(
    method='get',
    operation_description="Retrieve user profile information along with orders, warranty registrations, claims, and addresses.",
    responses={
        200: openapi.Response(
            description="Successful retrieval of user profile and related data",
            examples={
                "application/json": {
                    "user": {
                        "id": 1,
                        "username": "example@example.com"
                    },
                    "profile": {
                        "first_name": "John",
                        "last_name": "Doe",
                        "phone_no": "+1234567890",
                        "profile_picture": "url_to_picture"
                    },
                    "orders": [],
                    "addresses": []
                }
            }
        ),
        401: openapi.Response(
            description="Authentication required",
            examples={
                "application/json": {
                    "error": "Authentication required."
                }
            }
        )
    },
    security=[{'Bearer': []}],
)
@swagger_auto_schema(
    method='post',
    operation_description="Update user profile information.",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'first_name': openapi.Schema(type=openapi.TYPE_STRING, description='First name of the user'),
            'last_name': openapi.Schema(type=openapi.TYPE_STRING, description='Last name of the user'),
            'email': openapi.Schema(type=openapi.TYPE_STRING, description='Email address of the user'),
            'phone_no': openapi.Schema(type=openapi.TYPE_STRING, description='Phone number of the user'),
            'profile_picture': openapi.Schema(type=openapi.TYPE_FILE, description='Profile picture of the user'),
            'password': openapi.Schema(type=openapi.TYPE_STRING, description='New password for the user'),
        },
        required=['first_name', 'last_name', 'email', 'phone_no'],
    ),
    responses={
        200: openapi.Response(
            description="Profile updated successfully",
            examples={
                "application/json": {
                    "success": "Profile updated successfully."
                }
            }
        ),
        401: openapi.Response(
            description="Authentication required",
            examples={
                "application/json": {
                    "error": "Authentication required."
                }
            }
        )
    },
)
@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
@csrf_exempt
def api_profile(request):
    authorization_header = request.META.get('HTTP_AUTHORIZATION')
    print(authorization_header)
    if authorization_header is None:
        return JsonResponse({"success": False, "error": "login"}, status = 201)
    try:
        token = authorization_header.split(" ")[1]
        decoded_token = jwt.decode(token, options={"verify_signature": False})
        print(decoded_token)
        user_id = decoded_token["user_id"]
        print(user_id)
        user = User.objects.filter(id = user_id).first()
        if user is None:
            return JsonResponse({"success": False, "error": "login"}, status = 201)
        
    except jwt.InvalidTokenError:
        print("Invalid token")
        print(authorization_header)
    if user.is_authenticated and user.is_active:
        if request.method == "POST":
            data = json.loads(request.body.decode('utf-8'))
            first_name = data.get('first_name')
            last_name = data.get('last_name')
            email = data.get('email')
            phone_no = data.get('phone_no')
            image = request.FILES.get('profile_picture')
            password = data.get('password')

            profile = Profile.objects.filter(user=user).first()
            if profile:
                if image:
                    profile.profile_image = image
                profile.phone_number = phone_no
                profile.save()
            else:
                if image:
                    profile = Profile(user=user, profile_image=image, phone_number=phone_no)
                else:
                    profile = Profile(user=user, phone_number=phone_no)
                profile.save()

            user.first_name = first_name
            user.last_name = last_name
            user.email = email
            if password:
                user.set_password(password)
            user.save()

            messages.success(request, "Profile updated successfully.")
            serializer = ProfileSerializer(profile)
            return JsonResponse(serializer.data, status=200)


        profile = Profile.objects.filter(user=user).first()
        orders = Order.objects.filter(user=user).order_by('-date_added')
        w_registrations = WarrantyRegistration.objects.filter(user=user)
        w_claims = WarrantyClaim.objects.filter(user=user)
        addresses = Address.objects.filter(user=user)

        profile_serializer = ProfileSerializer(profile)
        u_serializer = UserSerializer(user, many=False)
        order_serializer = OrderSerializer(orders, many=True)
        w_registration_serializer = WarrantyRegistrationSerializer(w_registrations, many=True)
        w_claim_serializer = WarrantyClaimSerializer(w_claims, many=True)
        address_serializer = AddressSerializer(addresses, many=True)

        data = {
            'user': profile_serializer.data,
            'profile':u_serializer.data,
            'orders': order_serializer.data,
            'w_registrations': w_registration_serializer.data,
            'w_claims': w_claim_serializer.data,
            'addresses': address_serializer.data
        }
        return JsonResponse(data)

    return JsonResponse({'error': 'Authentication required.'}, status=401)



@swagger_auto_schema(
    method='get',
    operation_description="Retrieve all orders for the authenticated user.",
    responses={
        200: openapi.Response(
            description="Successful retrieval of user orders",
            examples={
                "application/json": {
                    "orders": [
                        ""
                    ]
                }
            }
        ),
        401: openapi.Response(
            description="Authentication required",
            examples={
                "application/json": {
                    "error": "Authentication required."
                }
            }
        ),
        201: openapi.Response(
            description="Login required",
            examples={
                "application/json": {
                    "success": False,
                    "error": "login"
                }
            }
        )
    },
    security=[{'Bearer': []}],
)
@api_view(['GET'])
@permission_classes([AllowAny])
@csrf_exempt
def api_order_view(request):
    authorization_header = request.META.get('HTTP_AUTHORIZATION')
    print(authorization_header)
    if authorization_header is None:
        return JsonResponse({"success": False, "error": "login"}, status = 201)
    try:
        token = authorization_header.split(" ")[1]
        decoded_token = jwt.decode(token, options={"verify_signature": False})
        print(decoded_token)
        user_id = decoded_token["user_id"]
        print(user_id)
        user = User.objects.filter(id = user_id).first()
        if user is None:
            return JsonResponse({"success": False, "error": "login"}, status = 201)
        
    except jwt.InvalidTokenError:
        print("Invalid token")
        print(authorization_header)
    if user.is_authenticated and user.is_active:
        
        orders = Order.objects.filter(user=user).order_by('-date_added')
        print(orders)
        order_serializer = OrderSerializer(orders, many=True)

        data = {
            'orders': order_serializer.data,
        }
        return JsonResponse(data)

    return JsonResponse({'error': 'Authentication required.'}, status=401)


@swagger_auto_schema(
    method='post',
    operation_description="Submit a contact form to reach out to the team.",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'first_name': openapi.Schema(type=openapi.TYPE_STRING, description='First name of the user'),
            'last_name': openapi.Schema(type=openapi.TYPE_STRING, description='Last name of the user'),
            'email': openapi.Schema(type=openapi.TYPE_STRING, description='Email address of the user'),
            'phone_no': openapi.Schema(type=openapi.TYPE_STRING, description='Phone number of the user'),
            'message': openapi.Schema(type=openapi.TYPE_STRING, description='Message from the user'),
        },
        required=['first_name', 'last_name', 'email', 'phone_no', 'message'],
    ),
    responses={
        200: openapi.Response(
            description="Successfully submitted contact form",
            examples={
                "application/json": {
                    "message": "Our team will reach out to you shortly."
                }
            }
        ),
        405: openapi.Response(
            description="Method not allowed",
        ),
    }
)
@api_view(['POST'])
@permission_classes([AllowAny])
@csrf_exempt
def api_contact(request):
    if request.method == "POST":
        data = json.loads(request.body.decode('utf-8'))
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        email = data.get('email')
        phone_no = data.get('phone_no')
        message = data.get('message')

        c = Contact(first_name=first_name, last_name=last_name, email=email, phone_no=phone_no, message=message)
        c.save()

        response_data = {
            'message': 'Our team will reach out to you shortly.'
        }
        return JsonResponse(response_data)

    return JsonResponse(status=405)  # Method Not Allowed


@api_view(['GET'])
@csrf_exempt
def api_partner_locator(request):
    state = request.data.get('state')
    pincode = request.data.get('pincode')
    if state:
        partner = Partner.objects.filter(state=state, status="Approved")
        if not partner:
            response_data = {
                'message': 'No partners found in your location.'
            }
            return JsonResponse(response_data)
    elif pincode:
        partner = Partner.objects.filter(pin_code=pincode, status="Approved")
        if not partner:
            response_data = {
                'message': 'No partners found in your location.'
            }
            return JsonResponse(response_data)
    else:
        response_data = {
            'message': 'Please enter state/city or zipcode.'
        }
        return JsonResponse(response_data)

    partner_serializer = PartnerSerializer(partner, many=True)
    response_data = {
        'partner': partner_serializer.data
    }
    return JsonResponse(response_data)

@api_view(['POST'])
@csrf_exempt
def api_partner_registration(request):
    data = json.loads(request.body.decode('utf-8'))
    name = data.get('name')
    father_name = data.get('father_name')
    email = data.get('email')
    number = data.get('number')
    image = request.FILES.get('image')
    identity_proof = request.FILES.get('identity_proof')
    partner_type = data.get('partner_type')
    state = data.get('state')
    pincode = data.get('pincode')
    bankname = data.get('bankname')
    account_holder_name = data.get('account_holder_name')
    account_no = data.get('account_no')
    ifsc_code = data.get('ifsc_code')
    bank_details = request.FILES.get('bank_details')
    payment_method = data.get('payment_method')
    pay_method_no = data.get('pay_method_no')

    p = Partner(name=name, father_name=father_name, email=email, mob_number=number, image=image,
                identity_proof=identity_proof, partner_type=partner_type, state=state,
                pin_code=pincode, bank_name=bankname, account_holder_name=account_holder_name,
                bank_account_no=account_no, bank_ifsc_code=ifsc_code, bank_details=bank_details,
                pay_method=payment_method, pay_method_no=pay_method_no)
    p.save()

    wrr = Partner.objects.filter(name=name, email=email, mob_number=number).first()
    try:
        msg_body = f"""Dear Customer, Your registration for {partner_type} is under processing.
                    Your registration id is {wrr.partner_id}.
                    Shop with us again. For more details login to https://gluoenelectrical.com.
                    The FURNITURE
                    """
        # Code for sending SMS
    except Exception as e:
        print(e)

    number = str(number)
    
    try:
        subject = 'Partner Registration'
        message = f"""Dear Customer, Your registration for {partner_type} is under processing.
                Your registration id is {wrr.partner_id}.
                Shop with us again. For more details login to https://gluoenelectrical.com.
                The FURNITURE
                """
        from_email = 'contact@swastik.ai'
        recipient_list = [wrr.email,]
        send_mail(subject, message, from_email, recipient_list)
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
    
    response_data = {
        'message': f"Your registration for {partner_type} is completed."
    }
    return JsonResponse(response_data)


@csrf_exempt
def warranty_registration_check(request):
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


@api_view(['POST'])
@csrf_exempt
def api_claim_warranty(request):
    authorization_header = request.META.get('HTTP_AUTHORIZATION')

    # Decode the token and get the user ID
    print(authorization_header)
    if authorization_header is None:
        return JsonResponse({"success": False, "error": "login"}, status = 201)
    try:
        token = authorization_header.split(" ")[1]
        decoded_token = jwt.decode(token, options={"verify_signature": False})
        print(decoded_token)
        user_id = decoded_token["user_id"]
        print(user_id)
        user = User.objects.filter(id = user_id).first()
        if user is None:
            return JsonResponse({"success": False, "error": "login"}, status = 201)
        
    except jwt.InvalidTokenError:
        print("Invalid token")
        print(authorization_header)
    data = json.loads(request.body.decode('utf-8'))
    reg_number = data.get('reg_number')
    wrr = WarrantyRegistration.objects.filter(reg_id=reg_number, status="Approved").first()
    name = data.get('name', wrr.name)
    email = data.get('email', wrr.email)
    mobile = data.get('number', wrr.mob_number)
    manufacturing_date = data.get('manufacturing_date', wrr.product_manufacturing_date)
    batch_no = data.get('batch_no', wrr.product_batch_no)
    serial_no = data.get('serial_no', wrr.product_serial_no)
    color = data.get('color', wrr.product_color)
    warranty_registration_date = data.get('warranty_registration_date', wrr.date_added)
    product_image = data.get('product_image')
    warranty_card = data.get('warranty_card')
    state = data.get('state')
    district = data.get('district')
    city = data.get('city')
    postoffice = data.get('postoffice')
    zipcode = data.get('zipcode')
    landmark = data.get('landmark')
    purchase_source = data.get('category')
    address = data.get('address')

    wrr_reg = WarrantyRegistration.objects.filter(reg_id = reg_number, product_batch_no = batch_no).first()

    if wrr_reg:
        wrr = WarrantyClaim.objects.filter(product_serial_no = serial_no, product_batch_no = batch_no).first()
        if wrr:
            messages.error(request, f"Your Warranty registration is allready completed.")
            return redirect('customer_service')
        if user.is_authenticated:
            warranty = WarrantyClaim(user=user, name=name, email=email,
                                    mob_number=mobile, warranty_registration=reg_number,
                                    product_manufacturing_date=manufacturing_date,
                                    product_batch_no=batch_no, product_serial_no=serial_no,
                                    product_color=color, registration_date=warranty_registration_date,
                                    product_image=product_image, warranty_card=warranty_card,
                                    state=state, district=district, city=city, post_office=postoffice,
                                    zipcode=zipcode, land_mark=landmark, purchase_source=landmark, address=address)
            warranty.save()
        else:
            warranty = WarrantyClaim(name=name, email=email,
                                    mob_number=mobile, warranty_registration=reg_number,
                                    product_manufacturing_date=manufacturing_date,
                                    product_batch_no=batch_no, product_serial_no=serial_no,
                                    product_color=color, registration_date=warranty_registration_date,
                                    product_image=product_image, warranty_card=warranty_card,
                                    state=state, district=district, city=city, post_office=postoffice,
                                    zipcode=zipcode, land_mark=landmark, purchase_source=purchase_source, address=address)
            warranty.save()

        wrr = WarrantyClaim.objects.filter(name=name, product_batch_no=batch_no).first()
        msg_body = f"""Dear Customer, Your registration for warranty claim for {batch_no} is successfully processed.
                    Your registration id is {wrr.claim_id}.
                    Shop with us again. For more details login to https://gluoenelectrical.com.
                    The FURNITURE
                    """
        # Code for sending SMS
        try:
            mobile = str(mobile)
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
        try:
            subject = 'Warranty Claim'
            message = f"""Dear Customer, Your registration for warranty claim for {batch_no} is successfully processed.
                    Your registration id is {wrr.claim_id}.
                    Shop with us again. For more details login to https://gluoenelectrical.com.
                    The FURNITURE
                    """
            from_email = 'contact@swastik.ai'
            recipient_list = [wrr.email,]
            send_mail(subject, message, from_email, recipient_list)
        except Exception as e:
            print(e)

        response_data = {
            'message': 'Your Warranty Claim is registered.'
        }
        return JsonResponse(response_data)


@api_view(['POST'])
@csrf_exempt
def api_warranty_registration(request):

    authorization_header = request.META.get('HTTP_AUTHORIZATION')

    # Decode the token and get the user ID
    print(authorization_header)
    if authorization_header is None:
        return JsonResponse({"success": False, "error": "login"}, status = 201)
    try:
        token = authorization_header.split(" ")[1]
        decoded_token = jwt.decode(token, options={"verify_signature": False})
        print(decoded_token)
        user_id = decoded_token["user_id"]
        print(user_id)
        user = User.objects.filter(id = user_id).first()
        if user is None:
            return JsonResponse({"success": False, "error": "login"}, status = 201)
        
    except jwt.InvalidTokenError:
        print("Invalid token")
        print(authorization_header)

    data = json.loads(request.body.decode('utf-8'))
    name = data.get('name')
    email = data.get('email')
    mobile = data.get('number')
    product = data.get('product')
    manufacturing_date = data.get('manufacturing_date')
    batch_no = data.get('batch_no')
    serial_no = data.get('serial_no')
    color = data.get('color')
    order_date = data.get('order_date')
    invoice_no = data.get('invoice_no')
    invoice = request.FILES.get('invoice')
    price = data.get('price')
    state = data.get('state')
    district = data.get('district')
    city = data.get('city')
    postoffice = data.get('postoffice')
    zipcode = data.get('zipcode')
    landmark = data.get('landmark')
    purchasse_source = data.get('category')
    address = data.get('address')

    if user.is_authenticated:
        warranty = WarrantyRegistration(user=user, name=name, email=email,
                                        mob_number=mobile, product=product,
                                        product_manufacturing_date=manufacturing_date,
                                        product_batch_no=batch_no, product_serial_no=serial_no,
                                        product_color=color, order_date=order_date,
                                        invoice_no=invoice_no, invoice=invoice, price=price,
                                        state=state, district=district, city=city,
                                        post_office=postoffice, zipcode=zipcode, land_mark=landmark,
                                        purchase_source=purchasse_source, address=address)
        warranty.save()
    else:
        warranty = WarrantyRegistration(name=name, email=email, mob_number=mobile,
                                        product=product, product_manufacturing_date=manufacturing_date,
                                        product_batch_no=batch_no, product_serial_no=serial_no,
                                        product_color=color, order_date=order_date,
                                        invoice_no=invoice_no, invoice=invoice, price=price,
                                        state=state, district=district, city=city,
                                        post_office=postoffice, zipcode=zipcode, land_mark=landmark,
                                        purchase_source=purchasse_source, address=address)
        warranty.save()

    wrr = WarrantyRegistration.objects.filter(name=name, product_batch_no=batch_no).first()
    msg_body = f"""Dear Customer, Your registration for {product} is successfully processed.
                Your registration id is {wrr.reg_id}.
                Shop with us again. For more details login to https://gluoenelectrical.com.
                The FURNITURE
                """
    # Code for sending SMS
    try:
        mobile = str(mobile)
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

    try:
        subject = 'Warranty Registration'
        message = f"""Dear Customer, Your registration for {product} is successfully processed.
                Your registration id is {wrr.reg_id}.
                Shop with us again. For more details login to https://gluoenelectrical.com.
                The FURNITURE
                """
        from_email = 'contact@swastik.ai'
        recipient_list = [wrr.email,]
        send_mail(subject, message, from_email, recipient_list)
    except Exception as e:
        print(e)

    response_data = {
        'message': 'Your Warranty registration is successfully completed.'
    }
    return JsonResponse(response_data)


@swagger_auto_schema(
    method='get',
    operation_description="Retrieve invoice details for a specific order.",
    manual_parameters=[
        openapi.Parameter(
            'Authorization',
            openapi.IN_HEADER,
            description="Bearer token for user authentication",
            type=openapi.TYPE_STRING,
        ),
        openapi.Parameter(
            'sssinvoice_id',
            openapi.IN_PATH,
            description="ID of the invoice to retrieve",
            type=openapi.TYPE_STRING,
            required=True
        )
    ],
    responses={
        200: openapi.Response(
            description="Successfully retrieved invoice details",
            examples={
                "application/json": {
                    "order_id": "12345",
                    "user": "username",
                    "total": 100.00,
                    "status": "paid",
                    "date": "2024-09-21"
                }
            }
        ),
        400: openapi.Response(
            description="Invoice ID is required",
        ),
        404: openapi.Response(
            description="Invoice not found",
        ),
        401: openapi.Response(
            description="Unauthorized",
        ),
        201: openapi.Response(
            description="Login required",
        )
    }
)
@api_view(['GET'])
@permission_classes([AllowAny])
@csrf_exempt
def api_invoice(request, sssinvoice_id=None):
    authorization_header = request.META.get('HTTP_AUTHORIZATION')

    # Decode the token and get the user ID
    print(authorization_header)
    if authorization_header is None:
        return JsonResponse({"success": False, "error": "login"}, status = 201)
    try:
        token = authorization_header.split(" ")[1]
        decoded_token = jwt.decode(token, options={"verify_signature": False})
        print(decoded_token)
        user_id = decoded_token["user_id"]
        print(user_id)
        user = User.objects.filter(id = user_id).first()
        if user is None:
            return JsonResponse({"success": False, "error": "login"}, status = 201)
        
    except jwt.InvalidTokenError:
        print("Invalid token")
        print(authorization_header)
    if user.is_authenticated:
        if user.is_active == True:
            if invoice_id is not None:
                i = Order.objects.filter(user=user, order_id=invoice_id).first()
                if i is not None:
                    order_serializer = OrderSerializer(i)
                    return JsonResponse(order_serializer.data)
                else:
                    return JsonResponse({'error': 'Invoice not found.'}, status=404)
            else:
                return JsonResponse({'error': 'Invoice ID is required.'}, status=400)
    return JsonResponse({'error': 'Unauthorized.'}, status=401)


@swagger_auto_schema(
    method='get',
    operation_description="Retrieve the user's wishlist.",
    manual_parameters=[
        openapi.Parameter(
            'Authorization',
            openapi.IN_HEADER,
            description="Bearer token for user authentication",
            type=openapi.TYPE_STRING,
        )
    ],
    responses={
        200: openapi.Response(
            description="Successfully retrieved wishlist",
            examples={
                "application/json": [
                    {
                        "id": 1,
                        "product": "Product Name",
                        "date_added": "2024-09-21"
                    },
                    {
                        "id": 2,
                        "product": "Another Product",
                        "date_added": "2024-09-22"
                    }
                ]
            }
        ),
        201: openapi.Response(
            description="Login required",
        ),
        401: openapi.Response(
            description="Unauthorized",
        )
    }
)
@api_view(['GET'])
@permission_classes([AllowAny])
@csrf_exempt
def api_wishlist(request):
    authorization_header = request.META.get('HTTP_AUTHORIZATION')

    # Decode the token and get the user ID
    print(authorization_header)
    if authorization_header is None:
        return JsonResponse({"success": False, "error": "login"}, status = 201)
    try:
        token = authorization_header.split(" ")[1]
        decoded_token = jwt.decode(token, options={"verify_signature": False})
        print(decoded_token)
        user_id = decoded_token["user_id"]
        print(user_id)
        user = User.objects.filter(id = user_id).first()
        if user is None:
            return JsonResponse({"success": False, "error": "login"}, status = 201)
        
    except jwt.InvalidTokenError:
        print("Invalid token")
        print(authorization_header)
    if user.is_authenticated:
        if user.is_active == True:
            wishlist = Wish.objects.filter(user=user)
            wishlist_serializer = WishSerializer(wishlist, many=True)
            return JsonResponse(wishlist_serializer.data)
    return JsonResponse({'error': 'Unauthorized.'}, status=401)


@swagger_auto_schema(
    method='post',
    operation_description="Add a product to the user's wishlist.",
    manual_parameters=[
        openapi.Parameter(
            'Authorization',
            openapi.IN_HEADER,
            description="Bearer token for user authentication",
            type=openapi.TYPE_STRING,
        ),
        openapi.Parameter(
            'product_slug',
            openapi.IN_PATH,
            description="Slug of the product to add to the wishlist",
            type=openapi.TYPE_STRING,
            required=True
        )
    ],
    responses={
        200: openapi.Response(
            description="Product added to wishlist successfully.",
            examples={
                "application/json": {
                    "data": "success"
                }
            }
        ),
        201: openapi.Response(
            description="Login required",
        ),
        401: openapi.Response(
            description="Unauthorized",
        ),
        404: openapi.Response(
            description="Product not found",
        )
    }
)
@api_view(['POST'])
@permission_classes([AllowAny])
@csrf_exempt
def api_add_wishlist(request, product_slug):
    authorization_header = request.META.get('HTTP_AUTHORIZATION')

    # Decode the token and get the user ID
    print(authorization_header)
    if authorization_header is None:
        return JsonResponse({"success": False, "error": "login"}, status = 201)
    try:
        token = authorization_header.split(" ")[1]
        decoded_token = jwt.decode(token, options={"verify_signature": False})
        print(decoded_token)
        user_id = decoded_token["user_id"]
        print(user_id)
        user = User.objects.filter(id = user_id).first()
        if user is None:
            return JsonResponse({"success": False, "error": "login"}, status = 201)
        
    except jwt.InvalidTokenError:
        print("Invalid token")
        print(authorization_header)
    if user.is_authenticated:
        if user.is_active == True:
            product = get_object_or_404(Product, slug=product_slug)
            existing_wish = Wish.objects.filter(user=user, product=product).exists()

            if not existing_wish:
                w = Wish(user=user, product=product)
                w.save()
                return JsonResponse({'data': 'success'})

    return JsonResponse({'error': 'Unauthorized.'}, status=401)


@swagger_auto_schema(
    method='delete',
    operation_description="Remove a product from the user's wishlist.",
    manual_parameters=[
        openapi.Parameter(
            'Authorization',
            openapi.IN_HEADER,
            description="Bearer token for user authentication",
            type=openapi.TYPE_STRING,
        ),
        openapi.Parameter(
            'w_id',
            openapi.IN_PATH,
            description="ID of the wishlist item to remove",
            type=openapi.TYPE_INTEGER,
            required=True
        )
    ],
    responses={
        204: openapi.Response(
            description="Wishlist item removed successfully."
        ),
        201: openapi.Response(
            description="Login required",
        ),
        401: openapi.Response(
            description="Unauthorized",
        ),
        404: openapi.Response(
            description="Wishlist item not found",
        )
    }
)
@api_view(['DELETE'])
@permission_classes([AllowAny])
@csrf_exempt
def api_remove_wishlist(request, w_id):
    authorization_header = request.META.get('HTTP_AUTHORIZATION')

    # Decode the token and get the user ID
    print(authorization_header)
    if authorization_header is None:
        return JsonResponse({"success": False, "error": "login"}, status = 201)
    try:
        token = authorization_header.split(" ")[1]
        decoded_token = jwt.decode(token, options={"verify_signature": False})
        print(decoded_token)
        user_id = decoded_token["user_id"]
        print(user_id)
        user = User.objects.filter(id = user_id).first()
        if user is None:
            return JsonResponse({"success": False, "error": "login"}, status = 201)
        
    except jwt.InvalidTokenError:
        print("Invalid token")
        print(authorization_header)
    if user.is_authenticated:
        if user.is_active == True:
            w = Wish.objects.filter(w_id=w_id, user=user).first()
            if w:
                w.delete()
                return Response(status=204)
            else:
                return JsonResponse({'error': 'Wishlist item not found.'}, status=404)

    return JsonResponse({'error': 'Unauthorized.'}, status=401)

@swagger_auto_schema(
    method='get',
    operation_description="Add product to the cart or modify the quantity using query parameters.",
    manual_parameters=[
        openapi.Parameter(
            'Authorization',
            openapi.IN_HEADER,
            description="Bearer token for user authentication",
            type=openapi.TYPE_STRING,
            required=True
        ),
        openapi.Parameter(
            'increase',
            openapi.IN_QUERY,
            description="Increase the product quantity by 1 (set as '1')",
            type=openapi.TYPE_STRING,
            required=False
        ),
        openapi.Parameter(
            'decrease',
            openapi.IN_QUERY,
            description="Decrease the product quantity by 1 (set as '0')",
            type=openapi.TYPE_STRING,
            required=False
        ),
        openapi.Parameter(
            'quantity',
            openapi.IN_QUERY,
            description="Specify a specific quantity for the product",
            type=openapi.TYPE_INTEGER,
            required=False
        ),
        openapi.Parameter(
            'product_slug',
            openapi.IN_PATH,
            description="The slug of the product to add or modify in the cart",
            type=openapi.TYPE_STRING,
            required=True
        )
    ],
    responses={
        200: openapi.Response(
            description="Cart updated successfully.",
            examples={
                "application/json": {
                    "cart_data": [
                        {
                            "product": "Sample Product",
                            "quantity": 2,
                            "price": 100
                        }
                    ],
                    "totalitems": 1
                }
            }
        ),
        201: openapi.Response(
            description="Login required"
        ),
        500: openapi.Response(
            description="Internal server error"
        )
    }
)
@swagger_auto_schema(
    method='post',
    operation_description="Add a product to the cart or set its quantity using the POST body.",
    manual_parameters=[
        openapi.Parameter(
            'Authorization',
            openapi.IN_HEADER,
            description="Bearer token for user authentication",
            type=openapi.TYPE_STRING,
            required=True
        ),

        openapi.Parameter(
            'quantity',
            openapi.IN_QUERY,
            description="Specify a specific quantity for the product",
            type=openapi.TYPE_INTEGER,
            required=False
        ),

    ],
    responses={
        200: openapi.Response(
            description="Cart updated successfully.",
            examples={
                "application/json": {
                    "cart_data": [
                        {
                            "product": "Sample Product",
                            "quantity": 2,
                            "price": 100
                        }
                    ],
                    "totalitems": 1
                }
            }
        ),
        201: openapi.Response(
            description="Login required"
        ),
        500: openapi.Response(
            description="Internal server error"
        )
    }
)
@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
@csrf_exempt
def api_cart_add(request, product_slug):
    authorization_header = request.META.get('HTTP_AUTHORIZATION')

    # Decode the token and get the user ID
    print(authorization_header)
    if authorization_header is None:
        return JsonResponse({"success": False, "error": "login"}, status = 201)
    try:
        token = authorization_header.split(" ")[1]
        decoded_token = jwt.decode(token, options={"verify_signature": False})
        print(decoded_token)
        user_id = decoded_token["user_id"]
        print(user_id)
        user = User.objects.filter(id = user_id).first()
        if user is None:
            return JsonResponse({"success": False, "error": "login"}, status = 201)
        
    except jwt.InvalidTokenError:
        print("Invalid token")
        print(authorization_header)
        return JsonResponse({"success": False, "error": "login"}, status = 201)


    increase = request.GET.get('increase')
    decrease = request.GET.get('decrease')
    quantity = request.GET.get('quantity')
    print(increase, decrease, quantity, user)

    if increase == '1':
        quantity = 1
    elif decrease == '0':
        quantity = -1
    elif quantity:
        quantity = int(quantity)

    product = get_object_or_404(Product, slug=product_slug)
    print(product)

    o_quantity = None

    if request.method == "POST":
        data = json.loads(request.body)

        quantity_p = data.get('quantity')
        if quantity_p:
            o_quantity = int(quantity_p)
        else:
            o_quantity = 1

    if user.is_authenticated and user.is_active:
        try:
            cart_item, created = Cart.objects.get_or_create(user=user, product=product)
            # print(cart_item)
            # if created or quantity == 1:
                
            #     cart_item.quantity += 1
            # elif quantity == -1:
            #     cart_item.quantity -= 1
            # elif quantity:
            #     cart_item.quantity = quantity
            if created or o_quantity:
                cart_item.quantity = o_quantity
            cart_item.save()
        except Exception as e:
            print(e)
            return JsonResponse({"success": False, "error": str(e)}, status=500)
                                                    
    cart_data = Cart.objects.filter(user=user).all()
    print(cart_data)
    cart_serializer = CartSerializer(cart_data, many=True)
    response = {
        'cart_data': cart_serializer.data,
        'totalitems': len(cart_data)
    }
    return JsonResponse(response)



@swagger_auto_schema(
    method='get',
    operation_description="Retrieve the user's cart along with the total price and total not price.",
    manual_parameters=[
        openapi.Parameter(
            'Authorization',
            openapi.IN_HEADER,
            description="Bearer token for user authentication",
            type=openapi.TYPE_STRING,
            required=True,
        )
    ],
    responses={
        200: openapi.Response(
            description="Cart retrieved successfully.",
            examples={
                "application/json": {
                    "cart_data": [
                        {
                            "product": "Product Name",
                            "quantity": 1,
                            "price": 100,
                            "not_price": 120
                        }
                    ],
                    "total_price": 100,
                    "total_not_price": 120
                }
            }
        ),
        201: openapi.Response(description="Login required"),
        401: openapi.Response(description="Unauthorized"),
        500: openapi.Response(description="Internal server error"),
    }
)
@api_view(['GET'])
@permission_classes([AllowAny])
@csrf_exempt
def api_cart(request):
    authorization_header = request.META.get('HTTP_AUTHORIZATION')

    # Decode the token and get the user ID
    print(authorization_header)
    if authorization_header is None:
        return JsonResponse({"success": False, "error": "login"}, status = 201)
    try:
        token = authorization_header.split(" ")[1]
        decoded_token = jwt.decode(token, options={"verify_signature": False})
        print(decoded_token)
        user_id = decoded_token["user_id"]
        print(user_id)
        user = User.objects.filter(id = user_id).first()
        print(user)
        if user is None:
            return JsonResponse({"success": False, "error": "login"}, status = 201)
        
    except jwt.InvalidTokenError:
        print("Invalid token")
        print(authorization_header)
    total_price = 0
    total_not_price = 0
    try:
        if user.is_authenticated:
            if user.is_active:
                cart_data = Cart.objects.filter(user=user).all()
                for cart_item in cart_data:
                    total_price += cart_item.product.price * cart_item.quantity
                    total_not_price += cart_item.product.not_price * cart_item.quantity

        print(cart_data)
        cart_serializer = CartSerializer(cart_data, many=True)
    except Exception as e:
        print(e)
        cart_data = {}
        total_price = 0
        total_not_price = 0

    response = {
        'cart_data': cart_serializer.data,
        'total_price': total_price,
        'total_not_price': total_not_price
    }
    print(response)
    return JsonResponse(response, status=200)


@swagger_auto_schema(
    method='get',
    operation_description="Retrieve the length of the user's cart.",
    manual_parameters=[
        openapi.Parameter(
            'Authorization',
            openapi.IN_HEADER,
            description="Bearer token for user authentication",
            type=openapi.TYPE_STRING,
            required=True,
        ),
    ],
    responses={
        200: openapi.Response(
            description="Successfully retrieved the length of the cart.",
            examples={
                "application/json": {
                    "cart_data_len": 5  # Example response indicating 5 items in the cart
                }
            }
        ),
        201: openapi.Response(
            description="Login required or invalid token.",
            examples={
                "application/json": {
                    "success": False,
                    "error": "login"
                }
            }
        ),
    }
)
@api_view(['GET'])
@permission_classes([AllowAny])
@csrf_exempt
def api_cart_length(request):
    authorization_header = request.META.get('HTTP_AUTHORIZATION')

    # Decode the token and get the user ID
    print(authorization_header)
    if authorization_header is None:
        return JsonResponse({"success": False, "error": "login"}, status = 201)
    try:
        token = authorization_header.split(" ")[1]
        decoded_token = jwt.decode(token, options={"verify_signature": False})
        print(decoded_token)
        user_id = decoded_token["user_id"]
        print(user_id)
        user = User.objects.filter(id = user_id).first()
        print(user)
        if user is None:
            return JsonResponse({"success": False, "error": "login"}, status = 201)
        
    except jwt.InvalidTokenError:
        print("Invalid token")
        print(authorization_header)
        return JsonResponse({"success": False, "error": "login"}, status = 201)

    try:
        if user.is_authenticated:
            if user.is_active:
                cart_data = Cart.objects.filter(user=user).all()
                cart_data_len = len(cart_data)

    except Exception as e:
        print(e)

        cart_data_len = 0

    response = {
        'cart_data_len': cart_data_len
    }
    print(response)
    return JsonResponse(response, status=200)



@swagger_auto_schema(
    method='delete',
    operation_description="Remove a product from the user's cart.",
    manual_parameters=[
        openapi.Parameter(
            'Authorization',
            openapi.IN_HEADER,
            description="Bearer token for user authentication",
            type=openapi.TYPE_STRING,
            required=True,
        ),
        openapi.Parameter(
            'product_slug',
            openapi.IN_PATH,
            description="Slug of the product to remove from the cart",
            type=openapi.TYPE_STRING,
            required=True,
        )
    ],
    responses={
        200: openapi.Response(
            description="Product removed from cart successfully.",
            examples={
                "application/json": {
                    "message": "Product removed from cart successfully."
                }
            }
        ),
        201: openapi.Response(
            description="Login required or method not allowed.",
            examples={
                "application/json": {
                    "success": False,
                    "error": "login"
                }
            }
        ),
        404: openapi.Response(description="Product not found in the cart"),
        401: openapi.Response(description="Unauthorized access"),
    }
)
@api_view(['DELETE'])
@permission_classes([AllowAny])
@csrf_exempt
def cart_remove_api(request, product_slug):
    authorization_header = request.META.get('HTTP_AUTHORIZATION')

    # Decode the token and get the user ID
    print(authorization_header)
    if authorization_header is None:
        return JsonResponse({"success": False, "error": "login"}, status = 201)
    try:
        token = authorization_header.split(" ")[1]
        decoded_token = jwt.decode(token, options={"verify_signature": False})
        print(decoded_token)
        user_id = decoded_token["user_id"]
        print(user_id)
        user = User.objects.filter(id = user_id).first()
        if user is None:
            return JsonResponse({"success": False, "error": "login"}, status = 201)
        
    except jwt.InvalidTokenError:
        print("Invalid token")
        print(authorization_header)
    print(product_slug)
    if user.is_authenticated:
        if user.is_active:
            if request.method == "DELETE":
                product = get_object_or_404(Product, slug=product_slug)
                print(product)
                cart_data = Cart.objects.filter(user=user, product=product)
                cart_data.delete()

                print(cart_data)
                response = {
                    'message': 'Product removed from cart successfully.'
                }
                return JsonResponse(response, status=200)
            response = {
                    'message': 'Method Not Allowed.'
                }
            return JsonResponse(response, status=201)

    return JsonResponse({"success": False, "message": "User is not authenticated"}, status = 201)



@swagger_auto_schema(
    method='delete',
    operation_description="Clear all items from the user's cart.",
    manual_parameters=[
        openapi.Parameter(
            'Authorization',
            openapi.IN_HEADER,
            description="Bearer token for user authentication",
            type=openapi.TYPE_STRING,
            required=True,
        ),
    ],
    responses={
        200: openapi.Response(
            description="Successfully cleared the cart.",
            examples={
                "application/json": {
                    "message": "Cart cleared successfully."
                }
            }
        ),
        201: openapi.Response(
            description="Login required or invalid token.",
            examples={
                "application/json": {
                    "success": False,
                    "error": "login"
                }
            }
        ),
        405: openapi.Response(
            description="Method Not Allowed.",
            examples={
                "application/json": {
                    "message": "Method Not Allowed."
                }
            }
        )
    }
)
@api_view(['DELETE'])
@permission_classes([AllowAny])
@csrf_exempt
def clear_cart(request):
    authorization_header = request.META.get('HTTP_AUTHORIZATION')

    # Decode the token and get the user ID
    print(authorization_header)
    if authorization_header is None:
        return JsonResponse({"success": False, "error": "login"}, status = 201)
    try:
        token = authorization_header.split(" ")[1]
        decoded_token = jwt.decode(token, options={"verify_signature": False})
        print(decoded_token)
        user_id = decoded_token["user_id"]
        print(user_id)
        user = User.objects.filter(id = user_id).first()
        if user is None:
            return JsonResponse({"success": False, "error": "login"}, status = 201)
        
    except jwt.InvalidTokenError:
        print("Invalid token")
        print(authorization_header)
    if user.is_authenticated:
        if user.is_active:
            if request.method == "DELETE":
                c_data = Cart.objects.filter(user=user)
                print(c_data)
                for c in c_data:
                    c_data.delete()

                response = {
                    'message': 'Cart cleared successfully.'
                }
                return JsonResponse(response, status=200)
            response = {
                'message': 'Method Not Allowed.'
            }
            return JsonResponse(response, status=201)

    return JsonResponse({"success": False, "message": "User is not authenticated"}, status = 201)


@swagger_auto_schema(
    method='post',
    operation_description="Place an order immediately for a specified product.",
    manual_parameters=[
        openapi.Parameter(
            'Authorization',
            openapi.IN_HEADER,
            description="Bearer token for user authentication",
            type=openapi.TYPE_STRING,
            required=True,
        ),
    ],
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'product': openapi.Schema(type=openapi.TYPE_STRING, description='Slug of the product to purchase.'),
            'quantity': openapi.Schema(type=openapi.TYPE_INTEGER, description='Quantity of the product (default is 1).'),
            'address_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID of the shipping address.'),
            'coupon': openapi.Schema(type=openapi.TYPE_STRING, description='Optional coupon code for discount.'),
        },
        required=['product', 'address_id'],
    ),
    responses={
        200: openapi.Response(
            description="Order placed successfully.",
            examples={
                "application/json": {
                    "price_not": 100,
                    "price": 90,
                    "tax": 10,
                    "price_with_tax": 100,
                    "order_id": "12345",
                    "address": {
                        # Example address structure based on your AddressSerializer
                    }
                }
            }
        ),
        201: openapi.Response(
            description="Login required, invalid token, or error during processing.",
            examples={
                "application/json": {
                    "success": False,
                    "error": "login"
                },
                "application/json": {
                    "success": False,
                    "message": "This Coupon is expired or not available."
                }
            }
        )
    }
)
@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
@csrf_exempt
def buy_now(request):
    authorization_header = request.META.get('HTTP_AUTHORIZATION')

    # Decode the token and get the user ID
    print(authorization_header)
    if authorization_header is None:
        return JsonResponse({"success": False, "error": "login"}, status = 201)
    try:
        token = authorization_header.split(" ")[1]
        decoded_token = jwt.decode(token, options={"verify_signature": False})
        print(decoded_token)
        user_id = decoded_token["user_id"]
        print(user_id)
        user = User.objects.filter(id = user_id).first()
        if user is None:
            return JsonResponse({"success": False, "error": "login"}, status = 201)
        
    except jwt.InvalidTokenError:
        print("Invalid token")
        print(authorization_header)
    
    if user.is_authenticated and user.is_active:
        if request.method == "POST":
            data = json.loads(request.body)
            print(data)
            p = data.get('product')
            q = data.get('quantity', 1)
            a = data.get('address_id')

            try:
                if p:
                    product = get_object_or_404(Product, slug=p)
                    print(product)
                    addres = Address.objects.filter(user = user, address_id = a).first()
                    tax = round(product.price * product.tax / 100 , 2)
                    tp = product.price + tax
                    order = Order.objects.create(user=user, address = addres, order_status = "None", payment_status = "None", payment_method = "None", quantity = q, total_price = tp)
                    c = OrderData.objects.create(user = user, product = product, quantity = q, total_price = tp)                
                    order.product.add(c)
                    order.save()
                    print(order)
                    address_serializer = AddressSerializer(addres, many=False)
                    # product_serializer = ProductSerializer(product)
                    data = {
                        'price_not' : product.not_price,
                        'price' : product.price,
                        'tax' : tax,
                        'price_with_tax' : tp,
                        'order_id' : order.order_id,
                        # 'product' : product_serializer.data,
                        'address' : address_serializer.data
                    }
                    print(data)    
                    return JsonResponse(data, status=200)
            except Exception as e:
                print(e)
                s = f"{e}"
                return JsonResponse({"success": False, "message": s}, status = 201)

                
            c = data.get('coupon')
            if c:
                coupon = Offer.objects.filter(code=coupon_code, status=True).first()
                if coupon and coupon.status and coupon.start_date <= timezone.now() <= coupon.end_date:
                    od = OrderData.objects.filter(user = user).first()
                    orda = Order.objects.filter(user = user).first()
                    coupon_p = round((od.total_prrice * coupon.discount) / 100, 2)
                    od.coupon = coupon
                    tp = coupon_p + od.total_price
                    orda.total_price = tp
                    od.save()
                    orda.save()
                    data = {
                        
                        'coupon_price' : coupon_p,
                        'price_with_coupon_with_tax' : tp,
                        'order_id' : orda.order_id,
                    }
                    
                    return JsonResponse(data, status=200)
                response = {
                    'message': 'This Coupon is expoired or not available.'
                }
                return JsonResponse(response, status=201)
    return JsonResponse({"success": False, "message": "User is not authenticated"}, status = 201)




@swagger_auto_schema(
    method='post',
    operation_description="Buy products from the cart for a specific user.",
    manual_parameters=[
        openapi.Parameter(
            'Authorization',
            openapi.IN_HEADER,
            description="Bearer token for user authentication",
            type=openapi.TYPE_STRING,
            required=True,
        ),
    ],
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'address_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID of the shipping address (required).'),
            'coupon': openapi.Schema(type=openapi.TYPE_STRING, description='Optional coupon code for discount.'),
        },
        required=['address_id'],
    ),
    responses={
        200: openapi.Response(
            description="Order placed successfully.",
            examples={
                "application/json": {
                    "message": "Address used successfully.",
                    "order_id": "12345",
                    "address": {
                        # Example address structure based on your AddressSerializer
                    },
                    "tax": 10,
                    "price_not": 100,
                    "price": 90,
                    "price_with_tax": 100
                }
            }
        ),
        201: openapi.Response(
            description="Login required, invalid token, or error during processing.",
            examples={
                "application/json": {
                    "success": False,
                    "message": "This Coupon is expired or not available."
                },
                "application/json": {
                    "success": False,
                    "message": "User is not authenticated."
                }
            }
        )
    }
)
@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
@csrf_exempt
def buy_from_cart(request):
    authorization_header = request.META.get('HTTP_AUTHORIZATION')

    # Decode the token and get the user ID
    print(authorization_header)
    if authorization_header is None:
        return JsonResponse({"success": False, "error": "login"}, status = 201)
    try:
        token = authorization_header.split(" ")[1]
        decoded_token = jwt.decode(token, options={"verify_signature": False})
        print(decoded_token)
        user_id = decoded_token["user_id"]
        print(user_id)
        user = User.objects.filter(id = user_id).first()
        if user is None:
            return JsonResponse({"success": False, "error": "login"}, status = 201)
        
    except jwt.InvalidTokenError:
        print("Invalid token")
        print(authorization_header)
    
    if user.is_authenticated and user.is_active:
        if request.method == "POST":
            cart_data = Cart.objects.filter(user = user)
            if len(cart_data) > 0:
                data = json.loads(request.body)
                a = data.get('address_id')
                if a:
                    addres = Address.objects.filter(user = user, address_id = a).first()
                    order = Order.objects.create(user=user, address=addres, order_status = "None", payment_status = "None", payment_method = "None",total_price=0)
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
                        order_data = OrderData(user = user, product = c.product, total_price = total_am,
                                    quantity = c.quantity )
                        order_data.save()
                        order.product.add(order_data)
                    order.quantity = total_cart_q
                    total_price = total_cart_p + tax
                    order.total_price = int(total_price)
                    order.save()
                    address_serializer = AddressSerializer(addres, many=False)

                    response = {

                        'message': 'Address used successfully.',
                        'order_id' : order.order_id,
                        'address' : address_serializer.data,
                        'tax' : tax,
                        'price_not' : total_not_price,
                        'price' : total_cart_p,
                        'price_with_tax' : total_price
                    }
                    return JsonResponse(response, status=200)

            c = data.get('coupon')
            if c:
                coupon = Offer.objects.filter(code=coupon_code, status=True).first()
                cart_data = Cart.objects.filter(user = user)
                total_cart_p = 0
                total_cart_q = 0
                tax = 0
                total_not_price = 0
                coupon_p = 0
                if coupon and coupon.status and coupon.start_date <= timezone.now() <= coupon.end_date:
                    od = OrderData.objects.filter(user = user).first()
                    order = Order.objects.filter(user = user).first()
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
                    data = {
                        'coupon_price' : coupon_p,
                        'price_with_coupon_with_tax' : total_price,
                        'order_id' : order.order_id
                    }
                    
                    return JsonResponse(data, status=200)
                response = {
                    'message': 'This Coupon is expoired or not available.'
                }
                return JsonResponse(response, status=201)
        return JsonResponse({"success": False, "message": "Request Metod is not allowed"}, status = 201)
    return JsonResponse({"success": False, "message": "User is not authenticated"}, status = 201)



@swagger_auto_schema(
    method='post',
    operation_description="Confirm cash on delivery payment for a specific order.",
    manual_parameters=[
        openapi.Parameter(
            'Authorization',
            openapi.IN_HEADER,
            description="Bearer token for user authentication",
            type=openapi.TYPE_STRING,
            required=True,
        ),
        openapi.Parameter(
            'order_id',
            openapi.IN_PATH,
            description="ID of the order to confirm payment.",
            type=openapi.TYPE_STRING,
            required=True,
        ),
        openapi.Parameter(
            'from_cart',
            openapi.IN_QUERY,
            description="Indicates if the payment is from the cart (1 for true).",
            type=openapi.TYPE_STRING,
            required=False,
        ),
    ],
    responses={
        200: openapi.Response(
            description="Order placed successfully.",
            examples={
                "application/json": {
                    "message": "Order Placed Successfully."
                }
            }
        ),
        201: openapi.Response(
            description="Login required or error during processing.",
            examples={
                "application/json": {
                    "success": False,
                    "message": "User is not authenticated."
                },
                "application/json": {
                    "message": "Error message detail."
                }
            }
        )
    }
)
@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
@csrf_exempt
def cod_payment(request, order_id):
    authorization_header = request.META.get('HTTP_AUTHORIZATION')

    # Decode the token and get the user ID
    print(authorization_header)
    if authorization_header is None:
        return JsonResponse({"success": False, "error": "login"}, status = 201)
    try:
        token = authorization_header.split(" ")[1]
        decoded_token = jwt.decode(token, options={"verify_signature": False})
        print(decoded_token)
        user_id = decoded_token["user_id"]
        print(user_id)
        user = User.objects.filter(id = user_id).first()
        if user is None:
            return JsonResponse({"success": False, "error": "login"}, status = 201)
        
    except jwt.InvalidTokenError:
        print("Invalid token")
        print(authorization_header)
    
    if user.is_authenticated and user.is_active:
        try:
            if request.method == "POST":
                
                orda = Order.objects.filter(user = user, order_id=order_id).first()
                print(orda)
                f_cart = request.GET.get('from_cart')

                if orda.order_status == "None" and orda.payment_status == "None" and orda.payment_method == "None":
                    orda.order_status = "Placed"
                    orda.payment_status = "Unpaid"
                    orda.payment_method = "Cash On Delivery"
                    orda.save()
                    number = str(orda.address.phone)
                    print(number)
                    if f_cart == '1':
                        cart_data = Cart.objects.filter(user=user)
                        if cart_data:
                            for cart_item in cart_data:
                                # Decrease the quantity of the product in the cart
                                cart_item.product.quantity -= cart_item.quantity
                                cart_item.product.save()
                            cart_data.delete()
                    else:
                        for order_data in orda.product.all():
                            order_data.product.quantity -= orda.quantity
                            order_data.product.save()
                        
                    # Sending email
                    subject = 'Order Confirmation'
                    message = f"Dear {orda.address.first_name}, Thank you for your recent order from our online store. We are delighted to inform you that your order has been successfully processed. Your order details are as follows:\n\nOrder ID: {orda.order_id}\nTotal Amount: {orda.total_price}.\n\nShop with us again. For more details, please visit our website.\n\nThe FURNITURE"
                    from_email = 'contact@swastik.ai'
                    recipient_list = [orda.address.email,]
                    try:
                        send_mail(subject, message, from_email, recipient_list)
                    except Exception as e:
                        print(e)

                    # try:
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
                        # 'FURNITURE', f'Dear {orda.address.first_name} Your order id {orda.order_id} has been {orda.order_status} Thanks Furniture')
                        # print (resp)
                    # except Exception as e:
                    #     print(e)


                    response = {
                        'message': 'Order Placed Succesfully.'
                    }
                    return JsonResponse(response, status=200)
        except Exception as e:
            print(e)
            response = {
                'message': e
            }
            return JsonResponse(response, status=201)   
    return JsonResponse({"success": False, "message": "User is not authenticated"}, status = 201)


@swagger_auto_schema(
    method='post',
    operation_description="Process online payment for a specific order using Razorpay.",
    manual_parameters=[
        openapi.Parameter(
            'Authorization',
            openapi.IN_HEADER,
            description="Bearer token for user authentication",
            type=openapi.TYPE_STRING,
            required=True,
        ),
        openapi.Parameter(
            'order_id',
            openapi.IN_PATH,
            description="ID of the order to process payment.",
            type=openapi.TYPE_STRING,
            required=True,
        ),
    ],
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'from_cart': openapi.Schema(type=openapi.TYPE_STRING, description="Indicates if the payment is from the cart (1 for true)."),
            'payment_status': openapi.Schema(type=openapi.TYPE_STRING, description="Status of the payment."),
            'payment_id': openapi.Schema(type=openapi.TYPE_STRING, description="Payment ID from Razorpay."),
        },
        required=['payment_status', 'payment_id']
    ),
    responses={
        200: openapi.Response(
            description="Payment processed successfully.",
            examples={
                "application/json": {
                    "message": "Order Placed Successfully."
                }
            }
        ),
        201: openapi.Response(
            description="Error during processing or already updated.",
            examples={
                "application/json": {
                    "success": False,
                    "message": "User is not authenticated."
                },
                "application/json": {
                    "success": False,
                    "message": "Data already Updated"
                }
            }
        )
    }
)
@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
@csrf_exempt
def pay_payment(request, order_id):
    authorization_header = request.META.get('HTTP_AUTHORIZATION')

    # Decode the token and get the user ID
    print(authorization_header)
    if authorization_header is None:
        return JsonResponse({"success": False, "error": "login"}, status = 201)
    try:
        token = authorization_header.split(" ")[1]
        decoded_token = jwt.decode(token, options={"verify_signature": False})
        print(decoded_token)
        user_id = decoded_token["user_id"]
        print(user_id)
        user = User.objects.filter(id = user_id).first()
        if user is None:
            return JsonResponse({"success": False, "error": "login"}, status = 201)
        
    except jwt.InvalidTokenError:
        print("Invalid token")
        print(authorization_header)
    
    if user.is_authenticated and user.is_active:
        if request.method == "POST":
            data = json.loads(request.body)
            print(data)
            f_cart = data.get('from_cart')
            payment_status = data.get('payment_status')
            payment_id = data.get('payment_id')
            print(order_id, user)
            orda = Order.objects.filter(user = user, order_id = order_id).first()
            print(orda.order_status, orda.payment_status, orda.payment_method)
            razorpay_client = razorpay.Client(auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))
            print(razorpay_client)
            try:
                dataa = razorpay_client.payment.fetch(payment_id)
                print(dataa)
            except Exception as e:
                print(e)
            if orda.order_status == "None" and orda.payment_status == "None" and orda.payment_method == "None":
                
                if dataa['status'] == "authorized":
                    orda.order_status = "Placed"
                    orda.payment_status = "Paid"
                    orda.payment_method = "Online Payment"
                    orda.payment_id = payment_id
                    orda.save()

                    if f_cart == '1':
                        cart_data = Cart.objects.filter(user=user)
                        if cart_data:
                            for cart_item in cart_data:
                                # Decrease the quantity of the product in the cart
                                cart_item.product.quantity -= cart_item.quantity
                                cart_item.product.save()
                            cart_data.delete()
                    else:
                        
                        for order_data in orda.product.all():
                            order_data.product.quantity -= orda.quantity
                            order_data.product.save()

                    number = str(orda.address.phone)

                    # Sending email
                    subject = 'Order Confirmation'
                    message = f"Dear {orda.address.first_name}, Thank you for your recent order from our online store. We are delighted to inform you that your order has been successfully processed. Your order details are as follows:\n\nOrder ID: {orda.order_id}\nTotal Amount: {orda.total_price}.\n\nShop with us again. For more details, please visit our website.\n\nThe FURNITURE"
                    from_email = 'contact@swastik.ai'
                    recipient_list = [orda.address.email]
                    try:
                        send_mail(subject, message, from_email, recipient_list)
                    except Exception as e:
                        print(e)

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
                    # 'FURNITURE', f'Dear {orda.address.first_name} Your order id {orda.order_id} has been {orda.order_status} Thanks Furniture')
                    # print (resp)

                    response = {
                        'message': 'Order Placed Succesfully.'
                    }
                    return JsonResponse(response, status=200)
                else:
                    orda.order_status = "Failed"
                    orda.payment_status = "Failed"
                    orda.payment_method = "Online Payment"
                    orda.payment_id = payment_id
                    orda.save()

                    number = str(orda.address.phone)

                    # Sending email
                    subject = 'Payment Failed'
                    # message = f"Dear {orda.address.first_name}, Thank you for your recent order from our online store. We are delighted to inform you that your order has been successfully processed. Your order details are as follows:\n\nOrder ID: {orda.order_id}\nTotal Amount: {orda.total_price}.\n\nShop with us again. For more details, please visit our website.\n\nThe FURNITURE"
                    message = f"""We regret to inform you that there was an issue processing your payment for the order placed on {oop.date_added}. Unfortunately, the payment transaction was declined by your bank. Please note that your order has not been completed and will not be processed until payment has been successfully received. Shop with us again. For more details login to https://gluoenelectrical.com. The FURNITURE"""
                    from_email = 'contact@swastik.ai'
                    recipient_list = [orda.address.email]
                    try:
                        send_mail(subject, message, from_email, recipient_list)
                    except Exception as e:
                        print(e)

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
                    # 'FURNITURE', f'Dear {orda.address.first_name} Your order id {orda.order_id} has been {orda.order_status} Thanks Furniture')
                    # print (resp)

                    response = {
                        'message': 'Payment Failed Succesfully.'
                    }
                    return JsonResponse(response, status=200)
            return JsonResponse({"success": False, "message": "Data already Updated"}, status = 201)
    return JsonResponse({"success": False, "message": "User is not authenticated"}, status = 201)

@swagger_auto_schema(
    method='get',
    operation_description="Retrieve the privacy policy of the application.",
    responses={
        200: openapi.Response(
            description="Privacy policy retrieved successfully.",
            examples={
                "application/json": {
                    "privacy": "Your privacy policy text goes here."
                }
            }
        )
    }
)
@api_view(['GET'])
@permission_classes([AllowAny])
def privacy_policy(request):
    privacy = Privacy_Policy.objects.first()
    context = {
        'privacy' : privacy,
        'page' : "Privacy",
        'title': "Privacy Policy"
    }
    response = {
        'privacy': privacy.privacy
    }
    return JsonResponse(response, status=200)


@swagger_auto_schema(
    method='get',
    operation_description="Retrieve the information about the application.",
    responses={
        200: openapi.Response(
            description="About information retrieved successfully.",
            examples={
                "application/json": {
                    "about": "Information about the application goes here."
                }
            }
        ),
        404: openapi.Response(
            description="About information not found.",
            examples={
                "application/json": {
                    "error": "About information not found."
                }
            }
        )
    }
)
@api_view(['GET'])
@permission_classes([AllowAny])
def about(request):
    about = About.objects.first()
    context = {
        'about' : about,
        'page' : "About",
        'title': "About"
    }
    response = {
        'about': about.about
    }
    return JsonResponse(response, status=200)

@swagger_auto_schema(
    method='get',
    operation_description="Retrieve the return policy of the application.",
    responses={
        200: openapi.Response(
            description="Return policy retrieved successfully.",
            examples={
                "application/json": {
                    "return_policy": "Details of the return policy go here."
                }
            }
        ),
        404: openapi.Response(
            description="Return policy information not found.",
            examples={
                "application/json": {
                    "error": "Return policy information not found."
                }
            }
        )
    }
)
@api_view(['GET'])
@permission_classes([AllowAny])
def return_policy(request):
    return_policy = Return_Policy.objects.first()
    context = {
        'return_policy' : return_policy,
        'page' : "Return",
        'title': "Return Policy"
    }
    response = {
        'return_policy': return_policy.return_policy
    }
    return JsonResponse(response, status=200)


@swagger_auto_schema(
    method='get',
    operation_description="Retrieve the terms and conditions of the application.",
    responses={
        200: openapi.Response(
            description="Terms and conditions retrieved successfully.",
            examples={
                "application/json": {
                    "terms": "Details of the terms and conditions go here."
                }
            }
        ),
        404: openapi.Response(
            description="Terms and conditions information not found.",
            examples={
                "application/json": {
                    "error": "Terms and conditions information not found."
                }
            }
        )
    }
)
@api_view(['GET'])
@permission_classes([AllowAny])
def terms_condition(request):
    terms = Terms_Condition.objects.first()
    context = {
        'terms' : terms,
        'page' : "Terms",
        'title': "Terms & Condition"
    }
    response = {
        'terms': terms.terms
    }
    return JsonResponse(response, status=200)
