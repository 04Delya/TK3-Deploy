from django.shortcuts import render, redirect, get_object_or_404
from main.models import *
from django.contrib import messages

prescriptions_data = [
    {
        'treatment': Perawatan.objects.first(),
        'medicine': Obat.objects.first(),
        'quantity': 3,
    },
]

# Utility function untuk cek role izin
def user_can(role, action, resource):
    if resource == 'medicine':
        if role in ['dokter', 'perawat']:
            return action in ['create', 'update', 'update_stock', 'delete', 'read']
        return action == 'read'
    elif resource == 'treatment_type':
        if role in ['dokter', 'perawat']:
            return action in ['create', 'update', 'delete', 'read']
        return action == 'read'
    elif resource == 'prescriptions':
        if role == 'dokter':
            return action in ['create', 'update', 'delete', 'read']
        return action == 'read'
    return False


# === CREATE VIEWS ===
def create_medicine_view(request):
    role = request.session.get('role')
    if not user_can(role, 'create', 'medicine'):
        messages.error(request, "Anda tidak memiliki izin untuk membuat data obat.")
        return redirect('biru:list_medicine')

    if request.method == 'POST':
        kode = request.POST.get('kode')
        nama = request.POST.get('nama')
        harga = request.POST.get('harga')
        dosis = request.POST.get('dosis')
        stok = request.POST.get('stok')

        if not (kode and nama and harga and dosis and stok):
            messages.error(request, 'Semua field harus diisi.')
            return render(request, 'create_medicine.html')

        try:
            harga_int = int(harga)
            stok_int = int(stok)
        except ValueError:
            messages.error(request, 'Harga dan Stok harus berupa angka.')
            return render(request, 'create_medicine.html')

        if Obat.objects.filter(kode=kode).exists():
            messages.error(request, 'Kode obat sudah ada, gunakan kode lain.')
            return render(request, 'create_medicine.html')

        new_obat = Obat(kode=kode, nama=nama, harga=harga_int, dosis=dosis, stok=stok_int)
        new_obat.save()

        messages.success(request, 'Obat berhasil ditambahkan.')
        return redirect('biru:list_medicine')

    return render(request, 'create_medicine.html')


def create_prescriptions_view(request):
    role = request.session.get('role')
    if not user_can(role, 'create', 'prescriptions'):
        messages.error(request, "Anda tidak memiliki izin untuk membuat resep.")
        return redirect('biru:list_prescriptions')

    if request.method == 'POST':
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


def create_treatment_view(request):
    role = request.session.get('role')
    if not user_can(role, 'create', 'treatment_type'):
        messages.error(request, "Anda tidak memiliki izin untuk membuat jenis perawatan.")
        return redirect('biru:list_treatment_type')

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

        if Perawatan.objects.filter(kode_perawatan=kode_perawatan).exists():
            messages.error(request, 'Kode perawatan sudah ada, gunakan kode lain.')
            return render(request, 'create_treatment_type.html')

        Perawatan.objects.create(
            kode_perawatan=kode_perawatan,
            nama_perawatan=nama_perawatan,
            biaya_perawatan=biaya_int
        )
        messages.success(request, 'Jenis perawatan berhasil dibuat.')
        return redirect('biru:list_treatment_type')

    return render(request, 'create_treatment_type.html')


# === DELETE VIEWS ===
def delete_medicine_view(request, kode):
    role = request.session.get('role')
    if not user_can(role, 'delete', 'medicine'):
        messages.error(request, "Anda tidak memiliki izin menghapus obat.")
        return redirect('biru:list_medicine')

    obat = get_object_or_404(Obat, kode=kode)
    if request.method == "POST":
        obat.delete()
        messages.success(request, "Obat berhasil dihapus.")
        return redirect('biru:list_medicine')
    return render(request, 'delete_medicine.html', {'obat': obat})


def delete_prescriptions_view(request, treatment_kode, medicine_kode):
    role = request.session.get('role')
    if not user_can(role, 'delete', 'prescriptions'):
        messages.error(request, "Anda tidak memiliki izin menghapus resep.")
        return redirect('biru:list_prescriptions')

    prescription_to_delete = None
    for p in prescriptions_data:
        if p['treatment'].kode_perawatan == treatment_kode and p['medicine'].kode == medicine_kode:
            prescription_to_delete = p
            break

    if prescription_to_delete is None:
        messages.error(request, "Resep tidak ditemukan.")
        return redirect('biru:list_prescriptions')

    if request.method == 'POST':
        prescriptions_data.remove(prescription_to_delete)
        messages.success(request, "Resep berhasil dihapus.")
        return redirect('biru:list_prescriptions')

    return render(request, 'delete_prescriptions.html', {
        'prescription': prescription_to_delete,
        'treatment_kode': treatment_kode,
        'medicine_kode': medicine_kode,
    })


