from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from main.models import Hewan, JenisHewan, Klien  # Use main models that connect to Supabase
from django.contrib import messages
from django.db import connection
from django.urls import reverse
import uuid

# Hewan (Pet) views
def hewan_list(request):
    user_role = request.GET.get('role', 'frontdesk')  # Default to frontdesk to show all data
    klien_id = request.GET.get('klien_id')
    
    # Debug: Print session information
    print(f"Session data: {dict(request.session)}")
    print(f"GET role: {user_role}, GET klien_id: {klien_id}")
    
    # Only check session if no explicit role is provided in GET params
    if 'role' not in request.GET:
        session_role = request.session.get('role')
        if session_role in ['individu', 'perusahaan']:
            user_role = session_role
            # If switching to client role, get klien_id from session
            klien_id = request.session.get('klien_id')
    
    # If user is klien and no klien_id in URL, get it from session
    if user_role in ['klien', 'individu', 'perusahaan'] and not klien_id:
        klien_id = request.session.get('klien_id')
    
    print(f"Final: user_role={user_role}, klien_id={klien_id}")
      # Use raw SQL to fetch data from Supabase
    formatted_hewan_list = []
    
    with connection.cursor() as cursor:
        if user_role == 'frontdesk':
            # Fetch all animals with their jenis and owner info
            cursor.execute("""
                SELECT h.nama, h.no_identitas_klien, h.tanggal_lahir, h.id_jenis, h.url_foto,
                       jh.nama_jenis,
                       COALESCE(i.nama_depan || ' ' || i.nama_belakang, p.nama_perusahaan) as pemilik_nama
                FROM pet_clinic."HEWAN" h
                LEFT JOIN pet_clinic."JENIS_HEWAN" jh ON h.id_jenis = jh.id
                LEFT JOIN pet_clinic."INDIVIDU" i ON h.no_identitas_klien = i.no_identitas_klien
                LEFT JOIN pet_clinic."PERUSAHAAN" p ON h.no_identitas_klien = p.no_identitas_klien
                ORDER BY h.nama
                LIMIT 50
            """)
        else:
            # Fetch animals for specific client
            cursor.execute("""
                SELECT h.nama, h.no_identitas_klien, h.tanggal_lahir, h.id_jenis, h.url_foto,
                       jh.nama_jenis,
                       COALESCE(i.nama_depan || ' ' || i.nama_belakang, p.nama_perusahaan) as pemilik_nama
                FROM pet_clinic."HEWAN" h
                LEFT JOIN pet_clinic."JENIS_HEWAN" jh ON h.id_jenis = jh.id
                LEFT JOIN pet_clinic."INDIVIDU" i ON h.no_identitas_klien = i.no_identitas_klien
                LEFT JOIN pet_clinic."PERUSAHAAN" p ON h.no_identitas_klien = p.no_identitas_klien
                WHERE h.no_identitas_klien = %s
                ORDER BY h.nama
            """, [klien_id])
        
        rows = cursor.fetchall()
        
        for row in rows:
            nama, no_identitas_klien, tanggal_lahir, id_jenis, url_foto, jenis_nama, pemilik_nama = row
            # Wrap for template
            formatted_hewan_list.append(type('HewanObj', (), {
                'id': f"{nama}_{no_identitas_klien}",
                'nama': nama,
                'tanggal_lahir': tanggal_lahir,
                'jenis_hewan': type('JenisObj', (), {'nama': jenis_nama or 'Unknown'})(),
                'pemilik': type('PemilikObj', (), {'nama': pemilik_nama or 'Unknown Owner'})(),
                'can_delete': True,
                'url_foto': url_foto or ''
            })())
    context = {
        'hewan_list': formatted_hewan_list,
        'is_frontdesk': user_role == 'frontdesk',
        'user_role': user_role,
        'klien_id': klien_id
    }
    return render(request, 'HewanPeliharaan_list.html', context)

