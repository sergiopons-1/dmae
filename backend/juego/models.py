from django.db import models

# Create your models here.
from django.db import models
from usuarios.models import Paciente, Especialista

class Minijuego(models.Model):
    idMinijuego = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=255, unique=True)

    class Meta:
        db_table = "minijuego"

class Progreso(models.Model):
    idProgreso = models.AutoField(primary_key=True)
    paciente = models.OneToOneField(Paciente, on_delete=models.CASCADE)

    class Meta:
        db_table = "progreso"

class Rehabilitacion(models.Model):
    class EstadoRehabilitacion(models.TextChoices):
        PENDIENTE = "pendiente",   "Pendiente"
        EN_CURSO  = "en_curso",    "En curso"
        FINALIZADO = "finalizado",  "Finalizado"

    idRehabilitacion = models.AutoField(primary_key=True)
    progreso = models.ForeignKey(Progreso, on_delete=models.CASCADE)
    estado = models.CharField(max_length=20, choices=EstadoRehabilitacion.choices, default=EstadoRehabilitacion.PENDIENTE)
    fechaInicio = models.DateTimeField(auto_now_add=True)
    fechaFin = models.DateTimeField(null=True, blank=True)
    puntuacionRehabilitacion = models.IntegerField(default=0)

    class Meta:
        db_table = "rehabilitacion"

class Edificio(models.Model):
    class EstadoEdificio(models.TextChoices):
        BLOQUEADO   = "bloqueado",  "Bloqueado"
        EN_CURSO    = "en_curso",   "En curso"
        RESTAURADO  = "restaurado", "Restaurado"

    idEdificio = models.AutoField(primary_key=True)
    rehabilitacion = models.ForeignKey(Rehabilitacion, on_delete=models.CASCADE)
    minijuego = models.ForeignKey(Minijuego, on_delete=models.SET_NULL, null=True)
    nombre = models.CharField(max_length=255)
    estadoEdificio = models.CharField(max_length=20, choices=EstadoEdificio.choices, default=EstadoEdificio.BLOQUEADO)
    puntuacionEdificio = models.IntegerField(default=0)

    class Meta:
        db_table = "edificio"

class Notas(models.Model):
    idNota = models.AutoField(primary_key=True)
    progreso = models.ForeignKey(Progreso, on_delete=models.CASCADE)
    especialista = models.ForeignKey(Especialista, on_delete=models.SET_NULL, null=True)
    contenido = models.CharField(max_length=255)
    fechaNota = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "notas"