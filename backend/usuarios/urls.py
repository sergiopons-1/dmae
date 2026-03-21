from django.urls import path
from . import views

urlpatterns = [
    path('login/',    views.login),
    path('registro/', views.registro),
    path('registro-paciente/', views.registro_paciente),
]