import os
from django.core.management.base import BaseCommand
from django.db import transaction
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

from hotel.models import (
    Usuario,
    Sede,
    Planta,
    Habitacion,
    Inventario
)

class Command(BaseCommand):
    help = 'Puebla la base de datos con roles (grupos), permisos y un usuario administrador por defecto si no existen usuarios.'

    def handle(self, *args, **options):
        self.stdout.write("Iniciando proceso de seeding...")

        try:
            with transaction.atomic():
                # 1. Crear / Asegurar los Roles (Grupos) y sus Permisos
                roles_data = {
                    'Administrador': [
                        'can_clean_rooms', 'can_do_maintenance', 'can_manage_users',
                        'can_manage_roles', 'can_manage_inventory', 'can_manage_reservations',
                        'can_view_reports', 'can_manage_rooms'
                    ],
                    'Recepcionista': [
                        'can_manage_reservations', 'can_view_reports', 'can_manage_rooms'
                    ],
                    'Mantenimiento': [
                        'can_do_maintenance'
                    ],
                    'Limpieza': [
                        'can_clean_rooms'
                    ],
                    'Cliente': []
                }

                self.stdout.write("Configurando roles y permisos...")
                for role_name, permission_codenames in roles_data.items():
                    group, created = Group.objects.get_or_create(name=role_name)
                    if created:
                        self.stdout.write(f" - Rol '{role_name}' creado.")
                    
                    # Filtrar y asignar permisos correspondientes
                    perms = Permission.objects.filter(codename__in=permission_codenames)
                    group.permissions.set(perms)

                # 2. Crear una Sede por defecto
                self.stdout.write("Configurando Sede por defecto...")
                sede, created_sede = Sede.objects.get_or_create(
                    nombre="Sede Central",
                    defaults={
                        "direccion": "Av. Asturias 123, Lima",
                        "telefono": "+51999999999"
                    }
                )
                if created_sede:
                    self.stdout.write(" - Sede 'Sede Central' creada.")

                # 3. Crear una Planta por defecto
                self.stdout.write("Configurando Planta por defecto...")
                planta, created_planta = Planta.objects.get_or_create(
                    numero=1,
                    defaults={
                        "nombre": "Piso 1"
                    }
                )
                if created_planta:
                    self.stdout.write(" - Planta 'Piso 1' creada.")

                # 4. Crear un Usuario Administrador por defecto si no hay usuarios registrados
                self.stdout.write("Verificando usuarios existentes...")
                if Usuario.objects.count() == 0:
                    self.stdout.write("No se encontraron usuarios en la base de datos.")
                    self.stdout.write("Creando usuario administrador por defecto...")

                    admin_group = Group.objects.get(name='Administrador')
                    
                    admin_user = Usuario.objects.create_superuser(
                        username='admin@gmail.com',
                        email='admin@gmail.com',
                        password='Prueba123!',
                        first_name='Admin',
                        last_name='Admin',
                        role=admin_group,
                        sede_asignada=sede,
                        telefono='+51999999999',
                        status='ACTIVE'
                    )

                    self.stdout.write(
                        self.style.SUCCESS(
                            "\n=======================================================\n"
                            "¡USUARIO ADMINISTRADOR CREADO POR DEFECTO!\n"
                            "Email/Username: admin@gmail.com\n"
                            "Contraseña: adminpassword\n"
                            "=======================================================\n"
                        )
                    )
                else:
                    self.stdout.write("Ya existen usuarios registrados en el sistema. Se omite la creación del administrador por defecto.")

                # 5. Crear Habitaciones de demostración si no hay
                self.stdout.write("Configurando habitaciones de prueba...")
                if Habitacion.objects.count() == 0:
                    Habitacion.objects.create(
                        sede=sede,
                        planta=planta,
                        numero="101",
                        tipo="INDIVIDUAL",
                        capacidad=1,
                        precio_base=120.00,
                        estado="DISPONIBLE"
                    )
                    Habitacion.objects.create(
                        sede=sede,
                        planta=planta,
                        numero="102",
                        tipo="DOBLE",
                        capacidad=2,
                        precio_base=180.00,
                        estado="DISPONIBLE"
                    )
                    Habitacion.objects.create(
                        sede=sede,
                        planta=planta,
                        numero="103",
                        tipo="SUITE",
                        capacidad=2,
                        precio_base=350.00,
                        estado="DISPONIBLE"
                    )
                    self.stdout.write(" - Habitaciones 101, 102 y 103 creadas.")

                # 6. Crear Artículos de Inventario por defecto
                self.stdout.write("Configurando artículos de inventario de prueba...")
                if Inventario.objects.count() == 0:
                    Inventario.objects.create(
                        sede=sede,
                        nombre="Jabón de tocador",
                        stock_actual=50,
                        stock_minimo=10,
                        precio_unitario=2.50,
                        tipo="SUMINISTRO"
                    )
                    Inventario.objects.create(
                        sede=sede,
                        nombre="Agua Mineral 500ml",
                        stock_actual=100,
                        stock_minimo=20,
                        precio_unitario=4.00,
                        tipo="SUMINISTRO"
                    )
                    Inventario.objects.create(
                        sede=sede,
                        nombre="Juego de Sábanas Queen",
                        stock_actual=15,
                        stock_minimo=5,
                        precio_unitario=0.00,
                        tipo="INVENTARIO"
                    )
                    self.stdout.write(" - Artículos de inventario de prueba creados.")

            self.stdout.write(self.style.SUCCESS("¡Proceso de seeding completado exitosamente!"))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error durante el seeding: {str(e)}"))
