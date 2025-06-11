from django.db import models
import uuid

# Import the actual Supabase models instead of creating local ones
from main.models import JenisHewan, Hewan, Klien, Kunjungan

# This app now uses the models from main.models which connect directly to the Supabase database:
# - JenisHewan -> pet_clinic"."JENIS_HEWAN
# - Hewan -> pet_clinic"."HEWAN  
# - Klien -> pet_clinic"."KLIEN
# - Kunjungan -> pet_clinic"."KUNJUNGAN

# No local models needed - everything uses the Supabase database models