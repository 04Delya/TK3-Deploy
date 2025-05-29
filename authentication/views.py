from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import connection, transaction
from main.models import User, Pegawai, TenagaMedis, DokterHewan, PerawatHewan, FrontDesk, Klien, Individu, Perusahaan
import uuid
from datetime import date


def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            user = User.objects.get(email=email)
            if user.password == password:
                request.session['user_email'] = email

                # PEGAWAI ROLE
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

                # KLIEN ROLE
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

# def login_view(request):
#     if request.method == 'POST':
#         email = request.POST.get('email')
#         password = request.POST.get('password')

#         try:
#             user = User.objects.get(email=email)
#             if user.password == password:
#                 request.session['user_email'] = user.email
#                 # Cek role user
#                 if Klien.objects.filter(email=email).exists():
#                     request.session['role'] = 'klien'
#                     return redirect('main:dashboard_klien')
#                 elif Pegawai.objects.filter(email_user=email).exists():
#                     no_pegawai = Pegawai.objects.get(email_user=email).no_pegawai
#                     if DokterHewan.objects.filter(no_tenaga_medis__in=TenagaMedis.objects.filter(no_pegawai=no_pegawai).values_list('no_tenaga_medis', flat=True)).exists():
#                         request.session['role'] = 'dokter'
#                         return redirect('main:dashboard_dokterhewan')
#                     elif PerawatHewan.objects.filter(no_tenaga_medis__in=TenagaMedis.objects.filter(no_pegawai=no_pegawai).values_list('no_tenaga_medis', flat=True)).exists():
#                         request.session['role'] = 'perawat'
#                         return redirect('main:dashboard_perawat')
#                     elif FrontDesk.objects.filter(no_pegawai=no_pegawai).exists():
#                         request.session['role'] = 'frontdesk'
#                         return redirect('main:dashboard_frontdesk')
#             else:
#                 messages.error(request, "Password salah.")
#         except User.DoesNotExist:
#             messages.error(request, "Email tidak ditemukan.")
#     return render(request, 'login.html')

def register_selection(request):
    return render(request, 'register.html')

