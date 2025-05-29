from django.shortcuts import render, redirect, get_object_or_404
from django.db import connection
from django.contrib import messages

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
    # Check session and role
    no_tenaga_medis = request.session.get('no_tenaga_medis')
    if not no_tenaga_medis:
        return redirect('authentication:login')
    
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

        with connection.cursor() as cursor:
            # Check if medicine code exists
            cursor.execute("""
                SELECT EXISTS (
                    SELECT 1 FROM pet_clinic."OBAT"
                    WHERE kode = %s
                )
            """, [kode])
            exists = cursor.fetchone()[0]
            
            if exists:
                messages.error(request, 'Kode obat sudah ada, gunakan kode lain.')
                return render(request, 'create_medicine.html')

            # Insert new medicine
            cursor.execute("""
                INSERT INTO pet_clinic."OBAT" (kode, nama, harga, stok, dosis)
                VALUES (%s, %s, %s, %s, %s)
            """, [kode, nama, harga_int, stok_int, dosis])

        messages.success(request, 'Obat berhasil ditambahkan.')
        return redirect('biru:list_medicine')

    return render(request, 'create_medicine.html')

def create_prescriptions_view(request):
    role = request.session.get('role')
    if role != 'dokter':
        messages.error(request, "Anda tidak memiliki izin untuk membuat resep.")
        return redirect('biru:list_prescriptions')

    if request.method == 'POST':
        treatment_id = request.POST.get('treatment')
        medicine_id = request.POST.get('medicine')
        quantity = request.POST.get('quantity')

        if not treatment_id or not medicine_id or not quantity:
            messages.error(request, "Semua field harus diisi.")
            return redirect('biru:create_prescriptions')

        try:
            quantity_int = int(quantity)
            if quantity_int < 1:
                raise ValueError
        except ValueError:
            messages.error(request, "Kuantitas obat harus berupa angka positif.")
            return redirect('biru:create_prescriptions')

        with connection.cursor() as cursor:
            # Ambil stok dan harga obat
            cursor.execute('SELECT stok, harga, nama FROM pet_clinic."OBAT" WHERE kode = %s', [medicine_id])
            obat_data = cursor.fetchone()
            if not obat_data:
                messages.error(request, "Obat tidak ditemukan.")
                return redirect('biru:create_prescriptions')
            stok_obat, harga_obat, nama_obat = obat_data

            # Ambil biaya perawatan
            cursor.execute('SELECT biaya_perawatan FROM pet_clinic."PERAWATAN" WHERE kode_perawatan = %s', [treatment_id])
            row = cursor.fetchone()
            if not row:
                messages.error(request, "Jenis perawatan tidak ditemukan.")
                return redirect('biru:create_prescriptions')
            biaya_perawatan = row[0]

        total_harga_resep = harga_obat * quantity_int

        # Validasi total harga resep tidak boleh melebihi biaya perawatan
        if total_harga_resep > biaya_perawatan:
            messages.error(request, "ERROR: Total harga obat melebihi total harga perawatan. Mohon sesuaikan resep obat.")
            return redirect('biru:create_prescriptions')

        # Validasi stok obat cukup
        if quantity_int > stok_obat:
            messages.error(request, f'ERROR: Stok obat "{nama_obat}" tidak mencukupi untuk jumlah {quantity_int} unit.')
            return redirect('biru:create_prescriptions')

        # Jika validasi lolos, insert resep dan update stok obat
        with connection.cursor() as cursor:
            cursor.execute('''
                INSERT INTO pet_clinic."PERAWATAN_OBAT" (kode_perawatan, kode_obat, kuantitas_obat)
                VALUES (%s, %s, %s)
            ''', [treatment_id, medicine_id, quantity_int])

            cursor.execute('''
                UPDATE pet_clinic."OBAT"
                SET stok = stok - %s
                WHERE kode = %s
            ''', [quantity_int, medicine_id])

        messages.success(request, "Resep berhasil dibuat dan stok obat diperbarui.")
        return redirect('biru:list_prescriptions')

    # GET request: load data treatments & medicines
    with connection.cursor() as cursor:
        cursor.execute('SELECT kode_perawatan, nama_perawatan FROM pet_clinic."PERAWATAN" ORDER BY kode_perawatan')
        treatments = [{'kode_perawatan': r[0], 'nama_perawatan': r[1]} for r in cursor.fetchall()]

        cursor.execute('SELECT kode, nama, stok FROM pet_clinic."OBAT" ORDER BY kode')
        medicines = [{'kode': r[0], 'nama': r[1], 'stok': r[2]} for r in cursor.fetchall()]

    return render(request, 'create_prescriptions.html', {
        'treatments': treatments,
        'medicines': medicines,
    })

