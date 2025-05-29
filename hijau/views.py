from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods
from main.models import Hewan, Klien, Perawatan, Kunjungan, TenagaMedis, DokterHewan, PerawatHewan, FrontDesk, Pegawai, KunjunganKeperawatan, User
import uuid
from django.utils import timezone
from django.db import connection

def is_role(request, role_name):
    id_key = {
        "dokter": "no_tenaga_medis",
        "perawat": "no_tenaga_medis",
        "frontdesk": "no_front_desk"
    }.get(role_name)

    value = request.session.get(id_key)
    if not value:
        return False

    table_map = {
        "dokter": 'DOKTER_HEWAN',
        "perawat": 'PERAWAT_HEWAN',
        "frontdesk": 'FRONT_DESK'
    }

    with connection.cursor() as cursor:
        cursor.execute(f"""
            SELECT EXISTS (
                SELECT 1 FROM pet_clinic."{table_map[role_name]}"
                WHERE {id_key} = %s
            )
        """, [value])
        return cursor.fetchone()[0]

# Treatment views

def create_treatment_view(request):
    if request.method == "POST":
        id_kunjungan = request.POST.get("id_kunjungan")
        kode_perawatan = request.POST.get("kode_perawatan")
        catatan = request.POST.get("catatan")

        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    UPDATE pet_clinic."KUNJUNGAN"
                    SET catatan = %s
                    WHERE id_kunjungan = %s
                """, [catatan, id_kunjungan])

                cursor.execute("""
                    INSERT INTO pet_clinic."KUNJUNGAN_KEPERAWATAN" (
                        id_kunjungan, nama_hewan, no_identitas_klien,
                        no_front_desk, no_perawat_hewan, no_dokter_hewan, kode_perawatan
                    )
                    SELECT id_kunjungan, nama_hewan, no_identitas_klien,
                           no_front_desk, no_perawat_hewan, no_dokter_hewan, %s
                    FROM pet_clinic."KUNJUNGAN"
                    WHERE id_kunjungan = %s
                """, [kode_perawatan, id_kunjungan])

            return redirect('hijau:table_treatment')

        except Exception as e:
            return render(request, 'create_treatment.html', {
                'error': str(e),
                'kunjungan_list': get_kunjungan_dropdown_data(),
                'perawatan_list': get_perawatan_dropdown_data()
            })

    return render(request, 'create_treatment.html', {
        'kunjungan_list': get_kunjungan_dropdown_data(),
        'perawatan_list': get_perawatan_dropdown_data()
    })

def update_treatment_view(request, id_kunjungan):
    if request.method == "POST":
        kode_perawatan = request.POST.get("kode_perawatan")
        catatan = request.POST.get("catatan")

        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    UPDATE pet_clinic."KUNJUNGAN_KEPERAWATAN"
                    SET kode_perawatan = %s
                    WHERE id_kunjungan = %s
                """, [kode_perawatan, id_kunjungan])

                cursor.execute("""
                    UPDATE pet_clinic."KUNJUNGAN"
                    SET catatan = %s
                    WHERE id_kunjungan = %s
                """, [catatan, id_kunjungan])

            return redirect('hijau:table_treatment')

        except Exception as e:
            return HttpResponse(f"Error saat update: {e}")

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT k.kode_perawatan, p.nama_perawatan, u.catatan,
                   u.id_kunjungan, u.nama_hewan, u.no_identitas_klien,
                   u.no_front_desk, u.no_dokter_hewan, u.no_perawat_hewan
            FROM pet_clinic."KUNJUNGAN_KEPERAWATAN" k
            JOIN pet_clinic."PERAWATAN" p ON k.kode_perawatan = p.kode_perawatan
            JOIN pet_clinic."KUNJUNGAN" u ON u.id_kunjungan = k.id_kunjungan
            WHERE k.id_kunjungan = %s
        """, [id_kunjungan])
        row = cursor.fetchone()

    if not row:
        return HttpResponse("Data tidak ditemukan.")

    return render(request, 'update_treatment.html', {
        'treatment': {
            'kode_perawatan': row[0],
            'nama_perawatan': row[1]
        },
        'catatan': row[2],
        'kunjungan': {
            'id_kunjungan': row[3],
            'nama_hewan': row[4],
            'no_identitas_klien': row[5]
        },
        'email_frontdesk': get_email_by_pegawai(row[6]),
        'email_dokter': get_email_by_pegawai(row[7]),
        'email_perawat': get_email_by_pegawai(row[8]),
        'perawatan_list': get_perawatan_dropdown_data()
    })

def delete_treatment_view(request, id_kunjungan, kode_perawatan):
    if request.method == "POST":
        with connection.cursor() as cursor:
            cursor.execute("""
                DELETE FROM pet_clinic."KUNJUNGAN_KEPERAWATAN"
                WHERE id_kunjungan = %s AND kode_perawatan = %s
            """, [id_kunjungan, kode_perawatan])
        return redirect('hijau:table_treatment')

    return render(request, 'delete_treatment.html', {
        'treatment': {
            'id_kunjungan': id_kunjungan,
            'kode_perawatan': kode_perawatan
        }
    })

def table_treatment_view(request):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT kk.id_kunjungan, kk.nama_hewan, kk.no_identitas_klien,
                   kk.no_perawat_hewan, kk.no_dokter_hewan, kk.no_front_desk,
                   kk.kode_perawatan, p.nama_perawatan, k.catatan
            FROM pet_clinic."KUNJUNGAN_KEPERAWATAN" kk
            LEFT JOIN pet_clinic."PERAWATAN" p ON kk.kode_perawatan = p.kode_perawatan
            LEFT JOIN pet_clinic."KUNJUNGAN" k ON k.id_kunjungan = kk.id_kunjungan
        """)
        records = cursor.fetchall()

    treatment_list = []
    for i, row in enumerate(records):
        treatment_list.append({
            "no": i + 1,
            "id_kunjungan": str(row[0]),
            "nama_hewan": row[1],
            "id_klien": row[2],
            "perawat": row[3],
            "dokter": row[4],
            "frontdesk": row[5],
            "kode_perawatan": row[6],
            "jenis_perawatan": f"{row[6]} - {row[7]}" if row[7] else "-",
            "catatan_medis": row[8] or "-"
        })

    return render(request, 'table_treatment.html', {
        'treatment_list': treatment_list
    })

