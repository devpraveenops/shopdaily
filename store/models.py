from django.db import models
from django.contrib.auth.models import User, AbstractBaseUser, BaseUserManager
from django.db.models.signals import pre_save
# from djecom.utils import unique_slug_generator
# from django_countries.fields import CountryField, StateField
# from django_states.fields import StateField
from django.conf import settings
import datetime

ADDRESS_CHOICES = (
    ('B', 'Billing'),
    ('S', 'Shipping'),
)

AVAILABILITY_PRODUCT = (
    ('S', 'In Stock'),
    ('0', 'Out Of Range')
)

# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=200, null=True)

    @staticmethod
    def get_all_categories():
       return Category.objects.all()

    def __str__(self):
        return self.name
    class Meta:
        verbose_name_plural = 'Categories'

class Product(models.Model):
    name = models.CharField(max_length=200, null=True)
    price = models.FloatField(default=0)
    discount_price = models.FloatField(blank=True, null=True)
    slug = models.SlugField(blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, default=1)
    digital = models.BooleanField(default=False, null=True, blank=False)
    image = models.ImageField(null=True, blank=True, upload_to='uploads/products/')
    unit = models.CharField(max_length=11, null=True)
    storeNo = models.IntegerField(max_length=10, null=True)

    def __str__(self):
        return self.name

    @staticmethod
    def get_products_by_id(ids):
        return Product.objects.filter(id__in=ids)

    @staticmethod
    def get_all_products():
        return Product.objects.all()

    @staticmethod
    def get_all_products_by_id(category_id):
        if category_id:
            return Product.objects.filter(category=category_id)
        else:
            Product.objects.all()

    @property
    def imageURL(self):
        try:
            url = self.image.url
        except:
            url = ''
        return url


class ShopCart(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return self.product.name

    @property
    def price(self):
        return (self.product.price)

    @property
    def amount(self):
        return (self.quantity * self.product.price)

    class Meta:
        verbose_name_plural = 'Shop Carts'

class Order(models.Model):
    STATUS = (
        ('New', 'New'),
        ('Accepted', 'Accepted'),
        ('Completed', 'Completed'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=6, editable=False)
    first_name = models.CharField(max_length=11)
    phone = models.CharField(max_length=10, blank=True)
    s_address = models.CharField(max_length=200, null=True)
    city = models.CharField(max_length=200, null=True)
    state = models.CharField(max_length=200, null=True)
    zipcode = models.CharField(max_length=7,default='524201')
    total = models.FloatField()
    status = models.CharField(max_length=10, choices=STATUS)
    ip = models.CharField(blank=True, max_length=20)
    adminnote = models.CharField(blank=True, max_length=100)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    ordered = models.BooleanField(default=False)
        
    def __str__(self):
        return self.user.first_name

        

    
class OrderProduct(models.Model):
    STATUS = (
        ('New', 'New'),
        ('Accepted', 'Accepted'),
        ('Cancelled', 'Cancelled'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    quantity = models.IntegerField()
    price = models.FloatField()
    amount = models.FloatField()
    status = models.CharField(max_length=10, choices=STATUS,default='New')
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.product.name

# class Payment(models.Model):
#     stripe_charge_id = models.CharField(max_length=50)
#     user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
#     amount = models.FloatField()
#     timestamp = models.DateTimeField(auto_now_add=True)
#
#     def _str_(self):
#         return self.user.username
#

class Refund(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    reason = models.TextField()
    accepted = models.BooleanField(default=False)
    email = models.EmailField()

    def _str_(self):
        return f"{self.pk}"


class UserProfile(models.Model):
    # user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100,default="")
    last_name = models.CharField(max_length=100,default="")
    email = models.EmailField()
    phone = models.CharField(max_length=10)
    address = models.CharField(max_length=100)
    city = models.CharField(max_length=200, null=True)
    state = models.CharField(max_length=200, null=True)
    zipcode = models.CharField(max_length=100)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.first_name

    class Meta:
        verbose_name_plural = 'User Profiles'

class StoreUserManager(BaseUserManager):
    def create_user(self,store_name,phone,password=None):
        if not store_name:
            return ValueError("Store name required")
        if not phone:
            return ValueError("Phone required")
        user =self.model(
            store_name=store_name,
            phone=phone
        )
        user.set_password(password)
        user.save(using=self._db)
        return user


class Store(AbstractBaseUser):
    store_name=models.CharField(unique=True,max_length=100,default="")
    phone=models.CharField(max_length=10)
    is_active=models.BooleanField(default=False)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    REQUIRED_FIELDS=['store_name']

    def __str__(self):
        return self.store_name

    def has_perm(self, perm, obj=None):
        return True
    
    def has_module_perms(self, app_label):
        return True