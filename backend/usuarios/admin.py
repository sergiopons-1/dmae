from django.contrib import admin
from .models import Usuario, Paciente, Especialista, Clinica

# Register your models here.

admin.site.register(Usuario)
admin.site.register(Paciente)
admin.site.register(Especialista)
admin.site.register(Clinica)