def hewan_create(request):
    user_role = request.GET.get('role', 'klien')
    klien_id_from_get = request.GET.get('klien_id')
    
    # If user is klien and no klien_id in URL, get it from session
    if user_role in ['klien', 'individu', 'perusahaan'] and not klien_id_from_get:
        klien_id_from_get = request.session.get('klien_id')
    
    # If still no klien_id and role suggests it's a client, try to get from session
    if not klien_id_from_get and request.session.get('role') in ['individu', 'perusahaan']:
        klien_id_from_get = request.session.get('klien_id')
        user_role = request.session.get('role', 'klien')

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
                # Check if animal name already exists for this owner
                existing_hewan = Hewan.objects.filter(nama=nama, no_identitas_klien=pemilik_id).first()
                if existing_hewan:
                    messages.error(request, f'Hewan dengan nama "{nama}" sudah ada untuk pemilik ini.')
                else:
                    # Use raw SQL to insert into Supabase
                    with connection.cursor() as cursor:
                        cursor.execute(
                            'INSERT INTO pet_clinic."HEWAN" (nama, no_identitas_klien, tanggal_lahir, id_jenis, url_foto) VALUES (%s, %s, %s, %s, %s)',
                            [nama, str(pemilik_id), tanggal_lahir, str(jenis_hewan_id), foto_url or '']
                        )
                    # Ensure transaction is committed
                    connection.commit()
                    messages.success(request, f'Hewan "{nama}" berhasil ditambahkan!')
                    if user_role == 'frontdesk':
                        return redirect('hewan:HewanPeliharaan_list')
                    else:
                        from django.urls import reverse
                        redirect_url = reverse('hewan:HewanPeliharaan_list') + f"?role={user_role}&klien_id={pemilik_id}"
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
        nama = request.POST.get('nama')
        tanggal_lahir = request.POST.get('tanggal_lahir')
        jenis_hewan_id = request.POST.get('jenis_hewan')
        foto_url = request.POST.get('foto_url')
        pemilik_id = request.POST.get('pemilik') if user_role == 'frontdesk' else hewan_klien_id
        
        if nama and tanggal_lahir and jenis_hewan_id and pemilik_id:
            try:                # Check if new name conflicts with existing animals for this owner (except current animal)
                conflict_check_passed = True
                if not (nama == hewan_nama and pemilik_id == hewan_klien_id):
                    with connection.cursor() as cursor:
                        cursor.execute(
                            'SELECT COUNT(*) FROM pet_clinic."HEWAN" WHERE nama = %s AND no_identitas_klien = %s',
                            [nama, str(pemilik_id)]
                        )
                        if cursor.fetchone()[0] > 0:
                            conflict_check_passed = False
                            messages.error(request, f'Hewan dengan nama "{nama}" sudah ada untuk pemilik ini.')
                
                if conflict_check_passed:
                    # Use raw SQL to update in Supabase
                    with connection.cursor() as cursor:
                        if nama == hewan_nama and pemilik_id == hewan_klien_id:
                            # Simple update - same name and owner
                            cursor.execute(
                                'UPDATE pet_clinic."HEWAN" SET tanggal_lahir = %s, id_jenis = %s, url_foto = %s WHERE nama = %s AND no_identitas_klien = %s',
                                [tanggal_lahir, str(jenis_hewan_id), foto_url or '', hewan_nama, str(hewan_klien_id)]
                            )
                        else:
                            # Name or owner changed - need to delete old and insert new
                            cursor.execute(
                                'DELETE FROM pet_clinic."HEWAN" WHERE nama = %s AND no_identitas_klien = %s',
                                [hewan_nama, str(hewan_klien_id)]
                            )
                            cursor.execute(
                                'INSERT INTO pet_clinic."HEWAN" (nama, no_identitas_klien, tanggal_lahir, id_jenis, url_foto) VALUES (%s, %s, %s, %s, %s)',
                                [nama, str(pemilik_id), tanggal_lahir, str(jenis_hewan_id), foto_url or '']
                            )
                    
                    messages.success(request, f'Hewan berhasil diupdate!')
                    if user_role == 'frontdesk':
                        return redirect('hewan:HewanPeliharaan_list')
                    else:
                        redirect_url = reverse('hewan:HewanPeliharaan_list') + f"?role={user_role}&klien_id={pemilik_id}"
                        return redirect(redirect_url)
                    
            except Exception as e:
                messages.error(request, f'Gagal mengupdate hewan: {str(e)}')
        else:
            messages.error(request, 'Semua field wajib harus diisi.')
    
    jenis_hewan = JenisHewan.objects.all()
    klien_list = Klien.objects.all() if user_role == 'frontdesk' else None
    
    # Create wrapped hewan for template
    try:
        jenis = JenisHewan.objects.get(id=hewan.id_jenis)
        jenis_nama = jenis.nama_jenis
    except JenisHewan.DoesNotExist:
        jenis_nama = 'Unknown'
    try:
        from main.models import Individu, Perusahaan
        try:
            individu = Individu.objects.get(no_identitas_klien=hewan.no_identitas_klien)
            pemilik_nama = f"{individu.nama_depan} {individu.nama_belakang}"
        except Individu.DoesNotExist:
            perusahaan = Perusahaan.objects.get(no_identitas_klien=hewan.no_identitas_klien)
            pemilik_nama = perusahaan.nama_perusahaan
    except:
        pemilik_nama = 'Unknown Owner'
    hewan_wrapped = type('HewanObj', (), {
        'id': f"{hewan.nama}_{hewan.no_identitas_klien}",
        'nama': hewan.nama,
        'tanggal_lahir': hewan.tanggal_lahir,
        'foto_url': hewan.url_foto or '',
        'jenis_hewan': type('JenisObj', (), {'id': hewan.id_jenis, 'nama': jenis_nama})(),
        'pemilik': type('PemilikObj', (), {'id': hewan.no_identitas_klien, 'nama': pemilik_nama})()
    })()
    context = {
        'hewan': hewan_wrapped,
        'jenis_hewan': JenisHewan.objects.all(),
        'klien_list': Klien.objects.all() if user_role == 'frontdesk' else None,
        'is_frontdesk': user_role == 'frontdesk'
    }
    return render(request, 'HewanPeliharaan_update.html', context)

