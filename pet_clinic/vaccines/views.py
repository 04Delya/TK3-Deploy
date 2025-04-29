from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST

VACCINES = [
    {'id': 'VAK001', 'name': 'Vaksin Rabies',      'price': '250000', 'stock': 30},
    {'id': 'VAK002', 'name': 'Vaksin Flu Musiman', 'price': '200000', 'stock': 50},
    {'id': 'VAK003', 'name': 'Vaksin Parvovirus',  'price': '300000', 'stock': 25},
]

def vaccine_list(request):
    q = request.GET.get("q", "").lower()
    if q:
        data = [v for v in VACCINES if q in v["name"].lower()]
    else:
        data = VACCINES
    return render(request, "vaccines_list.html", {"vaccines": data})


def vaccine_create(request):
    if request.method == 'POST':
        return redirect('vaccine_list')
    return render(request, 'vaccines_create.html')


def vaccine_update(request):
    dummy = {'id': 'VAK001', 'name': 'Vaksin Rabies', 'price': '250000'}
    if request.method == 'POST':
        return redirect('vaccine_list')
    return render(request, 'vaccines_update.html', {'vaccine': dummy})


def vaccine_update_stock(request):
    dummy = {'id': 'VAK001', 'name': 'Vaksin Rabies', 'stock': 30}
    if request.method == 'POST':
        return redirect('vaccine_list')
    return render(request, 'vaccines_update_stock.html', {'vaccine': dummy})


@require_POST
def vaccine_delete(request, no):
    return redirect('vaccine_list')
