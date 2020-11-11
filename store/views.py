
from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.urls import path, resolve
# from django.views import View
from django.views.generic import ListView, DetailView, View
from django.views.generic.base import TemplateView
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.utils.crypto import get_random_string
from django.db import transaction
from re import search
import json
import re
import stripe
import os
from twilio.rest import Client

from .forms import SignupForm, OrderForm, UserProfileForm
from .models import *

stripe.api_key = "sk_test_4eC39HqLyjWDarjtT1zdp7dc"

# Create your views here.
class Store(View):
    def post(self, request):
        product = request.POST.get('product')
        remove = request.POST.get('remove')
        cart = request.session.get('cart')
        if cart:
            quantity = cart.get(product)
            if quantity:
                if remove:
                    if quantity <= 1:
                        cart.pop(product)
                    else:
                        cart[product] = quantity - 1
                else:
                    cart[product] = quantity + 1
            else:
                cart[product] = 1
        else:
            cart = {}
            cart[product] = 1

        request.session['cart'] = cart
        print('cart', request.session['cart'])
        return redirect('store')

    def get(self, request):
        # return HttpResponseRedirect('/store')
        print('hoem ul ------------')
        return home(request)

def home(request):
    cart = request.session.get('cart')

    if not cart:
        request.session['cart'] = {}

    products = None

    if request.user.is_authenticated:
        print('user is staff -------',request.user.is_staff)

    categoryId = request.GET.get('category')

    if categoryId:
        products = Product.get_all_products_by_id(categoryId)
    else:
        products = Product.get_all_products()

    classDisable = ""

    if request.get_full_path() == "/cart/":
        classDisable = True

    print("-----=============-------------", classDisable)
    categories = Category.get_all_categories()

    context = {'products': products, 'categories': categories, 'classDisable': classDisable}
    return render(request, 'store/store.html', context)

class Cart(View):
    def get(self , request):
        ids = list(request.session.get('cart').keys())
        products = Product.get_products_by_id(ids)
        print("-----=============-------------")
        print(products)
        print("-----=============-------------")
        if request.path == '/cart/':
            viewName = True

        context = {'products' : products, 'viewName':viewName}
        return render(request, 'store/cart.html', context)

class CheckOut(View):

    def get(self, request):
        
        form = OrderForm()
        if request.user.is_authenticated:
            try:                
                address = UserProfile.objects.get(user=request.user)
                order = Order()
                order.first_name = address.first_name
                order.phone = address.phone
                order.s_address = address.address
                order.city = address.city
                order.state = address.state
                order.zipcode = address.zipcode
                form = OrderForm(instance=order)
            except UserProfile.DoesNotExist:
                form = OrderForm()
        else:
            print("---------------User Not Logged --------------")

        cart = request.session.get('cart')
        products = Product.get_products_by_id(list(cart.keys()))
        
        formSignup = SignupForm()
        context = {
            'products': products,
            'form' : form,
            'formSignup':formSignup
        }
        print("---------------User Not Logged --------------",request.path)
        return render(request, 'store/checkout.html', context)

    @transaction.atomic
    def post(self, request):
        print('----------Checkout POST -----------')
        try:
            with transaction.atomic():
                if request.user.is_authenticated:
                    print('---------- User Authenticated -----------')
                    form = OrderForm(request.POST)
                    if form.is_valid():
                        order, created = Order.objects.get_or_create(
                            user = self.request.user,
                            first_name = form.cleaned_data['first_name'],
                            phone = form.cleaned_data['phone'],
                            s_address = form.cleaned_data['s_address'],
                            city = form.cleaned_data['city'],
                            state = form.cleaned_data['state'],
                            total = 0,
                            ordered=False
                        )
                        
                    cart = request.session.get('cart')
                    products = Product.get_products_by_id(list(cart.keys()))

                    totalAmount = 0    
                    for product in products:
                        shop_cart, created = ShopCart.objects.get_or_create(user=request.user,product=product,quantity=cart.get(str(product.id)))
                        totalAmount = totalAmount+shop_cart.amount
                        data = OrderProduct(
                            user = self.request.user,
                            order = order,
                            product = product,
                            quantity = shop_cart.quantity,
                            price = shop_cart.price,
                            amount = shop_cart.amount
                        )
                        # data.save()
                        order.orderproduct_set.add(data,bulk=False)
                    
                    Order.objects.filter(ordered=False).update(
                        ip = request.META.get('REMOTE_ADDR'),
                        total = totalAmount,
                        code = get_random_string(6).upper(),
                        ordered = True,
                        status = 'New'
                    )
                                  
                    if not UserProfile.objects.filter(user = self.request.user).exists():
                        UserProfile.objects.get_or_create(
                            user = self.request.user,
                            first_name = form.cleaned_data['first_name'],
                            phone = form.cleaned_data['phone'],
                            address = form.cleaned_data['s_address'],
                            city = form.cleaned_data['city'],
                            state = form.cleaned_data['state']
                        )
        except Order.DoesNotExist:
                address = None
       
        request.session['cart'] = {}
        lastRecord = Order.objects.last()
        print("Order details ===")
        messages.add_message(request,messages.SUCCESS, "Order Placed Successfully"+lastRecord.code)
        # send("061188")
        return redirect('order')

