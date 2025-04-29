from django.urls import path
from . import views

app_name = 'hijau'

urlpatterns = [
    path('treatment/create/', views.create_treatment_view, name='create_treatment'),
    path('treatment/update/', views.update_treatment_view, name='update_treatment'),
    path('treatment/delete/', views.delete_treatment_view, name='delete_treatment'),
    path('treatment/table/', views.table_treatment_view, name='table_treatment'),
    
    path('kunjungan/create/', views.create_kunjungan_view, name='create_kunjungan'),
    path('kunjungan/update/', views.update_kunjungan_view, name='update_kunjungan'),
    path('kunjungan/delete/', views.delete_kunjungan_view, name='delete_kunjungan'),
    path('kunjungan/table/', views.table_kunjungan_view, name='table_kunjungan'),

     path('rekammedis/create/', views.create_rekammedis_view, name='create_rekammedis'),
    path('rekammedis/update/', views.update_rekammedis_view, name='update_rekammedis'),
    path('rekammedis/notfound/', views.notfound_rekammedis_view, name='notfound_rekammedis'),
    path('rekammedis/view/', views.rekammedis_view, name='rekammedis'),
]
# buat push main