def register_individual(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        nama_depan = request.POST.get('nama_depan')
        nama_tengah = request.POST.get('nama_tengah')
        nama_belakang = request.POST.get('nama_belakang')
        telepon = request.POST.get('telepon')
        alamat = request.POST.get('alamat')
        
        # Validate required fields
        if not all([email, password, nama_depan, nama_belakang, telepon, alamat]):
            messages.error(request, 'Semua field wajib harus diisi.')
            return render(request, 'register_individual.html')
        
        # Check if user already exists
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email sudah terdaftar.')
            return render(request, 'register_individual.html')
        
        try:
            with transaction.atomic():
                # Create User
                user = User.objects.create(
                    email=email,
                    password=password,  # In production, you should hash this
                    alamat=alamat,
                    nomor_telepon=telepon
                )
                
                # Create Klien
                klien_id = uuid.uuid4()
                klien = Klien.objects.create(
                    no_identitas=klien_id,
                    tanggal_registrasi=date.today(),
                    email=email
                )
                
                # Create Individu
                individu = Individu.objects.create(
                    no_identitas_klien=klien_id,
                    nama_depan=nama_depan,
                    nama_tengah=nama_tengah,
                    nama_belakang=nama_belakang
                )
                
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
        
        # Validate required fields
        if not all([email, password, nama_perusahaan, telepon, alamat]):
            messages.error(request, 'Semua field wajib harus diisi.')
            return render(request, 'register_company.html')
        
        # Check if user already exists
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email sudah terdaftar.')
            return render(request, 'register_company.html')
        
        try:
            with transaction.atomic():
                # Create User
                user = User.objects.create(
                    email=email,
                    password=password,  # In production, you should hash this
                    alamat=alamat,
                    nomor_telepon=telepon
                )
                
                # Create Klien
                klien_id = uuid.uuid4()
                klien = Klien.objects.create(
                    no_identitas=klien_id,
                    tanggal_registrasi=date.today(),
                    email=email
                )
                
                # Create Perusahaan
                perusahaan = Perusahaan.objects.create(
                    no_identitas_klien=klien_id,
                    nama_perusahaan=nama_perusahaan
                )
                
                messages.success(request, 'Registrasi berhasil! Silakan login.')
                return redirect('authentication:login')
                
        except Exception as e:
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
        
        # Validate required fields
        if not all([email, password, telepon, tanggal_diterima, alamat]):
            messages.error(request, 'Semua field wajib harus diisi.')
            return render(request, 'register_frontdesk.html')
        
        # Check if user already exists
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email sudah terdaftar.')
            return render(request, 'register_frontdesk.html')
        
        try:
            with transaction.atomic():
                # Create User
                user = User.objects.create(
                    email=email,
                    password=password,  # In production, you should hash this
                    alamat=alamat,
                    nomor_telepon=telepon
                )
                
                # Create Pegawai
                pegawai_id = uuid.uuid4()
                pegawai = Pegawai.objects.create(
                    no_pegawai=pegawai_id,
                    tanggal_mulai_kerja=tanggal_diterima,
                    email_user=email
                )
                
                # Create FrontDesk
                frontdesk = FrontDesk.objects.create(
                    no_front_desk=uuid.uuid4(),
                    no_pegawai=pegawai_id
                )
                
                messages.success(request, 'Registrasi berhasil! Silakan login.')
                return redirect('authentication:login')
                
        except Exception as e:
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
        
        # Validate required fields
        if not all([no_izin, email, password, telepon, tanggal_diterima, alamat]):
            messages.error(request, 'Semua field wajib harus diisi.')
            return render(request, 'register_vet.html')
        
        # Check if user already exists
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email sudah terdaftar.')
            return render(request, 'register_vet.html')
        
        try:
            with transaction.atomic():
                # Create User
                user = User.objects.create(
                    email=email,
                    password=password,  # In production, you should hash this
                    alamat=alamat,
                    nomor_telepon=telepon
                )
                
                # Create Pegawai
                pegawai_id = uuid.uuid4()
                pegawai = Pegawai.objects.create(
                    no_pegawai=pegawai_id,
                    tanggal_mulai_kerja=tanggal_diterima,
                    email_user=email
                )
                
                # Create TenagaMedis
                tenaga_medis_id = uuid.uuid4()
                tenaga_medis = TenagaMedis.objects.create(
                    no_tenaga_medis=tenaga_medis_id,
                    no_pegawai=pegawai_id,
                    no_izin_praktik=no_izin
                )
                
                # Create DokterHewan
                dokter = DokterHewan.objects.create(
                    no_dokter_hewan=uuid.uuid4(),
                    no_tenaga_medis=tenaga_medis_id
                )
                
                messages.success(request, 'Registrasi berhasil! Silakan login.')
                return redirect('authentication:login')
                
        except Exception as e:
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
        
        # Validate required fields
        if not all([no_izin, email, password, telepon, tanggal_diterima, alamat]):
            messages.error(request, 'Semua field wajib harus diisi.')
            return render(request, 'register_nurse.html')
        
        # Check if user already exists
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email sudah terdaftar.')
            return render(request, 'register_nurse.html')
        
        try:
            with transaction.atomic():
                # Create User
                user = User.objects.create(
                    email=email,
                    password=password,  # In production, you should hash this
                    alamat=alamat,
                    nomor_telepon=telepon
                )
                
                # Create Pegawai
                pegawai_id = uuid.uuid4()
                pegawai = Pegawai.objects.create(
                    no_pegawai=pegawai_id,
                    tanggal_mulai_kerja=tanggal_diterima,
                    email_user=email
                )
                
                # Create TenagaMedis
                tenaga_medis_id = uuid.uuid4()
                tenaga_medis = TenagaMedis.objects.create(
                    no_tenaga_medis=tenaga_medis_id,
                    no_pegawai=pegawai_id,
                    no_izin_praktik=no_izin
                )
                
                # Create PerawatHewan
                perawat = PerawatHewan.objects.create(
                    no_perawat_hewan=uuid.uuid4(),
                    no_tenaga_medis=tenaga_medis_id
                )
                
                messages.success(request, 'Registrasi berhasil! Silakan login.')
                return redirect('authentication:login')
                
        except Exception as e:
            messages.error(request, f'Terjadi kesalahan: {str(e)}')
            return render(request, 'register_nurse.html')
    
    return render(request, 'register_nurse.html')

def logout_view(request):
    request.session.flush()
    messages.success(request, "Anda berhasil logout.")
    return redirect('main:landing_page')
