from rest_framework import serializers
from django.contrib.auth.models import Group, Permission
from .models import Usuario

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
    repeatPassword = serializers.CharField(write_only=True, required=False)  # ignorado, solo validación front
    username = serializers.CharField(required=False)  # se deriva del email si no se envía

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
        # Descartar campos que son solo del frontend
        validated_data.pop('repeatPassword', None)

        # Extraemos los datos mapeados
        first_name = validated_data.get('first_name', '')
        last_name = validated_data.get('last_name', '')
        telefono = validated_data.get('telefono', '')
        email = validated_data.get('email', '')
        username = validated_data.get('username')
        role = validated_data.get('role', None)
        
        # Si no viene username (porque el front envía email), usamos email como username
        if not username and email:
            username = email

        # Asignamos el rol por defecto ADMIN si no se envía ninguno y es el requerimiento
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