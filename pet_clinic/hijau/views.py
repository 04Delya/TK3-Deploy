from django.shortcuts import render

def create_treatment_view(request):
    return render(request, 'create_treatment.html')

def update_treatment_view(request):
    return render(request, 'update_treatment.html')

def delete_treatment_view(request):
    return render(request, 'delete_treatment.html')

def table_treatment_view(request):
    return render(request, 'table_treatment.html')
# 
def create_kunjungan_view(request):
    return render(request, 'create_kunjungan.html')

def update_kunjungan_view(request):
    return render(request, 'update_kunjungan.html')

def delete_kunjungan_view(request):
    return render(request, 'delete_kunjungan.html')

def table_kunjungan_view(request):
    return render(request, 'table_kunjungan.html')
# 
def create_rekammedis_view(request):
    return render(request, 'create_rekammedis.html')

def update_rekammedis_view(request):
    return render(request, 'update_rekammedis.html')

def notfound_rekammedis_view(request):
    return render(request, 'notfound_rekammedis.html')

def rekammedis_view(request):
    return render(request, 'rekammedis.html')