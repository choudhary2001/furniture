from rest_framework import serializers
from main.models import crousel, News, Product, Faq, Category,  productreview, Address, Profile, Order, WarrantyRegistration, WarrantyClaim, Partner, Wish

class WarrantyRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        date_added = serializers.DateTimeField(source='date_added', format='%Y-%m-%d')
        model = WarrantyRegistration
        fields = '__all__'