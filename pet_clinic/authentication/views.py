from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import connection
from main.models import User, Pegawai, TenagaMedis, DokterHewan, PerawatHewan, FrontDesk, Klien, Individu, Perusahaan
import uuid
from datetime import date
from main.models import User, DokterHewan, TenagaMedis, Pegawai

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
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        nama = request.POST.get('nama')
        
        if username and password and nama:
            with transaction.atomic():
                # Create a Django user
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password
                )
                
                # Add user to individual clients group
                client_group, _ = Group.objects.get_or_create(name='individual_clients')
                user.groups.add(client_group)
                
                # Create a Klien for the user
                klien = Klien.objects.create(
                    id=uuid.uuid4(),
                    nama=nama,
                    jenis='individual'
                )
                
                login(request, user)
                return redirect('main:landing_page')
    
    return render(request, 'register_individual.html')

def register_company(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        nama_perusahaan = request.POST.get('nama_perusahaan')
        
        if username and password and nama_perusahaan:
            with transaction.atomic():
                # Create a Django user
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password
                )
                
                # Add user to company clients group
                client_group, _ = Group.objects.get_or_create(name='company_clients')
                user.groups.add(client_group)
                
                # Create a Klien for the user
                klien = Klien.objects.create(
                    id=uuid.uuid4(),
                    nama=nama_perusahaan,
                    jenis='company'
                )
                
                login(request, user)
                return redirect('landing_page')
    
    return render(request, 'register_company.html')

def register_frontdesk(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        nama = request.POST.get('nama')
        
        if username and password and nama:
            with transaction.atomic():
                # Create a Django user
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password
                )
                
                # Add user to staff group
                staff_group, _ = Group.objects.get_or_create(name='frontdesk')
                user.groups.add(staff_group)
                user.is_staff = True
                user.save()
                
                login(request, user)
                return redirect('landing_page')
    
    return render(request, 'register_frontdesk.html')

def register_vet(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        nama = request.POST.get('nama')
        
        if username and password and nama:
            with transaction.atomic():
                # Create a Django user
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password
                )
                
                # Add user to vet group
                vet_group, _ = Group.objects.get_or_create(name='veterinarians')
                user.groups.add(vet_group)
                user.is_staff = True
                user.save()
                
                login(request, user)
                return redirect('landing_page')
    
    return render(request, 'register_vet.html')

def register_nurse(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        nama = request.POST.get('nama')
        
        if username and password and nama:
            with transaction.atomic():
                # Create a Django user
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password
                )
                
                # Add user to nurse group
                nurse_group, _ = Group.objects.get_or_create(name='nurses')
                user.groups.add(nurse_group)
                user.is_staff = True
                user.save()
                
                login(request, user)
                return redirect('landing_page')
    
    return render(request, 'register_nurse.html')

def logout_view(request):
    request.session.flush()
    messages.success(request, "Anda berhasil logout.")
    return redirect('main:landing_page')
