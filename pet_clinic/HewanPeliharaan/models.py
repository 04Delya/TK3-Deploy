from django.db import models
import uuid
from Pengguna.models import Klien
from JenisHewan.models import JenisHewan

# Create your models here.
class Hewan(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    pemilik = models.ForeignKey(Klien, on_delete=models.CASCADE, related_name='hewan')
    jenis_hewan = models.ForeignKey(JenisHewan, on_delete=models.PROTECT)
    nama = models.CharField(max_length=100)
    tanggal_lahir = models.DateField()
    foto_url = models.URLField(blank=True, null=True)
    
    def __str__(self):
        return self.nama
    
    class Meta:
        ordering = ['pemilik__nama', 'jenis_hewan__nama', 'nama']

class Kunjungan(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    hewan = models.ForeignKey(Hewan, on_delete=models.CASCADE, related_name='kunjungan')
    tanggal_mulai = models.DateTimeField()
    tanggal_selesai = models.DateTimeField(null=True, blank=True)
    aktif = models.BooleanField(default=True)
    
    def __str__(self):
        return f"Kunjungan {self.hewan.nama} pada {self.tanggal_mulai.strftime('%d-%m-%Y')}"
    
    def save(self, *args, **kwargs):
        if self.tanggal_selesai is not None:
            self.aktif = False
        super().save(*args, **kwargs)
        
    class Meta:
        ordering = ['-tanggal_mulai']