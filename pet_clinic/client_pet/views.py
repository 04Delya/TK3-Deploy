from django.shortcuts import render

CLIENTS = [
    {
        "id": "C001",
        "identity": "a1b2c3d4-e5f6-7a8b-9c0d-e1f2a3b4c5d6",
        "type": "Perusahaan",
        "name": "PT Maju Jaya Abadi",
        "address": "Jl. Melati No 23, Sukamaju, Cibinong",
        "phone": "081234567890",
        "email": "maju@abadi.com",
        "pets": [
            {"no": 1, "name": "Bella", "species": "Anjing", "dob": "2019-05-01"},
            {"no": 2, "name": "Toby",  "species": "Kucing", "dob": "2020-06-01"},
            {"no": 3, "name": "Lola", "species": "Kucing", "dob": "2020-06-02"},
        ],
    },
    {
        "id": "C002",
        "identity": "a1b2c3d4-e5f6-7a8b-9c0d-e1f2a3b4c5d6",
        "type": "Individu",
        "name": "Andi Pratama Saputra",
        "address": "Jl. Melati No. 12, RT 01/RW 02, Cilandak, Jakarta Selatan",
        "phone": "081234567890",
        "email": "andi.pratama@gmail.com",
        "pets": [
            {"no": 1, "name": "Bella", "species": "Anjing", "dob": "2019-05-01"},
            {"no": 2, "name": "Toby",  "species": "Kucing", "dob": "2020-06-01"},
            {"no": 3, "name": "Lola", "species": "Kucing", "dob": "2020-06-02"},
        ],
    },
]

from django.shortcuts import render

CLIENTS = [
    {
        "id": "C001",
        "identity": "a1b2c3d4-e5f6-7a8b-9c0d-e1f2a3b4c5d6",
        "type": "Perusahaan",
        "name": "PT Maju Jaya Abadi",
        "address": "Jl. Melati No 23, Sukamaju, Cibinong",
        "phone": "081234567890",
        "email": "maju@abadi.com",
        "pets": [
            {"no": 1, "name": "Bella", "species": "Anjing", "dob": "2019-05-01"},
            {"no": 2, "name": "Toby",  "species": "Kucing", "dob": "2020-06-01"},
            {"no": 3, "name": "Lola", "species": "Kucing", "dob": "2020-06-02"},
        ],
    },
    {
        "id": "C002",
        "identity": "a1b2c3d4-e5f6-7a8b-9c0d-e1f2a3b4c5d6",
        "type": "Individu",
        "name": "Andi Pratama Saputra",
        "address": "Jl. Melati No. 12, RT 01/RW 02, Cilandak, Jakarta Selatan",
        "phone": "081234567890",
        "email": "andi.pratama@gmail.com",
        "pets": [
            {"no": 1, "name": "Bella", "species": "Anjing", "dob": "2019-05-01"},
            {"no": 2, "name": "Toby",  "species": "Kucing", "dob": "2020-06-01"},
            {"no": 3, "name": "Lola", "species": "Kucing", "dob": "2020-06-02"},
        ],
    },
]

def client_list(request):
    return render(request, "clients_list.html", {"clients": CLIENTS})

def client_detail(request, cid):
    client = next((c for c in CLIENTS if c["id"] == cid), None)
    if client is None:
        return redirect("client_pet:list")        
    return render(request, "client_detail.html", {"client": client})
