from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.http import require_http_methods, require_POST
from django.db import connection, transaction, DatabaseError

def vaccination_list(request):
    no_tenaga_medis = request.session.get('no_tenaga_medis')
    if not no_tenaga_medis:
        return redirect('authentication:login')

    # Validasi: hanya dokter
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT EXISTS (
                SELECT 1 FROM pet_clinic."DOKTER_HEWAN"
                WHERE no_tenaga_medis = %s
            )
        """, [no_tenaga_medis])
        is_dokter = cursor.fetchone()[0]

    if not is_dokter:
        return redirect('authentication:login')
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                k.id_kunjungan,
                k.timestamp_awal,
                v.kode,
                v.nama
            FROM pet_clinic."KUNJUNGAN" k
            INNER JOIN pet_clinic."VAKSIN" v ON k.kode_vaksin = v.kode
            WHERE k.kode_vaksin IS NOT NULL
              AND k.timestamp_akhir IS NULL
              AND k.no_dokter_hewan = %s
            ORDER BY k.timestamp_awal DESC
        """, [no_tenaga_medis])
        rows = cursor.fetchall()

    # Format hasil ke template
    data = []
    for i, (id_kunjungan, timestamp, kode_vaksin, nama_vaksin) in enumerate(rows, start=1):
        tanggal = timestamp.strftime('%A, %-d %B %Y') if timestamp else "-"
        vaksin_info = f"{kode_vaksin} - {nama_vaksin}" if kode_vaksin and nama_vaksin else "N/A"
        data.append({
            'no': i,
            'kunjungan': id_kunjungan,
            'tanggal': tanggal,
            'vaksin': vaksin_info
        })

    return render(request, 'vaccinations_list.html', {
        'vaccinations': data
    })

