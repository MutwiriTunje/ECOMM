from django.urls import path
from . import views

urlpatterns = [
    path('stk_push/', views.makepayment, name="prompt m-pesa payment"),
    path('express-payment-callback/', views.processingPayment, name="mpesa daraja callback"),
    path('checkPayment/', views.checkPayment, name="check payment"),
]