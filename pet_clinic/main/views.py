from django.shortcuts import render, redirect

# Create your views here.

def landing_page(request):
     return render(request, 'landingpage.html')

def dashboard(request):
      context = {
          "user_type": "dokter",         
          "identity":  "CSEGE02070-001",
          "email":     "doc@example.com",
          "name":      "drh. Maya Nanda",       
          "nama_depan": "Maya", "nama_tengah": "", "nama_belakang": "Nanda",
          "tgl_daftar": "24 April 2025",
          "tgl_akhir":  "—",                   
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
      return render(request, "dashboard_pengguna.html", context)

def update_profile(request):
    if request.method == "POST":
        return redirect("dashboard")
    return render(request, "update_profile.html")

def update_password(request):
    if request.method == "POST":
        return redirect("dashboard")
    return render(request, "update_password.html")