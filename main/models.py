from django.db import models
from django.contrib.auth.models import User
from autoslug import AutoSlugField
import uuid
from PIL import Image
import io
import base64

# Create your models here.
class crousel(models.Model):
    c_id = models.CharField(max_length=8, unique=True, editable=False, default="")
    name = models.CharField(max_length=255)
    description = models.TextField()
    image = models.ImageField(upload_to='crouselimages/')
    link = models.CharField(max_length=255)

    def save(self, *args, **kwargs):
        if not self.c_id:
            self.c_id = str(uuid.uuid4().int)[:8]
        super(crousel, self).save(*args, **kwargs)

# class category(models.Model):
#     name = models.CharField(max_length=225)
#     slug = models.CharField(max_length=500)
#     image = models.ImageField(upload_to='categoryimages/')

# class subcategory(models.Model):
#     name = models.CharField(max_length=225)
#     slug = models.CharField(max_length=500)
#     category = models.ForeignKey(category, related_name='category', on_delete=models.CASCADE)

class Category(models.Model):
    parent = models.ForeignKey('self', related_name='children', on_delete=models.CASCADE, blank = 
    True, null=True)
    title = models.CharField(max_length=100) 
    slug = AutoSlugField(populate_from='title', unique=True, null=False, editable=False)
    image = models.ImageField(upload_to='categoryimages/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    class Meta:
        unique_together = ('slug', 'parent',)    
        verbose_name_plural = "categories"

    def __str__(self):                           
        full_path = [self.title]                  
        k = self.parent
        while k is not None:
            full_path.append(k.title)
            k = k.parent
        return ' -> '.join(full_path[::-1])  



class User_verification(models.Model):
    username = models.CharField(max_length=225)
    otp = models.CharField(max_length=6)
    date_added = models.DateTimeField(auto_now_add=True)

class Product(models.Model):
    title = models.CharField(max_length=255)
    details = models.TextField()
    features = models.TextField(default="")
    specifications = models.TextField()
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    slug = AutoSlugField(populate_from='title', unique=True, null=False, editable=False)
    image1 = models.ImageField(upload_to="productimage/")
    image2 = models.ImageField(upload_to="productimage/", default="", null=True, blank=True)
    image3 = models.ImageField(upload_to="productimage/", default="", null=True, blank=True)
    image4 = models.ImageField(upload_to="productimage/", default="", null=True, blank=True)
    image5 = models.ImageField(upload_to="productimage/", default="", null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    price = models.PositiveIntegerField(default=1)
    not_price = models.PositiveIntegerField(default=0)
    date_added = models.DateTimeField(auto_now_add=True)
    is_featured = models.BooleanField(default=False)
    status = models.BooleanField(default=True)
    tax = models.IntegerField(default=0)
    def to_dict(self):
        return {
            'title' : self.title,
            'details' : self.details,
            'features' : self.features,
            'specifications' : self.specifications,
            'slug' : self.slug,
            'quantity' : self.quantity,
            'price' : self.price,
            'not_price' : self.not_price,
            'is_featured' : self.is_featured
        }


class productreview(models.Model):
    review_id = models.CharField(max_length=8, unique=True, editable=False, default="")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    review_text = models.TextField()
    review_rating = models.PositiveIntegerField(default=0)
    date_added = models.DateTimeField(auto_now_add=True)

    def get_review_rating(self):
        return self.review_rating

    def save(self, *args, **kwargs):
        if not self.review_id:
            self.review_id = str(uuid.uuid4().int)[:8]
        super(productreview, self).save(*args, **kwargs)


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

class Address(models.Model):
    address_id = models.CharField(max_length=8, unique=True, editable=False, default="")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    country = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    local_address = models.CharField(max_length=255)
    town = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    postalcode = models.CharField(max_length=20)  # Change to CharField to handle large postal codes
    phone = models.CharField(max_length=20)  
    email = models.CharField(max_length=255)
    date_added = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.address_id:
            self.address_id = str(uuid.uuid4().int)[:8]
        super(Address, self).save(*args, **kwargs)

class Partner(models.Model):
    partner_id = models.CharField(max_length=8, unique=True, editable=False)
    name = models.CharField(max_length=255)
    father_name = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    mob_number = models.CharField(max_length=255)
    image = models.ImageField(upload_to="partner/")
    identity_proof = models.ImageField(upload_to="partner/")
    partner_type = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    pin_code = models.CharField(max_length=255)
    bank_name = models.CharField(max_length=255)
    account_holder_name = models.CharField(max_length=255)
    bank_account_no = models.CharField(max_length=255)
    bank_ifsc_code = models.CharField(max_length=255)
    bank_details = models.ImageField(upload_to="partner/")
    pay_method = models.CharField(max_length=255)
    pay_method_no = models.CharField(max_length=255)
    status = models.CharField(max_length=255, default = "Processing")
    date_added = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.partner_id:
            self.partner_id = str(uuid.uuid4().int)[:8]
        super(Partner, self).save(*args, **kwargs)


class Offer(models.Model):
    code = models.CharField(max_length=255, unique=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    discount = models.IntegerField(default=0)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    status = models.BooleanField(default = True)

class OrderData(models.Model):
    order_id = models.CharField(max_length=8, unique=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    total_price = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField(default=1)
    date_added = models.DateTimeField(auto_now_add=True)
    coupon = models.ForeignKey(Offer, on_delete = models.CASCADE, blank=True, null = True)
    def save(self, *args, **kwargs):
        if not self.order_id:
            self.order_id = str(uuid.uuid4().int)[:8]
        super(OrderData, self).save(*args, **kwargs)


class Order(models.Model):
    order_id = models.CharField(max_length=8, unique=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ManyToManyField(OrderData)
    address = models.ForeignKey(Address, on_delete=models.CASCADE)
    order_status = models.CharField(max_length=255)
    payment_status = models.CharField(max_length=255)
    payment_method = models.CharField(max_length=255)
    date_added = models.DateTimeField(auto_now_add=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    payment_id = models.CharField( max_length=250, default = "")
    partner = models.ForeignKey(
        Partner,
        on_delete=models.CASCADE, 
        default=None,
        null=True, 
        blank=True,
    )

    def save(self, *args, **kwargs):
        if not self.order_id:
            self.order_id = str(uuid.uuid4().int)[:8]
        super(Order, self).save(*args, **kwargs)

class WarrantyRegistration(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank = True, null=True)
    reg_id = models.CharField(max_length=8, unique=True, editable=False)
    name = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    mob_number = models.CharField(max_length=255)
    product = models.CharField(max_length=255)
    product_manufacturing_date = models.CharField(max_length=255)
    product_batch_no = models.CharField(max_length=255)
    product_serial_no = models.CharField(max_length=255)
    product_color = models.CharField(max_length=255)
    order_date = models.CharField(max_length=255)
    invoice_no = models.CharField(max_length=255)
    invoice = models.ImageField(upload_to="warranty/registration/")
    price = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    district = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    post_office = models.CharField(max_length=255)
    zipcode = models.CharField(max_length=255)
    land_mark = models.CharField(max_length=255)
    purchase_source = models.CharField(max_length=255)
    address = models.TextField()
    status = models.CharField(max_length=255, default="Processing")
    date_added = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.reg_id:
            self.reg_id = str(uuid.uuid4().int)[:8]
        super(WarrantyRegistration, self).save(*args, **kwargs)


class WarrantyClaim(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank = True, null=True)
    claim_id = models.CharField(max_length=8, unique=True, editable=False)
    name = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    mob_number = models.CharField(max_length=255)
    warranty_registration = models.CharField(max_length=255)
    product_manufacturing_date = models.CharField(max_length=255)
    product_batch_no = models.CharField(max_length=255)
    product_serial_no = models.CharField(max_length=255)
    product_color = models.CharField(max_length=255)
    registration_date = models.CharField(max_length=255)
    # product_image = models.ImageField(upload_to="warranty/claim/")
    # waranty_card = models.ImageField(upload_to="warranty/claim/")
    product_image = models.TextField()
    waranty_card = models.TextField()
    state = models.CharField(max_length=255)
    district = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    post_office = models.CharField(max_length=255)
    zipcode = models.CharField(max_length=255)
    land_mark = models.CharField(max_length=255)
    purchase_source = models.CharField(max_length=255)
    address = models.TextField()
    status = models.CharField(max_length=255, default="Processing")
    date_added = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.claim_id:
            self.claim_id = str(uuid.uuid4().int)[:8]
        super(WarrantyClaim, self).save(*args, **kwargs)



class Profile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    profile_image = models.ImageField(upload_to='userprofile/')
    phone_number = models.CharField(max_length=255)
    is_active = models.BooleanField(default=False)
    date_added = models.DateTimeField(auto_now_add=True)

class Contact(models.Model):
    contact_id = models.CharField(max_length=8, unique=True, editable=False, default="")
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    phone_no = models.CharField(max_length=255)
    message = models.TextField()
    date_added = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.contact_id:
            self.contact_id = str(uuid.uuid4().int)[:8]
        super(Contact, self).save(*args, **kwargs)


class Complainet(models.Model):
    complaint_id = models.CharField(max_length=8, unique=True, editable=False, default="")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.CharField(max_length=255)
    complaint = models.TextField()
    date_added = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.complaint_id:
            self.complaint_id = str(uuid.uuid4().int)[:8]
        super(Complainet, self).save(*args, **kwargs)

class News(models.Model):
    news_id = models.CharField(max_length=8, unique=True, editable=False, default="")
    title = models.CharField(max_length=255)
    image = models.ImageField(upload_to='news/')
    date_added = models.DateTimeField()
    slug = models.SlugField()
    status = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.news_id:
            self.news_id = str(uuid.uuid4().int)[:8]
        super(News, self).save(*args, **kwargs)

class Wish(models.Model):
    w_id = models.CharField(max_length=8, unique=True, editable=False, default="")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)    
    date_added = models.DateTimeField(auto_now_add=True)
    
    
    def save(self, *args, **kwargs):
        if not self.w_id:
            self.w_id = str(uuid.uuid4().int)[:8]
        super(Wish, self).save(*args, **kwargs)

class Faq(models.Model):
    faq_id = models.CharField(max_length=8, unique=True, editable=False, default="")
    title = models.CharField(max_length=255)
    description = models.TextField()
    status = models.CharField(max_length=5, default="Show")
    date_added = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.faq_id:
            self.faq_id = str(uuid.uuid4().int)[:8]
        super(Faq, self).save(*args, **kwargs)

class Subscribe(models.Model):
    email = models.CharField(max_length=255)
    date_added = models.DateTimeField(auto_now_add=True)


class About(models.Model):
    about_id = models.CharField(max_length=8, unique=True, editable=False, default="")
    about = models.TextField()

    def save(self, *args, **kwargs):
        if not self.about_id:
            self.about_id = str(uuid.uuid4().int)[:8]
        super(About, self).save(*args, **kwargs)

class Terms_Condition(models.Model):
    terms_id = models.CharField(max_length=8, unique=True, editable=False, default="")
    terms = models.TextField()
    
    def save(self, *args, **kwargs):
        if not self.terms_id:
            self.terms_id = str(uuid.uuid4().int)[:8]
        super(Terms_Condition, self).save(*args, **kwargs)

class Privacy_Policy(models.Model):
    privacy_id = models.CharField(max_length=8, unique=True, editable=False, default="")
    privacy = models.TextField()
    
    def save(self, *args, **kwargs):
        if not self.privacy_id:
            self.privacy_id = str(uuid.uuid4().int)[:8]
        super(Privacy_Policy, self).save(*args, **kwargs)


class Return_Policy(models.Model):
    return_id = models.CharField(max_length=8, unique=True, editable=False, default="")
    return_policy = models.TextField()
    
    def save(self, *args, **kwargs):
        if not self.return_id:
            self.return_id = str(uuid.uuid4().int)[:8]
        super(Return_Policy, self).save(*args, **kwargs)

class Video(models.Model):
    video_id = models.CharField(max_length=8, unique=True, editable=False, default="")
    video = models.FileField(upload_to='video/')
    date_added = models.DateTimeField(auto_now_add = True)

    def save(self, *args, **kwargs):
        if not self.video_id:
            self.video_id = str(uuid.uuid4().int)[:8]
        super(Video, self).save(*args, **kwargs)