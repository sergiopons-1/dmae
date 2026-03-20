from django.shortcuts import render

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from django.utils import timezone
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from rest_framework_simplejwt.tokens import RefreshToken
from usuarios.models import Usuario, Especialista, Clinica

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
        'rol': user.rol,
        'nombre': nombre_completo,
        'email': user.email,
    })

@api_view(['POST'])
def registro(request):
    username = (request.data.get('username') or '').strip()
    password = (request.data.get('password') or '').strip()
    email = (request.data.get('email') or '').strip()
    first_name = (request.data.get('first_name') or '').strip()
    last_name = (request.data.get('last_name') or '').strip()

    if not all([username, password, email, first_name, last_name]):
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

    temp_user = Usuario(username=username, email=email, first_name=first_name, last_name=last_name, rol='especialista')
    
    try:
        validate_password(password, user=temp_user)
    except ValidationError as exc:
        return Response({'error': exc.messages[0]}, status=status.HTTP_400_BAD_REQUEST)

    if Usuario.objects.filter(username=username).exists():
        return Response({'error': 'El nombre de usuario ya está en uso'}, status=status.HTTP_400_BAD_REQUEST)
    elif Usuario.objects.filter(email__iexact=email).exists():
        return Response({'error': 'El correo electrónico ya está en uso'}, status=status.HTTP_400_BAD_REQUEST)

    user = Usuario.objects.create_user(
        username=username, password=password,
        email=email, first_name=first_name,
        last_name=last_name, rol='especialista'
    )
    user.last_login = timezone.now()
    user.save(update_fields=['last_login'])
    
    refresh = RefreshToken.for_user(user)
    nombre_completo = user.get_full_name().strip() or user.username
    return Response(
        {'token': str(refresh.access_token), 'nombre': nombre_completo, 'email': user.email},
        status=status.HTTP_201_CREATED,
    )

@api_view(['GET'])
def nombre(request, name):
    user = Usuario.objects.filter(username=name).first()
    if user and user.rol == 'especialista':
        return Response({'nombre': user.get_full_name()})
    return Response({'error': 'Especialista no encontrado'}, status=status.HTTP_404_NOT_FOUND)