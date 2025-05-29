from django.shortcuts import redirect, render
from django.contrib import messages
from django.db import transaction
from main.models import *

# Create your views here.
def landing_page(request):
    return render(request, 'landing_page.html')

def dashboard(request):
    role = request.session.get('role', None)
    if not role:
        messages.error(request, "Anda harus login terlebih dahulu.")
        return redirect('authentication:login')

    if role in ['individu', 'perusahaan', 'klien']:
        return dashboard_klien(request)
    elif role == 'perawat':
        return dashboard_perawat(request)
    elif role == 'dokter':
        return dashboard_dokterhewan(request)
    elif role == 'frontdesk':
        return dashboard_frontdesk(request)
    else:
        messages.error(request, "Role user tidak dikenali.")
        return redirect('authentication:login')


def update_profile(request):
    role = request.session.get('role')
    user_email = request.session.get('user_email')

    if not role or not user_email:
        messages.error(request, "Anda harus login terlebih dahulu.")
        return redirect('authentication:login')

    try:
        user = User.objects.get(email=user_email)
    except User.DoesNotExist:
        messages.error(request, "Data user tidak ditemukan.")
        return redirect('main:dashboard')

    # Handle GET request — tampilkan form dengan data sesuai role
    if request.method == 'GET':
        context = {'role': role, 'email': user.email}

        if role == 'individu':
            klien_id = request.session.get('klien_id')
            klien = Klien.objects.get(no_identitas=klien_id)
            individu = Individu.objects.get(no_identitas_klien=klien.no_identitas)
            context.update({
                'alamat': user.alamat,
                'telepon': user.nomor_telepon,
                'first_name': individu.nama_depan,
                'middle_name': individu.nama_tengah,
                'last_name': individu.nama_belakang,
            })
            return render(request, 'update_profile.html', context)

        elif role == 'perusahaan':
            klien_id = request.session.get('klien_id')
            perusahaan = Perusahaan.objects.get(no_identitas_klien=klien_id)
            context.update({
                'alamat': user.alamat,
                'telepon': user.nomor_telepon,
                'company_name': perusahaan.nama_perusahaan,
            })
            return render(request, 'update_profile.html', context)

        elif role == 'frontdesk':
            pegawai = Pegawai.objects.get(no_pegawai=request.session.get('pegawai_id'))
            context.update({
                'alamat': user.alamat,
                'telepon': user.nomor_telepon,
                'tgl_akhir': pegawai.tanggal_akhir_kerja,
            })
            return render(request, 'update_profile.html', context)

        elif role == 'dokter':
            pegawai = Pegawai.objects.get(no_pegawai=request.session.get('pegawai_id'))
            tenaga = TenagaMedis.objects.get(no_pegawai=pegawai.no_pegawai)
            dokter = DokterHewan.objects.get(no_tenaga_medis=tenaga.no_tenaga_medis)
            # Ambil sertifikat dan jadwal dari database atau dummy placeholder
            sertifikat = [  # Contoh dummy data; sesuaikan dengan data sebenarnya
                {"no": 1, "kode": "CERT001", "nama": "Sertifikat Kompetensi A"},
                {"no": 2, "kode": "CERT002", "nama": "Sertifikat Kompetensi B"},
            ]
            jadwal = [
                {"no": 1, "hari": "Senin", "mulai": "09.00", "selesai": "12.00"},
                {"no": 2, "hari": "Kamis", "mulai": "13.00", "selesai": "16.00"},
            ]
            context.update({
                'alamat': user.alamat,
                'telepon': user.nomor_telepon,
                'tgl_akhir': pegawai.tanggal_akhir_kerja,
                'sertifikat': sertifikat,
                'jadwal': jadwal,
            })
            return render(request, 'update_profile.html', context)

        elif role == 'perawat':
            pegawai = Pegawai.objects.get(no_pegawai=request.session.get('pegawai_id'))
            tenaga = TenagaMedis.objects.get(no_pegawai=pegawai.no_pegawai)
            perawat = PerawatHewan.objects.get(no_tenaga_medis=tenaga.no_tenaga_medis)
            sertifikat = [
                {"no": 1, "kode": "CERT101", "nama": "Sertifikat Keperawatan A"},
            ]
            context.update({
                'alamat': user.alamat,
                'telepon': user.nomor_telepon,
                'tgl_akhir': pegawai.tanggal_akhir_kerja,
                'sertifikat': sertifikat,
            })
            return render(request, 'update_profile.html', context)

        else:
            messages.error(request, "Role tidak dikenali.")
            return redirect('main:dashboard')

    # Handle POST request — proses update sesuai role
    if request.method == 'POST':
        try:
            with transaction.atomic():
                # Update alamat dan telepon semua role bisa
                alamat = request.POST.get('alamat', '').strip()
                telepon = request.POST.get('telepon', '').strip()
                user.alamat = alamat
                user.nomor_telepon = telepon
                user.save()

                if role == 'individu':
                    klien_id = request.session.get('klien_id')
                    klien = Klien.objects.get(no_identitas=klien_id)
                    individu = Individu.objects.get(no_identitas_klien=klien.no_identitas)
                    individu.nama_depan = request.POST.get('first_name', '').strip()
                    individu.nama_tengah = request.POST.get('middle_name', '').strip()
                    individu.nama_belakang = request.POST.get('last_name', '').strip()
                    individu.save()

                elif role == 'perusahaan':
                    klien_id = request.session.get('klien_id')
                    perusahaan = Perusahaan.objects.get(no_identitas_klien=klien_id)
                    perusahaan.nama_perusahaan = request.POST.get('company_name', '').strip()
                    perusahaan.save()

                elif role in ['frontdesk', 'dokter', 'perawat']:
                    pegawai = Pegawai.objects.get(no_pegawai=request.session.get('pegawai_id'))
                    # Update tanggal akhir kerja
                    tgl_akhir_str = request.POST.get('tgl_akhir', '').strip()
                    if tgl_akhir_str:
                        from datetime import datetime
                        pegawai.tanggal_akhir_kerja = datetime.strptime(tgl_akhir_str, '%Y-%m-%d').date()
                    else:
                        pegawai.tanggal_akhir_kerja = None
                    pegawai.save()

                    # Update sertifikat dan jadwal khusus dokter dan perawat
                    if role in ['dokter', 'perawat']:
                        # NOTE: Update sertifikat & jadwal sebaiknya dikelola di halaman terpisah / model terkait.
                        # Di sini hanya dummy contoh, silakan sesuaikan implementasi sebenarnya.
                        pass

                messages.success(request, "Profil berhasil diperbarui.")
                # Redirect ke dashboard sesuai role
                if role in ['individu', 'perusahaan', 'klien']:
                    return redirect('main:dashboard_klien')
                elif role == 'dokter':
                    return redirect('main:dashboard_dokterhewan')
                elif role == 'perawat':
                    return redirect('main:dashboard_perawat')
                elif role == 'frontdesk':
                    return redirect('main:dashboard_frontdesk')
                else:
                    return redirect('main:dashboard')

        except Exception as e:
            messages.error(request, f"Gagal memperbarui profil: {str(e)}")
            return redirect('main:update_profile')


