from django.urls import path

from . import views

urlpatterns = [
    path('ajustes/', views.obtener_ajustes_calibracion),
    path('calibracion/', views.guardar_ajustes_calibracion),
]
