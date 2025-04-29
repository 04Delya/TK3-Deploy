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
