from rest_framework import serializers
from .models import Usuario

class UsuarioSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    repeatPassword = serializers.CharField(write_only=True, required=False)  # ignorado, solo validación front
    username = serializers.CharField(required=False)  # se deriva del email si no se envía

    firstName = serializers.CharField(source='first_name', required=False)
    lastName = serializers.CharField(source='last_name', required=False)
    phone = serializers.CharField(source='telefono', required=False)

    class Meta:
        model = Usuario
        fields = ('id', 'username', 'email', 'password', 'repeatPassword', 'firstName', 'lastName', 'role', 'sede_asignada', 'phone')

    def create(self, validated_data):
        # Descartar campos que son solo del frontend
        validated_data.pop('repeatPassword', None)

        # Extraemos los datos mapeados
        first_name = validated_data.get('first_name', '')
        last_name = validated_data.get('last_name', '')
        telefono = validated_data.get('telefono', '')
        email = validated_data.get('email', '')
        username = validated_data.get('username')
        
        # Si no viene username (porque el front envía email), usamos email como username
        if not username and email:
            username = email

        user = Usuario.objects.create_user(
            username=username,
            email=email,
            password=validated_data['password'],
            first_name=first_name,
            last_name=last_name,
            role=validated_data.get('role', Usuario.Rol.USER),
            sede_asignada=validated_data.get('sede_asignada', None),
            telefono=telefono
        )
        return user