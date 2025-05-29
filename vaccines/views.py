from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from main.models import Vaksin, PerawatHewan, Kunjungan
from django.contrib import messages
from django.db import connection

def vaccine_list(request):
    # Cek hanya bisa diakses oleh perawat
    no_tenaga_medis = request.session.get('no_tenaga_medis')
    if not no_tenaga_medis:
        return redirect('authentication:login')

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT COUNT(*) FROM pet_clinic."PERAWAT_HEWAN"
            WHERE no_tenaga_medis = %s
        """, [no_tenaga_medis])
        if cursor.fetchone()[0] == 0:
            return redirect('authentication:login')

    # Ambil keyword pencarian
    q = request.GET.get("q", "").lower()

    # Query vaksin sesuai pencarian (desc by kode)
    with connection.cursor() as cursor:
        if q:
            cursor.execute("""
                SELECT kode, nama, harga, stok 
                FROM pet_clinic."VAKSIN"
                WHERE LOWER(nama) LIKE %s
                ORDER BY kode DESC
            """, [f"%{q}%"])
        else:
            cursor.execute("""
                SELECT kode, nama, harga, stok 
                FROM pet_clinic."VAKSIN"
                ORDER BY kode DESC
            """)
        vaccines_raw = cursor.fetchall()

    # Ambil kode vaksin yang pernah digunakan
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT DISTINCT kode_vaksin 
            FROM pet_clinic."KUNJUNGAN" 
            WHERE kode_vaksin IS NOT NULL
        """)
        used_kodes = set(row[0] for row in cursor.fetchall())

    # Format data untuk template
    vaccines = []
    for row in vaccines_raw:
        vaccines.append({
            'kode': row[0],
            'nama': row[1],
            'harga': row[2],
            'stok': row[3],
            'pernah_dipakai': row[0] in used_kodes
        })

    return render(request, "vaccines_list.html", {"vaccines": vaccines})