class OrderSummaryView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.filter(user=self.request.user, ordered=True)
            # orderProducts = OrderProduct.objects.filter(order=order).values_list()
            context = {
                'order': order
            }
            return render(self.request, 'store/order.html', context)
        except ObjectDoesNotExist:
            messages.warning(self.request, "You do not have an active order")
            return redirect("/")

class UpdateCart(View):
    def get(self, request, *args, **kwargs):
        print('--- Update Cart args ------', args)
        print('--- Update Cart kwargs ------', self.kwargs['int'])
        print('--- Update Cart json.loads(request.body) ------', request.GET.get('action'))

        product = self.kwargs['int']
        action = request.GET.get('action')
        cart = request.session.get('cart')
        quantity = cart.get(product)

        if action == 'add':
            print('Action:', action)
            print('Product:', product)
            print('quantity:', quantity)
            # orderItem.quantity = (orderItem.quantity + 1)
            cart[product] = quantity + 1
            print('-------Add Product ------', cart)
            messages.add_message(request,messages.SUCCESS, "Product added in cart")
        elif action == 'remove':
            print('Action:', action)
            print('Product:', product)
            print('quantity:', quantity)
            if quantity <= 1:
                cart.pop(product)
            else:
                cart[product] = quantity - 1
            messages.add_message(request,messages.WARNING, "Product removed in cart")
        request.session['cart'] = cart
        return redirect('cart')

class Signup(View):
    def get(self, request):
        print(':: Signup HTTP_REFERER ::', request.META.get('HTTP_REFERER','/'), request.GET.get('next'))

        http_referer = request.META.get('HTTP_REFERER','/')
        
        if search("checkout",http_referer):
            print ("found", http_referer)
            request.session['key-checkout'] = "checkout"
        
        if request.user.is_authenticated:
            return redirect("store")
        else:
            form = SignupForm()
            return render(request, 'store/signup.html', {'form': form})

    def post(self, request):
        print(' -------- Signup Post method ----', request.session.get('key-checkout'))
        form = SignupForm(request.POST)
        print(' -------- is valid ----', form.is_valid())
        next = ""
        try:
            if form.is_valid():
                user = form.save()
                login(request, user)

                nextURL = ""
                if 'key-checkout' in request.session:
                    print("rtrtrtrtrtrtrtrtrtrtrtrt")
                    nextURL =  request.session.get('key-checkout', default='Guest')
                    # del request.session.get('key-checkout')
                else:
                    nextURL = request.META['HTTP_REFERER']
                    next = request.POST.get('next')
                
                print(' -------- signup next ----', nextURL)
                return redirect(nextURL)
            else:
                print(' -------- form.is_valid() else ----')
                postData = request.POST
                username = postData.get('username')
                email = postData.get('email')
                values = {
                    'username': username,
                    'email': email
                }
                next = request.POST.get('next')
               
        except Exception as e:
            raise e
        context = {'values': values, 'form':form}
        
        if next:
            messages.add_message(request,messages.WARNING, form.errors)
            return redirect(next)
        else:
            return render(request, 'store/signup.html', context)
        

