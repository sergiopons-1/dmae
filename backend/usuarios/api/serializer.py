from rest_framework import serializers
from ..models import Paciente

class PacienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Paciente
        fields = '__all__'


class PacienteListSerializer(serializers.ModelSerializer):
    nombre = serializers.SerializerMethodField()
    apellidos = serializers.SerializerMethodField()
    especialista = serializers.SerializerMethodField()
    rehabilitaciones = serializers.SerializerMethodField()

    class Meta:
        model = Paciente
        fields = ['id', 'nombre', 'apellidos', 'rehabilitaciones', 'especialista']

    def get_nombre(self, obj):
        return obj.usuario.first_name

    def get_apellidos(self, obj):
        return obj.usuario.last_name

    def get_especialista(self, obj):
        if obj.especialista:
            return obj.especialista.usuario.get_full_name().strip() or obj.especialista.usuario.username
        return "Sin asignar"

    def get_rehabilitaciones(self, obj):
        # Pendiente de conectar con sesiones reales.
        return 0