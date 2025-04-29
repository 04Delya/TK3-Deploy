from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.http import JsonResponse
from .models import JenisHewan

# Create your views here.

def landing_page(request):
    return render(request, 'main/landing_page.html')

def register_selection(request):
    return render(request, 'registration/register.html')

def register_individual(request):
    return render(request, 'registration/register_individual.html')

def register_company(request):
    return render(request, 'registration/register_company.html')

def register_frontdesk(request):
    return render(request, 'registration/register_frontdesk.html')

def register_vet(request):
    return render(request, 'registration/register_vet.html')

def register_nurse(request):
    return render(request, 'registration/register_nurse.html')

# Jenis Hewan views
def jenis_hewan_list(request):
    # In a real app, you would check the user role here
    # For demonstration, we'll use a query parameter
    user_role = request.GET.get('role', 'frontdesk')  # Default to frontdesk
    jenis_hewan = JenisHewan.objects.all()
    
    context = {
        'jenis_hewan': jenis_hewan,
        'is_frontdesk': user_role == 'frontdesk',
        'user_role': user_role
    }
    return render(request, 'main/jenis_hewan/list.html', context)

def jenis_hewan_create(request):
    if request.method == 'POST':
        nama = request.POST.get('nama')
        if nama:
            JenisHewan.objects.create(nama=nama)
            return redirect('jenis_hewan_list')
    return render(request, 'main/jenis_hewan/create.html')

def jenis_hewan_update(request, id):
    jenis_hewan = get_object_or_404(JenisHewan, id=id)
    
    if request.method == 'POST':
        nama = request.POST.get('nama')
        if nama:
            jenis_hewan.nama = nama
            jenis_hewan.save()
            return redirect('jenis_hewan_list')
    
    context = {'jenis_hewan': jenis_hewan}
    return render(request, 'main/jenis_hewan/update.html', context)

def jenis_hewan_delete(request, id):
    jenis_hewan = get_object_or_404(JenisHewan, id=id)
    
    if request.method == 'POST':
        jenis_hewan.delete()
        return redirect('jenis_hewan_list')
    
    context = {'jenis_hewan': jenis_hewan}
    return render(request, 'main/jenis_hewan/delete_confirm.html', context)

def check_can_delete_jenis_hewan(request, id):
    # In a real implementation, you would check if any pets use this type
    # For now, we'll just return a placeholder response
    # Assume no pets are using this type for demonstration
    can_delete = True
    return JsonResponse({'can_delete': can_delete})
