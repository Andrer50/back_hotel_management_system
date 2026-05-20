from rest_framework import serializers
from django.contrib.auth.models import Group, Permission
from .models import Planta, Usuario, Huesped, Habitacion, Sede, AreaComun, RegistroLimpieza, Incidencia, Reserva, Inventario

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

class HuespedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Huesped
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
    

class PersonalLimpiezaSerializer(serializers.ModelSerializer):
    firstName = serializers.CharField(source='first_name')
    lastName = serializers.CharField(source='last_name')

    class Meta:
        model = Usuario
        fields = ('id', 'firstName', 'lastName', 'email', 'username')

class UsuarioResumenSerializer(serializers.ModelSerializer):
    # Serializer para mostrar nombre en la parte de limpiezas/incidencias
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = Usuario
        fields = ('id', 'full_name')

    def get_full_name(self, obj):
        return obj.get_full_name() or obj.username


class RegistroLimpiezaSerializer(serializers.ModelSerializer):
    personal_limpieza_details = UsuarioResumenSerializer(
        source='personal_limpieza', read_only=True
    )
    habitacion_numero = serializers.CharField(
        source='habitacion.numero', read_only=True
    )
    estado_display = serializers.CharField(
        source='get_estado_display', read_only=True
    )
    personal_limpieza = serializers.PrimaryKeyRelatedField(
        queryset=Usuario.objects.filter(is_active=True),
        required=False,
        allow_null=True
    )

    class Meta:
        model = RegistroLimpieza
        fields = '__all__'


class IncidenciaSerializer(serializers.ModelSerializer):
    asignado_a_details = UsuarioResumenSerializer(
        source='asignado_a', read_only=True
    )
    reportado_por_details = UsuarioResumenSerializer(
        source='reportado_por', read_only=True
    )
    reportado_por = serializers.PrimaryKeyRelatedField(
        read_only=True
    )
    fecha_reporte = serializers.DateTimeField(read_only=True)
    habitacion_numero = serializers.CharField(
        source='habitacion.numero', read_only=True
    )
    prioridad_display = serializers.CharField(
        source='get_prioridad_display', read_only=True
    )
    estado_display = serializers.CharField(
        source='get_estado_display', read_only=True
    )

    class Meta:
        model = Incidencia
        fields = '__all__'

    def validate(self, attrs):
        habitacion = attrs['habitacion'] if 'habitacion' in attrs else getattr(self.instance, 'habitacion', None)
        area_comun = attrs['area_comun'] if 'area_comun' in attrs else getattr(self.instance, 'area_comun', None)

        if not habitacion and not area_comun:
            raise serializers.ValidationError(
                'Debe especificar una habitacion o un area_comun para la incidencia.'
            )

        if habitacion and area_comun:
            raise serializers.ValidationError(
                'La incidencia solo puede estar asociada a una habitacion o a un area_comun, no a ambas.'
            )

        asignado_a = attrs.get('asignado_a')
        if asignado_a is not None:
            role = getattr(asignado_a, 'role', None)
            if not role or not role.permissions.filter(codename='can_do_maintenance').exists():
                raise serializers.ValidationError({
                    'asignado_a': 'El usuario asignado debe tener permisos de mantenimiento.'
                })

        return attrs

class ReservaSerializer(serializers.ModelSerializer):
    huesped_nombre = serializers.SerializerMethodField(read_only=True)
    habitacion_numero = serializers.CharField(source='habitacion.numero', read_only=True)
    noches = serializers.SerializerMethodField(read_only=True)
    total = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Reserva
        fields = '__all__'

    def get_huesped_nombre(self, obj):
        return f"{obj.huesped.nombre} {obj.huesped.apellido}"

    def get_noches(self, obj):
        if obj.fecha_salida and obj.fecha_entrada:
            diff = (obj.fecha_salida - obj.fecha_entrada).days
            return max(1, diff)
        return 1

    def get_total(self, obj):
        return obj.tarifa_aplicada * self.get_noches(obj)

class InventarioSerializer(serializers.ModelSerializer):
    sede_details = SedeSerializer(source='sede', read_only=True)

    class Meta:
        model = Inventario
        fields = '__all__'