def update_password(request):
    role = request.session.get('role')
    user_email = request.session.get('user_email')

    if not role or not user_email:
        messages.error(request, "Anda harus login terlebih dahulu.")
        return redirect('authentication:login')

    if request.method == 'GET':
        return render(request, 'update_password.html')

    if request.method == 'POST':
        old_pw = request.POST.get('old_pw')
        new_pw1 = request.POST.get('new_pw1')
        new_pw2 = request.POST.get('new_pw2')

        if new_pw1 != new_pw2:
            messages.error(request, "Password baru dan konfirmasi tidak cocok.")
            return redirect('main:update_password')

        try:
            user = User.objects.get(email=user_email)
            if user.password != old_pw:
                messages.error(request, "Password lama salah.")
                return redirect('main:update_password')

            user.password = new_pw1
            user.save()
            messages.success(request, "Password berhasil diperbarui.")

            # Redirect sesuai role
            if role in ['individu', 'perusahaan', 'klien']:
                return redirect('main:dashboard_klien')
            elif role == 'dokter':
                return redirect('main:dashboard_dokterhewan')
            elif role == 'perawat':
                return redirect('main:dashboard_perawat')
            elif role == 'frontdesk':
                return redirect('main:dashboard_frontdesk')
            else:
                return redirect('main:dashboard')

        except Exception as e:
            messages.error(request, f"Gagal memperbarui password: {str(e)}")
            return redirect('main:update_password')


