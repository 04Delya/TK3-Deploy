from django.urls import path
from . import views

app_name = 'jenis'

urlpatterns = [
    path('', views.jenis_hewan_list, name='JenisHewan_list'),
    path('create/', views.jenis_hewan_create, name='create'),
    path('<uuid:id>/update/', views.jenis_hewan_update, name='update'),
    path('<uuid:id>/delete/', views.jenis_hewan_delete, name='delete'),
    path('<uuid:id>/check-can-delete/', views.check_can_delete_jenis_hewan, name='check_can_delete'),
]