def treatment_views(request, action):
    if action == 'create':
        return render(request, 'create_treatment.html')
    elif action == 'update':
        return render(request, 'update_treatment.html')
    elif action == 'delete':
        return render(request, 'delete_treatment.html')
    else:
        return HttpResponse('Invalid action')

# === HELPERS ===
def get_email_by_pegawai(no_pegawai):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT u.email
            FROM pet_clinic."PEGAWAI" p
            JOIN pet_clinic."USER" u ON u.email = p.email_user
            WHERE p.no_pegawai = %s
        """, [no_pegawai])
        row = cursor.fetchone()
    return row[0] if row else "-"

def get_perawatan_dropdown_data():
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT kode_perawatan, nama_perawatan
            FROM pet_clinic."PERAWATAN"
        """)
        rows = cursor.fetchall()
    return [{"kode_perawatan": r[0], "nama_perawatan": r[1]} for r in rows]

def get_kunjungan_dropdown_data():
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT id_kunjungan, nama_hewan, no_identitas_klien, no_front_desk, no_dokter_hewan, no_perawat_hewan
            FROM pet_clinic."KUNJUNGAN"
        """)
        rows = cursor.fetchall()

    result = []
    for row in rows:
        result.append({
            "id_kunjungan": row[0],
            "nama_hewan": row[1],
            "no_identitas_klien": row[2],
            "frontdesk_email": get_email_by_pegawai(row[3]),
            "dokter_email": get_email_by_pegawai(row[4]),
            "perawat_email": get_email_by_pegawai(row[5]),
        })
    return result

# Kunjungan views

def get_klien_dropdown_data():
    with connection.cursor() as cursor:
        cursor.execute("""SELECT no_identitas FROM pet_clinic."KLIEN" """)
        return [{"no_identitas": row[0]} for row in cursor.fetchall()]

def get_hewan_dropdown_data():
    with connection.cursor() as cursor:
        cursor.execute("""SELECT nama FROM pet_clinic."HEWAN" """)
        return [{"nama": row[0]} for row in cursor.fetchall()]

def get_dokter_dropdown_data():
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT p.no_pegawai, u.email
            FROM pet_clinic."PEGAWAI" p
            JOIN pet_clinic."USER" u ON p.email_user = u.email
            WHERE u.role = 'dokter'
        """)
        return [{"no_dokter_hewan": row[0], "nama": row[1]} for row in cursor.fetchall()]

