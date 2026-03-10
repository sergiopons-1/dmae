from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator, MinLengthValidator

# Create your models here.
from django.db import models

class Clinica(models.Model):
    idClinica = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=255)
    direccion = models.CharField(max_length=255)
    codigoPostal = models.CharField(max_length=5, validators=[MinLengthValidator(5)])

    class Meta:
        db_table = "clinica"

class Usuario(AbstractUser):
    ROL_ESPECIALISTA = "especialista"
    ROL_PACIENTE = "paciente"

    ROL_CHOICES = [
        (ROL_ESPECIALISTA, "Especialista"),
        (ROL_PACIENTE, "Paciente"),
    ]

    rol = models.CharField(max_length=20, choices=ROL_CHOICES)

    @property
    def nombre(self):
        return self.first_name

    @property
    def apellidos(self):
        return self.last_name

    class Meta:
        db_table = "usuario"

class Especialista(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, primary_key=True)
    clinica = models.ForeignKey("Clinica", on_delete=models.CASCADE, null=True)

    class Meta:
        db_table = "especialista"

class Paciente(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, primary_key=True)
    especialista = models.ForeignKey(Especialista, on_delete=models.SET_NULL, null=True)
    dni = models.CharField(
        max_length=9,
        unique=True,
        validators=[
            RegexValidator(r'^\d{8}$', 'El DNI debe contener exactamente 8 dígitos.'),
            MinLengthValidator(8)   
        ],
        verbose_name="DNI"
    )
    fechaNacimiento = models.DateField(null=True, blank=True)
    codigoInicioSesion = models.CharField(max_length=100, unique=True, null=True, blank=True)

    class Meta:
        db_table = "paciente"