# def dashboard_klien(request):
#     context = {
#         "identity":  "KLN-001",
#         "email":     "klien@example.com",
#         "name":      "Delya Ardiyanti",
#         "tgl_daftar":"28 April 2025",
#         "alamat":    "Jl. Margonda, Depok",
#         "telepon":   "0812-3456-7890",
#     }
#     return render(request, 'dashboard_klien.html', context)


def dashboard_klien(request):
    klien_id = request.session.get('klien_id')
    if not klien_id:
        messages.error(request, "ID klien tidak ditemukan.")
        return redirect('authentication:login')
    
    try:
        klien = Klien.objects.get(no_identitas=klien_id)
        user = User.objects.get(email=klien.email)
        # Cek apakah klien adalah individu atau perusahaan
        if Individu.objects.filter(no_identitas_klien=klien.no_identitas).exists():
            individu = Individu.objects.get(no_identitas_klien=klien.no_identitas)
            name = f"{individu.nama_depan} {individu.nama_tengah or ''} {individu.nama_belakang}".strip()
        elif Perusahaan.objects.filter(no_identitas_klien=klien.no_identitas).exists():
            perusahaan = Perusahaan.objects.get(no_identitas_klien=klien.no_identitas)
            name = perusahaan.nama_perusahaan
        else:
            name = "Nama tidak ditemukan"

        context = {
            "identity": str(klien.no_identitas),
            "email": user.email,
            "name": name,
            "tgl_daftar": klien.tanggal_registrasi.strftime('%d %B %Y'),
            "alamat": user.alamat,
            "telepon": user.nomor_telepon,
        }
        return render(request, 'dashboard_klien.html', context)
    
    except Klien.DoesNotExist:
        messages.error(request, "Data klien tidak ditemukan.")
        return redirect('authentication:login')
    except User.DoesNotExist:
        messages.error(request, "Data user tidak ditemukan.")
        return redirect('authentication:login')


def dashboard_frontdesk(request):
    pegawai_id = request.session.get('pegawai_id')
    if not pegawai_id:
        messages.error(request, "ID pegawai tidak ditemukan.")
        return redirect('authentication:login')

    try:
        pegawai = Pegawai.objects.get(no_pegawai=pegawai_id)
        user = User.objects.get(email=pegawai.email_user)
        frontdesk = FrontDesk.objects.get(no_pegawai=pegawai.no_pegawai)

        context = {
            "identity": str(frontdesk.no_front_desk),
            "email": user.email,
            "tgl_daftar": pegawai.tanggal_mulai_kerja.strftime('%d %B %Y'),
            "tgl_akhir": pegawai.tanggal_akhir_kerja.strftime('%d %B %Y') if pegawai.tanggal_akhir_kerja else "—",
            "alamat": user.alamat,
            "telepon": user.nomor_telepon,
        }
        return render(request, 'dashboard_frontdesk.html', context)
    
    except (Pegawai.DoesNotExist, User.DoesNotExist, FrontDesk.DoesNotExist):
        messages.error(request, "Data frontdesk tidak ditemukan.")
        return redirect('authentication:login')


