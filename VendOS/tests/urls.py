from django.urls import path
from . import views as v

urlpatterns = [
    path('test-motors/', v.test_motors_page, name='test_motors'),
    path("activate-motor-test/<int:motor_id>/", v.test_motor, name="activate_motor"),
]
