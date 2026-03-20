from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from ..models import Paciente
from .serializer import PacienteSerializer, PacienteListSerializer

class PacienteViewSet(viewsets.ModelViewSet):
    queryset = Paciente.objects.all()
    serializer_class = PacienteSerializer

    @action(detail=False, methods=['get'])
    def por_clinica(self, request):
        clinic_id = request.query_params.get('clinic_id')
        if not clinic_id:
            return Response(
                {'error': 'clinic_id es requerido'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        pacientes = Paciente.objects.filter(
            usuario__clinica_id=clinic_id
        ).select_related('usuario', 'especialista__usuario')

        serializer = PacienteListSerializer(pacientes, many=True)
        return Response(serializer.data)