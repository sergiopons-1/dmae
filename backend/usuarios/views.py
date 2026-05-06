import secrets
import string
from datetime import datetime, date

from django.db import transaction
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import authenticate
from django.utils import timezone
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from usuarios.models import Usuario, Especialista, Paciente, Clinica
from juego.models import Progreso, Rehabilitacion, Edificio
from eye_tracking.models import AjustesPaciente


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    username = request.data.get('username')
    password = request.data.get('password')

    user = Usuario.objects.filter(username=username).first()
    if not user:
        return Response({'error': 'Nombre de usuario incorrecto'}, status=status.HTTP_401_UNAUTHORIZED)
    
    if not user.check_password(password):
        return Response({'error': 'Contraseña incorrecta'}, status=status.HTTP_401_UNAUTHORIZED)

    user = authenticate(username=username, password=password)
    if user is None:
        return Response({'error': 'Credenciales incorrectas'}, status=status.HTTP_401_UNAUTHORIZED)

    primer_login_paciente = user.rol == 'paciente' and user.last_login is None
    if not primer_login_paciente:
        user.last_login = timezone.now()
        user.save(update_fields=['last_login'])

    refresh = RefreshToken.for_user(user)
    nombre_completo = user.get_full_name().strip() or user.username
    if user.rol == 'especialista':
        return Response({
        'token': str(refresh.access_token),
        'refresh': str(refresh),
        'id': user.id,
        'rol': user.rol,
        'nombre': nombre_completo,
        'email': user.email,
        'clinic_id': user.clinica_id,
        })
    elif user.rol == 'paciente':
        paciente = Paciente.objects.filter(usuario=user).first()
        dni = paciente.dni if paciente else ""
        fecha_nacimiento = paciente.fechaNacimiento.isoformat() if paciente and paciente.fechaNacimiento else ""
        return Response({
            'token': str(refresh.access_token),
            'refresh': str(refresh),
            'id': paciente.id if paciente else user.id,
            'rol': user.rol,
            'nombre': nombre_completo,
            'email': user.email,
            'dni': dni,
            'birth_date': fecha_nacimiento,
            'force_password_change': primer_login_paciente,
        })

