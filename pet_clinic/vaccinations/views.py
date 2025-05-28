from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.db.models import Q
from django.db import connection
from main.models import Kunjungan, Vaksin  

def vaccination_list(request):
    vaksinasi = Kunjungan.objects.filter(kode_vaksin__isnull=False)

    data = []
    for i, item in enumerate(vaksinasi, start=1):
        vaksin = Vaksin.objects.filter(kode=item.kode_vaksin).first()
        data.append({
            'no': i,
            'kunjungan': item.id_kunjungan,
            'tanggal': item.timestamp_awal.strftime('%A, %-d %B %Y'),
            'vaksin': f'{vaksin.kode} - {vaksin.nama}' if vaksin else 'N/A'
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

        kunjungan = get_object_or_404(Kunjungan, id_kunjungan=kunjungan_id)
        vaksin = get_object_or_404(Vaksin, kode=vaksin_id)

        if kunjungan.timestamp_akhir:
            messages.error(request, 'Kunjungan sudah selesai.')
        elif kunjungan.kode_vaksin:
            messages.error(request, 'Kunjungan ini sudah divaksin.')
        elif vaksin.stok <= 0:
            messages.error(request, 'Stok vaksin yang dipilih sudah habis.')
        else:
            # Simpan vaksin ke kunjungan (pakai raw SQL karena managed = False)
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

    # FILTER hanya kunjungan terbuka oleh dokter login
    # kunjungan_list = Kunjungan.objects.filter(
    #     kode_vaksin__isnull=True,
    #     timestamp_akhir__isnull=True,
    #     no_dokter_hewan=dokter_id
    # )
    kunjungan_list = Kunjungan.objects.filter()

    # FILTER hanya vaksin yang stok-nya masih ada
    vaksin_list = Vaksin.objects.filter(stok__gt=0)

    return render(request, 'create_vac.html', {
        'kunjungan_list': kunjungan_list,
        'vaksin_list': vaksin_list,
    })

def vaccination_update(request):
    kunjungan = Kunjungan.objects.filter(kode_vaksin__isnull=False).first()

    if not kunjungan:
        messages.error(request, 'Tidak ada kunjungan yang bisa diperbarui.')
        return redirect('vaccination_list')

    if request.method == 'POST':
        vaksin_baru = get_object_or_404(Vaksin, kode=request.POST.get('vaksin'))
        vaksin_lama = get_object_or_404(Vaksin, kode=kunjungan.kode_vaksin)

        if vaksin_baru.stok <= 0:
            messages.error(request, 'Stok vaksin baru habis.')
        else:
            vaksin_lama.stok += 1
            vaksin_baru.stok -= 1
            kunjungan.kode_vaksin = vaksin_baru.kode
            vaksin_lama.save()
            vaksin_baru.save()
            kunjungan.save()
            messages.success(request, 'Vaksinasi berhasil diubah.')
            return redirect('vaccination_list')

    vaksin_list = Vaksin.objects.all()
    selected_vaksin = f"{kunjungan.kode_vaksin} - {Vaksin.objects.get(kode=kunjungan.kode_vaksin).nama} [{Vaksin.objects.get(kode=kunjungan.kode_vaksin).stok}]"

    return render(request, 'update_vac.html', {
        'kunjungan': kunjungan.id_kunjungan,
        'vaksin_list': [f"{v.kode} - {v.nama} [{v.stok}]" for v in vaksin_list],
        'selected_vaksin': selected_vaksin
    })

@require_POST
def vaccination_delete(request, no):
    kunjungan = get_object_or_404(Kunjungan, id_kunjungan=no)

    if not kunjungan.kode_vaksin:
        messages.error(request, 'Kunjungan ini belum divaksin.')
        return redirect('vaccination_list')

    vaksin = get_object_or_404(Vaksin, kode=kunjungan.kode_vaksin)
    vaksin.stok += 1
    vaksin.save()

    kunjungan.kode_vaksin = None
    kunjungan.save()

    messages.success(request, 'Vaksinasi berhasil dihapus.')
    return redirect('vaccination_list')

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
