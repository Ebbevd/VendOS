from django.urls import path
from . import views as v

urlpatterns = [
    path('checkout/<int:product_slot>/', v.checkout, name='checkout'),
    path('checkout/check-payment/<str:session_id>', v.check_payment, name='check-payment'),
    path('webhook/', v.stripe_webhook, name='stripe-webhook'),
    path('checkout/success/<str:session_id>', v.payment_success, name='payment_success'),
]