@api_view(['POST'])
@permission_classes([AllowAny])
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
@permission_classes([AllowAny])
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
@permission_classes([AllowAny])
def nombre(request, name):
    user = Usuario.objects.filter(username=name).first()
    if user and user.rol == 'especialista':
        return Response({'nombre': user.get_full_name()})
    return Response({'error': 'Especialista no encontrado'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cambiar_contrasena(request):
    password = (request.data.get('password') or '').strip()

    if not password:
        return Response({'error': 'La contraseña es obligatoria'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        validate_password(password, user=request.user)
    except ValidationError as exc:
        return Response({'error': exc.messages[0]}, status=status.HTTP_400_BAD_REQUEST)

    request.user.set_password(password)
    update_fields = ['password']
    if request.user.last_login is None:
        request.user.last_login = timezone.now()
        update_fields.append('last_login')
    request.user.save(update_fields=update_fields)

    return Response({'message': 'Contraseña actualizada correctamente'}, status=status.HTTP_200_OK)


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


NOMBRES_EDIFICIOS_REHABILITACION = [
    Edificio.NombreEdificio.BIBLIOTECA,
    Edificio.NombreEdificio.HUERTO,
    Edificio.NombreEdificio.MUSEO,
    Edificio.NombreEdificio.MERCADILLO,
    Edificio.NombreEdificio.CAMPANARIO,
]


def _estado_edificio_por_puntuacion(puntuacion: int) -> str:
    if puntuacion >= 2:
        return Edificio.EstadoEdificio.RESTAURADO
    return Edificio.EstadoEdificio.EN_CURSO


def _siguiente_edificio(edificios: list[dict]) -> str | None:
    for item in edificios:
        if item.get('estado') == Edificio.EstadoEdificio.EN_CURSO:
            return item.get('nombre')
    for item in edificios:
        if item.get('estado') == Edificio.EstadoEdificio.BLOQUEADO:
            return item.get('nombre')
    return None


def _asegurar_edificios_rehabilitacion(rehabilitacion: Rehabilitacion) -> list[Edificio]:
    existentes = {
        e.nombre: e
        for e in Edificio.objects.filter(rehabilitacion=rehabilitacion)
    }

    for nombre_edificio in NOMBRES_EDIFICIOS_REHABILITACION:
        if nombre_edificio in existentes:
            continue
        existentes[nombre_edificio] = Edificio.objects.create(
            rehabilitacion=rehabilitacion,
            nombre=nombre_edificio,
            estadoEdificio=Edificio.EstadoEdificio.BLOQUEADO,
            puntuacionEdificio=0,
        )

    return [existentes[nombre] for nombre in NOMBRES_EDIFICIOS_REHABILITACION]


def _activar_siguiente_bloqueado(edificios: list[Edificio]) -> str | None:
    for edificio in edificios:
        if edificio.estadoEdificio == Edificio.EstadoEdificio.EN_CURSO:
            return edificio.nombre

    for edificio in edificios:
        if edificio.estadoEdificio == Edificio.EstadoEdificio.BLOQUEADO:
            edificio.estadoEdificio = Edificio.EstadoEdificio.EN_CURSO
            edificio.save(update_fields=['estadoEdificio'])
            return edificio.nombre

    return None


def _actualizar_estado_rehabilitacion(rehabilitacion: Rehabilitacion, edificios: list[Edificio]) -> None:
    puntuacion_total = sum(int(e.puntuacionEdificio or 0) for e in edificios)
    todos_restaurados = all(e.estadoEdificio == Edificio.EstadoEdificio.RESTAURADO for e in edificios)

    update_fields = ['puntuacionRehabilitacion']
    rehabilitacion.puntuacionRehabilitacion = puntuacion_total

    if todos_restaurados:
        rehabilitacion.estado = Rehabilitacion.EstadoRehabilitacion.FINALIZADO
        rehabilitacion.fechaFin = timezone.now()
        update_fields.extend(['estado', 'fechaFin'])
    elif rehabilitacion.estado != Rehabilitacion.EstadoRehabilitacion.EN_CURSO:
        rehabilitacion.estado = Rehabilitacion.EstadoRehabilitacion.EN_CURSO
        rehabilitacion.fechaFin = None
        update_fields.extend(['estado', 'fechaFin'])

    rehabilitacion.save(update_fields=update_fields)


def _ajustes_calibracion_paciente(usuario) -> AjustesPaciente:
    ajustes, _ = AjustesPaciente.objects.get_or_create(
        paciente=usuario,
        defaults={
            'esta_calibrado': False,
            'sensibilidad': 1.0,
        },
    )
    return ajustes


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def mi_progreso_paciente(request):
    if request.user.rol != 'paciente':
        return Response({'error': 'Solo pacientes pueden consultar este recurso'}, status=status.HTTP_403_FORBIDDEN)

    progreso = Progreso.objects.filter(paciente=request.user).first()
    if progreso is None:
        return Response({'rehabilitaciones': []}, status=status.HTTP_200_OK)

    rehabilitaciones_qs = Rehabilitacion.objects.filter(progreso=progreso).order_by('fechaInicio')
    rehabilitaciones = [
        {
            'idRehabilitacion': item.idRehabilitacion,
            'Número': str(indice),
            'Fecha inicio': item.fechaInicio.date().isoformat() if item.fechaInicio else '-',
            'Fecha fin': item.fechaFin.date().isoformat() if item.fechaFin else '-',
            'Estado': item.get_estado_display(),
            'estado_codigo': item.estado,
            'Puntuación': item.puntuacionRehabilitacion,
        }
        for indice, item in enumerate(rehabilitaciones_qs, start=1)
    ]

    return Response({'rehabilitaciones': rehabilitaciones}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def iniciar_rehabilitacion_paciente(request):
    if request.user.rol != 'paciente':
        return Response(
            {'error': 'Solo pacientes pueden iniciar una rehabilitación'},
            status=status.HTTP_403_FORBIDDEN,
        )

    ajustes = _ajustes_calibracion_paciente(request.user)
    if not ajustes.esta_calibrado:
        return Response(
            {'error': 'Debes calibrar la mirada en Ajustes antes de iniciar una rehabilitación'},
            status=status.HTTP_409_CONFLICT,
        )

    progreso, _ = Progreso.objects.get_or_create(paciente=request.user)

    with transaction.atomic():
        rehabilitacion = Rehabilitacion.objects.create(
            progreso=progreso,
            estado=Rehabilitacion.EstadoRehabilitacion.EN_CURSO,
            puntuacionRehabilitacion=0,
        )
        edificios = _asegurar_edificios_rehabilitacion(rehabilitacion)
        siguiente = _activar_siguiente_bloqueado(edificios)

    return Response(
        {
            'idRehabilitacion': rehabilitacion.idRehabilitacion,
            'estado': rehabilitacion.estado,
            'fechaInicio': rehabilitacion.fechaInicio.isoformat() if rehabilitacion.fechaInicio else None,
            'puntuacionRehabilitacion': rehabilitacion.puntuacionRehabilitacion,
            'siguienteEdificio': siguiente,
        },
        status=status.HTTP_201_CREATED,
    )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def registrar_puntuacion_edificio_paciente(request):
    if request.user.rol != 'paciente':
        return Response(
            {'error': 'Solo pacientes pueden registrar puntuaciones'},
            status=status.HTTP_403_FORBIDDEN,
        )

    ajustes = _ajustes_calibracion_paciente(request.user)
    if not ajustes.esta_calibrado:
        return Response(
            {'error': 'Debes calibrar la mirada en Ajustes antes de jugar'},
            status=status.HTTP_409_CONFLICT,
        )

    nombre_edificio = (request.data.get('edificio') or '').strip().lower()
    puntuacion = request.data.get('puntuacion')
    id_rehabilitacion = request.data.get('idRehabilitacion')

    if not nombre_edificio:
        return Response({'error': 'El campo edificio es obligatorio'}, status=status.HTTP_400_BAD_REQUEST)

    edificios_validos = {str(valor) for valor, _ in Edificio.NombreEdificio.choices}
    if nombre_edificio not in edificios_validos:
        return Response({'error': 'El edificio indicado no es válido'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        puntuacion = int(puntuacion)
    except (TypeError, ValueError):
        return Response({'error': 'La puntuación debe ser un número entero'}, status=status.HTTP_400_BAD_REQUEST)

    if puntuacion < 0 or puntuacion > 3:
        return Response({'error': 'La puntuación debe estar entre 0 y 3'}, status=status.HTTP_400_BAD_REQUEST)

    progreso = Progreso.objects.filter(paciente=request.user).first()
    if progreso is None:
        return Response({'error': 'No existe progreso para este paciente'}, status=status.HTTP_400_BAD_REQUEST)

    rehabilitaciones_en_curso = Rehabilitacion.objects.filter(
        progreso=progreso,
        estado=Rehabilitacion.EstadoRehabilitacion.EN_CURSO,
    )

    if id_rehabilitacion is not None:
        try:
            id_rehabilitacion = int(id_rehabilitacion)
        except (TypeError, ValueError):
            return Response({'error': 'idRehabilitacion no es válido'}, status=status.HTTP_400_BAD_REQUEST)

        rehabilitacion = rehabilitaciones_en_curso.filter(idRehabilitacion=id_rehabilitacion).first()
    else:
        rehabilitacion = rehabilitaciones_en_curso.order_by('-fechaInicio', '-idRehabilitacion').first()

    if rehabilitacion is None:
        return Response({'error': 'No hay una rehabilitación en curso'}, status=status.HTTP_400_BAD_REQUEST)

    with transaction.atomic():
        Rehabilitacion.objects.select_for_update().filter(idRehabilitacion=rehabilitacion.idRehabilitacion).exists()
        edificios = _asegurar_edificios_rehabilitacion(rehabilitacion)
        edificios_por_nombre = {e.nombre: e for e in edificios}
        edificio = edificios_por_nombre.get(nombre_edificio)

        if edificio is None:
            return Response({'error': 'El edificio indicado no pertenece a la rehabilitación'}, status=status.HTTP_400_BAD_REQUEST)

        edificio_en_curso = next(
            (e for e in edificios if e.estadoEdificio == Edificio.EstadoEdificio.EN_CURSO),
            None,
        )
        if edificio_en_curso is None:
            _activar_siguiente_bloqueado(edificios)
            edificio_en_curso = next(
                (e for e in edificios if e.estadoEdificio == Edificio.EstadoEdificio.EN_CURSO),
                None,
            )

        if edificio_en_curso is not None and edificio_en_curso.nombre != nombre_edificio:
            return Response(
                {
                    'error': 'Debes jugar primero el edificio en curso',
                    'edificioEnCurso': edificio_en_curso.nombre,
                },
                status=status.HTTP_409_CONFLICT,
            )

        edificio.puntuacionEdificio = puntuacion
        edificio.estadoEdificio = _estado_edificio_por_puntuacion(puntuacion)
        edificio.save(update_fields=['puntuacionEdificio', 'estadoEdificio'])

        if edificio.estadoEdificio == Edificio.EstadoEdificio.RESTAURADO:
            _activar_siguiente_bloqueado(edificios)

        _actualizar_estado_rehabilitacion(rehabilitacion, edificios)

        edificios_payload = [
            {
                'nombre': e.nombre,
                'estado': e.estadoEdificio,
                'puntuacion': e.puntuacionEdificio,
            }
            for e in edificios
        ]

    return Response(
        {
            'idRehabilitacion': rehabilitacion.idRehabilitacion,
            'edificio': nombre_edificio,
            'puntuacionEdificio': edificio.puntuacionEdificio,
            'estadoEdificio': edificio.estadoEdificio,
            'estadoRehabilitacion': rehabilitacion.estado,
            'puntuacionRehabilitacion': rehabilitacion.puntuacionRehabilitacion,
            'edificios': edificios_payload,
            'siguienteEdificio': _siguiente_edificio(edificios_payload),
        },
        status=status.HTTP_200_OK,
    )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def detalle_rehabilitacion_paciente(request, id_rehabilitacion):
    if request.user.rol != 'paciente':
        return Response({'error': 'Solo pacientes pueden consultar este recurso'}, status=status.HTTP_403_FORBIDDEN)

    ajustes = _ajustes_calibracion_paciente(request.user)
    if not ajustes.esta_calibrado:
        return Response(
            {'error': 'Debes calibrar la mirada en Ajustes antes de continuar la rehabilitación'},
            status=status.HTTP_409_CONFLICT,
        )

    progreso = Progreso.objects.filter(paciente=request.user).first()
    if progreso is None:
        return Response({'error': 'No existe progreso para este paciente'}, status=status.HTTP_400_BAD_REQUEST)

    rehabilitacion = Rehabilitacion.objects.filter(
        progreso=progreso,
        idRehabilitacion=id_rehabilitacion,
    ).first()
    if rehabilitacion is None:
        return Response({'error': 'Rehabilitación no encontrada'}, status=status.HTTP_404_NOT_FOUND)

    if rehabilitacion.estado != Rehabilitacion.EstadoRehabilitacion.EN_CURSO:
        return Response({'error': 'Solo se puede continuar rehabilitaciones en curso'}, status=status.HTTP_400_BAD_REQUEST)

    with transaction.atomic():
        Rehabilitacion.objects.select_for_update().filter(idRehabilitacion=rehabilitacion.idRehabilitacion).exists()
        edificios_model = _asegurar_edificios_rehabilitacion(rehabilitacion)
        _activar_siguiente_bloqueado(edificios_model)
        edificios = [
            {
                'nombre': e.nombre,
                'estado': e.estadoEdificio,
                'puntuacion': e.puntuacionEdificio,
            }
            for e in edificios_model
        ]

    return Response(
        {
            'idRehabilitacion': rehabilitacion.idRehabilitacion,
            'estado': rehabilitacion.estado,
            'puntuacionRehabilitacion': rehabilitacion.puntuacionRehabilitacion,
            'edificios': edificios,
            'siguienteEdificio': _siguiente_edificio(edificios),
        },
        status=status.HTTP_200_OK,
    )


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