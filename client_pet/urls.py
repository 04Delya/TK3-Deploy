from django.urls import path
from . import views

app_name = "client_pet"  

urlpatterns = [
    path("", views.client_list, name="list"),
    path("detail/<str:cid>/",   views.client_detail, name="client_detail"),
]