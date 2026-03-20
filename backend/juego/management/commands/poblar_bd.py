import random
from datetime import timedelta
 
from django.contrib.auth.hashers import make_password
from django.core.management.base import BaseCommand
from django.utils import timezone
 
from usuarios.models import Clinica, Usuario, Especialista, Paciente
from juego.models import Minijuego, Progreso, Rehabilitacion, Edificio, Notas
from eye_tracking.models import AjustesPaciente, SesionGaze
 
 
GESTOS = ['Guiño ojo izquierdo', 'Abrir la boca', 'Cerrar los dos ojos']
 
NOMBRES_EDIFICIOS = ['biblioteca', 'huerto', 'museo', 'mercadillo', 'campanario']
 
CONTENIDOS_NOTAS = [
    'El paciente muestra mejoría notable en coordinación.',
    'Se recomienda aumentar la dificultad del siguiente nivel.',
    'Paciente reporta cansancio visual tras la sesión.',
    'Excelente progreso esta semana.',
    'Revisar calibración del dispositivo en la próxima visita.',
    'El paciente completó todos los edificios sin ayuda.',
    'Se observa dificultad con el minijuego de memoria.',
    'Sesión suspendida por indisposición del paciente.',
]
 
 
class Command(BaseCommand):
    #Clínicas
    def crear_clinicas(self):
        self.stdout.write(self.style.SUCCESS('▶ Creando clínicas...'))
        datos = [
            {'nombre': 'Clínica Sevilla Centro', 'direccion': 'Calle Sierpes 10',  'codigoPostal': '41001'},
            {'nombre': 'Clínica Norte',           'direccion': 'Av. Kansas City 5', 'codigoPostal': '41013'},
            {'nombre': 'Clínica Sur',             'direccion': 'Calle Feria 22',    'codigoPostal': '41004'},
        ]
        clinicas = []
        for d in datos:
            obj, created = Clinica.objects.get_or_create(nombre=d['nombre'], defaults=d)
            clinicas.append(obj)
            if created:
                self.stdout.write(f'  ✔ Clínica: {obj.nombre}')
        return clinicas
    
    #Especialistas
    def crear_especialistas(self, clinicas):
        datos = [
            {'username': 'ana.garcia',    'first_name': 'Ana',    'last_name': 'García López',   'email': 'ana.garcia@clinica.es'},
            {'username': 'carlos.mtz',    'first_name': 'Carlos', 'last_name': 'Martínez Ruiz',  'email': 'carlos.mtz@clinica.es'},
            {'username': 'lucia.fvega',   'first_name': 'Lucía',  'last_name': 'Fernández Vega', 'email': 'lucia.fvega@clinica.es'},
            {'username': 'pedro.sanchez', 'first_name': 'Pedro',  'last_name': 'Sánchez Torres', 'email': 'pedro.s@clinica.es'},
            {'username': 'marta.romero',  'first_name': 'Marta',  'last_name': 'Romero Díaz',    'email': 'marta.r@clinica.es'},
        ]
        especialistas = []
        for i, d in enumerate(datos):
            clinica_asignada = clinicas[i % len(clinicas)]
            usuario, created = Usuario.objects.get_or_create(
                username=d['username'],
                defaults={
                    'first_name': d['first_name'],
                    'last_name':  d['last_name'],
                    'email':      d['email'],
                    'password':   make_password('password123'),
                    'rol':        'especialista',
                    'clinica':    clinica_asignada,
                }
            )
            esp, _ = Especialista.objects.get_or_create(
                usuario=usuario
            )
            especialistas.append(esp)
            if created:
                self.stdout.write(f'  ✔ Especialista: {usuario.get_full_name()} - Clínica: {clinica_asignada.nombre}')
        return especialistas
 
    # Pacientes
    def crear_pacientes(self, especialistas):
        datos = [
            {'username': 'luis.perez',     'first_name': 'Luis',   'last_name': 'Pérez Gómez',    'email': 'luis.pg@mail.com',    'dni': '12345678', 'fecha': '1985-03-12'},
            {'username': 'elena.ruiz',     'first_name': 'Elena',  'last_name': 'Ruiz Morales',   'email': 'elena.rm@mail.com',   'dni': '23456789', 'fecha': '1990-07-22'},
            {'username': 'miguel.lc',      'first_name': 'Miguel', 'last_name': 'López Castro',   'email': 'miguel.lc@mail.com',  'dni': '34567890', 'fecha': '1978-11-05'},
            {'username': 'sofia.torres',   'first_name': 'Sofía',  'last_name': 'Torres Ibáñez',  'email': 'sofia.ti@mail.com',   'dni': '45678901', 'fecha': '1995-01-30'},
            {'username': 'jorge.navarro',  'first_name': 'Jorge',  'last_name': 'Navarro Gil',    'email': 'jorge.ng@mail.com',   'dni': '56789012', 'fecha': '1982-06-18'},
            {'username': 'carmen.molina',  'first_name': 'Carmen', 'last_name': 'Molina Reyes',   'email': 'carmen.mr@mail.com',  'dni': '67890123', 'fecha': '1993-09-09'},
            {'username': 'pablo.herrera',  'first_name': 'Pablo',  'last_name': 'Herrera Blanco', 'email': 'pablo.hb@mail.com',   'dni': '78901234', 'fecha': '1988-04-14'},
            {'username': 'isabel.jimenez', 'first_name': 'Isabel', 'last_name': 'Jiménez Cano',   'email': 'isabel.jc@mail.com',  'dni': '89012345', 'fecha': '1975-12-01'},
        ]
        pacientes = []
        for i, d in enumerate(datos):
            especialista_asignado = especialistas[i % len(especialistas)]
            # La clínica del paciente es la misma que la del especialista que lo atiende (acceso vía usuario)
            clinica_asignada = especialista_asignado.usuario.clinica
            
            usuario, created = Usuario.objects.get_or_create(
                username=d['username'],
                defaults={
                    'first_name': d['first_name'],
                    'last_name':  d['last_name'],
                    'email':      d['email'],
                    'password':   make_password('password123'),
                    'rol':        'paciente',
                    'clinica':    clinica_asignada,
                }
            )
            pac, _ = Paciente.objects.get_or_create(
                usuario=usuario,
                defaults={
                    'especialista':        especialista_asignado,
                    'dni':                 d['dni'],
                    'fechaNacimiento':     d['fecha'],
                    'codigoInicioSesion':  f'COD{i:04d}',
                }
            )
            pacientes.append(pac)
            if created:
                self.stdout.write(f'  ✔ Paciente: {usuario.get_full_name()} - Clínica: {clinica_asignada.nombre}')
        return pacientes
 
    # Ajustes de paciente (eye_tracking)
    def crear_ajustes(self, pacientes):
        for pac in pacientes:
            obj, created = AjustesPaciente.objects.get_or_create(
                paciente=pac.usuario,
                defaults={
                    'esta_calibrado':   random.choice([True, False]),
                    'gesto_clic':       random.choice(GESTOS),
                    'gesto_doble_clic': random.choice(GESTOS),
                    'sensibilidad':     round(random.uniform(0.5, 2.0), 2),
                }
            )
            if created:
                self.stdout.write(f'  ✔ Ajustes para: {pac.usuario.get_full_name()}')
 
    # Minijuegos
    def crear_minijuegos(self):
        nombres = ['Globos', 'Memoria', 'Puzzle', 'Laberinto', 'Colores']
        minijuegos = []
        for nombre in nombres:
            obj, created = Minijuego.objects.get_or_create(nombre=nombre)
            minijuegos.append(obj)
            if created:
                self.stdout.write(f'  ✔ Minijuego: {nombre}')
        return minijuegos
 
    # Rehabilitaciones + Edificios + Notas + SesionGaze
    def crear_rehabilitaciones(self, pacientes, especialistas, minijuegos):
        for pac in pacientes:
            # Progreso: uno por paciente (OneToOne con Usuario)
            progreso, _ = Progreso.objects.get_or_create(paciente=pac.usuario)
 
            for _ in range(2):  # 2 rehabilitaciones por paciente
                estado = random.choice(Rehabilitacion.EstadoRehabilitacion.values)
 
                # Generar puntuaciones de los 5 edificios primero,
                # para que la puntuación total de la rehab sea su suma real (0–15).
                puntuaciones_edificios = [random.randint(0, 3) for _ in NOMBRES_EDIFICIOS]
 
                rehab = Rehabilitacion.objects.create(
                    progreso=progreso,
                    estado=estado,
                    fechaFin=(timezone.now() - timedelta(days=random.randint(1, 10))
                              if estado == 'finalizado' else None),
                    puntuacionRehabilitacion=sum(puntuaciones_edificios),  # 0–15
                )
 
                # 5 edificios nuevos por cada rehabilitación.
                # Nombre fijo (choices), puntuación y estado propios de esta rehab.
                #   puntuacion 0 → bloqueado  (no jugado)
                #   puntuacion 1–2 → en_curso (jugado, no completado)
                #   puntuacion 3 → restaurado (completado)
                for nombre_ed, puntuacion_ed in zip(NOMBRES_EDIFICIOS, puntuaciones_edificios):
                    if puntuacion_ed == 0:
                        estado_ed = 'bloqueado'
                    elif puntuacion_ed == 3 or puntuacion_ed == 2:
                        estado_ed = 'restaurado'
                    else:
                        estado_ed = 'en_curso'
 
                    Edificio.objects.create(
                        rehabilitacion=rehab,
                        minijuego=random.choice(minijuegos),
                        nombre=nombre_ed,
                        estadoEdificio=estado_ed,
                        puntuacionEdificio=puntuacion_ed,
                    )
 
                # Datos de eye tracking para esta rehabilitación
                for _ in range(random.randint(5, 15)):
                    SesionGaze.objects.create(
                        rehabilitacion=rehab,
                        pos_x=round(random.uniform(0, 1920), 2),
                        pos_y=round(random.uniform(0, 1080), 2),
                        tipo_evento=random.choice(SesionGaze.TipoEvento.values),
                        duracion_ms=random.randint(50, 800),
                    )
 
                # Notas del especialista sobre el progreso
                for _ in range(random.randint(1, 3)):
                    Notas.objects.create(
                        progreso=progreso,
                        especialista=random.choice(especialistas).usuario,
                        contenido=random.choice(CONTENIDOS_NOTAS),
                    )
 
            self.stdout.write(f'  ✔ Rehabs + edificios + notas para: {pac.usuario.get_full_name()}')
 
    # Entry point
    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.MIGRATE_HEADING('\n══════ Poblando base de datos ══════\n'))
 
        # ── Limpieza previa (orden inverso a las FK) ──────────────────────
        self.stdout.write(self.style.WARNING('▶ Borrando datos existentes...'))
        SesionGaze.objects.all().delete()
        Notas.objects.all().delete()
        Edificio.objects.all().delete()
        Rehabilitacion.objects.all().delete()
        Progreso.objects.all().delete()
        AjustesPaciente.objects.all().delete()
        Minijuego.objects.all().delete()
        Paciente.objects.all().delete()
        Especialista.objects.all().delete()
        Usuario.objects.filter(is_superuser=False).delete()  # conserva superusuarios
        Clinica.objects.all().delete()
        self.stdout.write(self.style.WARNING('Base de datos limpia\n'))
        # ─────────────────────────────────────────────────────────────────
 
        self.stdout.write(self.style.MIGRATE_LABEL('▶ Clínicas'))
        clinicas = self.crear_clinicas()
 
        self.stdout.write(self.style.MIGRATE_LABEL('▶ Especialistas'))
        especialistas = self.crear_especialistas(clinicas)
 
        self.stdout.write(self.style.MIGRATE_LABEL('▶ Pacientes'))
        pacientes = self.crear_pacientes(especialistas)
 
        self.stdout.write(self.style.MIGRATE_LABEL('▶ Ajustes de paciente'))
        self.crear_ajustes(pacientes)
 
        self.stdout.write(self.style.MIGRATE_LABEL('▶ Minijuegos'))
        minijuegos = self.crear_minijuegos()
 
        self.stdout.write(self.style.MIGRATE_LABEL('▶ Rehabilitaciones / Edificios / Notas / SesionGaze'))
        self.crear_rehabilitaciones(pacientes, especialistas, minijuegos)
 
        self.stdout.write(self.style.SUCCESS('\n✅ Base de datos poblada correctamente.\n'))