from django.shortcuts import render

# === CREATE VIEWS ===
def create_medicine_view(request):
    return render(request, 'create_medicine.html')

def create_prescriptions_view(request):
    return render(request, 'create_prescriptions.html')

def create_treatment_view(request):
    return render(request, 'create_treatment.html')

# === DELETE VIEWS ===
def delete_medicine_view(request):
    return render(request, 'delete_medicine.html')

def delete_prescriptions_view(request):
    return render(request, 'delete_prescriptions.html')

def delete_treatment_view(request):
    return render(request, 'delete_treatment.html')

# === LIST VIEWS ===
def list_medicine_view(request):
    return render(request, 'list_medicine.html')

def list_prescriptions_view(request):
    return render(request, 'list_prescriptions.html')

def list_treatment_view(request):
    return render(request, 'list_treatment.html')

# === UPDATE VIEWS ===
def update_medicine_view(request):
    return render(request, 'update_medicine.html')

def update_treatment_view(request):
    return render(request, 'update_treatment.html')

def update_stock_medicine_view(request):
    return render(request, 'updateStock_medicine.html')