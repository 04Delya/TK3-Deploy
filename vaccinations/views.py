from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.db.models import Q
from django.db import connection
from main.models import DokterHewan, Kunjungan, Vaksin
import locale

def vaccination_list(request):
    # Ambil sesi user
    no_tenaga_medis = request.session.get('no_tenaga_medis')
    if not no_tenaga_medis:
        return redirect('authentication:login')

    # Validasi role: hanya dokter hewan yang boleh mengakses
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT COUNT(*) 
            FROM pet_clinic."DOKTER_HEWAN"
            WHERE no_tenaga_medis = %s
        """, [no_tenaga_medis])
        is_dokter = cursor.fetchone()[0] > 0

    if not is_dokter:
        return redirect('authentication:login')

    # Ambil data vaksinasi milik dokter login
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                k.id_kunjungan, 
                k.timestamp_awal, 
                v.kode, 
                v.nama
            FROM pet_clinic."KUNJUNGAN" k
            LEFT JOIN pet_clinic."VAKSIN" v ON k.kode_vaksin = v.kode
            WHERE k.kode_vaksin IS NOT NULL
              AND k.no_dokter_hewan = %s
            ORDER BY k.timestamp_awal DESC
        """, [no_tenaga_medis])
        rows = cursor.fetchall()

    # Set locale ke Bahasa Indonesia jika tersedia
    try:
        locale.setlocale(locale.LC_TIME, 'id_ID.UTF-8')
    except locale.Error:
        pass  # fallback: tetap pakai format default jika locale tidak tersedia

    # Format data untuk template
    data = []
    for i, row in enumerate(rows, start=1):
        tanggal = row[1].strftime('%A, %-d %B %Y') if row[1] else "-"
        vaksin_info = f"{row[2]} - {row[3]}" if row[2] and row[3] else "N/A"
        data.append({
            'no': i,
            'kunjungan': row[0],
            'tanggal': tanggal,
            'vaksin': vaksin_info
        })

    return render(request, 'vaccinations_list.html', {
        'vaccinations': data
    })

# def vaccination_create(request):
#     if request.method == 'POST':
#         kunjungan_id = request.POST.get('kunjungan')
#         vaksin_id = request.POST.get('vaksin')

#         kunjungan = get_object_or_404(Kunjungan, id_kunjungan=kunjungan_id)
#         vaksin = get_object_or_404(Vaksin, kode=vaksin_id)

#         if kunjungan.timestamp_akhir:
#             messages.error(request, 'Kunjungan sudah selesai.')
#         elif kunjungan.kode_vaksin:
#             messages.error(request, 'Kunjungan ini sudah divaksin.')
#         elif vaksin.stok <= 0:
#             messages.error(request, 'Stok vaksin habis.')
#         else:
#             kunjungan.kode_vaksin = vaksin.kode
#             vaksin.stok -= 1
#             kunjungan.save()
#             vaksin.save()
#             messages.success(request, 'Vaksinasi berhasil dicatat.')
#             return redirect('vaccination_list')

#     kunjungan_list = Kunjungan.objects.all()
#     vaksin_list = Vaksin.objects.filter(stok__gt=0)

#     return render(request, 'create_vac.html', {
#         'kunjungan_list': kunjungan_list,
#         'vaksin_list': [f"{v.kode} - {v.nama} [{v.stok}]" for v in vaksin_list],
#     })

#kalo udh ada login
def vaccination_create(request):
    dokter_id = request.session.get('dokter_id')
    if not dokter_id:
        messages.error(request, "Dokter belum login.")
        return redirect('authentication:login')

    if request.method == 'POST':
        kunjungan_id = request.POST.get('kunjungan')
        vaksin_id = request.POST.get('vaksin')

        try:
            kunjungan = Kunjungan.objects.get(id_kunjungan=kunjungan_id)
            vaksin = Vaksin.objects.get(kode=vaksin_id)
        except (Kunjungan.DoesNotExist, Vaksin.DoesNotExist):
            messages.error(request, 'Data tidak ditemukan.')
            return redirect('vaccinations:vaccination_create')

        if kunjungan.timestamp_akhir:
            messages.error(request, 'Kunjungan sudah selesai.')
        elif kunjungan.kode_vaksin:
            messages.error(request, 'Kunjungan ini sudah divaksin.')
        elif vaksin.stok <= 0:
            messages.error(request, 'Stok vaksin yang dipilih sudah habis.')
        else:
            with connection.cursor() as cursor:
                cursor.execute("""
                    UPDATE "pet_clinic"."KUNJUNGAN"
                    SET kode_vaksin = %s
                    WHERE id_kunjungan = %s
                """, [vaksin.kode, kunjungan.id_kunjungan])

                cursor.execute("""
                    UPDATE "pet_clinic"."VAKSIN"
                    SET stok = stok - 1
                    WHERE kode = %s
                """, [vaksin.kode])

            messages.success(request, 'Vaksinasi berhasil dicatat.')
            return redirect('vaccinations:vaccination_list')

    kunjungan_list = Kunjungan.objects.filter(
        # timestamp_akhir__isnull=True,
        # kode_vaksin__isnull=True,
        # no_dokter_hewan=dokter_id
    )

    vaksin_list = Vaksin.objects.filter(stok__gt=0)

    return render(request, 'create_vac.html', {
        'kunjungan_list': kunjungan_list,
        'vaksin_list': vaksin_list,
    })

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import connection
from main.models import Kunjungan, Vaksin

