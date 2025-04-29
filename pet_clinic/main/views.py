from django.shortcuts import render

# Create your views here.

def landing_page(request):
    return render(request, 'main/landing_page.html')

def login(request):
    return render(request, 'main/login.html')