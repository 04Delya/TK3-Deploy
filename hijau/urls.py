from django.urls import path
from . import views

app_name = 'hijau'

urlpatterns = [

    # === TREATMENT ===
    path('treatment/create/', views.create_treatment_view, name='create_treatment'),
    path(
        'treatment/update/<uuid:id_kunjungan>/<str:nama_hewan>/<str:no_identitas_klien>/<str:no_front_desk>/<str:no_perawat_hewan>/<str:no_dokter_hewan>/<str:kode_perawatan>/',
        views.update_treatment_view,
        name='update_treatment'
    ),
    path('treatment/update/<uuid:id_kunjungan>/', views.update_treatment_view, name='update_treatment'),
    path('treatment/delete/<uuid:id_kunjungan>/<str:kode_perawatan>/', views.delete_treatment_view, name='delete_treatment'),
    path('treatment/table/', views.table_treatment_view, name='table_treatment'),

    # === KUNJUNGAN ===
    path('kunjungan/create/', views.create_kunjungan_view, name='create_kunjungan'),
    path('kunjungan/update/<uuid:id_kunjungan>/', views.update_kunjungan_view, name='update_kunjungan'),
    path('kunjungan/delete/<uuid:id_kunjungan>/', views.delete_kunjungan_view, name='delete_kunjungan'),
    path('kunjungan/table/', views.table_kunjungan_view, name='table_kunjungan'),

    # === REKAM MEDIS ===
    path('rekammedis/update/<uuid:id_kunjungan>/', views.update_rekammedis_view, name='update_rekammedis'),
    path('rekammedis/notfound/<uuid:id_kunjungan>/', views.notfound_rekammedis_view, name='notfound_rekammedis'),
    path('rekammedis/create/<uuid:id_kunjungan>/', views.create_rekammedis_view, name='create_rekammedis'),
    path('rekammedis/view/<uuid:id_kunjungan>/', views.rekammedis_view, name='rekammedis'),
]
