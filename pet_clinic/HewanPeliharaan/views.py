from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .models import Hewan
from JenisHewan.models import JenisHewan
from Pengguna.models import Klien
from django.contrib import messages

# Hewan (Pet) views
def hewan_list(request):
    user_role = request.GET.get('role', 'klien')  # Default to klien
    klien_id = request.GET.get('klien_id')  # Would normally come from auth
    
    if user_role == 'frontdesk':
        hewan_list = Hewan.objects.all()
    else:
        if not klien_id:
            return render(request, 'HewanPeliharaan_list.html', {'hewan_list': []})
        hewan_list = Hewan.objects.filter(pemilik_id=klien_id)
    
    for hewan in hewan_list:
        hewan.can_delete = not hewan.kunjungan.filter(aktif=True).exists()
    
    context = {
        'hewan_list': hewan_list,
        'is_frontdesk': user_role == 'frontdesk',
        'user_role': user_role
    }
    return render(request, 'HewanPeliharaan_list.html', context)

def hewan_create(request):
    user_role = request.GET.get('role', 'klien')
    klien_id_from_get = request.GET.get('klien_id')

    jenis_hewan_list = JenisHewan.objects.all()
    klien_list_for_frontdesk = Klien.objects.all() if user_role == 'frontdesk' else None

    form_data = {} 

    if request.method == 'POST':
        nama = request.POST.get('nama')
        tanggal_lahir = request.POST.get('tanggal_lahir')
        jenis_hewan_id = request.POST.get('jenis_hewan')
        foto_url = request.POST.get('foto_url')

        # Store POST data for re-rendering in case of error
        form_data = request.POST.copy()

        pemilik_id = None
        if user_role == 'frontdesk':
            pemilik_id = request.POST.get('pemilik')
        else:
            pemilik_id = klien_id_from_get

        if nama and tanggal_lahir and jenis_hewan_id and pemilik_id:
            try:
                Hewan.objects.create(
                    nama=nama,
                    tanggal_lahir=tanggal_lahir,
                    jenis_hewan_id=jenis_hewan_id,
                    pemilik_id=pemilik_id,
                    foto_url=foto_url if foto_url else None
                )
                messages.success(request, 'Hewan peliharaan berhasil ditambahkan.')
                
                redirect_url = 'hewan:HewanPeliharaan_list'
                query_params = []
                if user_role:
                    query_params.append(f"role={user_role}")
                if klien_id_from_get and user_role != 'frontdesk': 
                    query_params.append(f"klien_id={klien_id_from_get}")
                
                if query_params:
                    return redirect(f"{redirect(redirect_url).url}?{'&'.join(query_params)}")
                else:
                    return redirect(redirect_url)

            except Exception as e:
                messages.error(request, f'Gagal menambahkan hewan: {str(e)}')
        else:
            error_messages_list = []
            if not nama:
                error_messages_list.append("Nama hewan harus diisi.")
            if not tanggal_lahir:
                error_messages_list.append("Tanggal lahir harus diisi.")
            if not jenis_hewan_id:
                error_messages_list.append("Jenis hewan harus dipilih.")
            if not pemilik_id:
                if user_role == 'frontdesk':
                    error_messages_list.append("Pemilik harus dipilih.")
                else: # klien role
                    error_messages_list.append("Informasi pemilik (klien_id) tidak ditemukan di URL. Tidak dapat menambahkan hewan.")
            
            if error_messages_list:
                messages.error(request, " ".join(error_messages_list))
            else:
               
                messages.error(request, 'Gagal menambahkan hewan. Mohon periksa kembali data yang Anda masukkan.')

    context = {
        'jenis_hewan': jenis_hewan_list,
        'klien_list': klien_list_for_frontdesk,
        'is_frontdesk': user_role == 'frontdesk',
        'form_data': form_data,
        'user_role': user_role,
        'klien_id': klien_id_from_get
    }
    return render(request, 'HewanPeliharaan_create.html', context)

def hewan_update(request, id):
    user_role = request.GET.get('role', 'klien')
    klien_id = request.GET.get('klien_id')
    
    hewan = get_object_or_404(Hewan, id=id)
    
    if user_role != 'frontdesk' and str(hewan.pemilik.id) != klien_id:
        return redirect('hewan:HewanPeliharaan_list')
    
    if request.method == 'POST':
        nama = request.POST.get('nama')
        tanggal_lahir = request.POST.get('tanggal_lahir')
        jenis_hewan_id = request.POST.get('jenis_hewan')
        foto_url = request.POST.get('foto_url')
        
        if user_role == 'frontdesk':
            pemilik_id = request.POST.get('pemilik')
            if pemilik_id:
                hewan.pemilik_id = pemilik_id
        
        if nama:
            hewan.nama = nama
        if tanggal_lahir:
            hewan.tanggal_lahir = tanggal_lahir
        if jenis_hewan_id:
            hewan.jenis_hewan_id = jenis_hewan_id
        
        hewan.foto_url = foto_url if foto_url else None
        hewan.save()
        return redirect('hewan:HewanPeliharaan_list')
    
    jenis_hewan = JenisHewan.objects.all()
    klien_list = Klien.objects.all() if user_role == 'frontdesk' else None
    
    context = {
        'hewan': hewan,
        'jenis_hewan': jenis_hewan,
        'klien_list': klien_list,
        'is_frontdesk': user_role == 'frontdesk'
    }
    return render(request, 'HewanPeliharaan_update.html', context)

def hewan_delete(request, id):
    user_role = request.GET.get('role', 'klien')
    
    if user_role != 'frontdesk':
        return redirect('hewan:HewanPeliharaan_list')
    
    hewan = get_object_or_404(Hewan, id=id)
    
    if hewan.kunjungan.filter(aktif=True).exists():
        return JsonResponse({'error': 'Cannot delete pet with active visits'}, status=400)
    
    if request.method == 'POST':
        hewan.delete()
        return redirect('hewan:HewanPeliharaan_list')
    
    context = {
        'hewan': hewan,
    }
    return render(request, 'HewanPeliharaan_delete_confirm.html', context)

def check_can_delete_hewan(request, id):
    hewan = get_object_or_404(Hewan, id=id)
    can_delete = not hewan.kunjungan.filter(aktif=True).exists()
    return JsonResponse({'can_delete': can_delete})