def create_treatment_view(request):
    # Check session and role
    no_tenaga_medis = request.session.get('no_tenaga_medis')
    if not no_tenaga_medis:
        return redirect('authentication:login')
    
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

        with connection.cursor() as cursor:
            # Check if treatment code exists
            cursor.execute("""
                SELECT EXISTS (
                    SELECT 1 FROM pet_clinic."PERAWATAN"
                    WHERE kode_perawatan = %s
                )
            """, [kode_perawatan])
            exists = cursor.fetchone()[0]
            
            if exists:
                messages.error(request, 'Kode perawatan sudah ada, gunakan kode lain.')
                return render(request, 'create_treatment_type.html')

            # Insert new treatment
            cursor.execute("""
                INSERT INTO pet_clinic."PERAWATAN" (kode_perawatan, nama_perawatan, biaya_perawatan)
                VALUES (%s, %s, %s)
            """, [kode_perawatan, nama_perawatan, biaya_int])

        messages.success(request, 'Jenis perawatan berhasil dibuat.')
        return redirect('biru:list_treatment_type')

    return render(request, 'create_treatment_type.html')

# === DELETE VIEWS ===
def delete_medicine_view(request, kode):
    # Check session and role
    no_tenaga_medis = request.session.get('no_tenaga_medis')
    if not no_tenaga_medis:
        return redirect('authentication:login')
    
    role = request.session.get('role')
    if not user_can(role, 'delete', 'medicine'):
        messages.error(request, "Anda tidak memiliki izin menghapus obat.")
        return redirect('biru:list_medicine')

    if request.method == "POST":
        with connection.cursor() as cursor:
            cursor.execute("""
                DELETE FROM pet_clinic."OBAT"
                WHERE kode = %s
            """, [kode])
        messages.success(request, "Obat berhasil dihapus.")
        return redirect('biru:list_medicine')

    # Get medicine data for confirmation
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT kode, nama, harga, stok, dosis
            FROM pet_clinic."OBAT"
            WHERE kode = %s
        """, [kode])
        obat = cursor.fetchone()

    if not obat:
        messages.error(request, "Obat tidak ditemukan.")
        return redirect('biru:list_medicine')

    return render(request, 'delete_medicine.html', {'obat': {
        'kode': obat[0],
        'nama': obat[1],
        'harga': obat[2],
        'stok': obat[3],
        'dosis': obat[4]
    }})

def delete_prescriptions_view(request, index):
    role = request.session.get('role')
    if role != 'dokter':
        messages.error(request, "Anda tidak memiliki izin menghapus resep.")
        return redirect('biru:list_prescriptions')

    prescriptions = request.session.get('prescriptions', [])

    if request.method == 'POST':
        try:
            index = int(index)
            prescriptions.pop(index)
            request.session['prescriptions'] = prescriptions
            messages.success(request, "Resep berhasil dihapus.")
        except (IndexError, ValueError):
            messages.error(request, "Resep tidak ditemukan atau indeks salah.")
        return redirect('biru:list_prescriptions')

    if 0 <= index < len(prescriptions):
        prescription = prescriptions[index]
    else:
        messages.error(request, "Resep tidak ditemukan.")
        return redirect('biru:list_prescriptions')

    return render(request, 'delete_prescriptions.html', {
        'prescription': prescription,
        'index': index,
    })



def delete_treatment_view(request, kode_perawatan):
    # Check session and role
    no_tenaga_medis = request.session.get('no_tenaga_medis')
    if not no_tenaga_medis:
        return redirect('authentication:login')
    
    role = request.session.get('role')
    if not user_can(role, 'delete', 'treatment_type'):
        messages.error(request, "Anda tidak memiliki izin menghapus jenis perawatan.")
        return redirect('biru:list_treatment_type')

    if request.method == 'POST':
        with connection.cursor() as cursor:
            cursor.execute("""
                DELETE FROM pet_clinic."PERAWATAN"
                WHERE kode_perawatan = %s
            """, [kode_perawatan])
        messages.success(request, 'Jenis perawatan berhasil dihapus.')
        return redirect('biru:list_treatment_type')

    # Get treatment data for confirmation
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT kode_perawatan, nama_perawatan, biaya_perawatan
            FROM pet_clinic."PERAWATAN"
            WHERE kode_perawatan = %s
        """, [kode_perawatan])
        treatment = cursor.fetchone()

    if not treatment:
        messages.error(request, "Jenis perawatan tidak ditemukan.")
        return redirect('biru:list_treatment_type')

    return render(request, 'delete_treatment_type.html', {'treatment': {
        'kode_perawatan': treatment[0],
        'nama_perawatan': treatment[1],
        'biaya_perawatan': treatment[2]
    }})

