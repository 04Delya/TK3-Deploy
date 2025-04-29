from django.urls import path
from .views import landing_page, dashboard, update_password, update_profile

urlpatterns = [
    path('', landing_page, name='landing_page'),
    path('dashboard/', dashboard, name="dashboard"),
    path('profile/update/', update_profile, name='update_profile'),
    path('password/update/', update_password, name='update_password'),
]