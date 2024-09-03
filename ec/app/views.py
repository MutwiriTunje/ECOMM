import json
from django.conf import settings
from django.db.models import Count, Q
from django.shortcuts import redirect, render
from django.http import HttpResponse, JsonResponse
from django.urls import reverse
from django.views import View
# import razorpay
import requests
from . models import Cart, Customer, OrderPlaced, Payment, Product
from . forms import CustomerProfileForm, CustomerRegistrationForm
from django.contrib import messages
# from django_daraja.mpesa.core import MpesaClient
# import logging

from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

# Create your views here.

 
def home(request):
    return render(request,"app/home.html")

def about(request):
    return render(request,"app/about.html")

def contact(request):
    return render(request,"app/contact.html")

class CategoryView(View):
    def get(self,request,val):
        product = Product.objects.filter(category=val)
        title = Product.objects.filter(category=val).values('title').annotate(total=Count('title'))
        return render(request,"app/category.html",locals())

class CategoryTitle(View):
    def get(self,request,val):
        product = Product.objects.filter(title=val)
        title = Product.objects.filter(category=product[0].category).values('title')
        return render(request,"app/category.html",locals())

class ProductDetail(View):
    def get(self,request,pk):
        product = Product.objects.get(pk=pk)
        return render(request,"app/productdetail.html",locals())
    
class CustomerRegistrationView(View):
    def get(self,request):
        form = CustomerRegistrationForm()
        return render(request, "app/customerregistration.html",locals())
    def post(self,request):
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request,"User Registered Successfully")
        else:
            messages.warning(request,"Invalid Input Data")
        return render(request, 'app/customerregistration.html',locals())
    
class ProfileView(View):
    def get(self,request):
        form =CustomerProfileForm()
        return render(request, 'app/profile.html',locals())
    def post(self,request):
        form = CustomerProfileForm(request.POST)
        if form.is_valid():
            user = request.user
            name =form.cleaned_data['name']
            locality = form.cleaned_data['locality']
            city = form.cleaned_data['city']
            mobile = form.cleaned_data['mobile']
            county = form.cleaned_data['county']
            zipcode = form.cleaned_data['zipcode']

            reg = Customer(user=user,name=name,locality=locality,mobile=mobile,city=city,county=county,zipcode=zipcode)
            reg.save()
            messages.success(request,"Profile saved successfully")
        else:
            messages.warning(request,"Invalid input data")
        return render(request, 'app/profile.html',locals())

def address(request):
    add =Customer.objects.filter(user=request.user)
    return render(request, 'app/address.html',locals())

class updateAddress(View):
    def get(self,request,pk):
        add = Customer.objects.get(pk=pk)
        form =CustomerProfileForm(instance=add)
        return render(request, 'app/updateAddress.html',locals())
    def post(self, request,pk):
        form =CustomerProfileForm(request.POST)
        if form.is_valid():
            add = Customer.objects.get(pk=pk)
            add.name =form.cleaned_data['name']
            add.locality = form.cleaned_data['locality']
            add.city = form.cleaned_data['city']
            add.mobile = form.cleaned_data['mobile']
            add.county = form.cleaned_data['county']
            add.zipcode = form.cleaned_data['zipcode']
            add.save()
            messages.success(request,"Profile update saved successfully")
        else:
            messages.warning(request,"Invalid input data")
        return redirect("address")

def add_to_cart(request):
    print("to cart now")
    user=request.user
    product_id=request.GET.get('prod_id')
    product = Product.objects.get(id=product_id)
    Cart(user=user,product=product).save()
    return redirect("/cart")

def show_cart(request):
    print("buy now here")
    user = request.user
    cart = Cart.objects.filter(user=user)
    amount = 0
    for p in cart:
        value = p.quantity * p.product.discounted_price
        amount = amount + value
    totalamount = amount + 50

    return render(request, 'app/addtocart.html',locals())

class checkout(View):
    def get(self,request):
        user=request.user
        add=Customer.objects.filter(user=user)
        cart_items=Cart.objects.filter(user=user)
        famount = 0
        for p in cart_items:
            value = p.quantity * p.product.discounted_price
            famount = famount + value
        totalamount = famount + 50
        razoramount =int(totalamount * 100)
        # client = razorpay.Client(auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))
        # data = { "amount": razoramount, "currency": "KSH", "receipt": "order_rcptid_11"}
        # payment_response = client.order.create(data=data)
        # print(payment_response)

        # order_id = payment_response['id']
        # order_status = payment_response['status']
        # if order_status == 'created':
        #     payment = Payment(
        #         user=user,
        #         amount=totalamount,
        #         razorpay_order_id=order_id,
        #         razorpay_payment_status = order_status
        #     )
        #     payment.save()
        return render(request, 'app/checkout.html',locals())


def payment_done(request):
    order_id=request.GET.get('order_id')
    payment_id=request.GET.get('payment_id')
    cust_id=request.GET.get('cust_id')
    #print("payment_done : oid = ",order_id," pid = ",payment_id," cid = ",cust_id")
    user=request.user
    #return redirect('orders')
    customer=Customer.objects.get(id=cust_id)
    #to update payment status and payment id
    payment=Payment.objects.get(razorpay_order_id=order_id)
    payment.paid = True
    payment.razorpay_payment_id = payment_id
    payment.save()
    #to save order details
    cart=Cart.objects.filter(user=user)
    for c in cart:
        OrderPlaced(user=user,customer=customer,product=c.product,quantity=c.quantity,payment=payment).save()
        c.delete()

    return redirect("orders")



def plus_cart(request):
    if request.method == 'GET':
        prod_id=request.GET['prod_id']
        c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
        c.quantity+=1
        c.save()
        user =request.user
        cart = Cart.objects.filter(user=user)
        amount = 0
        for p in cart:
            value = p.quantity * p.product.discounted_price
            amount = amount + value
        totalamount = amount + 50
        data={
            'quantity':c.quantity,
            'amount':amount,
            'totalamount':totalamount
        }
    return JsonResponse(data)

def minus_cart(request):
    if request.method == 'GET':
        prod_id=request.GET['prod_id']
        c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
        c.quantity-=1
        c.save()
        user =request.user
        cart = Cart.objects.filter(user=user)
        amount = 0
        for p in cart:
            value = p.quantity * p.product.discounted_price
            amount = amount + value
        totalamount = amount + 50
        data={
            'quantity':c.quantity,
            'amount':amount,
            'totalamount':totalamount
        }
    return JsonResponse(data)

def remove_cart(request):
    if request.method == 'GET':
        prod_id=request.GET['prod_id']
        c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
        c.quantity+=1
        c.delete()
        user =request.user
        cart = Cart.objects.filter(user=user)
        amount = 0
        for p in cart:
            value = p.quantity * p.product.discounted_price
            amount = amount + value
        totalamount = amount + 50
        data={
            'amount':amount,
            'totalamount':totalamount
        }
    return JsonResponse(data)