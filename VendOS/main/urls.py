from django.urls import path
from . import views as v

urlpatterns = [
    path('', v.splash_screen_view, name='splash_screen'),
    path('order', v.order_screen_view, name='order_screen'),
    path('order/confirm', v.order_package, name='order_package'),
]