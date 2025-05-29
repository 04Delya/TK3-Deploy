from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import connection
import uuid
from datetime import date

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        with connection.cursor() as cursor:
            cursor.execute('SELECT password FROM pet_clinic."USER" WHERE email = %s', [email])
            user = cursor.fetchone()
            if not user:
                messages.error(request, 'Email tidak ditemukan.')
                return render(request, 'login.html')

            if user[0] != password:
                messages.error(request, 'Password salah.')
                return render(request, 'login.html')

            request.session['user_email'] = email

            # PEGAWAI
            cursor.execute('SELECT no_pegawai FROM pet_clinic."PEGAWAI" WHERE email_user = %s', [email])
            pegawai = cursor.fetchone()
            if pegawai:
                request.session['pegawai_id'] = str(pegawai[0])

                cursor.execute('SELECT no_tenaga_medis FROM pet_clinic."TENAGA_MEDIS" WHERE no_pegawai = %s', [pegawai[0]])
                tenaga = cursor.fetchone()
                if tenaga:
                    request.session['no_tenaga_medis'] = str(tenaga[0])

                    cursor.execute('SELECT no_dokter_hewan FROM pet_clinic."DOKTER_HEWAN" WHERE no_tenaga_medis = %s', [tenaga[0]])
                    dokter = cursor.fetchone()
                    if dokter:
                        request.session['role'] = 'dokter'
                        request.session['no_dokter_hewan'] = str(dokter[0])
                        return redirect('main:landing_page')

                    cursor.execute('SELECT no_perawat_hewan FROM pet_clinic."PERAWAT_HEWAN" WHERE no_tenaga_medis = %s', [tenaga[0]])
                    perawat = cursor.fetchone()
                    if perawat:
                        request.session['role'] = 'perawat'
                        request.session['no_perawat_hewan'] = str(perawat[0])
                        return redirect('main:landing_page')

                cursor.execute('SELECT no_front_desk FROM pet_clinic."FRONT_DESK" WHERE no_pegawai = %s', [pegawai[0]])
                frontdesk = cursor.fetchone()
                if frontdesk:
                    request.session['role'] = 'frontdesk'
                    request.session['no_front_desk'] = str(frontdesk[0])
                    return redirect('main:landing_page')

            # KLIEN
            cursor.execute('SELECT no_identitas FROM pet_clinic."KLIEN" WHERE email = %s', [email])
            klien = cursor.fetchone()
            if klien:
                request.session['klien_id'] = str(klien[0])

                cursor.execute('SELECT 1 FROM pet_clinic."INDIVIDU" WHERE no_identitas_klien = %s', [klien[0]])
                if cursor.fetchone():
                    request.session['role'] = 'individu'
                    return redirect('main:landing_page')

                cursor.execute('SELECT 1 FROM pet_clinic."PERUSAHAAN" WHERE no_identitas_klien = %s', [klien[0]])
                if cursor.fetchone():
                    request.session['role'] = 'perusahaan'
                    return redirect('main:landing_page')

            messages.error(request, 'Akun tidak memiliki role yang valid.')
            return render(request, 'login.html')

    return render(request, 'login.html')


