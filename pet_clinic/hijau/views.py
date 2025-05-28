from django.shortcuts import render, redirect, get_object_or_404
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

def update_treatment_view(request, id_kunjungan, nama_hewan, no_identitas_klien, no_front_desk, no_perawat_hewan, no_dokter_hewan, kode_perawatan):
    
    try:
        treatment = KunjunganKeperawatan.objects.get(
            id_kunjungan=id_kunjungan,
            nama_hewan=nama_hewan,
            no_identitas_klien=no_identitas_klien,
            no_front_desk=no_front_desk,
            no_perawat_hewan=no_perawat_hewan,
            no_dokter_hewan=no_dokter_hewan,
            kode_perawatan=kode_perawatan
        )
        kunjungan = Kunjungan.objects.get(id_kunjungan=id_kunjungan)

        if request.method == "POST":
            treatment.kode_perawatan = request.POST.get("kode_perawatan")
            kunjungan.catatan = request.POST.get("catatan")
            treatment.save()
            kunjungan.save()
            return redirect('hijau:table_treatment')

        return render(request, 'update_treatment.html', {
            'treatment': treatment,
            'kunjungan': kunjungan,
            'perawatan_list': Perawatan.objects.all(),
        })
    except Exception as e:
        return HttpResponse(f"Error: {e}")

def delete_treatment_view(request, id_kunjungan, nama_hewan, no_identitas_klien, no_front_desk, no_perawat_hewan, no_dokter_hewan, kode_perawatan):
    try:
        treatment = KunjunganKeperawatan.objects.get(
            id_kunjungan=id_kunjungan,
            nama_hewan=nama_hewan,
            no_identitas_klien=no_identitas_klien,
            no_front_desk=no_front_desk,
            no_perawat_hewan=no_perawat_hewan,
            no_dokter_hewan=no_dokter_hewan,
            kode_perawatan=kode_perawatan
        )

        if request.method == "POST":
            treatment.delete()
            return redirect('hijau:table_treatment')

        return render(request, 'delete_treatment.html', {
            'treatment': treatment
        })
    except Exception as e:
        return HttpResponse(f"Error: {e}")


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
            "kode_kunjungan": str(record.id_kunjungan),
            "id_klien": record.no_identitas_klien,
            "nama_hewan": record.nama_hewan,
            "perawat": record.no_perawat_hewan,
            "dokter": record.no_dokter_hewan,
            "frontdesk": record.no_front_desk,
            "kode_perawatan": record.kode_perawatan,
            "jenis_perawatan": f"{record.kode_perawatan} - {perawatan.nama_perawatan}" if perawatan else "-",
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
    records = Kunjungan.objects.all()
    print("Jumlah kunjungan:", records.count())  # DEBUG
    data = []

    for i, record in enumerate(records):
        data.append({
            "no": i + 1,
            "id_kunjungan": record.id_kunjungan,
            "no_identitas_klien": record.no_identitas_klien,
            "nama_hewan": record.nama_hewan,
            "tipe_kunjungan": record.tipe_kunjungan,
            "timestamp_awal": record.timestamp_awal,
            "timestamp_akhir": record.timestamp_akhir,
        })

    print("DATA:", data)  # DEBUG

    return render(request, 'table_kunjungan.html', {
        'kunjungan_list': data
    })


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
def create_rekammedis_view(request, id_kunjungan):
    kunjungan = get_object_or_404(Kunjungan, id_kunjungan=id_kunjungan)

    if request.method == "POST":
        suhu = request.POST.get("suhu")
        berat = request.POST.get("berat_badan")
        catatan = request.POST.get("catatan")

        try:
            kunjungan.suhu = int(suhu) if suhu else None
            kunjungan.berat_badan = float(berat) if berat else None
            kunjungan.catatan = catatan
            kunjungan.save()
            return redirect('hijau:rekammedis', id_kunjungan=id_kunjungan)
        except Exception as e:
            return render(request, 'create_rekammedis.html', {
                'kunjungan': kunjungan,
                'error': str(e)
            })

    return render(request, 'create_rekammedis.html', {'kunjungan': kunjungan})


def update_rekammedis_view(request, id_kunjungan):
    kunjungan = get_object_or_404(Kunjungan, id_kunjungan=id_kunjungan)

    if request.method == "POST":
        suhu = request.POST.get("suhu")
        berat_badan = request.POST.get("berat_badan")
        catatan = request.POST.get("catatan")

        try:
            kunjungan.suhu = int(suhu) if suhu else None
            kunjungan.berat_badan = float(berat_badan) if berat_badan else None
            kunjungan.catatan = catatan
            kunjungan.save()
            return redirect('hijau:rekammedis', id_kunjungan=id_kunjungan)
        except Exception as e:
            return render(request, 'update_rekammedis.html', {
                'error': str(e),
                'kunjungan': kunjungan,
            })

    return render(request, 'update_rekammedis.html', {
        'kunjungan': kunjungan,
    })

def notfound_rekammedis_view(request, id_kunjungan):
    return render(request, 'notfound_rekammedis.html', {
        'id_kunjungan': id_kunjungan
    })


def rekammedis_view(request, id_kunjungan):
    try:
        kunjungan = Kunjungan.objects.get(id_kunjungan=id_kunjungan)

        if kunjungan.suhu is None and kunjungan.berat_badan is None and not kunjungan.catatan:
            return redirect('hijau:notfound_rekammedis', id_kunjungan=id_kunjungan)

        return render(request, 'rekammedis.html', {
            'id_kunjungan': id_kunjungan,
            'suhu': kunjungan.suhu or "-",
            'berat_badan': f"{kunjungan.berat_badan} kg" if kunjungan.berat_badan else "- kg",
            'catatan': kunjungan.catatan or "-",
        })

    except Kunjungan.DoesNotExist:
        return redirect('hijau:notfound_rekammedis', id_kunjungan=id_kunjungan)


