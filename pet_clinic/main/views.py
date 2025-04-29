from django.shortcuts import render, redirect

# Create your views here.

def landing_page(request):
     return render(request, 'landingpage.html')


# def pet_create(request):
#     if request.method == 'POST':
#         form = PetForm(request.POST, request.FILES)
#         if form.is_valid():
#             form.save()
#             return redirect('pet_list')
#     else:
#         form = PetForm()
#     return render(request, 'main/pet_form.html', {'form': form})