def delete_treatment_view(request, kode_perawatan):
    role = request.session.get('role')
    if not user_can(role, 'delete', 'treatment_type'):
        messages.error(request, "Anda tidak memiliki izin menghapus jenis perawatan.")
        return redirect('biru:list_treatment_type')

    treatment = get_object_or_404(Perawatan, kode_perawatan=kode_perawatan)
    if request.method == 'POST':
        treatment.delete()
        messages.success(request, 'Jenis perawatan berhasil dihapus.')
        return redirect('biru:list_treatment_type')
    return render(request, 'delete_treatment_type.html', {'treatment': treatment})


# === LIST VIEWS ===
def list_medicine_view(request):
    role = request.session.get('role')
    obat_list = Obat.objects.all()

    can_edit = user_can(role, 'update', 'medicine') or user_can(role, 'delete', 'medicine') or user_can(role, 'update_stock', 'medicine')
    return render(request, 'list_medicine.html', {
        'obat_list': obat_list,
        'can_edit': can_edit,
    })


def list_prescriptions_view(request):
    role = request.session.get('role')
    can_edit = user_can(role, 'update', 'prescriptions') or user_can(role, 'delete', 'prescriptions')
    return render(request, 'list_prescriptions.html', {
        'prescriptions': prescriptions_data,
        'can_edit': can_edit,
    })


def list_treatment_view(request):
    role = request.session.get('role')
    treatment_list = Perawatan.objects.all()
    can_edit = user_can(role, 'update', 'treatment_type') or user_can(role, 'delete', 'treatment_type')
    return render(request, 'list_treatment_type.html', {
        'treatment_list': treatment_list,
        'can_edit': can_edit,
    })


# === UPDATE VIEWS ===
def update_medicine_view(request, kode):
    role = request.session.get('role')
    if not user_can(role, 'update', 'medicine'):
        messages.error(request, "Anda tidak memiliki izin mengubah data obat.")
        return redirect('biru:list_medicine')

    obat = get_object_or_404(Obat, kode=kode)
    if request.method == "POST":
        obat.nama = request.POST.get('nama')
        obat.harga = int(request.POST.get('harga'))
        obat.dosis = request.POST.get('dosis')
        obat.stok = int(request.POST.get('stok'))
        obat.save()
        messages.success(request, "Obat berhasil diperbarui.")
        return redirect('biru:list_medicine')
    context = {'obat': obat}
    return render(request, 'update_medicine.html', context)


def update_treatment_view(request, kode_perawatan):
    role = request.session.get('role')
    if not user_can(role, 'update', 'treatment_type'):
        messages.error(request, "Anda tidak memiliki izin mengubah jenis perawatan.")
        return redirect('biru:list_treatment_type')

    treatment = get_object_or_404(Perawatan, kode_perawatan=kode_perawatan)

    if request.method == 'POST':
        nama_perawatan = request.POST.get('nama_perawatan')
        biaya_perawatan = request.POST.get('biaya_perawatan')

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

        treatment.nama_perawatan = nama_perawatan
        treatment.biaya_perawatan = biaya_int
        treatment.save()

        messages.success(request, 'Data jenis perawatan berhasil diperbarui.')
        return redirect('biru:list_treatment_type')

    return render(request, 'update_treatment_type.html', {'treatment': treatment})


def update_stock_medicine_view(request, kode):
    role = request.session.get('role')
    if not user_can(role, 'update_stock', 'medicine'):
        messages.error(request, "Anda tidak memiliki izin mengubah stok obat.")
        return redirect('biru:list_medicine')

    obat = get_object_or_404(Obat, kode=kode)
    if request.method == "POST":
        obat.stok = int(request.POST.get('stok'))
        obat.save()
        messages.success(request, "Stok obat berhasil diperbarui.")
        return redirect('biru:list_medicine')
    return render(request, 'updateStock_medicine.html', {'obat': obat})