def vaccine_create(request):
    # Cek apakah user adalah perawat
    no_tenaga_medis = request.session.get('no_tenaga_medis')
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT COUNT(*) FROM pet_clinic."PERAWAT_HEWAN"
            WHERE no_tenaga_medis = %s
        """, [no_tenaga_medis])
        is_perawat = cursor.fetchone()[0] > 0

    if not no_tenaga_medis or not is_perawat:
        return redirect('authentication:login')

    if request.method == 'POST':
        nama = request.POST.get('name')
        harga = request.POST.get('price')
        stok = request.POST.get('stock')

        # Validasi input kosong
        if not nama or not harga or not stok:
            messages.error(request, "Semua field wajib diisi.")
            return render(request, 'vaccines_create.html')

        try:
            harga = int(harga)
            stok = int(stok)

            if harga < 0:
                messages.error(request, "Harga tidak boleh bernilai negatif.")
                return render(request, 'vaccines_create.html')
            if stok < 0:
                messages.error(request, "Stok tidak boleh bernilai negatif.")
                return render(request, 'vaccines_create.html')

        except ValueError:
            messages.error(request, "Harga dan stok harus berupa angka.")
            return render(request, 'vaccines_create.html')

        # Generate kode vaksin baru
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT kode FROM pet_clinic."VAKSIN"
                WHERE kode LIKE 'VAK%%'
                ORDER BY kode DESC LIMIT 1
            """)
            result = cursor.fetchone()
            if result:
                last_number = int(result[0][3:])
                new_kode = f"VAK{last_number + 1:03}"
            else:
                new_kode = "VAK001"

        # Insert ke DB
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO pet_clinic."VAKSIN"(kode, nama, harga, stok)
                VALUES (%s, %s, %s, %s)
            """, [new_kode, nama, harga, stok])

        messages.success(request, f"Vaksin {nama} berhasil ditambahkan.")
        return redirect('vaccine_list')

    return render(request, 'vaccines_create.html')

def vaccine_update(request, kode):
    # Cek apakah user adalah perawat
    no_tenaga_medis = request.session.get('no_tenaga_medis')
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT COUNT(*) FROM pet_clinic."PERAWAT_HEWAN"
            WHERE no_tenaga_medis = %s
        """, [no_tenaga_medis])
        is_perawat = cursor.fetchone()[0] > 0

    if not no_tenaga_medis or not is_perawat:
        return redirect('authentication:login')

    # Ambil data vaksin berdasarkan kode
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT kode, nama, harga FROM pet_clinic."VAKSIN"
            WHERE kode = %s
        """, [kode])
        row = cursor.fetchone()

    if not row:
        return redirect('vaccine_list')  # vaksin tidak ditemukan

    if request.method == 'POST':
        nama = request.POST.get('name')
        harga = request.POST.get('price')

        if not nama or not harga:
            messages.error(request, "Semua field wajib diisi.")
        else:
            try:
                harga = int(harga)
                if harga < 0:
                    messages.error(request, "Harga tidak boleh bernilai negatif.")
                    return render(request, 'vaccines_update.html', {
                        'vaccine': {'id': kode, 'name': nama, 'price': harga}
                    })

                with connection.cursor() as cursor:
                    cursor.execute("""
                        UPDATE pet_clinic."VAKSIN"
                        SET nama = %s, harga = %s
                        WHERE kode = %s
                    """, [nama, harga, kode])

                messages.success(request, "Data vaksin berhasil diperbarui.")
                return redirect('vaccine_list')

            except ValueError:
                messages.error(request, "Harga harus berupa angka.")

    context = {
        'vaccine': {
            'id': row[0],
            'name': row[1],
            'price': row[2],
        }
    }
    return render(request, 'vaccines_update.html', context)

def vaccine_update_stock(request, kode):
    # Cek hanya boleh diakses perawat
    no_tenaga_medis = request.session.get('no_tenaga_medis')
    if not no_tenaga_medis or not PerawatHewan.objects.filter(no_tenaga_medis=no_tenaga_medis).exists():
        return redirect('authentication:login')

    # Ambil data vaksin dari database
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT kode, nama, stok
            FROM pet_clinic."VAKSIN"
            WHERE kode = %s
        """, [kode])
        row = cursor.fetchone()

    if not row:
        return render(request, '404.html', status=404)

    if request.method == 'POST':
        stok_baru = request.POST.get('stock')

        if stok_baru is None or stok_baru.strip() == "":
            messages.error(request, "Field stok tidak boleh kosong.")
        else:
            try:
                stok_baru = int(stok_baru)
                if stok_baru < 0:
                    messages.error(request, "Stok tidak boleh bernilai negatif.")
                else:
                    with connection.cursor() as cursor:
                        cursor.execute("""
                            UPDATE pet_clinic."VAKSIN"
                            SET stok = %s
                            WHERE kode = %s
                        """, [stok_baru, kode])
                    messages.success(request, "Stok vaksin berhasil diperbarui.")
                    return redirect('vaccine_list')
            except ValueError:
                messages.error(request, "Stok harus berupa angka bulat.")

    context = {
        'vaccine': {
            'id': row[0],
            'name': row[1],
            'stock': row[2],
        }
    }
    return render(request, 'vaccines_update_stock.html', context)

@require_POST
def vaccine_delete(request, kode):
    # Cek role perawat
    no_tenaga_medis = request.session.get('no_tenaga_medis')
    if not no_tenaga_medis or not PerawatHewan.objects.filter(no_tenaga_medis=no_tenaga_medis).exists():
        return redirect('authentication:login')

    # Cek apakah vaksin pernah digunakan
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 1
            FROM pet_clinic."KUNJUNGAN"
            WHERE kode_vaksin = %s
            LIMIT 1
        """, [kode])
        used = cursor.fetchone()

    if used:
        messages.error(request, "Vaksin ini sudah pernah digunakan dan tidak dapat dihapus.")
        return redirect('vaccine_list')

    # Ambil nama vaksin untuk pesan success
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT nama
            FROM pet_clinic."VAKSIN"
            WHERE kode = %s
        """, [kode])
        row = cursor.fetchone()

    if not row:
        messages.error(request, "Vaksin tidak ditemukan.")
        return redirect('vaccine_list')

    nama_vaksin = row[0]

    # Hapus vaksin
    with connection.cursor() as cursor:
        cursor.execute("""
            DELETE FROM pet_clinic."VAKSIN"
            WHERE kode = %s
        """, [kode])

    messages.success(request, f"Vaksin {nama_vaksin} berhasil dihapus.")
    return redirect('vaccine_list')