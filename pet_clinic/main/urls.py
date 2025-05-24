from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing_page, name='landing_page'),
    path('login/', views.login, name='login'),
    path('profile/update/', views.update_profile, name='update_profile'),
    path('password/update/', views.update_password, name='update_password'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/klien/', views.dashboard_klien, name='dashboard_klien'),
    path('dashboard/fdo/', views.dashboard_frontdesk, name='dashboard_frontdesk'),
    path('dashboard/dokter/', views.dashboard_dokterhewan, name='dashboard_dokterhewan'),
    path('dashboard/perawat/', views.dashboard_perawat, name='dashboard_perawat'),
]
