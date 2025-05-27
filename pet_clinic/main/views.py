from django.shortcuts import redirect, render

# Create your views here.

def landing_page(request):
    return render(request, 'main/landing_page.html')

def login(request):
    if request.method == "POST":
        # Ambil role dari form
        role = request.POST.get('role', 'klien')
        request.session['role'] = role  # Simpan ke session
        return redirect('dashboard')
    return render(request, 'login.html')

def landing_page(request):
    return render(request, 'landingpage.html')


def dashboard(request):
    # For demonstration purposes, redirect to perawat dashboard
    # In a real application, you would determine the user type from the session/authentication
    # and redirect accordingly
    user_type = request.GET.get('type', 'klien')  # Default to klien if no type specified
    
    if user_type == 'perawat':
        return redirect('dashboard_perawat')
    elif user_type == 'dokter':
        return redirect('dashboard_dokterhewan')
    elif user_type == 'fdo':
        return redirect('dashboard_frontdesk')
    else:
        return redirect('dashboard_klien')


def update_profile(request):
    if request.method == "POST":
        return redirect('dashboard_klien')
    return render(request, 'update_profile.html')


def update_password(request):
    if request.method == "POST":
        return redirect('dashboard_klien')
    return render(request, 'update_password.html')


def dashboard_klien(request):
    context = {
        "identity":  "KLN-001",
        "email":     "klien@example.com",
        "name":      "Delya Ardiyanti",
        "tgl_daftar":"28 April 2025",
        "alamat":    "Jl. Margonda, Depok",
        "telepon":   "0812-3456-7890",
    }
    return render(request, 'dashboard_klien.html', context)


def dashboard_frontdesk(request):
    context = {
        "identity":  "FDO-123",
        "email":     "fdo@petclinic.com",
        "tgl_daftar":"28 April 2025",
        "tgl_akhir": "—",
        "alamat":    "Jl. Margonda, Depok",
        "telepon":   "0812-3456-7890",
    }
    return render(request, 'dashboard_frontdesk.html', context)


def dashboard_dokterhewan(request):
    context = {
        "identity":  "CSEGE02070-001",
        "email":     "doc@example.com",
        "tgl_daftar":"24 April 2025",
        "tgl_akhir": "—",
        "alamat":    "Jl. Margonda, Depok",
        "telepon":   "0812-3456-7890",
        "sertifikat": [
            {"no": 1, "kode": "VAK/045", "nama": "Sertifikat Organisasi"},
            {"no": 2, "kode": "VAK/046", "nama": "Sertifikat Organisasi"},
        ],
        "jadwal": [
            {"no": 1, "hari": "Jumat", "mulai": "13.00", "selesai": "16.30"},
            {"no": 2, "hari": "Senin", "mulai": "09.00", "selesai": "12.00"},
        ],
    }
    return render(request, 'dashboard_dokterhewan.html', context)


def dashboard_perawat(request):
    context = {
        "identity":  "PRW-001",
        "email":     "perawat@example.com",
        "tgl_daftar":"25 April 2025",
        "tgl_akhir": "—",
        "alamat":    "Jl. Margonda, Depok",
        "telepon":   "0812-3456-7890",
        "sertifikat": [
            {"no": 1, "kode": "CERT/001", "nama": "Sertifikat Keperawatan"},
        ],
    }
    return render(request, 'dashboard_perawat.html', context)