from django.db import models
from usuarios.models import Usuario
from juego.models import Rehabilitacion

class AjustesPaciente(models.Model):
    paciente = models.OneToOneField(Usuario, on_delete=models.CASCADE, primary_key=True, limit_choices_to={'rol': 'paciente'})
    esta_calibrado = models.BooleanField(default=False)
    gesto_clic = models.CharField(max_length=50)
    gesto_doble_clic = models.CharField(max_length=50)
    sensibilidad = models.FloatField(default=1.0)

    class Meta:
        db_table = "ajustes_paciente"

class SesionGaze(models.Model):
    class TipoEvento(models.TextChoices):
        FIJACION = "fijacion",  "Fijación"
        SACCADA  = "saccada",   "Sácada"
        PARPADEO = "parpadeo",  "Parpadeo"

    rehabilitacion = models.ForeignKey(Rehabilitacion, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    pos_x = models.FloatField()
    pos_y = models.FloatField()
    tipo_evento = models.CharField(max_length=20, choices=TipoEvento.choices)
    duracion_ms = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = "sesion_gaze"
        ordering = ["timestamp"]