def register_individual(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        nama_depan = request.POST.get('nama_depan')
        nama_tengah = request.POST.get('nama_tengah')
        nama_belakang = request.POST.get('nama_belakang')
        telepon = request.POST.get('telepon')
        alamat = request.POST.get('alamat')

        if not all([email, password, nama_depan, nama_belakang, telepon, alamat]):
            messages.error(request, 'Semua field wajib harus diisi.')
            return render(request, 'register_individual.html')

        with connection.cursor() as cursor:
            cursor.execute('SELECT 1 FROM pet_clinic."USER" WHERE email = %s', [email])
            if cursor.fetchone():
                messages.error(request, 'Email sudah terdaftar.')
                return render(request, 'register_individual.html')

            try:
                no_identitas = str(uuid.uuid4())

                cursor.execute("""
                    INSERT INTO pet_clinic."USER"(email, password, alamat, nomor_telepon)
                    VALUES (%s, %s, %s, %s)
                """, [email, password, alamat, telepon])

                cursor.execute("""
                    INSERT INTO pet_clinic."KLIEN"(no_identitas, tanggal_registrasi, email)
                    VALUES (%s, %s, %s)
                """, [no_identitas, date.today(), email])

                cursor.execute("""
                    INSERT INTO pet_clinic."INDIVIDU"(no_identitas_klien, nama_depan, nama_tengah, nama_belakang)
                    VALUES (%s, %s, %s, %s)
                """, [no_identitas, nama_depan, nama_tengah, nama_belakang])

                messages.success(request, 'Registrasi berhasil! Silakan login.')
                return redirect('authentication:login')
            except Exception as e:
                messages.error(request, f'Terjadi kesalahan: {str(e)}')
                return render(request, 'register_individual.html')

    return render(request, 'register_individual.html')


def register_company(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        nama_perusahaan = request.POST.get('nama_perusahaan')
        telepon = request.POST.get('telepon')
        alamat = request.POST.get('alamat')

        if not all([email, password, nama_perusahaan, telepon, alamat]):
            messages.error(request, 'Semua field wajib harus diisi.')
            return render(request, 'register_company.html')

        with connection.cursor() as cursor:
            cursor.execute('SELECT 1 FROM "pet_clinic"."USER" WHERE email = %s', [email])
            if cursor.fetchone():
                messages.error(request, 'Email sudah terdaftar.')
                return render(request, 'register_company.html')

            try:
                klien_id = str(uuid.uuid4())
                cursor.execute('BEGIN')
                cursor.execute("""
                    INSERT INTO "pet_clinic"."USER"(email, password, alamat, nomor_telepon)
                    VALUES (%s, %s, %s, %s)
                """, [email, password, alamat, telepon])
                cursor.execute("""
                    INSERT INTO "pet_clinic"."KLIEN"(no_identitas, tanggal_registrasi, email)
                    VALUES (%s, %s, %s)
                """, [klien_id, date.today(), email])
                cursor.execute("""
                    INSERT INTO "pet_clinic"."PERUSAHAAN"(no_identitas_klien, nama_perusahaan)
                    VALUES (%s, %s)
                """, [klien_id, nama_perusahaan])
                cursor.execute('COMMIT')

                messages.success(request, 'Registrasi berhasil! Silakan login.')
                return redirect('authentication:login')
            except Exception as e:
                cursor.execute('ROLLBACK')
                messages.error(request, f'Terjadi kesalahan: {str(e)}')
                return render(request, 'register_company.html')

    return render(request, 'register_company.html')


def register_frontdesk(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        telepon = request.POST.get('telepon')
        tanggal_diterima = request.POST.get('tanggal_diterima')
        alamat = request.POST.get('alamat')

        if not all([email, password, telepon, tanggal_diterima, alamat]):
            messages.error(request, 'Semua field wajib harus diisi.')
            return render(request, 'register_frontdesk.html')

        with connection.cursor() as cursor:
            cursor.execute('SELECT 1 FROM "pet_clinic"."USER" WHERE email = %s', [email])
            if cursor.fetchone():
                messages.error(request, 'Email sudah terdaftar.')
                return render(request, 'register_frontdesk.html')

            try:
                pegawai_id = str(uuid.uuid4())
                frontdesk_id = str(uuid.uuid4())

                cursor.execute('BEGIN')
                cursor.execute("""
                    INSERT INTO "pet_clinic"."USER"(email, password, alamat, nomor_telepon)
                    VALUES (%s, %s, %s, %s)
                """, [email, password, alamat, telepon])
                cursor.execute("""
                    INSERT INTO "pet_clinic"."PEGAWAI"(no_pegawai, tanggal_mulai_kerja, email_user)
                    VALUES (%s, %s, %s)
                """, [pegawai_id, tanggal_diterima, email])
                cursor.execute("""
                    INSERT INTO "pet_clinic"."FRONT_DESK"(no_front_desk, no_pegawai)
                    VALUES (%s, %s)
                """, [frontdesk_id, pegawai_id])
                cursor.execute('COMMIT')

                messages.success(request, 'Registrasi berhasil! Silakan login.')
                return redirect('authentication:login')
            except Exception as e:
                cursor.execute('ROLLBACK')
                messages.error(request, f'Terjadi kesalahan: {str(e)}')
                return render(request, 'register_frontdesk.html')

    return render(request, 'register_frontdesk.html')


def register_vet(request):
    if request.method == 'POST':
        no_izin = request.POST.get('no_izin')
        email = request.POST.get('email')
        password = request.POST.get('password')
        telepon = request.POST.get('telepon')
        tanggal_diterima = request.POST.get('tanggal_diterima')
        alamat = request.POST.get('alamat')

        if not all([no_izin, email, password, telepon, tanggal_diterima, alamat]):
            messages.error(request, 'Semua field wajib harus diisi.')
            return render(request, 'register_vet.html')

        with connection.cursor() as cursor:
            cursor.execute('SELECT 1 FROM "pet_clinic"."USER" WHERE email = %s', [email])
            if cursor.fetchone():
                messages.error(request, 'Email sudah terdaftar.')
                return render(request, 'register_vet.html')

            try:
                pegawai_id = str(uuid.uuid4())
                tenaga_id = str(uuid.uuid4())
                dokter_id = str(uuid.uuid4())

                cursor.execute('BEGIN')
                cursor.execute("""
                    INSERT INTO "pet_clinic"."USER"(email, password, alamat, nomor_telepon)
                    VALUES (%s, %s, %s, %s)
                """, [email, password, alamat, telepon])
                cursor.execute("""
                    INSERT INTO "pet_clinic"."PEGAWAI"(no_pegawai, tanggal_mulai_kerja, email_user)
                    VALUES (%s, %s, %s)
                """, [pegawai_id, tanggal_diterima, email])
                cursor.execute("""
                    INSERT INTO "pet_clinic"."TENAGA_MEDIS"(no_tenaga_medis, no_pegawai, no_izin_praktik)
                    VALUES (%s, %s, %s)
                """, [tenaga_id, pegawai_id, no_izin])
                cursor.execute("""
                    INSERT INTO "pet_clinic"."DOKTER_HEWAN"(no_dokter_hewan, no_tenaga_medis)
                    VALUES (%s, %s)
                """, [dokter_id, tenaga_id])
                cursor.execute('COMMIT')

                messages.success(request, 'Registrasi berhasil! Silakan login.')
                return redirect('authentication:login')

            except Exception as e:
                cursor.execute('ROLLBACK')
                messages.error(request, f'Terjadi kesalahan: {str(e)}')
                return render(request, 'register_vet.html')

    return render(request, 'register_vet.html')


def register_nurse(request):
    if request.method == 'POST':
        no_izin = request.POST.get('no_izin')
        email = request.POST.get('email')
        password = request.POST.get('password')
        telepon = request.POST.get('telepon')
        tanggal_diterima = request.POST.get('tanggal_diterima')
        alamat = request.POST.get('alamat')

        if not all([no_izin, email, password, telepon, tanggal_diterima, alamat]):
            messages.error(request, 'Semua field wajib harus diisi.')
            return render(request, 'register_nurse.html')

        with connection.cursor() as cursor:
            cursor.execute('SELECT 1 FROM "pet_clinic"."USER" WHERE email = %s', [email])
            if cursor.fetchone():
                messages.error(request, 'Email sudah terdaftar.')
                return render(request, 'register_nurse.html')

            try:
                pegawai_id = str(uuid.uuid4())
                tenaga_id = str(uuid.uuid4())
                perawat_id = str(uuid.uuid4())

                cursor.execute('BEGIN')
                cursor.execute("""
                    INSERT INTO "pet_clinic"."USER"(email, password, alamat, nomor_telepon)
                    VALUES (%s, %s, %s, %s)
                """, [email, password, alamat, telepon])
                cursor.execute("""
                    INSERT INTO "pet_clinic"."PEGAWAI"(no_pegawai, tanggal_mulai_kerja, email_user)
                    VALUES (%s, %s, %s)
                """, [pegawai_id, tanggal_diterima, email])
                cursor.execute("""
                    INSERT INTO "pet_clinic"."TENAGA_MEDIS"(no_tenaga_medis, no_pegawai, no_izin_praktik)
                    VALUES (%s, %s, %s)
                """, [tenaga_id, pegawai_id, no_izin])
                cursor.execute("""
                    INSERT INTO "pet_clinic"."PERAWAT_HEWAN"(no_perawat_hewan, no_tenaga_medis)
                    VALUES (%s, %s)
                """, [perawat_id, tenaga_id])
                cursor.execute('COMMIT')

                messages.success(request, 'Registrasi berhasil! Silakan login.')
                return redirect('authentication:login')

            except Exception as e:
                cursor.execute('ROLLBACK')
                messages.error(request, f'Terjadi kesalahan: {str(e)}')
                return render(request, 'register_nurse.html')

    return render(request, 'register_nurse.html')


def logout_view(request):
    request.session.flush()
    messages.success(request, "Anda berhasil logout.")
    return redirect('main:landing_page')
