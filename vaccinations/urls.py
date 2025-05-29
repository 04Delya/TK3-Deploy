from django.urls import path
from . import views

app_name = 'vaccinations'

urlpatterns = [
    path('', views.vaccination_list, name='vaccination_list'),
    path('create/', views.vaccination_create, name='vaccination_create'),
    path('update/<uuid:no>/', views.vaccination_update, name='vaccination_update'),
    path('delete/<uuid:no>/', views.vaccination_delete, name='vaccination_delete'),
    path('history/', views.vaccination_history, name='vaccination_history'),

]