import secrets
import string
from datetime import datetime, date

from django.db import transaction
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate
from django.utils import timezone
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from usuarios.models import Usuario, Especialista, Paciente, Clinica

########################################### ESPECIALISTA ####################################################

@api_view(['POST'])
def login(request):
    username = request.data.get('username')
    password = request.data.get('password')

    user = Usuario.objects.filter(username=username).first()
    if user is None or user.rol != 'especialista':
        return Response({'error': 'Nombre de usuario incorrecto'}, status=status.HTTP_401_UNAUTHORIZED)

    if not user.check_password(password):
        return Response({'error': 'Contraseña incorrecta'}, status=status.HTTP_401_UNAUTHORIZED)

    user = authenticate(username=username, password=password)
    if user is None:
        return Response({'error': 'Credenciales incorrectas'}, status=status.HTTP_401_UNAUTHORIZED)

    user.last_login = timezone.now()
    user.save(update_fields=['last_login'])

    refresh = RefreshToken.for_user(user)
    nombre_completo = user.get_full_name().strip() or user.username
    return Response({
        'token': str(refresh.access_token),
        'refresh': str(refresh),
        'rol': user.rol,
        'nombre': nombre_completo,
        'email': user.email,
        'clinic_id': user.clinica_id,
    })

@api_view(['POST'])
def registro(request):
    username = (request.data.get('username') or '').strip()
    password = (request.data.get('password') or '').strip()
    email = (request.data.get('email') or '').strip()
    first_name = (request.data.get('first_name') or '').strip()
    last_name = (request.data.get('last_name') or '').strip()
    clinic_id = request.data.get('clinic_id')

    if not all([username, password, email, first_name, last_name]) or clinic_id in (None, ""):
        return Response({'error': 'Todos los campos son obligatorios'}, status=status.HTTP_400_BAD_REQUEST)
    elif len(username) > 150:
        return Response({'error': 'El nombre de usuario no puede superar 150 caracteres'}, status=status.HTTP_400_BAD_REQUEST)
    elif len(first_name) > 150:
        return Response({'error': 'El nombre no puede superar 150 caracteres'}, status=status.HTTP_400_BAD_REQUEST)
    elif len(last_name) > 150:
        return Response({'error': 'Los apellidos no pueden superar 150 caracteres'}, status=status.HTTP_400_BAD_REQUEST)
    elif len(email) > 254:
        return Response({'error': 'El correo electrónico no puede superar 254 caracteres'}, status=status.HTTP_400_BAD_REQUEST)

    username_validator = UnicodeUsernameValidator()
    try:
        username_validator(username)
    except ValidationError:
        return Response(
            {'error': 'El nombre de usuario solo puede contener letras, dígitos y @/./+/-/_'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        validate_email(email)
    except ValidationError:
        return Response({'error': 'El correo electrónico no es válido'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        clinic_id = int(clinic_id)
    except (TypeError, ValueError):
        return Response({'error': 'La clínica seleccionada no es válida'}, status=status.HTTP_400_BAD_REQUEST)

    clinica = Clinica.objects.filter(pk=clinic_id).first()
    if clinica is None:
        return Response({'error': 'La clínica seleccionada no existe'}, status=status.HTTP_400_BAD_REQUEST)

    temp_user = Usuario(username=username, email=email, first_name=first_name, last_name=last_name, rol='especialista')
    
    try:
        validate_password(password, user=temp_user)
    except ValidationError as exc:
        return Response({'error': exc.messages[0]}, status=status.HTTP_400_BAD_REQUEST)

    if Usuario.objects.filter(username=username).exists():
        return Response({'error': 'El nombre de usuario ya está en uso'}, status=status.HTTP_400_BAD_REQUEST)
    elif Usuario.objects.filter(email__iexact=email).exists():
        return Response({'error': 'El correo electrónico ya está en uso'}, status=status.HTTP_400_BAD_REQUEST)

    with transaction.atomic():
        user = Usuario.objects.create_user(
            username=username, password=password,
            email=email, first_name=first_name,
            last_name=last_name, rol='especialista',
            clinica=clinica,
        )
        Especialista.objects.get_or_create(usuario=user)
    user.last_login = timezone.now()
    user.save(update_fields=['last_login'])
    
    refresh = RefreshToken.for_user(user)
    nombre_completo = user.get_full_name().strip() or user.username
    return Response(
        {
            'token': str(refresh.access_token),
            'refresh': str(refresh),
            'nombre': nombre_completo,
            'email': user.email,
            'clinic_id': user.clinica_id,
        },
        status=status.HTTP_201_CREATED,
    )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    refresh_token = (request.data.get('refresh') or '').strip()
    if not refresh_token:
        return Response({'error': 'El refresh token es obligatorio'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        token = RefreshToken(refresh_token)
        token.blacklist()
    except TokenError:
        return Response({'error': 'Refresh token no válido o ya invalidado'}, status=status.HTTP_400_BAD_REQUEST)

    return Response({'message': 'Sesión cerrada correctamente'}, status=status.HTTP_200_OK)


@api_view(['GET'])
def clinicas(request):
    data = [
        {
            'id': clinica.idClinica,
            'nombre': clinica.nombre,
            'direccion': clinica.direccion,
        }
        for clinica in Clinica.objects.all().order_by('nombre')
    ]
    return Response(data, status=status.HTTP_200_OK)

@api_view(['GET'])
def nombre(request, name):
    user = Usuario.objects.filter(username=name).first()
    if user and user.rol == 'especialista':
        return Response({'nombre': user.get_full_name()})
    return Response({'error': 'Especialista no encontrado'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cambiar_contrasena(request):
    if request.user.rol != 'especialista':
        return Response({'error': 'Solo un especialista puede cambiar su contraseña'}, status=status.HTTP_403_FORBIDDEN)

    password = (request.data.get('password') or '').strip()

    if not password:
        return Response({'error': 'La contraseña es obligatoria'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        validate_password(password, user=request.user)
    except ValidationError as exc:
        return Response({'error': exc.messages[0]}, status=status.HTTP_400_BAD_REQUEST)

    request.user.set_password(password)
    request.user.save(update_fields=['password'])

    return Response({'message': 'Contraseña actualizada correctamente'}, status=status.HTTP_200_OK)



########################################### PACIENTE ####################################################

def _parse_birth_date(value: str):
    for fmt in ('%Y-%m-%d', '%d/%m/%Y'):
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            continue
    return None


def _generar_codigo(longitud: int = 7) -> str:
    caracteres = string.ascii_uppercase + string.digits
    return ''.join(secrets.choice(caracteres) for _ in range(longitud))


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def registro_paciente(request):
    username = (request.data.get('username') or '').strip()
    dni = (request.data.get('dni') or '').strip()
    email = (request.data.get('email') or '').strip()
    first_name = (request.data.get('first_name') or '').strip()
    last_name = (request.data.get('last_name') or '').strip()
    birth_date = (request.data.get('birth_date') or '').strip()

    if not all([username, dni, email, first_name, last_name, birth_date]):
        return Response({'error': 'Todos los campos son obligatorios'}, status=status.HTTP_400_BAD_REQUEST)
    elif len(username) > 150:
        return Response({'error': 'El nombre de usuario no puede superar 150 caracteres'}, status=status.HTTP_400_BAD_REQUEST)
    elif len(first_name) > 150:
        return Response({'error': 'El nombre no puede superar 150 caracteres'}, status=status.HTTP_400_BAD_REQUEST)
    elif len(last_name) > 150:
        return Response({'error': 'Los apellidos no pueden superar 150 caracteres'}, status=status.HTTP_400_BAD_REQUEST)
    elif len(email) > 254:
        return Response({'error': 'El correo electrónico no puede superar 254 caracteres'}, status=status.HTTP_400_BAD_REQUEST)

    username_validator = UnicodeUsernameValidator()
    try:
        username_validator(username)
    except ValidationError:
        return Response(
            {'error': 'El nombre de usuario solo puede contener letras, dígitos y @/./+/-/_'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if not dni.isdigit() or len(dni) != 8:
        return Response({'error': 'El DNI debe contener exactamente 8 dígitos'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        validate_email(email)
    except ValidationError:
        return Response({'error': 'El correo electrónico no es válido'}, status=status.HTTP_400_BAD_REQUEST)

    fecha_nacimiento = _parse_birth_date(birth_date)
    if fecha_nacimiento is None:
        return Response({'error': 'La fecha de nacimiento no es válida. Usa DD/MM/AAAA'}, status=status.HTTP_400_BAD_REQUEST)

    if fecha_nacimiento < date(1900, 1, 1) or fecha_nacimiento > date.today():
        return Response(
            {'error': 'La fecha de nacimiento debe estar entre 01/01/1900 y hoy'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if request.user.rol != 'especialista':
        return Response({'error': 'Solo un especialista puede registrar pacientes'}, status=status.HTTP_403_FORBIDDEN)

    especialista, _ = Especialista.objects.get_or_create(usuario=request.user)

    
    if Paciente.objects.filter(dni=dni).exists():
        return Response({'error': 'El DNI ya está en uso'}, status=status.HTTP_400_BAD_REQUEST)
    elif Usuario.objects.filter(username=username).exists():
        return Response({'error': 'El nombre de usuario ya está en uso'}, status=status.HTTP_400_BAD_REQUEST)
    elif Usuario.objects.filter(email__iexact=email).exists():
        return Response({'error': 'El correo electrónico ya está en uso'}, status=status.HTTP_400_BAD_REQUEST)

    codigo = _generar_codigo()

    with transaction.atomic():
        user = Usuario.objects.create_user(
            username=username,
            password=codigo,
            email=email,
            first_name=first_name,
            last_name=last_name,
            rol='paciente',
            clinica=request.user.clinica,
        )

        paciente = Paciente(
            usuario=user,
            especialista=especialista,
            dni=dni,
            fechaNacimiento=fecha_nacimiento,
            codigoInicioSesion=codigo,
        )
        try:
            paciente.full_clean()
        except ValidationError as exc:
            mensaje = exc.messages[0] if exc.messages else 'Los datos del paciente no son válidos'
            return Response({'error': mensaje}, status=status.HTTP_400_BAD_REQUEST)
        paciente.save()

    user.last_login = timezone.now()
    user.save(update_fields=['last_login'])

    return Response(
        {
            'codigo': codigo,
            'username': username,
            'nombre': user.get_full_name().strip() or user.username,
            'email': user.email,
            'clinic_id': user.clinica_id,
            'dni': dni,
            'birth_date': fecha_nacimiento.isoformat(),
        },
        status=status.HTTP_201_CREATED,
    )