from django.db import models
from django.contrib import admin

# ================= USER =================
class User(models.Model):
    email = models.CharField(max_length=50, primary_key=True)
    password = models.CharField(max_length=100)
    alamat = models.TextField()
    nomor_telepon = models.CharField(max_length=15)

    class Meta:
        db_table = 'pet_clinic"."USER'
        managed = False

# ================= PEGAWAI =================
class Pegawai(models.Model):
    no_pegawai = models.UUIDField(primary_key=True)
    tanggal_mulai_kerja = models.DateField()
    tanggal_akhir_kerja = models.DateField(null=True, blank=True)
    email_user = models.CharField(max_length=50)

    class Meta:
        db_table = 'pet_clinic"."PEGAWAI'
        managed = False

# ================= KLIEN =================
class Klien(models.Model):
    no_identitas = models.UUIDField(primary_key=True)
    tanggal_registrasi = models.DateField()
    email = models.CharField(max_length=50)

    class Meta:
        db_table = 'pet_clinic"."KLIEN'
        managed = False

# ================= INDIVIDU =================
class Individu(models.Model):
    no_identitas_klien = models.UUIDField(primary_key=True)
    nama_depan = models.CharField(max_length=50)
    nama_tengah = models.CharField(max_length=50, null=True, blank=True)
    nama_belakang = models.CharField(max_length=50)

    class Meta:
        db_table = 'pet_clinic"."INDIVIDU'
        managed = False

# ================= PERUSAHAAN =================
class Perusahaan(models.Model):
    no_identitas_klien = models.UUIDField(primary_key=True)
    nama_perusahaan = models.CharField(max_length=100)

    class Meta:
        db_table = 'pet_clinic"."PERUSAHAAN'
        managed = False

# ================= TENAGA MEDIS =================
class TenagaMedis(models.Model):
    no_tenaga_medis = models.UUIDField(primary_key=True)
    no_pegawai = models.UUIDField()
    no_izin_praktik = models.CharField(max_length=20, unique=True)

    class Meta:
        db_table = 'pet_clinic"."TENAGA_MEDIS'
        managed = False

# ================= DOKTER HEWAN =================
class DokterHewan(models.Model):
    no_dokter_hewan = models.UUIDField(primary_key=True)
    no_tenaga_medis = models.UUIDField()

    class Meta:
        db_table = 'pet_clinic"."DOKTER_HEWAN'
        managed = False

# ================= PERAWAT HEWAN =================
class PerawatHewan(models.Model):
    no_perawat_hewan = models.UUIDField(primary_key=True)
    no_tenaga_medis = models.UUIDField()

    class Meta:
        db_table = 'pet_clinic"."PERAWAT_HEWAN'
        managed = False

# ================= FRONT DESK =================
class FrontDesk(models.Model):
    no_front_desk = models.UUIDField(primary_key=True)
    no_pegawai = models.UUIDField()

    class Meta:
        db_table = 'pet_clinic"."FRONT_DESK'
        managed = False

# ================= OBAT =================
class Obat(models.Model):
    kode = models.CharField(max_length=10, primary_key=True)
    nama = models.CharField(max_length=100)
    harga = models.IntegerField()
    stok = models.IntegerField()
    dosis = models.TextField()

    class Meta:
        db_table = 'pet_clinic"."OBAT'
        managed = False

# ================= VAKSIN =================
class Vaksin(models.Model):
    kode = models.CharField(max_length=6, primary_key=True)
    nama = models.CharField(max_length=50)
    harga = models.IntegerField()
    stok = models.IntegerField()

    class Meta:
        db_table = 'pet_clinic"."VAKSIN'
        managed = False

# ================= PERAWATAN =================
class Perawatan(models.Model):
    kode_perawatan = models.CharField(max_length=10, primary_key=True)
    nama_perawatan = models.CharField(max_length=100)
    biaya_perawatan = models.IntegerField()

    class Meta:
        db_table = 'pet_clinic"."PERAWATAN'
        managed = False

# ================= JENIS HEWAN =================
class JenisHewan(models.Model):
    id = models.UUIDField(primary_key=True)
    nama_jenis = models.CharField(max_length=50)

    class Meta:
        db_table = 'pet_clinic"."JENIS_HEWAN'
        managed = False

# ================= HEWAN =================
class Hewan(models.Model):
    nama = models.CharField(max_length=50, primary_key=True)
    no_identitas_klien = models.UUIDField()
    tanggal_lahir = models.DateField()
    id_jenis = models.UUIDField()
    url_foto = models.CharField(max_length=255)

    class Meta:
        db_table = 'pet_clinic"."HEWAN'
        managed = False
        unique_together = (('nama', 'no_identitas_klien'),)

# ================= KUNJUNGAN =================
class Kunjungan(models.Model):
    id_kunjungan = models.UUIDField(primary_key=True)  # 👈 WAJIB pakai ini!
    nama_hewan = models.CharField(max_length=50)
    no_identitas_klien = models.UUIDField()
    no_front_desk = models.UUIDField()
    no_perawat_hewan = models.UUIDField()
    no_dokter_hewan = models.UUIDField()
    kode_vaksin = models.CharField(max_length=6, null=True, blank=True)
    tipe_kunjungan = models.CharField(max_length=10)
    timestamp_awal = models.DateTimeField()
    timestamp_akhir = models.DateTimeField(null=True, blank=True)
    suhu = models.IntegerField(null=True, blank=True)
    berat_badan = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    class Meta:
        db_table = 'pet_clinic"."KUNJUNGAN'
        managed = False

# ================= KUNJUNGAN_KEPERAWATAN =================
class KunjunganKeperawatan(models.Model):
    id_kunjungan = models.UUIDField()
    nama_hewan = models.CharField(max_length=50)
    no_identitas_klien = models.UUIDField()
    no_front_desk = models.UUIDField()
    no_perawat_hewan = models.UUIDField()
    no_dokter_hewan = models.UUIDField()
    kode_perawatan = models.CharField(max_length=10, primary_key=True)
    catatan = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'pet_clinic"."KUNJUNGAN_KEPERAWATAN'
        managed = False
        unique_together = ("id_kunjungan", "nama_hewan", "no_identitas_klien", "no_front_desk", "no_perawat_hewan", "no_dokter_hewan", "kode_perawatan")

# ================= REGISTER ADMIN =================
admin.site.register(User)
admin.site.register(Pegawai)
admin.site.register(Klien)
admin.site.register(Individu)
admin.site.register(Perusahaan)
admin.site.register(TenagaMedis)
admin.site.register(DokterHewan)
admin.site.register(PerawatHewan)
admin.site.register(FrontDesk)
admin.site.register(Obat)
admin.site.register(Vaksin)
admin.site.register(Perawatan)
admin.site.register(JenisHewan)
admin.site.register(Hewan)
admin.site.register(Kunjungan)
admin.site.register(KunjunganKeperawatan)
