from django.urls import path
from . import views

app_name = 'biru'

urlpatterns = [
    # Create Views
    path('create_medicine/', views.create_medicine_view, name='create_medicine'),
    path('create_prescriptions/', views.create_prescriptions_view, name='create_prescriptions'),
    path('create_treatment/', views.create_treatment_view, name='create_treatment'),

    # Delete Views
    path('delete_medicine/', views.delete_medicine_view, name='delete_medicine'),
    path('delete_prescriptions/', views.delete_prescriptions_view, name='delete_prescriptions'),
    path('delete_treatment/', views.delete_treatment_view, name='delete_treatment'),

    # List Views
    path('list_medicine/', views.list_medicine_view, name='list_medicine'),
    path('list_prescriptions/', views.list_prescriptions_view, name='list_prescriptions'),
    path('list_treatment/', views.list_treatment_view, name='list_treatment'),

    # Update Views
    path('update_medicine/', views.update_medicine_view, name='update_medicine'),
    path('update_treatment/', views.update_treatment_view, name='update_treatment'),
    path('update_stock_medicine/', views.update_stock_medicine_view, name='update_stock_medicine'),
]