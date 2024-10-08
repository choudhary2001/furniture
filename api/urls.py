from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.urls.conf import include
from rest_framework_simplejwt import views as jwt_views
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('signup', views.api_signup, name='api_signup'),
    path('signin', views.api_signin, name='api_signin'),
    path('user-verification', views.api_twoverificationmobile, name='api_twoverificationmobile'),
   	path('change-password', views.api_forget_password_change, name='api_forget_password_change'),
   	path('logout', views.api_logout_view, name='api_logout_view'),
   	path('index', views.api_index, name='api_index'),
    path('products',views.api_products, name='api_products'),
    path('products/<category_slug>',views.api_products, name='api_products'),
    path('products/<category_slug>/<product_slug>',views.api_product_details, name='api_product_details'),
    path('add/review',views.api_add_product_review, name='api_add_product_review'),
    path('user/address',views.api_add_address, name='api_add_address'),
    path('user/address/edit/<address_id>',views.api_change_address, name='api_change_address'),
    path('user/address/delete/<address_id>',views.api_delete_address, name='api_delete_address'),
    path('complaint',views.api_complaint, name='api_complaint'),
    path('profile',views.api_profile, name='api_profile'),
    path('orders',views.api_order_view, name='api_order_view'),
    path('contact',views.api_contact, name='api_contact'),
    #path('partnerlocator',views.api_partner_locator, name='api_partner_locator'),
    path('partner/registration',views.api_partner_registration, name='api_partner_registration'),
    # path('customer/warrantyregistration',views.api_warranty_registration, name='api_warranty_registration'),
    # path('validate_registration_number/',views.warranty_registration_check, name='warranty_registration_check'),
    # path('customer/warrantyclaim',views.api_claim_warranty, name='api_claim_warranty'),
    path('invoice/<invoice_id>',views.api_invoice, name='api_invoice'),
    path('wishlist',views.api_wishlist, name='api_wishlist'),
    path('wishlist/add/<product_slug>',views.api_add_wishlist, name='api_add_wishlist'),
    path('wishlist/remove/<w_id>',views.api_remove_wishlist, name='api_remove_wishlist'),
    path('add/cart/<product_slug>',views.api_cart_add, name='api_cart_add'),
    path('cart',views.api_cart, name='api_cart'),
    path('cart/length',views.api_cart_length, name='api_cart_length'),
    path('clear/cart',views.clear_cart, name='api_clear_cart'),
    path('remove/cart/<product_slug>',views.cart_remove_api, name='cart_remove_api'),
    path('buy_now',views.buy_now, name='buy_now'),
    path('buy_from_cart',views.buy_from_cart, name='buy_from_cart'),
    path('cod_payment/<int:order_id>',views.cod_payment, name='cod_payment'),
    path('payment/<int:order_id>',views.pay_payment, name='pay_payment'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('about',views.about, name='api_about'),
    path('privacy_policy',views.privacy_policy, name='api_privacy_policy'),
    path('return_policy',views.return_policy, name='api_return_policy'),
    path('terms_condition',views.terms_condition, name='api_terms_condition'),
]


urlpatterns+= static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns+= static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)