@require_http_methods(["GET", "POST"])
def vaccination_create(request):
    # 1. Validasi sesi & role dokter
    no_tenaga_medis = request.session.get('no_tenaga_medis')
    if not no_tenaga_medis:
        messages.error(request, "Dokter belum login.")
        return redirect('authentication:login')

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT EXISTS (
                SELECT 1
                FROM pet_clinic."DOKTER_HEWAN"
                WHERE no_tenaga_medis = %s
        )""", [no_tenaga_medis])
        if not cursor.fetchone()[0]:
            return redirect('authentication:login')

    # 2. HANDLE POST, simpan vaksinasi
    if request.method == "POST":
        id_kunjungan = request.POST.get("kunjungan")
        kode_vaksin  = request.POST.get("vaksin")

        if not id_kunjungan or not kode_vaksin:
            messages.error(request, "Data kunjungan dan vaksin harus dipilih.")
            return redirect("vaccinations:vaccination_create")

        try:
            with transaction.atomic(), connection.cursor() as cursor:
                # pastikan kunjungan masih terbuka & belum divaksin
                cursor.execute("""
                    SELECT COUNT(*)
                    FROM pet_clinic."KUNJUNGAN"
                    WHERE id_kunjungan     = %s
                      AND timestamp_akhir  IS NULL
                      AND kode_vaksin      IS NULL
                      AND no_dokter_hewan  = %s
                """, [id_kunjungan, no_tenaga_medis])
                if cursor.fetchone()[0] == 0:
                    raise ValueError("Kunjungan tidak valid atau sudah divaksin.")

                # update kode_vaksin 
                cursor.execute("""
                    UPDATE pet_clinic."KUNJUNGAN"
                    SET kode_vaksin = %s
                    WHERE id_kunjungan = %s
                """, [kode_vaksin, id_kunjungan])

            messages.success(request, "Vaksinasi berhasil dicatat.")
            return redirect("vaccinations:vaccination_list")

        except (DatabaseError, ValueError) as e:
            # DatabaseError muncul jika trigger RAISE EXCEPTION 
            messages.error(request, str(e))
            return redirect("vaccinations:vaccination_create")

    # 3. HANDLE GET, tampilkan form
    with connection.cursor() as cursor:
        # daftar kunjungan aktif tanpa vaksin milik dokter ini
        cursor.execute("""
            SELECT id_kunjungan
            FROM pet_clinic."KUNJUNGAN"
            WHERE timestamp_akhir IS NULL
              AND kode_vaksin IS NULL
              AND no_dokter_hewan = %s
        """, [no_tenaga_medis])
        kunjungan_list = [row[0] for row in cursor.fetchall()]

        cursor.execute("""
            SELECT kode, nama, stok
            FROM pet_clinic."VAKSIN"
        """)
        vaksin_list = cursor.fetchall()

    return render(
        request,
        "create_vac.html",
        {
            "kunjungan_list": kunjungan_list,
            "vaksin_list": vaksin_list, 
        },
    )

@require_http_methods(["GET", "POST"])
def vaccination_update(request, no):
    # 1. Validasi login & role dokter
    no_tenaga_medis = request.session.get("no_tenaga_medis")
    if not no_tenaga_medis:
        return redirect("authentication:login")

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT EXISTS (
                SELECT 1
                FROM pet_clinic."DOKTER_HEWAN"
                WHERE no_tenaga_medis = %s
        )""", [no_tenaga_medis])
        if not cursor.fetchone()[0]:
            return redirect("authentication:login")

    # 2. Ambil data kunjungan yg bersangkutan
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT id_kunjungan, kode_vaksin
            FROM pet_clinic."KUNJUNGAN"
            WHERE id_kunjungan   = %s
              AND no_dokter_hewan = %s
        """, [str(no), no_tenaga_medis])
        row = cursor.fetchone()

    if not row:
        messages.error(request, "Kunjungan tidak ditemukan.")
        return redirect("vaccinations:vaccination_list")

    id_kunjungan, kode_vaksin_lama = row

    if not kode_vaksin_lama:
        messages.error(request, "Kunjungan ini belum divaksin.")
        return redirect("vaccinations:vaccination_list")

    # 3. HANDLE  POST, ganti vaksin
    if request.method == "POST":
        kode_vaksin_baru = request.POST.get("vaksin")

        if not kode_vaksin_baru:
            messages.error(request, "Vaksin baru harus dipilih.")
            return redirect("vaccinations:vaccination_update", no=no)

        if kode_vaksin_baru == kode_vaksin_lama:
            messages.info(request, "Vaksin tidak berubah.")
            return redirect("vaccinations:vaccination_list")

        try:
            with transaction.atomic(), connection.cursor() as cursor:
                # Trigger akan: +1 stok lama, -1 stok baru, atau error jika stok baru habis
                cursor.execute("""
                    UPDATE pet_clinic."KUNJUNGAN"
                    SET kode_vaksin = %s
                    WHERE id_kunjungan = %s
                """, [kode_vaksin_baru, id_kunjungan])

            messages.success(request, "Vaksinasi berhasil diperbarui.")
            return redirect("vaccinations:vaccination_list")

        except DatabaseError as e:
            # Pesan dari trigger 
            messages.error(request, str(e))
            return redirect("vaccinations:vaccination_update", no=no)

    # 4. HANDLE  GET, tampilkan form pilih vaksin baru
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT kode, nama, stok
            FROM pet_clinic."VAKSIN"
        """)
        vaksin_list = cursor.fetchall()

    vaksin_display = [
        {
            "kode": v[0],
            "display": f"{v[0]} - {v[1]} [{v[2]}]",
            "stok": v[2],
        }
        for v in vaksin_list
    ]

    return render(
        request,
        "update_vac.html",
        {
            "kunjungan": {"id_kunjungan": id_kunjungan},
            "vaksin_list": vaksin_display,
            "selected_kode": kode_vaksin_lama,
        },
    )

