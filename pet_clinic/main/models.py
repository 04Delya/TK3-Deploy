from django.db import models
import uuid

# Create your models here.
class JenisHewan(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nama = models.CharField(max_length=100)
    
    def __str__(self):
        return self.nama
        
    class Meta:
        ordering = ['id']  # Order by ID in ascending order

# class Pet(models.Model):
#     name = models.CharField(max_length=100)
#     photo = models.ImageField(upload_to='pet_photos/', blank=True, null=True)