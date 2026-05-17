from rest_framework import status 
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from .utils import ApiResponse

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        # Extraemos los codenames de los permisos asociados al rol
        permissions_list = []
        role_name = None
        if user.role:
            role_name = user.role.name
            permissions_list = list(user.role.permissions.values_list('codename', flat=True))

        token['username'] = user.username
        token['role'] = role_name
        token['permissions'] = permissions_list
        token['email'] = user.email
        token['first_name'] = user.first_name
        token['last_name'] = user.last_name
        
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        
        permissions_list = []
        role_name = None
        if self.user.role:
            role_name = self.user.role.name
            permissions_list = list(self.user.role.permissions.values_list('codename', flat=True))

        # Add basic info to response body as well for easier front access
        data['user'] = {
            'id': self.user.id,
            'username': self.user.username,
            'email': self.user.email,
            'role': role_name,
            'permissions': permissions_list,
            'first_name': self.user.first_name,
            'last_name': self.user.last_name,
            'phone': getattr(self.user, 'telefono', '')
        }
        
        return data

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except Exception:
            return ApiResponse.error(
                message="Credenciales inválidas",
                status_code=status.HTTP_401_UNAUTHORIZED
            )

        return ApiResponse.success(
            data=serializer.validated_data,
            message="Login exitoso"
        )