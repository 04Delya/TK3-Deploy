"""
URL configuration for pet_clinic project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
<<<<<<< HEAD
    path('auth/', include('authentication.urls')),
    path('', include("main.urls")), 
=======
    path('', include('main.urls')),
    path('', landing_page, name='landing_page'),
    # Direct registration URLs
    path('register/', register_selection, name='register'),
    path('register/individual/', register_individual, name='register_individual'),
    path('register/company/', register_company, name='register_company'),
    path('register/frontdesk/', register_frontdesk, name='register_frontdesk'),
    path('register/vet/', register_vet, name='register_vet'),
    path('register/nurse/', register_nurse, name='register_nurse'),
>>>>>>> 1a23d5c80fdb0c6306be05e49937d1384efb1b6f
    # App URLs
    path('jenis-hewan/', include('JenisHewan.urls', namespace='jenis')),
    path('hewan/', include('HewanPeliharaan.urls', namespace='hewan')),
    path('hijau/', include('hijau.urls')),
    path('vaccinations/', include('vaccinations.urls')), 
    path('vaccines/', include('vaccines.urls')), 
    path("client-pet/", include("client_pet.urls")),
    path('biru/', include('biru.urls')),
    path("main/", include("main.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)