from django.urls import path
from . import views as v

urlpatterns = [
    path('update-status/', v.update_status, name='update_status'),
    path('get-status/', v.get_status, name='get_status'),
    path('get-stock/', v.get_storage_status, name='get_status'),
]
