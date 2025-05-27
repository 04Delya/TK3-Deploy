from django.shortcuts import render, redirect
from django.http import HttpResponse
from main.models import Hewan, Klien, Perawatan, Kunjungan, TenagaMedis, DokterHewan, PerawatHewan, FrontDesk, Pegawai, KunjunganKeperawatan

# Treatment views
def create_treatment_view(request):
    if request.method == "POST":
        id_kunjungan = request.POST.get("id_kunjungan")
        kode_perawatan = request.POST.get("kode_perawatan")
        catatan = request.POST.get("catatan")

        try:
            # Update catatan ke tabel KUNJUNGAN
            kunjungan = Kunjungan.objects.get(id_kunjungan=id_kunjungan)
            kunjungan.catatan = catatan
            kunjungan.save()

            # Tambah ke tabel KUNJUNGAN_KEPERAWATAN
            KunjunganKeperawatan.objects.create(
                id_kunjungan = kunjungan.id_kunjungan,
                nama_hewan = kunjungan.nama_hewan,
                no_identitas_klien = kunjungan.no_identitas_klien,
                no_front_desk = kunjungan.no_front_desk,
                no_perawat_hewan = kunjungan.no_perawat_hewan,
                no_dokter_hewan = kunjungan.no_dokter_hewan,
                kode_perawatan = kode_perawatan,
            )
            return redirect('hijau:table_treatment')
        except Exception as e:
            return render(request, 'create_treatment.html', {
                'kunjungan_list': Kunjungan.objects.all(),
                'perawatan_list': Perawatan.objects.all(),
                'error': str(e),
            })

    # GET request — tampilkan form kosong
    return render(request, 'create_treatment.html', {
        'kunjungan_list': Kunjungan.objects.all(),
        'perawatan_list': Perawatan.objects.all(),
    })

def update_treatment_view(request):
    return render(request, 'update_treatment.html')

def delete_treatment_view(request):
    return render(request, 'delete_treatment.html')

def table_treatment_view(request):
    records = KunjunganKeperawatan.objects.all()
    data = []

    for i, record in enumerate(records):
        try:
            perawatan = Perawatan.objects.get(kode_perawatan=record.kode_perawatan)
        except Perawatan.DoesNotExist:
            perawatan = None

        try:
            kunjungan = Kunjungan.objects.get(
                id_kunjungan=record.id_kunjungan,
                nama_hewan=record.nama_hewan,
                no_identitas_klien=record.no_identitas_klien,
                no_front_desk=record.no_front_desk,
                no_perawat_hewan=record.no_perawat_hewan,
                no_dokter_hewan=record.no_dokter_hewan,
            )
            catatan = kunjungan.catatan
        except Kunjungan.DoesNotExist:
            catatan = "-"

        data.append({
            "no": i + 1,
            "kode_kunjungan": record.id_kunjungan,
            "id_klien": record.no_identitas_klien,
            "nama_hewan": record.nama_hewan,
            "perawat": record.no_perawat_hewan,
            "dokter": record.no_dokter_hewan,
            "frontdesk": record.no_front_desk,
            "jenis_perawatan": f"{perawatan.kode_perawatan} - {perawatan.nama_perawatan}" if perawatan else "-",
            "catatan_medis": catatan or "-",
        })

    return render(request, 'table_treatment.html', {'treatment_list': data})

def treatment_views(request, action):
    if action == 'create':
        return render(request, 'create_treatment.html')
    elif action == 'update':
        return render(request, 'update_treatment.html')
    elif action == 'delete':
        return render(request, 'delete_treatment.html')
    else:
        return HttpResponse('Invalid action')

# Kunjungan views
def create_kunjungan_view(request):
    return render(request, 'create_kunjungan.html')

def update_kunjungan_view(request):
    return render(request, 'update_kunjungan.html')

def delete_kunjungan_view(request):
    return render(request, 'delete_kunjungan.html')

def table_kunjungan_view(request):
    return render(request, 'table_kunjungan.html')

def kunjungan_views(request, action):
    if action == 'create':
        return render(request, 'create_kunjungan.html')
    elif action == 'update':
        return render(request, 'update_kunjungan.html')
    elif action == 'delete':
        return render(request, 'delete_kunjungan.html')
    else:
        return HttpResponse('Invalid action')

# Rekam Medis views
def create_rekammedis_view(request):
    return render(request, 'create_rekammedis.html')

def update_rekammedis_view(request):
    return render(request, 'update_rekammedis.html')

def notfound_rekammedis_view(request):
    return render(request, 'notfound_rekammedis.html')

def rekammedis_view(request):
    return render(request, 'rekammedis.html')
