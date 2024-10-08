from rest_framework import serializers
from main.models import crousel, News, Product, Faq, Category,  productreview, Address, Profile, Order, WarrantyRegistration, WarrantyClaim, Partner, Wish, Cart, OrderData
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ('password',)

class CrouselSerializer(serializers.ModelSerializer):
    class Meta:
        model = crousel
        fields = '__all__'  # You can specify the fields you want to include explicitly

class NewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = News
        fields = '__all__'  # Include all fields from the News model


class FaqSerializer(serializers.ModelSerializer):
    class Meta:
        model = Faq
        fields = '__all__'  # Include all fields from the Faq model

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class ProductReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = productreview
        fields = '__all__'

class AddressSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    class Meta:
        model = Address
        fields = '__all__'

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = '__all__'

class OrderDataSerializer(serializers.ModelSerializer):
    product = ProductSerializer()
    class Meta:
        model = OrderData  # Assuming OrderData is the related model for the product field
        fields = '__all__'  # Adjust based on your actual fields



class WarrantyRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = WarrantyRegistration
        fields = '__all__'

class WarrantyClaimSerializer(serializers.ModelSerializer):
    class Meta:
        model = WarrantyClaim
        fields = '__all__'

class PartnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Partner
        fields = '__all__'

class OrderSerializer(serializers.ModelSerializer):
    product = OrderDataSerializer(many=True)
    address = AddressSerializer()
    partner = PartnerSerializer()
    class Meta:
        model = Order
        fields = '__all__'

class WishSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wish
        fields = '__all__'


class CartSerializer(serializers.ModelSerializer):
    product = ProductSerializer()
    class Meta:
        model = Cart
        fields = '__all__'