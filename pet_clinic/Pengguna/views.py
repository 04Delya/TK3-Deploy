from django.shortcuts import render, redirect
from django.contrib.auth.models import User, Group
from django.contrib.auth import login
from django.db import transaction
from .models import Klien
import uuid

# Create your views here.
def landing_page(request):
    return render(request, 'landingpage.html')

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
                return redirect('landing_page')
    
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