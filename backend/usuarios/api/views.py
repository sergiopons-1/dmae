from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from ..models import Paciente
from juego.models import Progreso, Rehabilitacion, Notas
from .serializer import PacienteSerializer, PacienteListSerializer

class PacienteViewSet(viewsets.ModelViewSet):
    queryset = Paciente.objects.all()
    serializer_class = PacienteSerializer
    permission_classes = [IsAuthenticated]

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

    @action(detail=True, methods=['get'])
    def progreso_individual(self, request, pk=None):
        paciente = Paciente.objects.filter(pk=pk).select_related('usuario').first()
        if paciente is None:
            return Response({'error': 'Paciente no encontrado'}, status=status.HTTP_404_NOT_FOUND)

        if request.user.rol != 'especialista':
            return Response({'error': 'Solo especialistas pueden consultar este recurso'}, status=status.HTTP_403_FORBIDDEN)

        if request.user.clinica_id != paciente.usuario.clinica_id:
            return Response({'error': 'No autorizado para este paciente'}, status=status.HTTP_403_FORBIDDEN)

        progreso = Progreso.objects.filter(paciente=paciente.usuario).first()
        if progreso is None:
            return Response(
                {
                    'paciente': {
                        'id': paciente.id,
                        'nombre': paciente.usuario.first_name,
                        'apellidos': paciente.usuario.last_name,
                    },
                    'rehabilitaciones': [],
                    'notas': [],
                }
            )

        rehabilitaciones_qs = Rehabilitacion.objects.filter(progreso=progreso).order_by('fechaInicio')
        notas_qs = Notas.objects.filter(progreso=progreso).order_by('-fechaNota')

        rehabilitaciones = [
            {
                'Número': str(indice),
                'Fecha inicio': item.fechaInicio.date().isoformat() if item.fechaInicio else '-',
                'Fecha fin': item.fechaFin.date().isoformat() if item.fechaFin else '-',
                'Estado': item.get_estado_display(),
                'Puntuación': item.puntuacionRehabilitacion,
            }
            for indice, item in enumerate(rehabilitaciones_qs, start=1)
        ]

        notas = [
            {
                'Número de nota': str(indice),
                'Descripción': item.contenido,
                'Fecha de emisión': item.fechaNota.date().isoformat() if item.fechaNota else '-',
            }
            for indice, item in enumerate(notas_qs, start=1)
        ]

        return Response(
            {
                'paciente': {
                    'id': paciente.id,
                    'nombre': paciente.usuario.first_name,
                    'apellidos': paciente.usuario.last_name,
                },
                'rehabilitaciones': rehabilitaciones,
                'notas': notas,
            }
        )