def get_perawat_dropdown_data():
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT p.no_pegawai, u.email
            FROM pet_clinic."PEGAWAI" p
            JOIN pet_clinic."USER" u ON p.email_user = u.email
            WHERE u.role = 'perawat'
        """)
        return [{"no_perawat_hewan": row[0], "nama": row[1]} for row in cursor.fetchall()]

def create_kunjungan_view(request):
    if request.method == "POST":
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO pet_clinic."KUNJUNGAN" (
                        id_kunjungan, nama_hewan, no_identitas_klien,
                        no_front_desk, no_perawat_hewan, no_dokter_hewan,
                        tipe_kunjungan, timestamp_awal, timestamp_akhir, suhu,
                        berat_badan, catatan
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, [
                    str(uuid.uuid4()),
                    request.POST.get("nama_hewan"),
                    request.POST.get("no_identitas_klien"),
                    request.session.get("no_pegawai"),
                    request.POST.get("no_perawat_hewan"),
                    request.POST.get("no_dokter_hewan"),
                    request.POST.get("tipe_kunjungan"),
                    request.POST.get("timestamp_awal"),
                    request.POST.get("timestamp_akhir"),
                    request.POST.get("suhu"),
                    request.POST.get("berat_badan"),
                    request.POST.get("catatan")
                ])
            return redirect("hijau:table_kunjungan")
        except Exception as e:
            return HttpResponse(f"Gagal menambahkan kunjungan: {e}")

    with connection.cursor() as cursor:
        cursor.execute("SELECT no_identitas FROM pet_clinic.\"KLIEN\"")
        klien_list = [{"no_identitas": row[0]} for row in cursor.fetchall()]

        cursor.execute("SELECT nama FROM pet_clinic.\"HEWAN\"")
        hewan_list = [{"nama": row[0]} for row in cursor.fetchall()]

        cursor.execute("""
            SELECT p.no_pegawai, p.email_user FROM pet_clinic."DOKTER_HEWAN" d
            JOIN pet_clinic."TENAGA_MEDIS" t ON d.no_tenaga_medis = t.no_tenaga_medis
            JOIN pet_clinic."PEGAWAI" p ON t.no_pegawai = p.no_pegawai
        """)
        dokter_list = [{"no_dokter_hewan": row[0], "nama": row[1]} for row in cursor.fetchall()]

        cursor.execute("""
            SELECT p.no_pegawai, p.email_user FROM pet_clinic."PERAWAT_HEWAN" pr
            JOIN pet_clinic."TENAGA_MEDIS" t ON pr.no_tenaga_medis = t.no_tenaga_medis
            JOIN pet_clinic."PEGAWAI" p ON t.no_pegawai = p.no_pegawai
        """)
        perawat_list = [{"no_perawat_hewan": row[0], "nama": row[1]} for row in cursor.fetchall()]

    return render(request, "create_kunjungan.html", {
        "klien_list": klien_list,
        "hewan_list": hewan_list,
        "dokter_list": dokter_list,
        "perawat_list": perawat_list
    })

def update_kunjungan_view(request, id_kunjungan):
    if request.method == "POST":
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    UPDATE pet_clinic."KUNJUNGAN"
                    SET nama_hewan = %s, no_identitas_klien = %s,
                        no_front_desk = %s, no_perawat_hewan = %s,
                        no_dokter_hewan = %s, tipe_kunjungan = %s,
                        timestamp_awal = %s, timestamp_akhir = %s,
                        suhu = %s, berat_badan = %s, catatan = %s
                    WHERE id_kunjungan = %s
                """, [
                    request.POST.get("nama_hewan"),
                    request.POST.get("no_identitas_klien"),
                    request.session.get("no_pegawai"),
                    request.POST.get("no_perawat_hewan"),
                    request.POST.get("no_dokter_hewan"),
                    request.POST.get("tipe_kunjungan"),
                    request.POST.get("timestamp_awal"),
                    request.POST.get("timestamp_akhir"),
                    request.POST.get("suhu"),
                    request.POST.get("berat_badan"),
                    request.POST.get("catatan"),
                    id_kunjungan
                ])
            return redirect("hijau:table_kunjungan")
        except Exception as e:
            return HttpResponse(f"Gagal mengubah kunjungan: {e}")

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT nama_hewan, no_identitas_klien, no_dokter_hewan, no_perawat_hewan,
                   tipe_kunjungan, timestamp_awal, timestamp_akhir,
                   suhu, berat_badan, catatan
            FROM pet_clinic."KUNJUNGAN"
            WHERE id_kunjungan = %s
        """, [id_kunjungan])
        row = cursor.fetchone()

        if not row:
            return HttpResponse("Kunjungan tidak ditemukan")

        cursor.execute("""
            SELECT p.no_pegawai, p.email_user FROM pet_clinic."DOKTER_HEWAN" d
            JOIN pet_clinic."TENAGA_MEDIS" t ON d.no_tenaga_medis = t.no_tenaga_medis
            JOIN pet_clinic."PEGAWAI" p ON t.no_pegawai = p.no_pegawai
        """)
        dokter_list = [{"no_dokter_hewan": r[0], "nama": r[1]} for r in cursor.fetchall()]

        cursor.execute("""
            SELECT p.no_pegawai, p.email_user FROM pet_clinic."PERAWAT_HEWAN" pr
            JOIN pet_clinic."TENAGA_MEDIS" t ON pr.no_tenaga_medis = t.no_tenaga_medis
            JOIN pet_clinic."PEGAWAI" p ON t.no_pegawai = p.no_pegawai
        """)
        perawat_list = [{"no_perawat_hewan": r[0], "nama": r[1]} for r in cursor.fetchall()]

    return render(request, 'update_kunjungan.html', {
        "kunjungan": {
            "id_kunjungan": id_kunjungan,
            "nama_hewan": row[0],
            "no_identitas_klien": row[1],
            "no_dokter_hewan": row[2],
            "no_perawat_hewan": row[3],
            "tipe_kunjungan": row[4],
            "timestamp_awal": row[5],
            "timestamp_akhir": row[6],
            "suhu": row[7],
            "berat_badan": row[8],
            "catatan": row[9],
        },
        "dokter_list": dokter_list,
        "perawat_list": perawat_list
    })

def delete_kunjungan_view(request, id_kunjungan):
    if request.method == "POST":
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    DELETE FROM pet_clinic."KUNJUNGAN"
                    WHERE id_kunjungan = %s
                """, [id_kunjungan])
            return redirect("hijau:table_kunjungan")
        except Exception as e:
            return HttpResponse(f"Gagal menghapus kunjungan: {e}")

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT id_kunjungan, nama_hewan
            FROM pet_clinic."KUNJUNGAN"
            WHERE id_kunjungan = %s
        """, [id_kunjungan])
        row = cursor.fetchone()

    if not row:
        return HttpResponse("Kunjungan tidak ditemukan")

    return render(request, 'delete_kunjungan.html', {
        "kunjungan": {
            "id_kunjungan": row[0],
            "nama_hewan": row[1]
        }
    })

def table_kunjungan_view(request):
    # if not (is_role(request, 'dokter') or is_role(request, 'frontdesk')):
    #     return redirect('authentication:login')

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT id_kunjungan, no_identitas_klien, nama_hewan,
                   tipe_kunjungan, timestamp_awal, timestamp_akhir
            FROM pet_clinic."KUNJUNGAN"
        """)
        records = cursor.fetchall()

    data = []
    for i, record in enumerate(records):
        data.append({
            "no": i + 1,
            "id_kunjungan": record[0],
            "no_identitas_klien": record[1],
            "nama_hewan": record[2],
            "tipe_kunjungan": record[3],
            "timestamp_awal": record[4],
            "timestamp_akhir": record[5],
        })

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