def vaccination_update(request, no):
    try:
        kunjungan = Kunjungan.objects.get(id_kunjungan=no)
    except Kunjungan.DoesNotExist:
        messages.error(request, 'Kunjungan tidak ditemukan.')
        return redirect('vaccinations:vaccination_list')

    # Cek apakah kunjungan sudah divaksin
    if not kunjungan.kode_vaksin:
        messages.error(request, 'Kunjungan ini belum divaksin.')
        return redirect('vaccinations:vaccination_list')

    if request.method == 'POST':
        kode_vaksin_baru = request.POST.get('vaksin')
        vaksin_baru = get_object_or_404(Vaksin, kode=kode_vaksin_baru)
        vaksin_lama = get_object_or_404(Vaksin, kode=kunjungan.kode_vaksin)

        if vaksin_baru.kode == vaksin_lama.kode:
            messages.info(request, 'Vaksin tidak berubah.')
            return redirect('vaccinations:vaccination_list')

        if vaksin_baru.stok <= 0:
            messages.error(request, 'Stok vaksin baru habis.')
            return redirect('vaccinations:vaccination_update', no=kunjungan.id_kunjungan)

        # Jalankan update dengan raw SQL (karena managed=False)
        with connection.cursor() as cursor:
            # Tambahkan stok vaksin lama
            cursor.execute("""
                UPDATE "pet_clinic"."VAKSIN"
                SET stok = stok + 1
                WHERE kode = %s
            """, [vaksin_lama.kode])

            # Kurangi stok vaksin baru
            cursor.execute("""
                UPDATE "pet_clinic"."VAKSIN"
                SET stok = stok - 1
                WHERE kode = %s
            """, [vaksin_baru.kode])

            # Update kunjungan dengan vaksin baru
            cursor.execute("""
                UPDATE "pet_clinic"."KUNJUNGAN"
                SET kode_vaksin = %s
                WHERE id_kunjungan = %s
            """, [vaksin_baru.kode, kunjungan.id_kunjungan])

        messages.success(request, 'Vaksinasi berhasil diperbarui.')
        return redirect('vaccinations:vaccination_list')

    vaksin_list = Vaksin.objects.all()

    return render(request, 'update_vac.html', {
        'kunjungan': kunjungan,       
        'vaksin_list': vaksin_list,
    })


@require_POST
def vaccination_delete(request, no):
    try:
        kunjungan = Kunjungan.objects.get(id_kunjungan=no)
    except Kunjungan.DoesNotExist:
        messages.error(request, 'Kunjungan tidak ditemukan.')
        return redirect('vaccinations:vaccination_list')

    if not kunjungan.kode_vaksin:
        messages.error(request, 'Kunjungan ini belum divaksin.')
        return redirect('vaccinations:vaccination_list')

    try:
        vaksin = Vaksin.objects.get(kode=kunjungan.kode_vaksin)
    except Vaksin.DoesNotExist:
        messages.error(request, 'Vaksin tidak ditemukan.')
        return redirect('vaccinations:vaccination_list')

    with connection.cursor() as cursor:
        # Tambah stok vaksin kembali
        cursor.execute("""
            UPDATE "pet_clinic"."VAKSIN"
            SET stok = stok + 1
            WHERE kode = %s
        """, [vaksin.kode])

        # Hapus vaksin dari kunjungan
        cursor.execute("""
            UPDATE "pet_clinic"."KUNJUNGAN"
            SET kode_vaksin = NULL
            WHERE id_kunjungan = %s
        """, [kunjungan.id_kunjungan])

    messages.success(request, 'Vaksinasi berhasil dihapus.')
    return redirect('vaccinations:vaccination_list')

def vaccination_history(request):
    pet_filter = request.GET.get('pet', '')
    vaksin_filter = request.GET.get('vaksin', '')

    query = """
        SELECT h.nama AS pet_name, 
            v.nama AS vaksin_name, 
            v.kode AS vaksin_id, 
            v.harga, 
            to_char(k.timestamp_awal, 'DD-MM-YYYY HH24:MI') AS waktu
        FROM "pet_clinic"."KUNJUNGAN" k
        JOIN "pet_clinic"."HEWAN" h ON k.nama_hewan = h.nama
        JOIN "pet_clinic"."VAKSIN" v ON k.kode_vaksin = v.kode
        WHERE k.kode_vaksin IS NOT NULL
    """

    params = []
    if pet_filter:
        query += " AND h.nama ILIKE %s"
        params.append(f'%{pet_filter}%')
    if vaksin_filter:
        query += " AND v.nama ILIKE %s"
        params.append(f'%{vaksin_filter}%')

    with connection.cursor() as cursor:
        cursor.execute(query, params)
        data = cursor.fetchall()

    # Ubah hasil ke bentuk dictionary biar mudah dibaca di HTML
    results = []
    for i, row in enumerate(data):
        results.append({
            'no': i + 1,
            'pet': row[0],
            'vaksin': row[1],
            'vaksin_id': row[2],
            'harga': row[3],
            'waktu': row[4],
        })

    return render(request, 'vaccinations/client_history.html', {
        'results': results,
        'pet_filter': pet_filter,
        'vaksin_filter': vaksin_filter,
    })