from rest_framework import serializers
from django.contrib.auth.models import Group, Permission
from django.contrib.auth import get_user_model
from datetime import datetime, timedelta  # ← AGREGAR ESTO
from .models import Planta, Usuario, Huesped, Habitacion, Sede, AreaComun, Reserva  # ← AGREGAR Reserva

User = get_user_model()

# ================================================================
# SERIALIZERS EXISTENTES (que ya tenía el orquestador)
# ================================================================

class SedeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sede
        fields = '__all__'

class AreaComunSerializer(serializers.ModelSerializer):
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    sede_details = SedeSerializer(source='sede', read_only=True)

    class Meta:
        model = AreaComun
        fields = '__all__'

class PlantaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Planta
        fields = '__all__'

class HabitacionSerializer(serializers.ModelSerializer):
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    sede = serializers.PrimaryKeyRelatedField(queryset=Sede.objects.all(), required=False, allow_null=True)
    planta_details = PlantaSerializer(source='planta', read_only=True)

    class Meta:
        model = Habitacion
        fields = '__all__'

class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ('id', 'name', 'codename')

class RoleSerializer(serializers.ModelSerializer):
    permissions = PermissionSerializer(many=True, read_only=True)
    permission_ids = serializers.PrimaryKeyRelatedField(
        queryset=Permission.objects.all(),
        many=True,
        write_only=True,
        required=False
    )

    class Meta:
        model = Group
        fields = ('id', 'name', 'permissions', 'permission_ids')

    def create(self, validated_data):
        permission_ids = validated_data.pop('permission_ids', [])
        group = Group.objects.create(**validated_data)
        if permission_ids:
            group.permissions.set(permission_ids)
        return group

    def update(self, instance, validated_data):
        permission_ids = validated_data.pop('permission_ids', None)
        instance.name = validated_data.get('name', instance.name)
        instance.save()
        if permission_ids is not None:
            instance.permissions.set(permission_ids)
        return instance

class UsuarioSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    repeatPassword = serializers.CharField(write_only=True, required=False)
    username = serializers.CharField(required=False)

    firstName = serializers.CharField(source='first_name', required=False)
    lastName = serializers.CharField(source='last_name', required=False)
    phone = serializers.CharField(source='telefono', required=False)
    
    role_details = RoleSerializer(source='role', read_only=True)
    role = serializers.PrimaryKeyRelatedField(
        queryset=Group.objects.all(),
        required=False,
        allow_null=True
    )

    class Meta:
        model = Usuario
        fields = ('id', 'username', 'email', 'password', 'repeatPassword', 'firstName', 'lastName', 'role', 'role_details', 'sede_asignada', 'phone')

    def create(self, validated_data):
        validated_data.pop('repeatPassword', None)

        first_name = validated_data.get('first_name', '')
        last_name = validated_data.get('last_name', '')
        telefono = validated_data.get('telefono', '')
        email = validated_data.get('email', '')
        username = validated_data.get('username')
        role = validated_data.get('role', None)
        
        if not username and email:
            username = email

        if not role:
            role, _ = Group.objects.get_or_create(name='Administrador')

        user = Usuario.objects.create_user(
            username=username,
            email=email,
            password=validated_data['password'],
            first_name=first_name,
            last_name=last_name,
            role=role,
            sede_asignada=validated_data.get('sede_asignada', None),
            telefono=telefono
        )
        return user


# ================================================================
# RF-09: HUÉSPEDES (VERSIÓN CORRECTA - SOLO UNA VEZ)
# ================================================================

class HuespedSerializer(serializers.ModelSerializer):
    nombre_completo = serializers.SerializerMethodField()
    estado = serializers.SerializerMethodField()
    ultima_visita = serializers.SerializerMethodField()
    total_estancias = serializers.SerializerMethodField()
    
    class Meta:
        model = Huesped
        fields = [
            'id', 'nombre', 'apellido', 'nombre_completo',
            'tipo_documento', 'documento', 'email', 'telefono',
            'preferencias_notas', 'estado', 'ultima_visita', 'total_estancias'
        ]
    
    def get_nombre_completo(self, obj):
        return f"{obj.nombre} {obj.apellido}"
    
    def get_estado(self, obj):
        seis_meses_atras = datetime.now().date() - timedelta(days=180)
        ultimas_reservas = obj.reservas.filter(fecha_entrada__gte=seis_meses_atras)
        return "ACTIVO" if ultimas_reservas.exists() else "INACTIVO"
    
    def get_ultima_visita(self, obj):
        ultima_reserva = obj.reservas.filter(
            estado__in=['COMPLETADA', 'EN_CURSO']
        ).order_by('-fecha_entrada').first()
        if ultima_reserva:
            return ultima_reserva.fecha_entrada.strftime('%d %b, %Y')
        return None
    
    def get_total_estancias(self, obj):
        return obj.reservas.filter(estado='COMPLETADA').count()


# ================================================================
# RF-10: HABITACIONES (VERSIÓN SIN SEDE - como pidió el equipo)
# ================================================================

class HabitacionListSerializer(serializers.ModelSerializer):
    """Serializer para listar habitaciones (sin sede)"""
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    
    class Meta:
        model = Habitacion
        fields = [
            'id', 'numero', 'tipo', 'tipo_display', 'capacidad',
            'precio_base', 'estado', 'estado_display'
        ]


# ================================================================
# RF-10: RESERVAS
# ================================================================

class ReservaSerializer(serializers.ModelSerializer):
    huesped_nombre = serializers.SerializerMethodField()
    huesped_documento = serializers.CharField(source='huesped.documento', read_only=True)
    habitacion_numero = serializers.CharField(source='habitacion.numero', read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    origen_display = serializers.CharField(source='get_origen_display', read_only=True)
    noches = serializers.SerializerMethodField()
    total = serializers.SerializerMethodField()
    
    class Meta:
        model = Reserva
        fields = [
            'id', 'codigo_reserva', 'huesped', 'huesped_nombre', 'huesped_documento',
            'habitacion', 'habitacion_numero',
            'fecha_entrada', 'fecha_salida', 'fecha_reserva',
            'estado', 'estado_display', 'tarifa_aplicada',
            'origen', 'origen_display', 'noches', 'total'
        ]
        read_only_fields = ['codigo_reserva']  
    
    def get_huesped_nombre(self, obj):
        return f"{obj.huesped.nombre} {obj.huesped.apellido}"
    
    def get_noches(self, obj):
        return (obj.fecha_salida - obj.fecha_entrada).days
    
    def get_total(self, obj):
        return float(obj.tarifa_aplicada) * self.get_noches(obj)