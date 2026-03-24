from django.urls import path
from . import views

urlpatterns = [
    path('login/',    views.login),
    path('registro/', views.registro),
    path('clinicas/', views.clinicas),
    path('registro-paciente/', views.registro_paciente),
    path('cambiar-contrasena/', views.cambiar_contrasena),
]