from django.shortcuts import render
from django.contrib.auth.models import Group, Permission
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from .models import Usuario, Huesped, Habitacion, Planta, AreaComun
from .serializers import UsuarioSerializer, RoleSerializer, PermissionSerializer, HuespedSerializer, HabitacionSerializer, PlantaSerializer, AreaComunSerializer
from .utils import ApiResponse

class PlantaListView(generics.ListCreateAPIView):
    queryset = Planta.objects.all().order_by('numero')
    serializer_class = PlantaSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return ApiResponse.success(data=serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return ApiResponse.success(data=serializer.data, message="Planta creada exitosamente", status_code=status.HTTP_201_CREATED)

class PlantaDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Planta.objects.all()
    serializer_class = PlantaSerializer
    permission_classes = (permissions.IsAuthenticated,)

class HabitacionListCreateView(generics.ListCreateAPIView):
    """Listar y crear habitaciones (VERSIÓN ÚNICA - ELIMINAR DUPLICADO)"""
    serializer_class = HabitacionSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        queryset = Habitacion.objects.all().order_by('id')
        disponibles = self.request.query_params.get('disponibles')
        if disponibles == 'true':
            queryset = queryset.filter(estado='DISPONIBLE')
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return ApiResponse.success(data=serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return ApiResponse.success(
            data=serializer.data,
            message="Habitación registrada exitosamente",
            status_code=status.HTTP_201_CREATED
        )

class HabitacionDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Habitacion.objects.all().order_by('id')
    serializer_class = HabitacionSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return ApiResponse.success(data=serializer.data)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return ApiResponse.success(data=serializer.data, message="Habitación actualizada exitosamente")

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return ApiResponse.success(message="Habitación eliminada exitosamente")

class HuespedListCreateView(generics.ListCreateAPIView):
    """Listar y crear huéspedes (RF-09)"""
    queryset = Huesped.objects.all().order_by('-id')
    serializer_class = HuespedSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.query_params.get('search', '')
        if search:
            queryset = queryset.filter(
                Q(nombre__icontains=search) |
                Q(apellido__icontains=search) |
                Q(email__icontains=search) |
                Q(documento__icontains=search)
            )
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return ApiResponse.success(data=serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return ApiResponse.success(
            data=serializer.data,
            message="Huésped registrado exitosamente",
            status_code=status.HTTP_201_CREATED
        )

class HuespedDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Huesped.objects.all().order_by('id')
    serializer_class = HuespedSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return ApiResponse.success(data=serializer.data)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return ApiResponse.success(data=serializer.data, message="Huésped actualizado exitosamente")

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return ApiResponse.success(message="Huésped eliminado exitosamente")

class RegisterView(generics.CreateAPIView):
    queryset = Usuario.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = UsuarioSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return ApiResponse.success(
            data=serializer.data,
            message="Usuario registrado exitosamente",
            status_code=status.HTTP_201_CREATED
        )

class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UsuarioSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        return self.request.user

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return ApiResponse.success(data=serializer.data)

class RoleListCreateView(generics.ListCreateAPIView):
    queryset = Group.objects.all().order_by('id')
    serializer_class = RoleSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return ApiResponse.success(data=serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return ApiResponse.success(
            data=serializer.data,
            message="Rol creado exitosamente",
            status_code=status.HTTP_201_CREATED
        )

class RoleDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Group.objects.all()
    serializer_class = RoleSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return ApiResponse.success(data=serializer.data)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return ApiResponse.success(data=serializer.data, message="Rol actualizado exitosamente")

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return ApiResponse.success(message="Rol eliminado exitosamente")

class PermissionListView(generics.ListAPIView):
    queryset = Permission.objects.filter(content_type__model='usuario', codename__startswith='can_')
    serializer_class = PermissionSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return ApiResponse.success(data=serializer.data)

class UserListView(generics.ListAPIView):
    queryset = Usuario.objects.all().order_by('id')
    serializer_class = UsuarioSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return ApiResponse.success(data=serializer.data)

class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return ApiResponse.success(data=serializer.data)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return ApiResponse.success(data=serializer.data, message="Usuario actualizado exitosamente")

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return ApiResponse.success(message="Usuario eliminado exitosamente")

class AreaComunListView(generics.ListCreateAPIView):
    queryset = AreaComun.objects.all().order_by('id')
    serializer_class = AreaComunSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return ApiResponse.success(data=serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return ApiResponse.success(
            data=serializer.data,
            message="Área común registrada exitosamente",
            status_code=status.HTTP_201_CREATED
        )

class AreaComunDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = AreaComun.objects.all()
    serializer_class = AreaComunSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return ApiResponse.success(data=serializer.data)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return ApiResponse.success(data=serializer.data, message="Área común actualizada exitosamente")

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return ApiResponse.success(message="Área común eliminada exitosamente")

class RegistroLimpiezaListView(generics.ListCreateAPIView):
    serializer_class = RegistroLimpiezaSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        # Filtra solo los registros activos (no completados) para el dashboard
        return RegistroLimpieza.objects.select_related(
            'habitacion', 'personal_limpieza'
        ).order_by('-fecha_inicio')

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return ApiResponse.success(data=serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return ApiResponse.success(
            data=serializer.data,
            message="Registro de limpieza creado exitosamente",
            status_code=status.HTTP_201_CREATED
        )


class RegistroLimpiezaDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = RegistroLimpieza.objects.all()
    serializer_class = RegistroLimpiezaSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', True)  # siempre partial
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        
        nuevo_estado = request.data.get('estado')
        
        # Si se completa la limpieza, registrar fecha_fin y poner habitación DISPONIBLE
        if nuevo_estado in ['COMPLETADO', 'INSPECCIONADO'] and not instance.fecha_fin:
            serializer.save(fecha_fin=timezone.now())
            instance.habitacion.estado = 'DISPONIBLE'
            instance.habitacion.save()
        else:
            serializer.save()
            
        return ApiResponse.success(
            data=serializer.data,
            message="Registro actualizado exitosamente"
        )


class IncidenciaListView(generics.ListCreateAPIView):
    serializer_class = IncidenciaSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        include_resueltas = self.request.query_params.get('include_resueltas', 'false')
        qs = Incidencia.objects.select_related(
            'habitacion', 'asignado_a', 'reportado_por'
        ).order_by('-prioridad', 'fecha_reporte')
        
        if include_resueltas != 'true':
            qs = qs.exclude(estado='RESUELTO')
        return qs

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return ApiResponse.success(data=serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return ApiResponse.success(
            data=serializer.data,
            message="Incidencia registrada exitosamente",
            status_code=status.HTTP_201_CREATED
        )

    def perform_create(self, serializer):
        serializer.save(reportado_por=self.request.user)


class IncidenciaDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Incidencia.objects.all()
    serializer_class = IncidenciaSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', True)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        estado_proporcionado = 'estado' in serializer.validated_data
        nuevo_estado = serializer.validated_data.get('estado')
        fecha_resolucion = serializer.validated_data.get('fecha_resolucion')

        if estado_proporcionado and nuevo_estado == 'RESUELTO' and instance.habitacion:
            if fecha_resolucion is None and not instance.fecha_resolucion:
                serializer.save(fecha_resolucion=timezone.now())
            else:
                serializer.save()

            habitacion = serializer.instance.habitacion
            if habitacion:
                habitacion.estado = 'DISPONIBLE'
                habitacion.save()
        else:
            serializer.save()
            
        return ApiResponse.success(
            data=serializer.data,
            message="Incidencia actualizada exitosamente"
        )

class PersonalLimpiezaListView(generics.ListAPIView):
    serializer_class = PersonalLimpiezaSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return Usuario.objects.filter(
            is_active=True,
            is_superuser=False,
            role__permissions__codename__in=['can_clean_rooms', 'can_do_maintenance']
        ).distinct().order_by('first_name')

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return ApiResponse.success(data=serializer.data)

class PersonalMantenimientoListView(generics.ListAPIView):
    serializer_class = PersonalLimpiezaSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return Usuario.objects.filter(
            is_active=True,
            is_superuser=False,
            role__permissions__codename='can_do_maintenance'
        ).distinct().order_by('first_name')

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return ApiResponse.success(data=serializer.data)

from rest_framework.views import APIView

class SelectDataView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        huespedes = Huesped.objects.all().order_by('nombre')
        data = {
            "huespedes": [
                {
                    "id": h.id,
                    "nombre_completo": f"{h.nombre} {h.apellido}",
                    "documento": h.documento
                } for h in huespedes
            ]
        }
        return ApiResponse.success(data=data)

class ReservaListView(generics.ListCreateAPIView):
    queryset = Reserva.objects.all().order_by('-id')
    serializer_class = ReservaSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return ApiResponse.success(data=serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return ApiResponse.success(
            data=serializer.data,
            message="Reserva registrada exitosamente",
            status_code=status.HTTP_201_CREATED
        )

class ReservaDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Reserva.objects.all().order_by('-id')
    serializer_class = ReservaSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return ApiResponse.success(data=serializer.data)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', True)  # Use partial update by default for easy PATCH
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return ApiResponse.success(data=serializer.data, message="Reserva actualizada exitosamente")

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return ApiResponse.success(message="Reserva eliminada exitosamente")

class DashboardStatsView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        total_rooms = Habitacion.objects.count()
        occupied_rooms = Habitacion.objects.filter(estado='OCUPADA').count()
        
        ocupacion = int((occupied_rooms / total_rooms) * 100) if total_rooms > 0 else 0
        total_huespedes = Huesped.objects.count()
        reservas_activas = Reserva.objects.filter(estado__in=['CONFIRMADA', 'EN_CURSO']).count()
        
        data = {
            "ocupacion": ocupacion,
            "total_huespedes": total_huespedes,
            "reservas_activas": reservas_activas
        }
        return ApiResponse.success(data=data)

class InventarioListView(generics.ListCreateAPIView):
    queryset = Inventario.objects.all().order_by('id')
    serializer_class = InventarioSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return ApiResponse.success(data=serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return ApiResponse.success(
            data=serializer.data,
            message="Artículo registrado exitosamente en el inventario",
            status_code=status.HTTP_201_CREATED
        )

class InventarioDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Inventario.objects.all().order_by('id')
    serializer_class = InventarioSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return ApiResponse.success(data=serializer.data)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', True)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return ApiResponse.success(data=serializer.data, message="Artículo actualizado exitosamente")

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return ApiResponse.success(message="Artículo eliminado exitosamente")

# ================================================================
# RF-10: RESERVAS
# ================================================================

class ReservaListCreateView(generics.ListCreateAPIView):
    """Listar y crear reservas"""
    queryset = Reserva.objects.select_related(
        'huesped', 'habitacion'
    ).all().order_by('-fecha_reserva')
    serializer_class = ReservaSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        estado = self.request.query_params.get('estado')
        if estado:
            queryset = queryset.filter(estado=estado)
        
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(codigo_reserva__icontains=search) |
                Q(huesped__nombre__icontains=search) |
                Q(huesped__apellido__icontains=search)
            )
        return queryset
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        codigo = f"AST-{uuid.uuid4().hex[:6].upper()}"
        serializer.save(codigo_reserva=codigo)
        return ApiResponse.success(
            data=serializer.data,
            message=f"Reserva {codigo} creada exitosamente",
            status_code=status.HTTP_201_CREATED
        )
class ReservaDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Obtener, actualizar o cancelar una reserva específica"""
    queryset = Reserva.objects.all()
    serializer_class = ReservaSerializer
    permission_classes = [IsAuthenticated]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return ApiResponse.success(data=serializer.data)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return ApiResponse.success(
            data=serializer.data,
            message="Reserva actualizada exitosamente"
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.estado = 'CANCELADA'
        instance.save()
        return ApiResponse.success(message="Reserva cancelada exitosamente")

# ========== ESTADÍSTICAS (KPIs) ==========
class DashboardStatsView(APIView):
    """Estadísticas para el dashboard"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        hoy = timezone.now().date()
        
        total_huespedes = Huesped.objects.count()
        reservas_activas = Reserva.objects.filter(estado='EN_CURSO').count()
        checkins_hoy = Reserva.objects.filter(
            fecha_entrada=hoy,
            estado__in=['CONFIRMADA', 'EN_CURSO']
        ).count()
        
        habitaciones_totales = Habitacion.objects.count()
        habitaciones_ocupadas = Habitacion.objects.filter(estado='OCUPADA').count()
        ocupacion = round((habitaciones_ocupadas / habitaciones_totales * 100), 1) if habitaciones_totales > 0 else 0
        
        return ApiResponse.success(data={
            'total_huespedes': total_huespedes,
            'reservas_activas': reservas_activas,
            'checkins_hoy': checkins_hoy,
            'ocupacion': ocupacion,
            'ingresos_mes': 0,
        })


# ========== DATOS PARA SELECTS (combos) ==========
class SelectDataView(APIView):
    """Datos para selects del frontend"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        huespedes = Huesped.objects.all().order_by('nombre', 'apellido')
        habitaciones = Habitacion.objects.filter(estado='DISPONIBLE')
        
        return ApiResponse.success(data={
            'huespedes': [
                {
                    'id': h.id,
                    'nombre': h.nombre,
                    'apellido': h.apellido,
                    'documento': h.documento,
                    'nombre_completo': f"{h.nombre} {h.apellido}"
                }
                for h in huespedes
            ],
            'habitaciones': [
                {
                    'id': h.id,
                    'numero': h.numero,
                    'precio_base': float(h.precio_base),
                    'tipo': h.get_tipo_display(),
                    'capacidad': h.capacidad
                }
                for h in habitaciones
            ]
        })