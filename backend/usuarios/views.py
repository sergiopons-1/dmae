from django.shortcuts import render

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from usuarios.models import Usuario, Especialista, Clinica

@api_view(['POST'])
def login(request):
    username = request.data.get('username')
    password = request.data.get('password')
    
    user = authenticate(username=username, password=password)
    if user is None:
        return Response({'error': 'Credenciales incorrectas'}, status=status.HTTP_401_UNAUTHORIZED)
    
    refresh = RefreshToken.for_user(user)
    return Response({
        'token': str(refresh.access_token),
        'rol': user.rol,
        'nombre': user.get_full_name(),
    })

@api_view(['POST'])
def registro(request):
    username   = request.data.get('username')
    password   = request.data.get('password')
    email      = request.data.get('email')
    first_name = request.data.get('first_name')
    last_name  = request.data.get('last_name')

    if Usuario.objects.filter(username=username).exists():
        return Response({'error': 'El usuario ya existe'}, status=status.HTTP_400_BAD_REQUEST)

    user = Usuario.objects.create_user(
        username=username, password=password,
        email=email, first_name=first_name,
        last_name=last_name, rol='especialista'
    )
    refresh = RefreshToken.for_user(user)
    return Response({'token': str(refresh.access_token)}, status=status.HTTP_201_CREATED)