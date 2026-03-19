from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario, Clinica

# Register your models here.

class UsuarioAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Datos adicionales', {'fields': ('rol', 'clinica', 'dni', 'fechaNacimiento', 'codigoInicioSesion', 'especialista_asignado')}),
    )
    list_display = ('username', 'email', 'first_name', 'last_name', 'rol')
    list_filter = ('rol',) + UserAdmin.list_filter

admin.site.register(Clinica)