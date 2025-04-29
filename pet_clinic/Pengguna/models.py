from django.db import models
import uuid

# Create your models here.
class Klien(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nama = models.CharField(max_length=100)
    jenis = models.CharField(max_length=20, choices=[('individual', 'Individual'), ('company', 'Company')], default='individual')
    
    def __str__(self):
        return f"{self.nama} ({self.get_jenis_display()})"