from rest_framework import serializers
from django.contrib.auth.models import Group, Permission
from django.contrib.auth import get_user_model
from datetime import datetime, timedelta  # ← AGREGAR ESTO
from .models import Planta, Usuario, Huesped, Habitacion, Sede, AreaComun, RegistroLimpieza, Incidencia, Reserva, Inventario, Reserva  # ← AGREGAR Reserva

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