@require_POST
def vaccination_delete(request, no):
    # 1. Validasi sesi & role dokter
    no_tenaga_medis = request.session.get("no_tenaga_medis")
    if not no_tenaga_medis:
        messages.error(request, "Dokter belum login.")
        return redirect("authentication:login")

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT EXISTS (
                SELECT 1
                FROM pet_clinic."DOKTER_HEWAN"
                WHERE no_tenaga_medis = %s
        )""", [no_tenaga_medis])
        if not cursor.fetchone()[0]:
            return redirect("authentication:login")

    # 2. Ambil info kunjungan & pemilik
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT kode_vaksin, no_dokter_hewan
            FROM pet_clinic."KUNJUNGAN"
            WHERE id_kunjungan = %s
        """, [str(no)])
        row = cursor.fetchone()

    if not row:
        messages.error(request, "Kunjungan tidak ditemukan.")
        return redirect("vaccinations:vaccination_list")

    kode_vaksin, dokter_pemilik = row
    if str(dokter_pemilik) != str(no_tenaga_medis):
        messages.error(request, "Kunjungan ini bukan milik Anda.")
        return redirect("vaccinations:vaccination_list")
    
    # 3. Hapus vaksinasi  (set kode_vaksin = NULL)
    #    Trigger akan +1 stok vaksin lama secara otomatis
    try:
        with transaction.atomic(), connection.cursor() as cursor:
            cursor.execute("""
                UPDATE pet_clinic."KUNJUNGAN"
                SET kode_vaksin = NULL
                WHERE id_kunjungan = %s
            """, [str(no)])

        messages.success(request, "Vaksinasi berhasil dihapus dari kunjungan.")

    except DatabaseError as e:
        # Apabila trigger menolak
        messages.error(request, str(e))

    return redirect("vaccinations:vaccination_list")

def vaccination_history(request):
    email = request.session.get('user_email')

    if not email:
        return redirect('authentication:login')

    # Validasi bahwa user adalah klien
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT no_identitas 
            FROM pet_clinic."KLIEN"
            WHERE email = %s
        """, [email])
        klien_row = cursor.fetchone()

    if not klien_row:
        return redirect('authentication:login')

    no_identitas_klien = klien_row[0]

    # Ambil filter dari query param
    pet_filter = request.GET.get('pet', '')
    vaksin_filter = request.GET.get('vaksin', '')

    # Ambil daftar nama hewan milik klien
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT DISTINCT nama
            FROM pet_clinic."HEWAN"
            WHERE no_identitas_klien = %s
        """, [no_identitas_klien])
        pet_options = [row[0] for row in cursor.fetchall()]

    # Ambil daftar nama vaksin yang pernah dipakai oleh klien
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT DISTINCT v.nama
            FROM pet_clinic."KUNJUNGAN" k
            JOIN pet_clinic."VAKSIN" v ON k.kode_vaksin = v.kode
            WHERE k.no_identitas_klien = %s
              AND k.kode_vaksin IS NOT NULL
        """, [no_identitas_klien])
        vaksin_options = [row[0] for row in cursor.fetchall()]

    # Query vaksinasi yang dilakukan oleh klien ini
    query = """
        SELECT h.nama AS pet_name, 
               v.nama AS vaksin_name, 
               v.kode AS vaksin_id, 
               v.harga, 
               to_char(k.timestamp_awal, 'DD-MM-YYYY HH24:MI') AS waktu
        FROM pet_clinic."KUNJUNGAN" k
        JOIN pet_clinic."HEWAN" h 
            ON k.nama_hewan = h.nama 
            AND k.no_identitas_klien = h.no_identitas_klien
        JOIN pet_clinic."VAKSIN" v ON k.kode_vaksin = v.kode
        WHERE k.kode_vaksin IS NOT NULL
          AND k.no_identitas_klien = %s
    """
    params = [no_identitas_klien]

    if pet_filter:
        query += " AND h.nama = %s"
        params.append(pet_filter)

    if vaksin_filter:
        query += " AND v.nama = %s"
        params.append(vaksin_filter)

    with connection.cursor() as cursor:
        cursor.execute(query, params)
        data = cursor.fetchall()

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

    return render(request, 'history_vac.html', {
        'results': results,
        'pet_filter': pet_filter,
        'vaksin_filter': vaksin_filter,
        'pet_options': pet_options,
        'vaksin_options': vaksin_options,
    })