from django.urls import path
from .views import landing_page

urlpatterns = [
    path('', views.landing_page, name='landing_page'),
    path('register/', views.register_selection, name='register'),
    path('register/individual/', views.register_individual, name='register_individual'),
    path('register/company/', views.register_company, name='register_company'),
    path('register/frontdesk/', views.register_frontdesk, name='register_frontdesk'),
    path('register/vet/', views.register_vet, name='register_vet'),
    path('register/nurse/', views.register_nurse, name='register_nurse'),
    
    # Jenis Hewan URLs
    path('jenis-hewan/', views.jenis_hewan_list, name='jenis_hewan_list'),
    path('jenis-hewan/create/', views.jenis_hewan_create, name='jenis_hewan_create'),
    path('jenis-hewan/<uuid:id>/update/', views.jenis_hewan_update, name='jenis_hewan_update'),
    path('jenis-hewan/<uuid:id>/delete/', views.jenis_hewan_delete, name='jenis_hewan_delete'),
    path('jenis-hewan/<uuid:id>/check-can-delete/', views.check_can_delete_jenis_hewan, name='check_can_delete_jenis_hewan'),
]