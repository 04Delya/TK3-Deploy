from django.urls import path
from . import views

app_name = 'biru'

urlpatterns = [
    # Create Views
    path('create_medicine/', views.create_medicine_view, name='create_medicine'),
    path('create_prescriptions/', views.create_prescriptions_view, name='create_prescriptions'),
    path('create_treatment_type/', views.create_treatment_view, name='create_treatment_type'),

    # Delete Views (delete_prescriptions butuh param index)
    path('delete_medicine/<str:kode>/', views.delete_medicine_view, name='delete_medicine'),
    path('delete_prescriptions/<int:index>/', views.delete_prescriptions_view, name='delete_prescriptions'),

    path('delete_treatment_type/<str:kode_perawatan>/', views.delete_treatment_view, name='delete_treatment_type'),

    # List Views
    path('list_medicine/', views.list_medicine_view, name='list_medicine'),
    path('list_prescriptions/', views.list_prescriptions_view, name='list_prescriptions'),
    path('list_treatment_type/', views.list_treatment_view, name='list_treatment_type'),

    # Update Views
    path('update_medicine/<str:kode>/', views.update_medicine_view, name='update_medicine'),
    path('update_treatment_type/<str:kode_perawatan>/', views.update_treatment_view, name='update_treatment_type'),
    path('update_stock_medicine/<str:kode>/', views.update_stock_medicine_view, name='update_stock_medicine'),
]
