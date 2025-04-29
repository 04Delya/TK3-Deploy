from django.shortcuts import render

def create_treatment_view(request):
    return render(request, 'create_treatment.html')

def update_treatment_view(request):
    return render(request, 'update_treatment.html')

def delete_treatment_view(request):
    return render(request, 'delete_treatment.html')

def create_kunjungan_view(request):
    return render(request, 'create_kunjungan.html')

def update_kunjungan_view(request):
    return render(request, 'update_kunjungan.html')

def delete_kunjungan_view(request):
    return render(request, 'delete_kunjungan.html')
from django.shortcuts import render
from django.http import HttpResponse

def treatment_views(request, action):
    if action == 'create':
        return render(request, 'create_treatment.html')
    elif action == 'update':
        return render(request, 'update_treatment.html')
    elif action == 'delete':
        return render(request, 'delete_treatment.html')
    else:
        return HttpResponse('Invalid action')

def kunjungan_views(request, action):
    if action == 'create':
        return render(request, 'create_kunjungan.html')
    elif action == 'update':
        return render(request, 'update_kunjungan.html')
    elif action == 'delete':
        return render(request, 'delete_kunjungan.html')
    else:
        return HttpResponse('Invalid action')