def dashboard_dokterhewan(request):
    no_dokter_hewan = request.session.get('no_dokter_hewan')
    try:
        # Ambil objek dokter hewan
        dokter = DokterHewan.objects.get(no_dokter_hewan=no_dokter_hewan)

        # Ambil objek tenaga medis terkait
        tenaga = TenagaMedis.objects.get(no_tenaga_medis=dokter.no_tenaga_medis)

        # Ambil pegawai terkait
        pegawai = Pegawai.objects.get(no_pegawai=tenaga.no_pegawai)

        # Ambil user terkait (alamat, telepon, email)
        user = User.objects.get(email=pegawai.email_user)

        context = {
            'identity': str(dokter.no_dokter_hewan),
            'sip_number': tenaga.no_izin_praktik,  # pastikan ini ada
            'email': user.email,
            'tgl_daftar': pegawai.tanggal_mulai_kerja.strftime('%d %B %Y'),
            'tgl_akhir': pegawai.tanggal_akhir_kerja.strftime('%d %B %Y') if pegawai.tanggal_akhir_kerja else '—',
            'alamat': user.alamat,
            'telepon': user.nomor_telepon,

            # sertifikat dan jadwal bisa diisi sesuai data Anda
            'sertifikat': [
                {"no": 1, "kode": "VAK/045", "nama": "Sertifikat Organisasi"},
                {"no": 2, "kode": "VAK/046", "nama": "Sertifikat Organisasi"},
            ],
            'jadwal': [
                {"no": 1, "hari": "Jumat", "mulai": "13.00", "selesai": "16.30"},
                {"no": 2, "hari": "Senin", "mulai": "09.00", "selesai": "12.00"},
            ],
        }
        return render(request, 'dashboard_dokterhewan.html', context)

    except DokterHewan.DoesNotExist:
        messages.error(request, "Data dokter hewan tidak ditemukan.")
        return redirect('main:landing_page')
    except TenagaMedis.DoesNotExist:
        messages.error(request, "Data tenaga medis tidak ditemukan.")
        return redirect('main:landing_page')
    except Pegawai.DoesNotExist:
        messages.error(request, "Data pegawai tidak ditemukan.")
        return redirect('main:landing_page')
    except User.DoesNotExist:
        messages.error(request, "Data user tidak ditemukan.")
        return redirect('main:landing_page')



def dashboard_perawat(request):
    pegawai_id = request.session.get('pegawai_id')
    if not pegawai_id:
        messages.error(request, "ID pegawai tidak ditemukan.")
        return redirect('authentication:login')

    try:
        pegawai = Pegawai.objects.get(no_pegawai=pegawai_id)
        user = User.objects.get(email=pegawai.email_user)

        # Cari TenagaMedis berdasarkan no_pegawai
        tenaga = TenagaMedis.objects.get(no_pegawai=pegawai.no_pegawai)

        # Cari PerawatHewan berdasarkan no_tenaga_medis dari TenagaMedis
        perawat = PerawatHewan.objects.get(no_tenaga_medis=tenaga.no_tenaga_medis)

        context = {
            "identity": str(perawat.no_perawat_hewan),  # gunakan no_perawat_hewan sebagai identity
            "email": user.email,
            "tgl_daftar": pegawai.tanggal_mulai_kerja.strftime('%d %B %Y'),
            "tgl_akhir": pegawai.tanggal_akhir_kerja.strftime('%d %B %Y') if pegawai.tanggal_akhir_kerja else "—",
            "alamat": user.alamat,
            "telepon": user.nomor_telepon,
            "sertifikat": [
                {"no": 1, "kode": "CERT/001", "nama": "Sertifikat Keperawatan"},
                # Tambahkan data sertifikat asli jika ada
            ],
        }
        return render(request, 'dashboard_perawat.html', context)

    except Pegawai.DoesNotExist:
        messages.error(request, "Data pegawai tidak ditemukan.")
        return redirect('authentication:login')
    except User.DoesNotExist:
        messages.error(request, "Data user tidak ditemukan.")
        return redirect('authentication:login')
    except TenagaMedis.DoesNotExist:
        messages.error(request, "Data tenaga medis tidak ditemukan.")
        return redirect('authentication:login')
    except PerawatHewan.DoesNotExist:
        messages.error(request, "Data perawat hewan tidak ditemukan.")
        return redirect('authentication:login')