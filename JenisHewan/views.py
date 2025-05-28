from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .models import JenisHewan

# Create your views here.
# Jenis Hewan views
def jenis_hewan_list(request):
    user_role = request.GET.get('role', 'frontdesk')  # Default to frontdesk
    jenis_hewan = JenisHewan.objects.all()
    
    context = {
        'jenis_hewan': jenis_hewan,
        'is_frontdesk': user_role == 'frontdesk',
        'user_role': user_role
    }
    return render(request, 'JenisHewan_list.html', context)

def jenis_hewan_create(request):
    if request.method == 'POST':
        nama = request.POST.get('nama')
        if nama:
            JenisHewan.objects.create(nama=nama)
            return redirect('jenis:JenisHewan_list')
    return render(request, 'JenisHewan_create.html')

def jenis_hewan_update(request, id):
    jenis_hewan = get_object_or_404(JenisHewan, id=id)
    
    if request.method == 'POST':
        nama = request.POST.get('nama')
        if nama:
            jenis_hewan.nama = nama
            jenis_hewan.save()
            return redirect('jenis:JenisHewan_list')
    
    context = {'jenis_hewan': jenis_hewan}
    return render(request, 'JenisHewan_update.html', context)

def jenis_hewan_delete(request, id):
    jenis_hewan = get_object_or_404(JenisHewan, id=id)
    
    if request.method == 'POST':
        jenis_hewan.delete()
        return redirect('jenis:JenisHewan_list')
    
    context = {'jenis_hewan': jenis_hewan}
    return render(request, 'JenisHewan_delete_confirm.html', context)

def check_can_delete_jenis_hewan(request, id):
    # Check if any pets are using this animal type
    jenis_hewan = get_object_or_404(JenisHewan, id=id)
    can_delete = not jenis_hewan.hewan_set.exists()
    return JsonResponse({'can_delete': can_delete})
