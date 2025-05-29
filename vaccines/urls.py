from django.urls import path
from . import views

urlpatterns = [
    path('', views.vaccine_list, name='vaccine_list'),
    path('create/', views.vaccine_create, name='vaccine_create'),
    path('update/<str:kode>/', views.vaccine_update, name='vaccine_update'),
    path('update-stock/<str:kode>/', views.vaccine_update_stock, name='vaccine_update_stock'),
    path('delete/<str:kode>/', views.vaccine_delete, name='vaccine_delete'),
]
