from django.urls import path
from . import views as v

urlpatterns = [
    path('', v.splash_screen_view, name='splash_screen'),
]