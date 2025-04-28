from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing_page, name='landing_page'),
    path('register/', views.register_selection, name='register'),
    path('register/individual/', views.register_individual, name='register_individual'),
    path('register/company/', views.register_company, name='register_company'),
    path('register/frontdesk/', views.register_frontdesk, name='register_frontdesk'),
    path('register/vet/', views.register_vet, name='register_vet'),
    path('register/nurse/', views.register_nurse, name='register_nurse'),
] 