def hewan_delete(request, id):
    user_role = request.GET.get('role', 'klien')
    klien_id = request.GET.get('klien_id')  # Added to pass back to list view
    
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
        try:
            # Check if this animal has any visits before deleting using raw SQL
            with connection.cursor() as cursor:
                cursor.execute(
                    'SELECT COUNT(*) FROM pet_clinic."KUNJUNGAN" WHERE nama_hewan = %s AND no_identitas_klien = %s',
                    [hewan_nama, str(hewan_klien_id)]
                )
                visits_count = cursor.fetchone()[0]
                
                if visits_count > 0:
                    messages.error(request, f'Tidak dapat menghapus hewan ini karena memiliki {visits_count} kunjungan.')
                    redirect_url = reverse('hewan:HewanPeliharaan_list')
                    if user_role != 'frontdesk' and klien_id:
                        redirect_url += f"?role={user_role}&klien_id={klien_id}"
                    return redirect(redirect_url)
                
                # Delete using raw SQL
                cursor.execute(
                    'DELETE FROM pet_clinic."HEWAN" WHERE nama = %s AND no_identitas_klien = %s',
                    [hewan_nama, str(hewan_klien_id)]
                )
            
            messages.success(request, f'Hewan "{hewan_nama}" berhasil dihapus!')
            return redirect('hewan:HewanPeliharaan_list')
            
        except Exception as e:
            messages.error(request, f'Gagal menghapus hewan: {str(e)}')
            # Redirect back to the list, possibly with role and klien_id if needed
            redirect_url = reverse('hewan:HewanPeliharaan_list')
            if user_role != 'frontdesk' and klien_id: # Should not happen
                 redirect_url += f"?role={user_role}&klien_id={klien_id}"
            return redirect(redirect_url)
    
    # Wrap hewan for delete confirm
    try:
        # Determine jenis and pemilik for template
        jenis = JenisHewan.objects.get(id=hewan.id_jenis)
        jenis_nama = jenis.nama_jenis
    except JenisHewan.DoesNotExist:
        jenis_nama = 'Unknown'
    try:
        from main.models import Individu, Perusahaan
        try:
            individu = Individu.objects.get(no_identitas_klien=hewan.no_identitas_klien)
            pemilik_nama = f"{individu.nama_depan} {individu.nama_belakang}"
        except Individu.DoesNotExist:
            perusahaan = Perusahaan.objects.get(no_identitas_klien=hewan.no_identitas_klien)
            pemilik_nama = perusahaan.nama_perusahaan
    except:
        pemilik_nama = 'Unknown Owner'
    
    # Create a hewan object that matches template expectations with composite ID
    hewan_wrapped = type('HewanObj', (), {
        'id': f"{hewan.nama}_{hewan.no_identitas_klien}",
        'nama': hewan.nama,
        'tanggal_lahir': hewan.tanggal_lahir,
        'jenis_hewan': type('JenisObj', (), {'nama': jenis_nama})(),
        'pemilik': type('PemilikObj', (), {'nama': pemilik_nama})()
    })()
    
    context = {
        'hewan': hewan_wrapped,
        'user_role': user_role,
        'klien_id': klien_id
    }
    return render(request, 'HewanPeliharaan_delete_confirm.html', context)

def check_can_delete_hewan(request, id):
    # Parse composite ID to get hewan name and klien id
    try:
        parts = id.split('_', 1)
        hewan_nama = parts[0]
        hewan_klien_id = parts[1]
        
        # Check if this animal has any visits using raw SQL
        with connection.cursor() as cursor:
            cursor.execute(
                'SELECT COUNT(*) FROM pet_clinic."KUNJUNGAN" WHERE nama_hewan = %s AND no_identitas_klien = %s',
                [hewan_nama, str(hewan_klien_id)]
            )
            visits_count = cursor.fetchone()[0]
            can_delete = visits_count == 0
        
    except:
        can_delete = False
    return JsonResponse({'can_delete': can_delete})
