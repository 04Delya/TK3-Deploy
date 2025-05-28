from django.urls import path
from django.shortcuts import redirect
from . import views

def redirect_to_main_landing(request):
    return redirect('landing_page')

app_name = 'authentication'

urlpatterns = [
    path('', redirect_to_main_landing),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_selection, name='register'),
    path('register/individual/', views.register_individual, name='register_individual'),
    path('register/company/', views.register_company, name='register_company'),
    path('register/frontdesk/', views.register_frontdesk, name='register_frontdesk'),
    path('register/vet/', views.register_vet, name='register_vet'),
    path('register/nurse/', views.register_nurse, name='register_nurse'),
]