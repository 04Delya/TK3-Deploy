from django.urls import path
from . import views

app_name = 'jenis'

urlpatterns = [
    path('', views.jenis_hewan_list, name='JenisHewan_list'),
    path('create/', views.jenis_hewan_create, name='create'),
    path('<str:id>/update/', views.jenis_hewan_update, name='update'),
    path('<str:id>/delete/', views.jenis_hewan_delete, name='delete'),
    path('<str:id>/check-can-delete/', views.check_can_delete_jenis_hewan, name='check_can_delete'),
]