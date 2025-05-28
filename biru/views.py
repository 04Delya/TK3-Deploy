from django.shortcuts import render, redirect, get_object_or_404
from main.models import *
from django.http import Http404
from django.contrib import messages
from django.utils.html import escape


prescriptions_data = [
    {
        'treatment': Perawatan.objects.first(),
        'medicine': Obat.objects.first(),
        'quantity': 3,
    },
]

# === CREATE VIEWS ===
def create_medicine_view(request):
    if request.method == 'POST':
        kode = request.POST.get('kode')
        nama = request.POST.get('nama')
        harga = request.POST.get('harga')
        dosis = request.POST.get('dosis')
        stok = request.POST.get('stok')

        # Validasi sederhana
        if not (kode and nama and harga and dosis and stok):
            messages.error(request, 'Semua field harus diisi.')
            return render(request, 'create_medicine.html')

        try:
            harga_int = int(harga)
            stok_int = int(stok)
        except ValueError:
            messages.error(request, 'Harga dan Stok harus berupa angka.')
            return render(request, 'create_medicine.html')

        # Cek jika kode sudah ada, agar tidak duplikat (optional)
        if Obat.objects.filter(kode=kode).exists():
            messages.error(request, 'Kode obat sudah ada, gunakan kode lain.')
            return render(request, 'create_medicine.html')

        # Simpan ke database
        new_obat = Obat(kode=kode, nama=nama, harga=harga_int, dosis=dosis, stok=stok_int)
        new_obat.save()

        messages.success(request, 'Obat berhasil ditambahkan.')
        return redirect('biru:list_medicine')

    # GET request
    return render(request, 'create_medicine.html')

def create_prescriptions_view(request):
    if request.method == 'POST':
        # Simpan data ke 'prescriptions_data' (hanya simulasi)
        treatment_id = request.POST.get('treatment')
        medicine_id = request.POST.get('medicine')
        quantity = int(request.POST.get('quantity', 0))

        treatment = Perawatan.objects.get(kode_perawatan=treatment_id)
        medicine = Obat.objects.get(kode=medicine_id)

        prescriptions_data.append({
            'treatment': treatment,
            'medicine': medicine,
            'quantity': quantity
        })
        return redirect('biru:list_prescriptions')

    treatments = Perawatan.objects.all()
    medicines = Obat.objects.all()
    return render(request, 'create_prescriptions.html', {
        'treatments': treatments,
        'medicines': medicines,
    })

from django.shortcuts import render, redirect
from main.models import Perawatan
from django.contrib import messages

def create_treatment_view(request):
    if request.method == 'POST':
        kode_perawatan = request.POST.get('kode_perawatan')
        nama_perawatan = request.POST.get('nama_perawatan')
        biaya_perawatan = request.POST.get('biaya_perawatan')

        if not (kode_perawatan and nama_perawatan and biaya_perawatan):
            messages.error(request, 'Semua field harus diisi.')
            return render(request, 'create_treatment_type.html')

        try:
            biaya_int = int(biaya_perawatan)
        except ValueError:
            messages.error(request, 'Biaya harus berupa angka.')
            return render(request, 'create_treatment_type.html')

        # Cek apakah kode_perawatan sudah ada
        if Perawatan.objects.filter(kode_perawatan=kode_perawatan).exists():
            messages.error(request, 'Kode perawatan sudah ada, gunakan kode lain.')
            return render(request, 'create_treatment_type.html')

        # Simpan data baru ke database
        Perawatan.objects.create(
            kode_perawatan=kode_perawatan,
            nama_perawatan=nama_perawatan,
            biaya_perawatan=biaya_int
        )
        messages.success(request, 'Jenis perawatan berhasil dibuat.')
        return redirect('biru:list_treatment_type')

    # GET request, tampilkan form kosong
    return render(request, 'create_treatment_type.html')




# === DELETE VIEWS ===
def delete_medicine_view(request, kode):
    obat = get_object_or_404(Obat, kode=kode)
    if request.method == "POST":
        obat.delete()
        return redirect('biru:list_medicine')
    return render(request, 'delete_medicine.html', {'obat': obat})

