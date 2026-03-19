from django.contrib import admin

from .models import Minijuego, Progreso, Rehabilitacion, Edificio, Notas

# Register your models here.
admin.site.register(Minijuego)
admin.site.register(Progreso)
admin.site.register(Rehabilitacion)
admin.site.register(Edificio)
admin.site.register(Notas)