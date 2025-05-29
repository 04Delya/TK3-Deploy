from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import connection, transaction
from main.models import User, Pegawai, TenagaMedis, DokterHewan, PerawatHewan, FrontDesk, Klien, Individu, Perusahaan
import uuid
from datetime import date
import psycopg2


def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            user = User.objects.get(email=email)
            if user.password == password:
                request.session['user_email'] = email

                pegawai = Pegawai.objects.filter(email_user=email).first()
                if pegawai:
                    request.session['pegawai_id'] = str(pegawai.no_pegawai)

                    tenaga = TenagaMedis.objects.filter(no_pegawai=pegawai.no_pegawai).first()
                    if tenaga:
                        request.session['no_tenaga_medis'] = str(tenaga.no_tenaga_medis)

                        dokter = DokterHewan.objects.filter(no_tenaga_medis=tenaga.no_tenaga_medis).first()
                        if dokter:
                            request.session['role'] = 'dokter'
                            request.session['no_dokter_hewan'] = str(dokter.no_dokter_hewan)
                            return redirect('main:landing_page')

                        perawat = PerawatHewan.objects.filter(no_tenaga_medis=tenaga.no_tenaga_medis).first()
                        if perawat:
                            request.session['role'] = 'perawat'
                            request.session['no_perawat_hewan'] = str(perawat.no_perawat_hewan)
                            return redirect('main:landing_page')

                    frontdesk = FrontDesk.objects.filter(no_pegawai=pegawai.no_pegawai).first()
                    if frontdesk:
                        request.session['role'] = 'frontdesk'
                        request.session['no_front_desk'] = str(frontdesk.no_front_desk)
                        return redirect('main:landing_page')

                klien = Klien.objects.filter(email=email).first()
                if klien:
                    request.session['klien_id'] = str(klien.no_identitas)

                    if Individu.objects.filter(no_identitas_klien=klien.no_identitas).exists():
                        request.session['role'] = 'individu'
                        return redirect('main:landing_page')

                    if Perusahaan.objects.filter(no_identitas_klien=klien.no_identitas).exists():
                        request.session['role'] = 'perusahaan'
                        return redirect('main:landing_page')

                messages.error(request, 'Akun tidak memiliki role yang valid.')
            else:
                messages.error(request, 'Password salah.')
        except User.DoesNotExist:
            messages.error(request, 'Email tidak ditemukan.')
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

        try:
            with transaction.atomic():
                # Insert user, trigger validasi email di DB akan jalan
                user = User.objects.create(
                    email=email,
                    password=password,
                    alamat=alamat,
                    nomor_telepon=telepon
                )

                klien_id = uuid.uuid4()
                klien = Klien.objects.create(
                    no_identitas=klien_id,
                    tanggal_registrasi=date.today(),
                    email=email
                )
                individu = Individu.objects.create(
                    no_identitas_klien=klien_id,
                    nama_depan=nama_depan,
                    nama_tengah=nama_tengah,
                    nama_belakang=nama_belakang
                )

                messages.success(request, 'Registrasi berhasil! Silakan login.')
                return redirect('authentication:login')

        except DatabaseError as e:
            # Tangkap pesan error trigger dan tampilkan
            err_msg = str(e)
            # Optional: ekstrak pesan dari err_msg untuk tampil lebih bersih
            messages.error(request, err_msg)
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

        klien_id = uuid.uuid4()
        try:
            with transaction.atomic():
                with connection.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO pet_clinic."USER" (email, password, alamat, nomor_telepon)
                        VALUES (%s, %s, %s, %s)
                    """, (email, password, alamat, telepon))

                    cursor.execute("""
                        INSERT INTO pet_clinic."KLIEN" (no_identitas, tanggal_registrasi, email)
                        VALUES (%s, %s, %s)
                    """, (str(klien_id), date.today(), email))

                    cursor.execute("""
                        INSERT INTO pet_clinic."PERUSAHAAN" (no_identitas_klien, nama_perusahaan)
                        VALUES (%s, %s)
                    """, (str(klien_id), nama_perusahaan))

            messages.success(request, 'Registrasi berhasil! Silakan login.')
            return redirect('authentication:login')

        except psycopg2.Error as e:
            messages.error(request, e.pgerror or str(e))
            return render(request, 'register_company.html')

    return render(request, 'register_company.html')

def register_selection(request):
    return render(request, 'register.html')

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

        pegawai_id = uuid.uuid4()
        try:
            with transaction.atomic():
                with connection.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO pet_clinic."USER" (email, password, alamat, nomor_telepon)
                        VALUES (%s, %s, %s, %s)
                    """, (email, password, alamat, telepon))

                    cursor.execute("""
                        INSERT INTO pet_clinic."PEGAWAI" (no_pegawai, tanggal_mulai_kerja, email_user)
                        VALUES (%s, %s, %s)
                    """, (str(pegawai_id), tanggal_diterima, email))

                    cursor.execute("""
                        INSERT INTO pet_clinic."FRONT_DESK" (no_front_desk, no_pegawai)
                        VALUES (%s, %s)
                    """, (str(uuid.uuid4()), str(pegawai_id)))

            messages.success(request, 'Registrasi berhasil! Silakan login.')
            return redirect('authentication:login')

        except psycopg2.Error as e:
            messages.error(request, e.pgerror or str(e))
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

        pegawai_id = uuid.uuid4()
        tenaga_medis_id = uuid.uuid4()
        try:
            with transaction.atomic():
                with connection.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO pet_clinic."USER" (email, password, alamat, nomor_telepon)
                        VALUES (%s, %s, %s, %s)
                    """, (email, password, alamat, telepon))

                    cursor.execute("""
                        INSERT INTO pet_clinic."PEGAWAI" (no_pegawai, tanggal_mulai_kerja, email_user)
                        VALUES (%s, %s, %s)
                    """, (str(pegawai_id), tanggal_diterima, email))

                    cursor.execute("""
                        INSERT INTO pet_clinic."TENAGA_MEDIS" (no_tenaga_medis, no_pegawai, no_izin_praktik)
                        VALUES (%s, %s, %s)
                    """, (str(tenaga_medis_id), str(pegawai_id), no_izin))

                    cursor.execute("""
                        INSERT INTO pet_clinic."DOKTER_HEWAN" (no_dokter_hewan, no_tenaga_medis)
                        VALUES (%s, %s)
                    """, (str(uuid.uuid4()), str(tenaga_medis_id)))

            messages.success(request, 'Registrasi berhasil! Silakan login.')
            return redirect('authentication:login')

        except psycopg2.Error as e:
            messages.error(request, e.pgerror or str(e))
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

        pegawai_id = uuid.uuid4()
        tenaga_medis_id = uuid.uuid4()
        try:
            with transaction.atomic():
                with connection.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO pet_clinic."USER" (email, password, alamat, nomor_telepon)
                        VALUES (%s, %s, %s, %s)
                    """, (email, password, alamat, telepon))

                    cursor.execute("""
                        INSERT INTO pet_clinic."PEGAWAI" (no_pegawai, tanggal_mulai_kerja, email_user)
                        VALUES (%s, %s, %s)
                    """, (str(pegawai_id), tanggal_diterima, email))

                    cursor.execute("""
                        INSERT INTO pet_clinic."TENAGA_MEDIS" (no_tenaga_medis, no_pegawai, no_izin_praktik)
                        VALUES (%s, %s, %s)
                    """, (str(tenaga_medis_id), str(pegawai_id), no_izin))

                    cursor.execute("""
                        INSERT INTO pet_clinic."PERAWAT_HEWAN" (no_perawat_hewan, no_tenaga_medis)
                        VALUES (%s, %s)
                    """, (str(uuid.uuid4()), str(tenaga_medis_id)))

            messages.success(request, 'Registrasi berhasil! Silakan login.')
            return redirect('authentication:login')

        except psycopg2.Error as e:
            messages.error(request, e.pgerror or str(e))
            return render(request, 'register_nurse.html')

    return render(request, 'register_nurse.html')


def logout_view(request):
    request.session.flush()
    messages.success(request, "Anda berhasil logout.")
    return redirect('main:landing_page')