class Login(View):
    return_url = None

    def get(self, request):
        Login.return_url = request.GET.get('return_url')
        return render(request, 'store/login.html')

    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request,user)
            print('return META url', request.META.get('HTTP_REFERER','/'))
            print('return META url', request.META['HTTP_REFERER'])
            next = request.POST.get('next')
            
            print('return path.location_url find', request.POST.get('next'))
            # print('return path.location_url search', search("login", str(path)))
            return redirect(next)
        else:
            error = "Invalid user"

        context ={'error':error}
        viewpage = request.POST.get('next', '/')
        print('viewpage -------------', viewpage)
        print('return META url', request.META.get('HTTP_REFERER','/'))
        if viewpage:
            messages.add_message(request,messages.WARNING, error)
            return redirect(viewpage)
            # return HttpResponseRedirect(request,viewpage, context)
        else:
            return render(request, 'store/login.html', context)

def logout(request):
    request.session.clear()
    return redirect('store')

def order(request):
    customer = request.session.get('customer')
    orders = Order.get_orders_by_customer(customer)
    print(orders)
    return render(request, 'store/order.html', {'orders': orders})


class Payment(View):
    def get(self, *args, **kwargs):
        context = {

        }
        return render(self.request,'store/payment.html', context)

    def post(self, *args, **kwargs):
        print('Payment Submitted')
        request.session['cart'] = {}
        return redirect("/")

class OrderDetailView(TemplateView):
    
    template_name = 'store/order_details.html'
    
    def get_context_data(self,*args,**kwargs):
        
        print("Order  ------",self.kwargs)
        order = Order()
        if self.kwargs['action'] == 'cancel':
            # OrderProduct.objects.filter(id=self.kwargs['id']).update(status="Cancelled")
            # orderProduct = OrderProduct.objects.get(id=self.kwargs['id'])
            # order = orderProduct.order
            Order.objects.filter(id=self.kwargs['id']).update(status="Cancelled")
        # else:
        #     order = Order.objects.get(id=self.kwargs['id'])
        order = Order.objects.get(id=self.kwargs['id'])
        print("Order  ------",order.id)
        context = {'order':order}
        return context

    

class Profile(TemplateView):
    
    template_name = 'store/profile.html'

    def get_context_data(self,*args,**kwargs):
        form = UserProfileForm()
        try:
            profile = UserProfile.objects.get(user=self.request.user)
            form = UserProfileForm(instance=profile)
      
        except UserProfile.DoesNotExist:
            print("---[ UserProfile.DoesNotExist ]-----")
            form = UserProfileForm()

        context ={'form':form}
        return context

    def post(self,request, *args, **kwargs):
        form = UserProfileForm(request.POST)
        
        if form.is_valid():
            try:
                exist = UserProfile.objects.get(user = self.request.user)
                form = UserProfileForm(request.POST, instance=exist)
                form.save()
                messages.add_message(request,messages.SUCCESS, "User Profile Updated Successfully")
            except UserProfile.DoesNotExist:
                form = UserProfileForm(request.POST)
                check = form.save(commit=False)
                check.user = self.request.user
                form.save(commit=True)
                messages.add_message(request,messages.SUCCESS, "User Profile Cretaed Successfully")
                
        return redirect('profile')


def send(orderId):
    # account_sid = os.environ['TWILIO_ACCOUNT_SID']
    # auth_token = os.environ['TWILIO_AUTH_TOKEN']
    try:
        account_sid = "AC897764297a26db59614fb3dd077e72a8"
        auth_token = "63ee38fd8334af1ea6c42196c2d54e2c"
        client = Client(account_sid, auth_token)

        message = client.messages \
                .create(
                     body="Order placed successfully! Order No :"+orderId,
                     from_='+19382223354',
                     to='+919059643289'
                 )

        print(message.sid)
    except ConnectionError as error:
        raise error
