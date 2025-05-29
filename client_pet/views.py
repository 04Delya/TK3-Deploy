from django.shortcuts import render, redirect
from main.models import Klien, Individu, Perusahaan, Hewan, Pegawai, FrontDesk, JenisHewan
from django.db import connection

def client_list(request):
    email = request.session.get("user_email")

    # Validasi user adalah front desk (dari tabel PEGAWAI dan FRONT_DESK)
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 1 FROM "pet_clinic"."PEGAWAI" p
            JOIN "pet_clinic"."FRONT_DESK" f ON p.no_pegawai = f.no_pegawai
            WHERE p.email_user = %s
        """, [email])
        if not cursor.fetchone():
            return redirect("authentication:login")

    # Ambil parameter search
    q = request.GET.get("q", "").strip().lower()

    # SQL query gabungan dari INDIVIDU dan PERUSAHAAN
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT k.no_identitas, k.email,
                   TRIM(COALESCE(i.nama_depan, '') || ' ' || COALESCE(i.nama_tengah, '') || ' ' || COALESCE(i.nama_belakang, '')) AS nama,
                   'Individu' AS jenis
            FROM "pet_clinic"."KLIEN" k
            JOIN "pet_clinic"."INDIVIDU" i ON i.no_identitas_klien = k.no_identitas
            WHERE LOWER(i.nama_depan || ' ' || COALESCE(i.nama_tengah, '') || ' ' || i.nama_belakang) LIKE %s

            UNION

            SELECT k.no_identitas, k.email,
                   p.nama_perusahaan AS nama,
                   'Perusahaan' AS jenis
            FROM "pet_clinic"."KLIEN" k
            JOIN "pet_clinic"."PERUSAHAAN" p ON p.no_identitas_klien = k.no_identitas
            WHERE LOWER(p.nama_perusahaan) LIKE %s

            ORDER BY nama ASC
        """, [f"%{q}%", f"%{q}%"])

        rows = cursor.fetchall()

    # Format ke bentuk yang akan dikirim ke template
    clients = [{
        "id": str(row[0]),
        "email": row[1],
        "name": row[2],
        "type": row[3]
    } for row in rows]

    return render(request, "clients_list.html", {"clients": clients})

from django.db import connection
from django.shortcuts import render, redirect
from main.models import Pegawai, FrontDesk

def client_detail(request, cid):
    email = request.session.get("user_email")

    # Validasi bahwa user adalah Front Desk
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 1 FROM "pet_clinic"."PEGAWAI" p
            JOIN "pet_clinic"."FRONT_DESK" f ON p.no_pegawai = f.no_pegawai
            WHERE p.email_user = %s
        """, [email])
        if not cursor.fetchone():
            return redirect("authentication:login")

    with connection.cursor() as cursor:
        # Ambil info klien, cek apakah dia Individu atau Perusahaan
        cursor.execute("""
            SELECT k.no_identitas, k.email, u.alamat, u.nomor_telepon,
                TRIM(COALESCE(i.nama_depan, '') || ' ' || COALESCE(i.nama_tengah, '') || ' ' || COALESCE(i.nama_belakang, '')) AS nama,
                'Individu' AS jenis
            FROM "pet_clinic"."KLIEN" k
            JOIN "pet_clinic"."USER" u ON u.email = k.email
            JOIN "pet_clinic"."INDIVIDU" i ON i.no_identitas_klien = k.no_identitas
            WHERE k.no_identitas = %s

            UNION

            SELECT k.no_identitas, k.email, u.alamat, u.nomor_telepon,
                p.nama_perusahaan AS nama,
                'Perusahaan' AS jenis
            FROM "pet_clinic"."KLIEN" k
            JOIN "pet_clinic"."USER" u ON u.email = k.email
            JOIN "pet_clinic"."PERUSAHAAN" p ON p.no_identitas_klien = k.no_identitas
            WHERE k.no_identitas = %s
        """, [cid, cid])
        client = cursor.fetchone()

    if not client:
        return redirect("client_pet:list")

    client_data = {
        "identity": str(client[0]),
        "email": client[1],
        "address": client[2],
        "phone": client[3],
        "name": client[4],
        "type": client[5],
    }

    # Ambil data hewan peliharaan + jenisnya
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT h.nama, j.nama_jenis, h.tanggal_lahir
            FROM "pet_clinic"."HEWAN" h
            JOIN "pet_clinic"."JENIS_HEWAN" j ON h.id_jenis = j.id
            WHERE h.no_identitas_klien = %s
            ORDER BY h.nama ASC
        """, [cid])
        pets_raw = cursor.fetchall()

    pet_list = [{
        "no": i + 1,
        "name": row[0],
        "species": row[1],
        "dob": row[2]
    } for i, row in enumerate(pets_raw)]

    client_data["pets"] = pet_list

    return render(request, "client_detail.html", {"client": client_data})