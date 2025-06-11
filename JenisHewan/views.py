from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from main.models import JenisHewan, Hewan  # Use main models that connect to Supabase
from django.contrib import messages
from django.db import connection, IntegrityError
from psycopg2 import Error as PostgreSQLError
import uuid

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
            try:
                # Generate UUID for new JenisHewan
                new_id = uuid.uuid4()
                
                # Use raw SQL to insert into Supabase
                with connection.cursor() as cursor:
                    # Check for duplicates manually (bypass the problematic trigger)
                    cursor.execute(
                        'SELECT COUNT(*) FROM pet_clinic."JENIS_HEWAN" WHERE LOWER(nama_jenis) = LOWER(%s)',
                        [nama]
                    )
                    
                    if cursor.fetchone()[0] > 0:
                        messages.error(request, f'Jenis hewan "{nama}" sudah ada!')
                        return render(request, 'JenisHewan_create.html')
                    
                    # Insert directly without triggering the problematic function
                    cursor.execute(
                        'INSERT INTO pet_clinic."JENIS_HEWAN" (id, nama_jenis) VALUES (%s, %s)',
                        [str(new_id), nama]
                    )
                
                messages.success(request, f'Jenis hewan "{nama}" berhasil ditambahkan!')
                return redirect('jenis:JenisHewan_list')
                
            except PostgreSQLError as e:
                # Extract error message from PostgreSQL trigger
                error_msg = str(e).strip()
                if "ERROR:" in error_msg:
                    error_msg = error_msg.split("ERROR:")[-1].strip()
                messages.error(request, error_msg)
            except Exception as e:
                messages.error(request, f'Gagal menambahkan jenis hewan: {str(e)}')
        else:
            messages.error(request, 'Nama jenis hewan harus diisi.')
    
    return render(request, 'JenisHewan_create.html')

def jenis_hewan_update(request, id):
    try:
        jenis_hewan = JenisHewan.objects.get(id=id)
    except JenisHewan.DoesNotExist:
        messages.error(request, 'Jenis hewan tidak ditemukan.')
        return redirect('jenis:JenisHewan_list')
    
    if request.method == 'POST':
        nama = request.POST.get('nama')
        if nama:
            try:
                # Use raw SQL to update in Supabase
                with connection.cursor() as cursor:
                    # Check for duplicates with other records (excluding current record)
                    cursor.execute(
                        'SELECT COUNT(*) FROM pet_clinic."JENIS_HEWAN" WHERE LOWER(nama_jenis) = LOWER(%s) AND id != %s',
                        [nama, str(id)]
                    )
                    
                    if cursor.fetchone()[0] > 0:
                        messages.error(request, f'Jenis hewan "{nama}" sudah ada!')
                        return render(request, 'JenisHewan_update.html', {'jenis_hewan': jenis_hewan})
                    
                    cursor.execute(
                        'UPDATE pet_clinic."JENIS_HEWAN" SET nama_jenis = %s WHERE id = %s',
                        [nama, str(id)]
                    )
                
                messages.success(request, f'Jenis hewan berhasil diupdate menjadi "{nama}"!')
                return redirect('jenis:JenisHewan_list')
                
            except PostgreSQLError as e:
                # Extract error message from PostgreSQL trigger
                error_msg = str(e).strip()
                if "ERROR:" in error_msg:
                    error_msg = error_msg.split("ERROR:")[-1].strip()
                messages.error(request, error_msg)
            except Exception as e:
                messages.error(request, f'Gagal mengupdate jenis hewan: {str(e)}')
        else:
            messages.error(request, 'Nama jenis hewan harus diisi.')
    
    context = {'jenis_hewan': jenis_hewan}
    return render(request, 'JenisHewan_update.html', context)

def jenis_hewan_delete(request, id):
    try:
        jenis_hewan = JenisHewan.objects.get(id=id)
    except JenisHewan.DoesNotExist:
        messages.error(request, 'Jenis hewan tidak ditemukan.')
        return redirect('jenis:JenisHewan_list')
    if request.method == 'POST':
        try:
            # Check if any animals are using this type before deleting
            animals_using = Hewan.objects.filter(id_jenis=id).count()
            if animals_using > 0:
                messages.error(request, f'Tidak dapat menghapus jenis hewan ini karena masih digunakan oleh {animals_using} hewan.')
                return redirect('jenis:JenisHewan_list')
            
            # Use raw SQL to delete from Supabase
            with connection.cursor() as cursor:
                cursor.execute(
                    'DELETE FROM pet_clinic."JENIS_HEWAN" WHERE id = %s',
                    [str(id)]
                )
            
            messages.success(request, f'Jenis hewan "{jenis_hewan.nama_jenis}" berhasil dihapus!')
            return redirect('jenis:JenisHewan_list')
            
        except Exception as e:
            messages.error(request, f'Gagal menghapus jenis hewan: {str(e)}')
            return redirect('jenis:JenisHewan_list')
    
    context = {'jenis_hewan': jenis_hewan}
    return render(request, 'JenisHewan_delete_confirm.html', context)

def check_can_delete_jenis_hewan(request, id):
    # Check if any pets are using this animal type
    try:
        jenis_hewan = JenisHewan.objects.get(id=id)
        # Check if any animals use this type
        can_delete = not Hewan.objects.filter(id_jenis=id).exists()
        return JsonResponse({'can_delete': can_delete})
    except JenisHewan.DoesNotExist:
        return JsonResponse({'can_delete': False})
