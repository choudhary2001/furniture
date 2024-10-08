from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.urls.conf import include

urlpatterns = [
    path('', views.index, name='admin-index'),
    path('user', views.home, name='admin_user'),
    path('user/status/<username>', views.user_status, name='user_status'),
    path('user/delete/<username>', views.delete_user, name='delete_user'),
    path('products/',views.admin_product, name='admin_products'),
    path('products/<category_slug>',views.admin_product, name='admin_products_data'),
    path('products/<category_slug>/<product_slug>',views.admin_product_details, name='admin_products_details'),
    path('delete/products/delete/<product_slug>',views.admin_product_delete, name='admin_product_delete'),
    path('products/reviews/delete/<product_slug>/<review_id>',views.admin_product_review_delete, name='admin_product_review_delete'),
    path('add/products/',views.admin_product_add, name='admin_product_add'),
    path('user/order/',views.admin_order, name='admin_order'),
    path('user/order/<category_slug>',views.admin_order, name='admin_order'),
    path('user/details/order/<order_id>',views.admin_order_detail, name='admin_order_detail'),
    path('user/status/order/<order_id>/',views.admin_change_order, name='admin_change_order'),
    path('user/partner/order/<order_id>/<partner_id>',views.admin_change_order_partner, name='admin_change_order_partner'),
    path('user/delete/order/delete/<order_id>',views.admin_delete_order, name='admin_delete_order'),
    path('partner/',views.admin_partner_locetor, name='admin_partner_locetor'),
    path('partner/details/<partner_id>',views.admin_partner_detail, name='admin_partner_detail'),
    path('partner/status/<partner_id>',views.admin_change_partner, name='admin_change_partner'),
    path('partner/delete/<partner_id>',views.admin_delete_partner, name='admin_delete_partner'),
    path('warranty_registration/',views.admin_wr_locetor, name='admin_wr_locetor'),
    path('warranty_registration/details/<reg_id>',views.admin_wr_detail, name='admin_wr_detail'),
    path('warranty_registration/status/<reg_id>',views.admin_change_wr, name='admin_change_wr'),
    path('warranty_registration/delete/<reg_id>',views.admin_delete_wr, name='admin_delete_wr'),
    path('warranty_claim/',views.admin_wc_locetor, name='admin_wc_locetor'),
    path('warranty_claim/details/<claim_id>',views.admin_wc_detail, name='admin_wc_detail'),
    path('warranty_claim/status/<claim_id>',views.admin_change_wc, name='admin_change_wc'),
    path('warranty_claim/delete/<claim_id>',views.admin_delete_wc, name='admin_delete_wc'),
    path('contact/',views.admin_contact, name='admin_contact'),
    path('contact/delete/<contact_id>',views.admin_delete_contact, name='admin_delete_contact'),
    path('complainet/',views.admin_complainet, name='admin_complainet'),
    path('complainet/delete/<complaint_id>',views.admin_delete_complainet, name='admin_delete_complainet'),
    path('subscribe/',views.admin_user_subscribe, name='admin_subscribe'),
    path('subscribe/delete/<email>',views.admin_delete_user_subscribe, name='admin_delete_subscrie'),
    path('news/',views.admin_news, name='admin_news'),
    path('news/status/<news_id>',views.admin_change_news, name='admin_change_news'),
    path('news/delete/<news_id>',views.admin_delete_news, name='admin_delete_news'),
    path('category/',views.admin_category, name='admin_category'),
    path('category/edit/<category_slug>',views.admin_change_category, name='admin_change_category'),
    path('category/delete/<category_slug>',views.admin_delete_category, name='admin_delete_category'),
    path('crousel/',views.admin_crousel, name='admin_crousel'),
    path('crousel/edit/<c_id>',views.admin_change_crousel, name='admin_change_crousel'),
    path('crousel/delete/<c_id>',views.admin_delete_crousel, name='admin_delete_crousel'),
    path('faq/',views.admin_faq, name='admin_faq'),
    path('faq/status/<faq_id>',views.admin_change_faq, name='admin_change_faq'),
    path('faq/delete/<faq_id>',views.admin_delete_faq, name='admin_delete_faq'),
    path('coupon/',views.admin_coupon, name='admin_coupon'),
    path('coupon/status/<code>',views.admin_change_coupon, name='admin_change_coupon'),
    path('coupon/delete/<code>',views.admin_delete_coupon, name='admin_delete_coupon'),
    path('partnerlocator',views.partner_locator, name='partner_locator'),
    path('privacy_policy/',views.privacy_policy, name='admin_privacy_policy'),
    path('about/',views.about, name='admin_about'),
    path('return_policy/',views.return_policy, name='admin_return_policy'),
    path('terms_condition/',views.terms_condition, name='admin_terms_condition'),
    path('privacy_policy/<privacy_id>',views.edit_privacy_policy, name='edit_privacy_policy'),
    path('about/<about_id>',views.edit_about, name='edit_about'),
    path('return_policy/<return_id>',views.edit_return_policy, name='edit_return_policy'),
    path('terms_condition/<terms_id>',views.edit_terms_condition, name='edit_terms_condition'),
    path('video/',views.admin_video, name='admin_video'),
    path('video/delete/<video_id>',views.admin_delete_video, name='admin_delete_video'),

]


urlpatterns+= static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns+= static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)