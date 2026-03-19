from django.db import models
from usuarios.models import Usuario
from django.core.validators import MaxValueValidator, MinValueValidator

class Minijuego(models.Model):
    idMinijuego = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=255, unique=True)

    class Meta:
        db_table = "minijuego"

class Progreso(models.Model):
    idProgreso = models.AutoField(primary_key=True)
    paciente = models.OneToOneField(Usuario, on_delete=models.CASCADE, limit_choices_to={'rol': 'paciente'})

    class Meta:
        db_table = "progreso"

class Rehabilitacion(models.Model):
    class EstadoRehabilitacion(models.TextChoices):
        PENDIENTE = "pendiente",   "Pendiente"
        EN_CURSO  = "en_curso",    "En curso"
        FINALIZADO = "finalizado",  "Finalizado"

    idRehabilitacion = models.AutoField(primary_key=True)
    progreso = models.ForeignKey(Progreso, on_delete=models.CASCADE)
    estado = models.CharField(choices=EstadoRehabilitacion.choices, default=EstadoRehabilitacion.PENDIENTE)
    fechaInicio = models.DateTimeField(auto_now_add=True)
    fechaFin = models.DateTimeField(null=True, blank=True)
    puntuacionRehabilitacion = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(15)])

    class Meta:
        db_table = "rehabilitacion"

class Edificio(models.Model):
    class EstadoEdificio(models.TextChoices):
        BLOQUEADO   = "bloqueado",  "Bloqueado"
        EN_CURSO    = "en_curso",   "En curso"
        RESTAURADO  = "restaurado", "Restaurado"

    class NombreEdificio(models.TextChoices):
        BIBLIOTECA = "biblioteca", "Biblioteca"
        HUERTO = "huerto", "Huerto"
        MUSEO = "museo", "Museo"
        MERCADILLO = "mercadillo", "Mercadillo"
        CAMPANARIO = "campanario", "Campanario"


    idEdificio = models.AutoField(primary_key=True)
    rehabilitacion = models.ForeignKey(Rehabilitacion, on_delete=models.CASCADE)
    minijuego = models.ForeignKey(Minijuego, on_delete=models.SET_NULL, null=True)
    nombre = models.CharField(choices=NombreEdificio.choices, default=NombreEdificio.BIBLIOTECA)
    estadoEdificio = models.CharField(choices=EstadoEdificio.choices, default=EstadoEdificio.BLOQUEADO)
    puntuacionEdificio = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(3)])

    class Meta:
        db_table = "edificio"

class Notas(models.Model):
    idNota = models.AutoField(primary_key=True)
    progreso = models.ForeignKey(Progreso, on_delete=models.CASCADE)
    especialista = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, limit_choices_to={'rol': 'especialista'})
    contenido = models.CharField(max_length=500)
    fechaNota = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "notas"