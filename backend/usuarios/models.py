from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator, MinLengthValidator


class Clinica(models.Model):
    idClinica = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=255)
    direccion = models.CharField(max_length=255)
    codigoPostal = models.CharField(max_length=5, validators=[MinLengthValidator(5)])

    def __str__(self):
        return self.nombre + " (" + self.direccion + ")"
    
    class Meta:
        db_table = "clinica"


class Usuario(AbstractUser):
    ROL_CHOICES = [
        ('especialista', 'Especialista'),
        ('paciente', 'Paciente'),
    ]
    rol = models.CharField(max_length=20, choices=ROL_CHOICES)
    clinica = models.ForeignKey(Clinica, on_delete=models.SET_NULL, null=True)

    def es_especialista(self):
        return self.rol == 'especialista'

    def es_paciente(self):
        return self.rol == 'paciente'

    class Meta:
        db_table = "usuario"
    
class Especialista(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE)
    @property
    def nombre(self):
        return self.usuario.first_name

    @property
    def apellidos(self):
        return self.usuario.last_name
    
    class Meta:
        db_table = "especialista"

class Paciente(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE)
    especialista = models.ForeignKey(
        Especialista,
        on_delete=models.SET_NULL,
        null=True
    )
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