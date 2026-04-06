from django.urls import path
from . import views

urlpatterns = [
    path('login/',    views.login),
    path('logout/', views.logout),
    path('registro/', views.registro),
    path('clinicas/', views.clinicas),
    path('registro-paciente/', views.registro_paciente),
    path('mi-progreso/', views.mi_progreso_paciente),
    path('iniciar-rehabilitacion/', views.iniciar_rehabilitacion_paciente),
    path('cambiar-contrasena/', views.cambiar_contrasena),
]