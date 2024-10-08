from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.urls.conf import include

urlpatterns = [
    path('', views.index, name='index'),
    # path('new', views.new_view, name='index'),
    path('signup', views.signup, name='signup'),
    path('signin', views.signin, name='login'),
    path('user-verification', views.twoverificationmobile, name='twoverificationmobile'),
   	path('logout', views.logoutuser, name='logout'),
   	path('forgot_password', views.forgot_password, name='forgot_password'),
   	path('verify', views.verify, name='verify'),
   	path('change_password', views.change_password, name='change_password'),
    path('products/',views.all_product, name='products'),
    path('products/<category_slug>',views.all_product, name='products'),
    path('products/<category_slug>/<product_slug>',views.product_details, name='products_details'),
    path('add/cart/<product_slug>',views.cart_add, name='cart_add'),
    path('cart',views.cart, name='cart'),
    path('clear/cart',views.clear_cart, name='clear_cart'),
    path('remove/cart/<product_slug>',views.cart_remove, name='cart_remove'),
    path('wishlist',views.wishlist, name='wishlist'),
    path('wishlist/add/<product_slug>',views.add_wishlist, name='add_wishlist'),
    path('wishlist/remove/<w_id>',views.remove_wishlist, name='remove_wishlist'),
    path('add/review',views.add_product_review, name='add_product_review'),
    path('checkout',views.checkout_page, name='checkout_page'),
    path('checkout/payment/<order_id>',views.cod_payment, name='cod_payment'),
    path('checkout/payment/process/<order_id>',views.payment_process, name='payment_process'),
    path('checkout/payment/confirm/<order_id>',views.complete_order, name='complete_order'),
    path('checkout/order',views.complete_order, name='complete_order'),
    path('customer/services',views.customer_service, name='customer_service'),
    path('customer/warrantyregistration',views.warranty_registration, name='warranty_registration'),
    path('validate_registration_number/',views.warranty_registration_verify, name='warranty_registration_verify'),
    path('customer/warrantyclaim',views.claim_warranty, name='claim_warranty'),
    path('partner/registration',views.partner_registration, name='partner_registration'),
    # path('partnerlocator',views.partner_locator, name='partner_locator'),
    path('contact',views.contact, name='contact'),
    path('profile',views.profile, name='profile'),
    path('complaint',views.complaint, name='complaint'),
    path('invoice/<invoice_id>',views.invoice, name='invoice'),
    path('user/address',views.add_address, name='add_address'),
    path('user/address/edit/<address_id>',views.change_address, name='change_address'),
    path('user/address/delete/<address_id>',views.delete_address, name='delete_address'),
    path('paymenthandler/',views.paymenthandler, name='paymenthandler'),
    path('payment_success/',views.payment_success, name='payment_success'),
    path('payment_failed/',views.payment_failed, name='payment_failed'),
    path('user/subscribe',views.subscribe, name='subscribe'),

    path('video',views.video_news, name='video'),
    path('about',views.about, name='about'),
    path('privacy_policy',views.privacy_policy, name='privacy_policy'),
    path('return_policy',views.return_policy, name='return_policy'),
    path('terms_condition',views.terms_condition, name='terms_condition'),



]


urlpatterns+= static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns+= static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)