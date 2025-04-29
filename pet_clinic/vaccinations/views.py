from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST

# Create your views here.

def vaccination_list(request):
    # Dummy data
    vaccinations = [
        { 'no': 1, 'kunjungan': 'KJN001', 'tanggal': 'Rabu, 5 Februari 2025', 'vaksin': 'VAK001 - Vaksin Rabies' },
        { 'no': 2, 'kunjungan': 'KJN002', 'tanggal': 'Jumat, 21 Februari 2025', 'vaksin': 'VAK002 - Vaksin Flu Musiman' },
        { 'no': 3, 'kunjungan': 'KJN003', 'tanggal': 'Selasa, 15 Maret 2025', 'vaksin': 'VAK003 - Vaksin Parvovirus' },
    ]
    return render(request, 'vaccinations_list.html', {
        'vaccinations': vaccinations
    })

def vaccination_create(request):
    kunjungan_list = ['KJN001', 'KJN002', 'KJN003']
    vaksin_list = [
        'VAK001 - Vaksin Rabies [30]',
        'VAK002 - Vaksin Flu Musiman [50]',
        'VAK003 - Vaksin Parvovirus [25]',
    ]
    return render(request, 'create_vac.html', {
        'kunjungan_list': kunjungan_list,
        'vaksin_list': vaksin_list,
    })

def vaccination_update(request):
    kunjungan = "KJN001"

    vaksin_list = [
        "VAK001 - Vaksin Rabies [30]",
        "VAK002 - Vaksin Flu Musiman [50]",
        "VAK003 - Vaksin Parvovirus [0]"
    ]

    selected_vaksin = "VAK001 - Vaksin Rabies [30]"

    return render(request, 'update_vac.html', {
        'kunjungan': kunjungan,
        'vaksin_list': vaksin_list,
        'selected_vaksin': selected_vaksin
    })

@require_POST
def vaccination_delete(request, no):
    return redirect('vaccination_list')
