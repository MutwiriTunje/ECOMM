from django.contrib import admin
from . models import Cart, OrderPlaced, Product, Customer

# Register your models here.

@admin.register(Product)
class ProductModelAdmin(admin.ModelAdmin):
    list_display = ['id','title','discounted_price','category','product_image']

@admin.register(Customer)
class ProductModelAdmin(admin.ModelAdmin):
    list_display = ['id','user','locality','city','county','zipcode']

@admin.register(Cart)
class CartModelAdmin(admin.ModelAdmin):
    list_display = ['id','user','product','quantity']

# @admin.register(Payment)
# class CartModelAdmin(admin.ModelAdmin):
#     list_display = ['id','user','amount','razorpay_order_id','razorpay_payment_status','razorpay_payment_id','paid']

# @admin.register(Payment)
# class PaymentAdmin(admin.ModelAdmin):
#     list_display = ['id', 'user', 'amount', 'mpesa_transaction_id', 'mpesa_payment_status', 'mpesa_payment_reference', 'paid']

# @admin.register(Transaction)
# class TransactionModelAdmin(admin.ModelAdmin):
#     list_display = ['transaction_no', 'phone_number', 'checkout_request_id', 'reference', 'description', 'amount', 'status','receipt_no','created','ip']


@admin.register(OrderPlaced)
class CartModelAdmin(admin.ModelAdmin):
    list_display = ['id','user','customer','product','quantity','ordered_date','status','payment']