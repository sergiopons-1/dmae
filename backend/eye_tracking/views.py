from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import AjustesPaciente


def _obtener_o_crear_ajustes(usuario):
    defaults = {
        'esta_calibrado': False,
        'sensibilidad': 1.0,
    }
    ajustes, _ = AjustesPaciente.objects.get_or_create(
        paciente=usuario,
        defaults=defaults,
    )
    return ajustes


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def obtener_ajustes_calibracion(request):
    if request.user.rol != 'paciente':
        return Response(
            {'error': 'Solo pacientes pueden consultar este recurso'},
            status=status.HTTP_403_FORBIDDEN,
        )

    ajustes = _obtener_o_crear_ajustes(request.user)
    return Response(
        {
            'esta_calibrado': ajustes.esta_calibrado,
            'sensibilidad': ajustes.sensibilidad,
        },
        status=status.HTTP_200_OK,
    )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def guardar_ajustes_calibracion(request):
    if request.user.rol != 'paciente':
        return Response(
            {'error': 'Solo pacientes pueden modificar este recurso'},
            status=status.HTTP_403_FORBIDDEN,
        )

    sensibilidad = request.data.get('sensibilidad', 1.0)
    esta_calibrado = bool(request.data.get('esta_calibrado', True))

    try:
        sensibilidad = float(sensibilidad)
    except (TypeError, ValueError):
        return Response(
            {'error': 'La sensibilidad debe ser un número válido'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if sensibilidad < 0.2 or sensibilidad > 3.0:
        return Response(
            {'error': 'La sensibilidad debe estar entre 0.2 y 3.0'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    ajustes = _obtener_o_crear_ajustes(request.user)
    ajustes.esta_calibrado = esta_calibrado
    ajustes.sensibilidad = sensibilidad
    ajustes.save(update_fields=['esta_calibrado', 'sensibilidad'])

    return Response(
        {
            'message': 'Calibración guardada correctamente',
            'esta_calibrado': ajustes.esta_calibrado,
            'sensibilidad': ajustes.sensibilidad,
        },
        status=status.HTTP_200_OK,
    )
