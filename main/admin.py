from django.contrib import admin
from django.contrib.auth.models import User

# Register your models here.

from .models import crousel, Category, Product, User_verification, productreview, WarrantyRegistration, WarrantyClaim
class CrasoulAdmin(admin.ModelAdmin):
    pass

class CategoryAdmin(admin.ModelAdmin):
    pass

class UserverificationAdmin(admin.ModelAdmin):
    pass

class ProductAdmin(admin.ModelAdmin):
    pass

class ProductreviewAdmin(admin.ModelAdmin):
    pass

class WarrantyRegistrationAdmin(admin.ModelAdmin):
    pass

class WarrantyClaimAdmin(admin.ModelAdmin):
    pass

admin.site.register(crousel, CrasoulAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(User_verification, UserverificationAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(productreview, ProductreviewAdmin)
admin.site.register(WarrantyRegistration, WarrantyRegistrationAdmin)
admin.site.register(WarrantyClaim, WarrantyClaimAdmin)