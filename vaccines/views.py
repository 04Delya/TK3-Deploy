from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_http_methods, require_POST
from django.contrib import messages
from django.db import connection, InternalError, DatabaseError, transaction
from psycopg2.errors import RaiseException 

@require_http_methods(["GET"])
def vaccine_list(request):
    # autentikasi & validasi role perawat 
    no_tenaga_medis = request.session.get("no_tenaga_medis")
    if not no_tenaga_medis:
        return redirect("authentication:login")

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 1
            FROM pet_clinic."PERAWAT_HEWAN"
            WHERE no_tenaga_medis = %s
            LIMIT 1
        """, [no_tenaga_medis])
        if cursor.fetchone() is None:
            return redirect("authentication:login")

    # pencarian optional
    q = (request.GET.get("q") or "").lower()

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

    # format data ke template 
    vaccines = [
        {
            "kode": kode,
            "nama": nama,
            "harga": harga,
            "stok": stok,
        }
        for (kode, nama, harga, stok) in vaccines_raw
    ]

    return render(request, "vaccines_list.html", {"vaccines": vaccines})

@require_http_methods(["GET", "POST"])
def vaccine_create(request):
    # Ambil sesi login perawat
    no_tenaga_medis = request.session.get('no_tenaga_medis')
    if not no_tenaga_medis:
        return redirect('authentication:login')

    # Validasi user adalah perawat
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT COUNT(*) FROM pet_clinic."PERAWAT_HEWAN"
            WHERE no_tenaga_medis = %s
        """, [no_tenaga_medis])
        is_perawat = cursor.fetchone()[0] > 0

    if not is_perawat:
        return redirect('authentication:login')

    if request.method == 'POST':
        nama = request.POST.get('name')
        harga = request.POST.get('price')
        stok = request.POST.get('stock')

        # Validasi field wajib
        if not nama or not harga or not stok:
            messages.error(request, "Semua field wajib diisi.")
            return render(request, 'vaccines:vaccines_create.html')

        try:
            harga = int(harga)
            stok = int(stok)

            if harga < 0:
                messages.error(request, "Harga tidak boleh bernilai negatif.")
                return render(request, 'vaccines:vaccines_create.html')
            if stok < 0:
                messages.error(request, "Stok tidak boleh bernilai negatif.")
                return render(request, 'vaccines:vaccines_create.html')

        except ValueError:
            messages.error(request, "Harga dan stok harus berupa angka.")
            return render(request, 'vaccines_create.html')
        
        # Cek duplikat nama
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 1 FROM pet_clinic."VAKSIN"
                WHERE LOWER(nama) = LOWER(%s)
                LIMIT 1
            """, [nama.strip()])
            if cursor.fetchone():
                messages.error(request, "Nama vaksin sudah digunakan. Gunakan nama lain.")
                return render(request, 'vaccines_create.html')

        # Generate kode vaksin otomatis
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT kode
                FROM pet_clinic."VAKSIN"
                WHERE kode LIKE 'VAK%%'
                ORDER BY kode DESC
                LIMIT 1
            """)
            last = cursor.fetchone()
            if last:
                last_num = int(last[0][3:])
                new_kode = f"VAK{last_num + 1:03}"
            else:
                new_kode = "VAK001"

        # Insert ke tabel VAKSIN
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO pet_clinic."VAKSIN"(kode, nama, harga, stok)
                VALUES (%s, %s, %s, %s)
            """, [new_kode, nama.strip(), harga, stok])

        messages.success(request, f"Vaksin {nama} berhasil ditambahkan.")
        return redirect('vaccines:vaccine_list') 

    return render(request, 'vaccines_create.html')

@require_http_methods(["GET", "POST"])
def vaccine_update(request, kode):
    # Validasi role perawat
    no_tenaga_medis = request.session.get('no_tenaga_medis')
    if not no_tenaga_medis:
        return redirect('authentication:login')

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT COUNT(*) FROM pet_clinic."PERAWAT_HEWAN"
            WHERE no_tenaga_medis = %s
        """, [no_tenaga_medis])
        is_perawat = cursor.fetchone()[0] > 0

    if not is_perawat:
        return redirect('authentication:login')

    # Ambil data vaksin
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT kode, nama, harga
            FROM pet_clinic."VAKSIN"
            WHERE kode = %s
        """, [kode])
        vaksin_row = cursor.fetchone()

    if not vaksin_row:
        messages.error(request, "Vaksin tidak ditemukan.")
        return redirect('vaccines:vaccine_list')

    if request.method == 'POST':
        nama = request.POST.get('name')
        harga = request.POST.get('price')

        if not nama or not harga:
            messages.error(request, "Nama dan harga wajib diisi.")
        else:
            try:
                harga = int(harga)
                if harga < 0:
                    messages.error(request, "Harga tidak boleh bernilai negatif.")
                else:
                    # Update nama dan harga vaksin
                    with connection.cursor() as cursor:
                        cursor.execute("""
                            UPDATE pet_clinic."VAKSIN"
                            SET nama = %s, harga = %s
                            WHERE kode = %s
                        """, [nama.strip(), harga, kode])

                    messages.success(request, "Data vaksin berhasil diperbarui.")
                    return redirect('vaccines:vaccine_list')

            except ValueError:
                messages.error(request, "Harga harus berupa angka.")

    # Tampilkan form update
    return render(request, 'vaccines_update.html', {
        'vaccine': {
            'id': vaksin_row[0],
            'name': vaksin_row[1],
            'price': vaksin_row[2]
        }
    })

@require_http_methods(["GET", "POST"])
def vaccine_update_stock(request, kode):
    # Validasi: hanya perawat
    no_tenaga_medis = request.session.get('no_tenaga_medis')
    if not no_tenaga_medis:
        return redirect('authentication:login')

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT COUNT(*)
            FROM pet_clinic."PERAWAT_HEWAN"
            WHERE no_tenaga_medis = %s
        """, [no_tenaga_medis])
        is_perawat = cursor.fetchone()[0] > 0

    if not is_perawat:
        return redirect('authentication:login')

    # Ambil data vaksin
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT kode, nama, stok
            FROM pet_clinic."VAKSIN"
            WHERE kode = %s
        """, [kode])
        vaksin_row = cursor.fetchone()

    if not vaksin_row:
        messages.error(request, "Data vaksin tidak ditemukan.")
        return redirect('vaccines:vaccine_list')

    if request.method == 'POST':
        stok_baru = request.POST.get('stock')

        if not stok_baru:
            messages.error(request, "Stok tidak boleh kosong.")
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
                    return redirect('vaccines:vaccine_list')
            except ValueError:
                messages.error(request, "Stok harus berupa angka bulat.")

    context = {
        'vaccine': {
            'id': vaksin_row[0],
            'name': vaksin_row[1],
            'stock': vaksin_row[2]
        }
    }

    return render(request, 'vaccines_update_stock.html', context)

@require_POST
def vaccine_delete(request, kode):
    # validasi role perawat 
    no_tenaga_medis = request.session.get('no_tenaga_medis')
    if not no_tenaga_medis:
        return redirect('authentication:login')

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 1 FROM pet_clinic."PERAWAT_HEWAN"
            WHERE no_tenaga_medis = %s
            LIMIT 1
        """, [no_tenaga_medis])
        if cursor.fetchone() is None:
            return redirect('authentication:login')

    # dapatkan nama vaksin
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT nama FROM pet_clinic."VAKSIN"
            WHERE kode = %s
        """, [kode])
        row = cursor.fetchone()
    if not row:
        messages.error(request, "Vaksin tidak ditemukan.")
        return redirect('vaccines:vaccine_list')

    nama_vaksin = row[0]

    # coba hapus & tangkap error trigger 
    try:
        with transaction.atomic():                      
            with connection.cursor() as cursor:
                cursor.execute("""
                    DELETE FROM pet_clinic."VAKSIN"
                    WHERE kode = %s
                """, [kode])

        messages.success(request, f"Vaksin {nama_vaksin} berhasil dihapus.")
    except (InternalError, DatabaseError) as e:
        # bersihkan transaksi gagal
        connection.rollback()

        err_text = str(e)
        if "Vaksin tidak dapat dihapus dikarenakan telah digunakan untuk vaksinasi" in err_text:
            messages.error(
                request,
                "ERROR: Vaksin tidak dapat dihapus dikarenakan telah digunakan untuk vaksinasi."
            )
        else:
            messages.error(request, f"Terjadi kesalahan: {err_text}")

    return redirect('vaccines:vaccine_list')