from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('authentication.urls')),
    path('', include("main.urls")), 
    # App URLs
    path('jenis-hewan/', include('JenisHewan.urls', namespace='jenis')),
    path('hewan/', include('HewanPeliharaan.urls', namespace='hewan')),
    path('hijau/', include(('hijau.urls', 'hijau'), namespace='hijau')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('vaccinations/', include('vaccinations.urls', namespace='vaccinations')),
    path('vaccines/', include('vaccines.urls')), 
    path("client-pet/", include("client_pet.urls")),
    path('biru/', include('biru.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