# === LIST VIEWS ===
def list_medicine_view(request):
    # Check session
    no_tenaga_medis = request.session.get('no_tenaga_medis')
    if not no_tenaga_medis:
        return redirect('authentication:login')
    
    role = request.session.get('role')
    can_edit = user_can(role, 'update', 'medicine') or user_can(role, 'delete', 'medicine') or user_can(role, 'update_stock', 'medicine')

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT kode, nama, harga, stok, dosis
            FROM pet_clinic."OBAT"
            ORDER BY nama
        """)
        obat_list = cursor.fetchall()

    # Convert to list of dicts for easier template access
    obat_list = [{
        'kode': row[0],
        'nama': row[1],
        'harga': row[2],
        'stok': row[3],
        'dosis': row[4]
    } for row in obat_list]

    return render(request, 'list_medicine.html', {
        'obat_list': obat_list,
        'can_edit': can_edit,
    })

def list_prescriptions_view(request):
    prescriptions = request.session.get('prescriptions', [])
    return render(request, 'list_prescriptions.html', {'prescriptions': prescriptions})

# def list_prescriptions_view(request):
#     role = request.session.get('role')
#     email = request.session.get('user_email')

#     if not role:
#         messages.error(request, "Anda harus login terlebih dahulu.")
#         return redirect('authentication:login')

#     prescriptions = []
#     try:
#         with connection.cursor() as cursor:
#             if role == 'dokter':
#                 # Dokter bisa melihat semua resep
#                 cursor.execute("""
#                     SELECT r.kode_perawatan, p.nama_perawatan, r.kode_obat, o.nama, r.kuantitas_obat, o.harga
#                     FROM pet_clinic."RESEP" r
#                     JOIN pet_clinic."PERAWATAN" p ON r.kode_perawatan = p.kode_perawatan
#                     JOIN pet_clinic."OBAT" o ON r.kode_obat = o.kode
#                     ORDER BY p.nama_perawatan, o.nama
#                 """)
#             elif role == 'klien':
#                 # Klien hanya melihat resep untuk dirinya sendiri
#                 # Asumsikan ada tabel KLIEN dengan email dan no_identitas
#                 # dan tabel HEWAN yang berelasi dengan KLIEN, serta KUNJUNGAN yang menghubungkan HEWAN dan RESEP
#                 # Namun karena RESEP tidak ada relasi ke kunjungan, kita perlu logika khusus sesuai desain Anda
#                 # Contoh asumsi sederhana: hanya menampilkan semua resep (bisa diubah sesuai kebutuhan)
#                 messages.info(request, "Fitur untuk klien belum diimplementasikan sepenuhnya.")
#                 cursor.execute("""
#                     SELECT r.kode_perawatan, p.nama_perawatan, r.kode_obat, o.nama, r.kuantitas_obat, o.harga
#                     FROM pet_clinic."RESEP" r
#                     JOIN pet_clinic."PERAWATAN" p ON r.kode_perawatan = p.kode_perawatan
#                     JOIN pet_clinic."OBAT" o ON r.kode_obat = o.kode
#                     ORDER BY p.nama_perawatan, o.nama
#                 """)
#             else:
#                 messages.error(request, "Role tidak dikenali atau tidak memiliki akses.")
#                 return redirect('main:landing_page')

#             rows = cursor.fetchall()
#             for row in rows:
#                 prescriptions.append({
#                     'kode_perawatan': row[0],
#                     'nama_perawatan': row[1],
#                     'kode_obat': row[2],
#                     'nama_obat': row[3],
#                     'kuantitas_obat': row[4],
#                     'total_harga': row[4] * row[5],  # kuantitas * harga satuan
#                 })

#     except Exception as e:
#         messages.error(request, f"Gagal mengambil data resep: {str(e)}")

#     can_edit = user_can(role, 'delete', 'prescriptions') or user_can(role, 'create', 'prescriptions')
#     return render(request, 'list_prescriptions.html', {
#         'prescriptions': prescriptions,
#         'can_edit': can_edit,
#     })