# views.py
def delete_prescriptions_view(request, treatment_kode, medicine_kode):
    # Cari prescription di list prescriptions_data berdasarkan kode treatment dan medicine
    prescription_to_delete = None
    for p in prescriptions_data:
        if p['treatment'].kode_perawatan == treatment_kode and p['medicine'].kode == medicine_kode:
            prescription_to_delete = p
            break
    
    if prescription_to_delete is None:
        # Jika tidak ditemukan, redirect ke list atau tampilkan error
        return redirect('biru:list_prescriptions')

    if request.method == 'POST':
        prescriptions_data.remove(prescription_to_delete)
        return redirect('biru:list_prescriptions')

    return render(request, 'delete_prescriptions.html', {
        'prescription': prescription_to_delete,
        'treatment_kode': treatment_kode,
        'medicine_kode': medicine_kode,
    })

def delete_treatment_view(request, kode_perawatan):
    treatment = get_object_or_404(Perawatan, kode_perawatan=kode_perawatan)
    if request.method == 'POST':
        treatment.delete()
        messages.success(request, 'Jenis perawatan berhasil dihapus.')
        return redirect('biru:list_treatment_type')
    return render(request, 'delete_treatment_type.html', {'treatment': treatment})

# === LIST VIEWS ===
def list_medicine_view(request):
    obat_list = Obat.objects.all()
    return render(request, 'list_medicine.html', {'obat_list': obat_list})

def list_prescriptions_view(request):
    # Mengirimkan data simulated prescriptions
    return render(request, 'list_prescriptions.html', {
        'prescriptions': prescriptions_data
    })

def list_treatment_view(request):
    treatment_list = Perawatan.objects.all()
    return render(request, 'list_treatment_type.html', {'treatment_list': treatment_list})

# === UPDATE VIEWS ===
def update_medicine_view(request, kode):
    obat = get_object_or_404(Obat, kode=kode)
    if request.method == "POST":
        obat.nama = request.POST.get('nama')
        obat.harga = int(request.POST.get('harga'))
        obat.dosis = request.POST.get('dosis')
        obat.stok = int(request.POST.get('stok'))
        obat.save()
        return redirect('biru:list_medicine')
    context = {'obat': obat}
    return render(request, 'update_medicine.html', context)

from django.shortcuts import render, redirect, get_object_or_404
from main.models import Perawatan
from django.contrib import messages

def update_treatment_view(request, kode_perawatan):
    treatment = get_object_or_404(Perawatan, kode_perawatan=kode_perawatan)
    
    if request.method == 'POST':
        nama_perawatan = request.POST.get('nama_perawatan')
        biaya_perawatan = request.POST.get('biaya_perawatan')

        # Validasi sederhana
        if not nama_perawatan:
            messages.error(request, 'Nama perawatan tidak boleh kosong.')
            return render(request, 'update_treatment_type.html', {'treatment': treatment})
        
        if not biaya_perawatan:
            messages.error(request, 'Biaya perawatan tidak boleh kosong.')
            return render(request, 'update_treatment_type.html', {'treatment': treatment})

        try:
            biaya_int = int(biaya_perawatan)
        except ValueError:
            messages.error(request, 'Biaya perawatan harus berupa angka.')
            return render(request, 'update_treatment_type.html', {'treatment': treatment})

        # Update data
        treatment.nama_perawatan = nama_perawatan
        treatment.biaya_perawatan = biaya_int
        treatment.save()

        messages.success(request, 'Data jenis perawatan berhasil diperbarui.')
        return redirect('biru:list_treatment_type')

    # GET request -> tampilkan form dengan data awal
    return render(request, 'update_treatment_type.html', {'treatment': treatment})


def update_stock_medicine_view(request, kode):
    obat = get_object_or_404(Obat, kode=kode)
    if request.method == "POST":
        obat.stok = int(request.POST.get('stok'))
        obat.save()
        return redirect('biru:list_medicine')
    return render(request, 'updateStock_medicine.html', {'obat': obat})