from django.urls import path
from . import views

app_name = 'hewan'

urlpatterns = [
    path('', views.hewan_list, name='HewanPeliharaan_list'),
    path('create/', views.hewan_create, name='create'),
    path('<uuid:id>/update/', views.hewan_update, name='update'),
    path('<uuid:id>/delete/', views.hewan_delete, name='delete'),
    path('<uuid:id>/check-can-delete/', views.check_can_delete_hewan, name='check_can_delete'),
]