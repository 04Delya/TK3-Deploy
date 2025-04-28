from django.shortcuts import render

# Create your views here.

def landing_page(request):
    return render(request, 'main/landing_page.html')

def register_selection(request):
    return render(request, 'registration/register.html')

def register_individual(request):
    return render(request, 'registration/register_individual.html')

def register_company(request):
    return render(request, 'registration/register_company.html')

def register_frontdesk(request):
    return render(request, 'registration/register_frontdesk.html')

def register_vet(request):
    return render(request, 'registration/register_vet.html')

def register_nurse(request):
    return render(request, 'registration/register_nurse.html')
