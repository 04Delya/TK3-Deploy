from django.db import models
import uuid

# Import the actual Supabase models instead of creating local ones
from main.models import JenisHewan

# This app now uses the JenisHewan model from main.models 
# which connects directly to the Supabase database table: pet_clinic"."JENIS_HEWAN

# No local models needed - everything uses the Supabase database models