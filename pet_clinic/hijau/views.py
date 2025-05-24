from django.shortcuts import render
from django.http import HttpResponse

# Treatment views
def create_treatment_view(request):
    return render(request, 'create_treatment.html')

def update_treatment_view(request):
    return render(request, 'update_treatment.html')

def delete_treatment_view(request):
    return render(request, 'delete_treatment.html')

def table_treatment_view(request):
    return render(request, 'table_treatment.html')

def treatment_views(request, action):
    if action == 'create':
        return render(request, 'create_treatment.html')
    elif action == 'update':
        return render(request, 'update_treatment.html')
    elif action == 'delete':
        return render(request, 'delete_treatment.html')
    else:
        return HttpResponse('Invalid action')

# Kunjungan views
def create_kunjungan_view(request):
    return render(request, 'create_kunjungan.html')

def update_kunjungan_view(request):
    return render(request, 'update_kunjungan.html')

def delete_kunjungan_view(request):
    return render(request, 'delete_kunjungan.html')

def table_kunjungan_view(request):
    return render(request, 'table_kunjungan.html')

def kunjungan_views(request, action):
    if action == 'create':
        return render(request, 'create_kunjungan.html')
    elif action == 'update':
        return render(request, 'update_kunjungan.html')
    elif action == 'delete':
        return render(request, 'delete_kunjungan.html')
    else:
        return HttpResponse('Invalid action')

# Rekam Medis views
def create_rekammedis_view(request):
    return render(request, 'create_rekammedis.html')

def update_rekammedis_view(request):
    return render(request, 'update_rekammedis.html')

def notfound_rekammedis_view(request):
    return render(request, 'notfound_rekammedis.html')

def rekammedis_view(request):
    return render(request, 'rekammedis.html')
