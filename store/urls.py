from django.urls import path
from . import views
from .views import *
from .models import Order

urlpatterns = [
    path('', Store.as_view(), name="store"),
    # path('store/', views.home),


    
    path('signup/', Signup.as_view(), name="signup"),
    path('profile/', Profile.as_view(), name="profile"),
    path('login/', Login.as_view(), name="login"),
    path('logout/', views.logout, name="logout"),
    path('cart/', Cart.as_view(), name="cart"),
    path('checkout/', CheckOut.as_view(), name="checkout"),
    # path('order/', views.order, name="order"),
    path('payment/<payment_option>', Payment.as_view(), name="payment"),
    path('order/', OrderSummaryView.as_view(), name='order'),
    # path('add-to-cart/<slug:slug>', add_to_cart, name='add-to-cart'),
    # path('remove-from-cart/<slug:slug>', remove_from_cart, name='remove-from-cart'),
    path('order/<int:id>/<str:action>',OrderDetailView.as_view(), name="order_details"),
    path('update_cart/<int>',UpdateCart.as_view(), name="updatecart"),
]