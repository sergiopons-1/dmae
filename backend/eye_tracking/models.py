from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from usuarios.models import Usuario


class AjustesPaciente(models.Model):
    paciente = models.OneToOneField(Usuario, on_delete=models.CASCADE, primary_key=True, limit_choices_to={'rol': 'paciente'})
    esta_calibrado = models.BooleanField(default=False)
    sensibilidad = models.FloatField(default=1.0, validators=[MinValueValidator(0.2), MaxValueValidator(3.0)])

    class Meta:
        db_table = "ajustes_paciente"