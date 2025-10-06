from django.urls import path
from . import views as v

urlpatterns = [
    path('test-motors/', v.test_motors_page, name='test_motors'),
    path("activate-motor-test/<int:motor_id>/", v.test_motor, name="activate_motor"),
    path("test-landing-page", v.test_landiong_page, name="test_landing_page"),
    path("payment-info/<int:test_mode>/", v.show_payment_info, name="payment_info"),
]
