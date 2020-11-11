from django.contrib import admin
from .models import *

# Register your models here.
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name','unit','price','discount_price','category']
    list_filter = ['name']

class OrderProductInline(admin.TabularInline):
    model = OrderProduct
    readonly_fields = ['user','product', 'quantity','price','amount']
    can_delete = False
    extra = 0

class OrderAdmin(admin.ModelAdmin):
    list_display = ['user','code','total','status']
    list_filter = ['user']
    readonly_fields = ['user','s_address','phone']
    can_delete = False
    extra = 0
    inlines = [OrderProductInline]

class ShopCartAdmin(admin.ModelAdmin):
    list_display = ['user','product', 'quantity','price','amount']
    list_filter = ['user']

class OrderProductAdmin(admin.ModelAdmin):
    list_display = ['user','product', 'quantity','price','amount']
    list_filter = ['user']

admin.site.register(Category)
admin.site.register(UserProfile)
admin.site.register(Product,ProductAdmin)
admin.site.register(Order,OrderAdmin)
admin.site.register(OrderProduct,OrderProductAdmin)
admin.site.register(ShopCart,ShopCartAdmin)


