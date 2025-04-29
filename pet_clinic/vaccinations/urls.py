from django.urls import path
from . import views

urlpatterns = [
    path('', views.vaccination_list, name='vaccination_list'),
    path('create/', views.vaccination_create, name='vaccination_create'),
    path('update/', views.vaccination_update, name='vaccination_update'), 
]