def list_treatment_view(request):
    # Check session
    no_tenaga_medis = request.session.get('no_tenaga_medis')
    if not no_tenaga_medis:
        return redirect('authentication:login')
    
    role = request.session.get('role')
    can_edit = user_can(role, 'update', 'treatment_type') or user_can(role, 'delete', 'treatment_type')

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT kode_perawatan, nama_perawatan, biaya_perawatan
            FROM pet_clinic."PERAWATAN"
            ORDER BY nama_perawatan
        """)
        treatment_list = cursor.fetchall()

    # Convert to list of dicts for easier template access
    treatment_list = [{
        'kode_perawatan': row[0],
        'nama_perawatan': row[1],
        'biaya_perawatan': row[2]
    } for row in treatment_list]

    return render(request, 'list_treatment_type.html', {
        'treatment_list': treatment_list,
        'can_edit': can_edit,
    })

# === UPDATE VIEWS ===
def update_medicine_view(request, kode):
    # Check session and role
    no_tenaga_medis = request.session.get('no_tenaga_medis')
    if not no_tenaga_medis:
        return redirect('authentication:login')
    
    role = request.session.get('role')
    if not user_can(role, 'update', 'medicine'):
        messages.error(request, "Anda tidak memiliki izin mengubah data obat.")
        return redirect('biru:list_medicine')

    if request.method == "POST":
        nama = request.POST.get('nama')
        harga = request.POST.get('harga')
        dosis = request.POST.get('dosis')
        stok = request.POST.get('stok')

        with connection.cursor() as cursor:
            cursor.execute("""
                UPDATE pet_clinic."OBAT"
                SET nama = %s, harga = %s, dosis = %s, stok = %s
                WHERE kode = %s
            """, [nama, int(harga), dosis, int(stok), kode])

        messages.success(request, "Obat berhasil diperbarui.")
        return redirect('biru:list_medicine')

    # Get current medicine data
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT kode, nama, harga, stok, dosis
            FROM pet_clinic."OBAT"
            WHERE kode = %s
        """, [kode])
        obat = cursor.fetchone()

    if not obat:
        messages.error(request, "Obat tidak ditemukan.")
        return redirect('biru:list_medicine')

    context = {'obat': {
        'kode': obat[0],
        'nama': obat[1],
        'harga': obat[2],
        'stok': obat[3],
        'dosis': obat[4]
    }}
    return render(request, 'update_medicine.html', context)

def update_treatment_view(request, kode_perawatan):
    # Check session and role
    no_tenaga_medis = request.session.get('no_tenaga_medis')
    if not no_tenaga_medis:
        return redirect('authentication:login')
    
    role = request.session.get('role')
    if not user_can(role, 'update', 'treatment_type'):
        messages.error(request, "Anda tidak memiliki izin mengubah jenis perawatan.")
        return redirect('biru:list_treatment_type')

    if request.method == 'POST':
        nama_perawatan = request.POST.get('nama_perawatan')
        biaya_perawatan = request.POST.get('biaya_perawatan')

        if not nama_perawatan:
            messages.error(request, 'Nama perawatan tidak boleh kosong.')
            return redirect('biru:update_treatment', kode_perawatan=kode_perawatan)

        if not biaya_perawatan:
            messages.error(request, 'Biaya perawatan tidak boleh kosong.')
            return redirect('biru:update_treatment', kode_perawatan=kode_perawatan)

        try:
            biaya_int = int(biaya_perawatan)
        except ValueError:
            messages.error(request, 'Biaya perawatan harus berupa angka.')
            return redirect('biru:update_treatment', kode_perawatan=kode_perawatan)

        with connection.cursor() as cursor:
            cursor.execute("""
                UPDATE pet_clinic."PERAWATAN"
                SET nama_perawatan = %s, biaya_perawatan = %s
                WHERE kode_perawatan = %s
            """, [nama_perawatan, biaya_int, kode_perawatan])

        messages.success(request, 'Data jenis perawatan berhasil diperbarui.')
        return redirect('biru:list_treatment_type')

    # Get current treatment data
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT kode_perawatan, nama_perawatan, biaya_perawatan
            FROM pet_clinic."PERAWATAN"
            WHERE kode_perawatan = %s
        """, [kode_perawatan])
        treatment = cursor.fetchone()

    if not treatment:
        messages.error(request, "Jenis perawatan tidak ditemukan.")
        return redirect('biru:list_treatment_type')

    return render(request, 'update_treatment_type.html', {'treatment': {
        'kode_perawatan': treatment[0],
        'nama_perawatan': treatment[1],
        'biaya_perawatan': treatment[2]
    }})

def update_stock_medicine_view(request, kode):
    # Check session and role
    no_tenaga_medis = request.session.get('no_tenaga_medis')
    if not no_tenaga_medis:
        return redirect('authentication:login')
    
    role = request.session.get('role')
    if not user_can(role, 'update_stock', 'medicine'):
        messages.error(request, "Anda tidak memiliki izin mengubah stok obat.")
        return redirect('biru:list_medicine')

    if request.method == "POST":
        stok = request.POST.get('stok')

        with connection.cursor() as cursor:
            cursor.execute("""
                UPDATE pet_clinic."OBAT"
                SET stok = %s
                WHERE kode = %s
            """, [int(stok), kode])

        messages.success(request, "Stok obat berhasil diperbarui.")
        return redirect('biru:list_medicine')

    # Get current medicine data
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT kode, nama, stok
            FROM pet_clinic."OBAT"
            WHERE kode = %s
        """, [kode])
        obat = cursor.fetchone()

    if not obat:
        messages.error(request, "Obat tidak ditemukan.")
        return redirect('biru:list_medicine')

    return render(request, 'updateStock_medicine.html', {'obat': {
        'kode': obat[0],
        'nama': obat[1],
        'stok': obat[2]
    }})