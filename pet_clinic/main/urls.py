from django.urls import path
from .views import landing_page, update_password, update_profile, dashboard_klien, dashboard_frontdesk, dashboard_dokterhewan, dashboard_perawat

urlpatterns = [
    path('', landing_page, name='landing_page'),
    path('profile/update/', update_profile, name='update_profile'),
    path('password/update/', update_password, name='update_password'),
    path('dashboard/klien/', dashboard_klien, name='dashboard_klien'),
    path('dashboard/fdo/', dashboard_frontdesk, name='dashboard_frontdesk'),
    path('dashboard/dokter/', dashboard_dokterhewan, name='dashboard_dokterhewan'),
    path('dashboard/perawat/', dashboard_perawat, name='dashboard_perawat'),
]