from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from main.models import Hewan, JenisHewan, Klien  # Use main models that connect to Supabase
from django.contrib import messages

# Hewan (Pet) views
def hewan_list(request):
    user_role = request.GET.get('role', 'frontdesk')  # Default to frontdesk to show all data
    klien_id = request.GET.get('klien_id')
    
    # Use the main models which contain the Supabase data
    if user_role == 'frontdesk':
        # Show all pets for frontdesk - get all data from main.models.Hewan
        hewan_list = Hewan.objects.all()[:50]  # Limit to first 50 for performance
    else:
        # Show pets for specific client
        if not klien_id:
            hewan_list = []
        else:
            hewan_list = Hewan.objects.filter(no_identitas_klien=klien_id)
    
    # Create objects that match template expectations
    formatted_hewan_list = []
    for hewan in hewan_list:
        # Get animal type
        try:
            jenis_hewan = JenisHewan.objects.get(id=hewan.id_jenis)
            jenis_nama = jenis_hewan.nama_jenis
        except:
            jenis_nama = "Unknown"
        
        # Get owner info
        try:
            klien = Klien.objects.get(no_identitas=hewan.no_identitas_klien)
            # Try to get individual info first
            try:
                from main.models import Individu
                individu = Individu.objects.get(no_identitas_klien=hewan.no_identitas_klien)
                pemilik_nama = f"{individu.nama_depan} {individu.nama_belakang}"
            except:
                # Try company info
                try:
                    from main.models import Perusahaan
                    perusahaan = Perusahaan.objects.get(no_identitas_klien=hewan.no_identitas_klien)
                    pemilik_nama = perusahaan.nama_perusahaan
                except:
                    pemilik_nama = "Unknown Owner"
        except:
            pemilik_nama = "Unknown Owner"
        
        # Create object that matches template expectations
        formatted_hewan = type('HewanObj', (), {
            'id': f"{hewan.nama}_{hewan.no_identitas_klien}",  # Composite key
            'nama': hewan.nama,
            'tanggal_lahir': hewan.tanggal_lahir,
            'jenis_hewan': type('JenisObj', (), {'nama': jenis_nama})(),
            'pemilik': type('PemilikObj', (), {'nama': pemilik_nama})(),
            'can_delete': True,  # Simplified for now
            'url_foto': hewan.url_foto
        })()
        formatted_hewan_list.append(formatted_hewan)
    
    context = {
        'hewan_list': formatted_hewan_list,
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
        foto_url = request.POST.get('foto_url')        # Store POST data for re-rendering in case of error
        form_data = request.POST.copy()
        pemilik_id = None
        if user_role == 'frontdesk':
            pemilik_id = request.POST.get('pemilik')
        else:
            pemilik_id = klien_id_from_get

        if nama and tanggal_lahir and jenis_hewan_id and pemilik_id:
            try:
                # Note: The main.models.Hewan is unmanaged, so we can't easily create through Django ORM
                messages.error(request, 'Creation through this interface is not supported for Supabase data. Please use the Supabase interface.')
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
    
    # Parse composite ID to get hewan name and klien id
    try:
        parts = id.split('_', 1)
        hewan_nama = parts[0]
        hewan_klien_id = parts[1]
        hewan = Hewan.objects.get(nama=hewan_nama, no_identitas_klien=hewan_klien_id)
    except:
        messages.error(request, 'Hewan tidak ditemukan.')
        return redirect('hewan:HewanPeliharaan_list')
    
    # Check permissions
    if user_role != 'frontdesk' and hewan_klien_id != klien_id:
        return redirect('hewan:HewanPeliharaan_list')
    
    if request.method == 'POST':
        # Note: Since this is an unmanaged model pointing to Supabase, 
        # we can't easily update through Django ORM
        messages.error(request, 'Update through this interface is not supported for Supabase data. Please use the Supabase interface.')
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
    
    # Parse composite ID to get hewan name and klien id
    try:
        parts = id.split('_', 1)
        hewan_nama = parts[0]
        hewan_klien_id = parts[1]
        hewan = Hewan.objects.get(nama=hewan_nama, no_identitas_klien=hewan_klien_id)
    except:
        messages.error(request, 'Hewan tidak ditemukan.')
        return redirect('hewan:HewanPeliharaan_list')
    
    if request.method == 'POST':
        # Note: Since this is an unmanaged model pointing to Supabase, 
        # we can't easily delete through Django ORM
        messages.error(request, 'Delete through this interface is not supported for Supabase data. Please use the Supabase interface.')
        return redirect('hewan:HewanPeliharaan_list')
    
    context = {
        'hewan': hewan,
    }
    return render(request, 'HewanPeliharaan_delete_confirm.html', context)

def check_can_delete_hewan(request, id):
    # Parse composite ID to get hewan name and klien id
    try:
        parts = id.split('_', 1)
        hewan_nama = parts[0]
        hewan_klien_id = parts[1]
        hewan = Hewan.objects.get(nama=hewan_nama, no_identitas_klien=hewan_klien_id)
        # For now, return false since deletion is not supported through this interface
        can_delete = False
    except:
        can_delete = False
    return JsonResponse({'can_delete': can_delete})
