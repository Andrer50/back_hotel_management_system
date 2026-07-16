from django.db import models
from django.shortcuts import render
from django.contrib.auth.models import Group, Permission
from django.db.models import F, Q
from django.utils import timezone
from django.db import transaction
from rest_framework import generics, permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from rest_framework_simplejwt.views import TokenObtainPairView

from .models import (
    Usuario,
    Huesped,
    Habitacion,
    Planta,
    AreaComun,
    RegistroLimpieza,
    Incidencia,
    Reserva,
    Inventario,
    ConsumoExtra,
    Estadia,
    Comprobante,
    RegistroAforoAreaComun,
    Temporada
)

from .serializers import (
    UsuarioSerializer,
    RoleSerializer,
    PermissionSerializer,
    HuespedSerializer,
    HabitacionSerializer,
    PlantaSerializer,
    AreaComunSerializer,
    RegistroLimpiezaSerializer,
    IncidenciaSerializer,
    PersonalLimpiezaSerializer,
    ReservaSerializer,
    InventarioSerializer,
    ConsumoExtraSerializer,
    ComprobanteSerializer,
    RegistroAforoSerializer,  
    TemporadaSerializer
)

from .utils import ApiResponse
import json
from .gemini_service import GeminiService
import uuid

# ================================================================
# PLANTAS
# ================================================================

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

# ================================================================
# HABITACIONES
# ================================================================

class HabitacionListCreateView(generics.ListCreateAPIView):
    """Listar y crear habitaciones (VERSIÓN ÚNICA)"""
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

# ================================================================
# HUÉSPEDES
# ================================================================

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

# ================================================================
# USUARIOS, ROLES Y AUTENTICACIÓN
# ================================================================

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

# ================================================================
# ÁREAS COMUNES Y REGISTROS DE AFORO
# ================================================================

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

# ================================================================
# REGISTROS DE LIMPIEZA
# ================================================================

class RegistroLimpiezaListView(generics.ListCreateAPIView):
    serializer_class = RegistroLimpiezaSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
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
        partial = kwargs.pop('partial', True)  # siempre parcial
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        
        nuevo_estado = request.data.get('estado')
        
        if nuevo_estado in ['COMPLETADO', 'INSPECCIONADO'] and not instance.fecha_fin:
            serializer.save(fecha_fin=timezone.now())
            instance.habitacion.estado = 'DISPONIBLE'
            instance.habitacion.save()
        else:
            serializer.save()
            
        return ApiResponse.success(
            data=serializer.data,
            message="Registro de limpieza actualizado exitosamente"
        )

# ================================================================
# INCIDENCIAS Y MANTENIMIENTO
# ================================================================

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

# ================================================================
# RESERVAS (RF-10)
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
        partial = kwargs.pop('partial', True)  # Partial PATCH por defecto
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

# ================================================================
# ESTADÍSTICAS Y KPI DEL DASHBOARD
# ================================================================

class DashboardStatsView(APIView):
    """Estadísticas principales para el dashboard del hotel"""
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

# ================================================================
# ENTRADAS PARA SELECTS Y COMBOBOXES
# ================================================================

class SelectDataView(APIView):
    """Retorna listados optimizados de huéspedes y habitaciones para controles select"""
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

# ================================================================
# LOGÍSTICA E INVENTARIOS
# ================================================================

class InventarioListView(generics.ListCreateAPIView):
    serializer_class = InventarioSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        queryset = Inventario.objects.all().order_by('id')
        tipo = self.request.query_params.get('tipo')
        if tipo:
            queryset = queryset.filter(tipo=tipo.upper())
        
        bajo_stock = self.request.query_params.get('bajo_stock')
        if bajo_stock == 'true':
            queryset = queryset.filter(stock_actual__lte=F('stock_minimo'))
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
# PREVISIÓN E INTELIGENCIA ARTIFICIAL DE INVENTARIO
# ================================================================

from datetime import timedelta
from django.db.models import Sum

class InventarioPredictivoView(APIView):
    """
    Endpoint para el cálculo de inventario predictivo (RF-23).
    Estima la demanda a partir del consumo promedio por reserva en los últimos 30 días
    multiplicado por la cantidad de reservas futuras.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        now = timezone.now()
        hoy = now.date()
        hace_30_dias = now - timedelta(days=30)
        dentro_de_15_dias = hoy + timedelta(days=15)

        # 1. Obtener cantidad de reservas en los últimos 30 días
        reservas_pasadas_count = Reserva.objects.filter(
            fecha_entrada__gte=hace_30_dias.date(),
            fecha_entrada__lte=hoy,
            estado__in=['CONFIRMADA', 'EN_CURSO', 'COMPLETADA']
        ).count()

        # Evitar división por cero
        if reservas_pasadas_count == 0:
            reservas_pasadas_count = 1

        # 2. Obtener cantidad de reservas futuras (próximos 15 días)
        reservas_futuras_count = Reserva.objects.filter(
            fecha_entrada__gt=hoy,
            fecha_entrada__lte=dentro_de_15_dias,
            estado__in=['PENDIENTE', 'CONFIRMADA', 'EN_CURSO']
        ).count()

        # 3. Calcular consumo por ítem en los últimos 30 días
        consumos_pasados = ConsumoExtra.objects.filter(
            fecha_consumo__gte=hace_30_dias,
            inventario__isnull=False
        ).values('inventario_id').annotate(total_cantidad=Sum('cantidad'))

        consumo_map = {c['inventario_id']: c['total_cantidad'] for c in consumos_pasados}

        # 4. Obtener inventario actual
        inventarios = Inventario.objects.all()
        resultado = []

        for item in inventarios:
            cant_consumida = consumo_map.get(item.id, 0)
            
            # Consumo diario promedio para calcular la fecha de desabastecimiento
            consumo_diario_simple = cant_consumida / 30.0

            # Consumo promedio por reserva
            consumo_por_reserva = cant_consumida / float(reservas_pasadas_count)

            # Consumo proyectado
            consumo_proyectado = round(consumo_por_reserva * reservas_futuras_count, 2)

            # Stock proyectado = stock_actual - consumo proyectado
            stock_proyectado = item.stock_actual - consumo_proyectado

            # Stock ideal = stock_minimo * 3
            stock_ideal = item.stock_minimo * 3

            # Sugerencia de pedido = stock_ideal - stock_proyectado (si da > 0)
            sugerencia_pedido = max(0, int(stock_ideal - stock_proyectado))

            # Fecha estimada de desabastecimiento
            if consumo_diario_simple > 0:
                dias_para_desabastecer = item.stock_actual / consumo_diario_simple
                if dias_para_desabastecer > 365:
                    fecha_desabastecimiento = "Más de un año"
                else:
                    fecha_estimada = hoy + timedelta(days=int(dias_para_desabastecer))
                    fecha_desabastecimiento = fecha_estimada.strftime('%Y-%m-%d')
            else:
                fecha_desabastecimiento = "Sin riesgo (Sin consumo reciente)"

            resultado.append({
                "id": item.id,
                "nombre": item.nombre,
                "descripcion": item.descripcion or "",
                "stock_actual": item.stock_actual,
                "stock_minimo": item.stock_minimo,
                "stock_ideal": stock_ideal,
                "projected_consumption": consumo_proyectado,
                "projected_stock": round(stock_proyectado, 2),
                "suggested_order": sugerencia_pedido,
                "estimated_stockout_date": fecha_desabastecimiento,
                "sede": item.sede.nombre if item.sede else "Sin Sede"
            })

        return ApiResponse.success(data=resultado, message="Predicción de inventario generada exitosamente")

class InventarioIAPredictionView(APIView):
    """
    Endpoint que analiza el inventario usando Gemini y predice necesidades.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not GeminiService.is_configured():
            return ApiResponse.error(
                message="El servicio de Inteligencia Artificial no está configurado o requiere que se asigne la clave GEMINI_API_KEY en el archivo .env.",
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        
        # Obtener los suministros e insumos del inventario
        inventarios = Inventario.objects.all()
        data_items = []
        for item in inventarios:
            data_items.append({
                "id": item.id,
                "nombre": item.nombre,
                "descripcion": item.descripcion or "",
                "stock_actual": item.stock_actual,
                "stock_minimo": item.stock_minimo,
                "precio_unitario": float(item.precio_unitario),
                "tipo": item.tipo
            })
            
        try:
            # Llamar al servicio
            analisis_str = GeminiService.predict_inventory_needs(data_items)
            analisis_json = json.loads(analisis_str)
            return ApiResponse.success(data=analisis_json, message="Análisis de inventario con IA generado exitosamente")
        except Exception as e:
            return ApiResponse.error(
                message=f"Error al generar predicciones de inventario: {str(e)}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

# ================================================================
# PROMOCIONES DE VENTAS CON IA
# ================================================================

class PromocionesIAView(APIView):
    """
    Endpoint que analiza reservas y consumos extras usando Gemini para sugerir promociones.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not GeminiService.is_configured():
            return ApiResponse.error(
                message="El servicio de Inteligencia Artificial no está configurado o requiere que se asigne la clave GEMINI_API_KEY en el archivo .env.",
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE
            )

        # Obtener reservas recientes (ej. últimas 50)
        reservas = Reserva.objects.select_related('huesped', 'habitacion').order_by('-fecha_reserva')[:50]
        # Obtener consumos extras recientes (ej. últimos 50)
        consumos = ConsumoExtra.objects.select_related('inventario').order_by('-fecha_consumo')[:50]

        # Formatear reservas
        reservas_data = []
        for r in reservas:
            reservas_data.append({
                "codigo": r.codigo_reserva,
                "habitacion": r.habitacion.numero if r.habitacion else "N/A",
                "tipo_habitacion": r.habitacion.tipo if r.habitacion else "N/A",
                "fecha_entrada": str(r.fecha_entrada),
                "fecha_salida": str(r.fecha_salida),
                "tarifa_aplicada": float(r.tarifa_aplicada),
                "origen": r.origen,
                "estado": r.estado
            })

        # Formatear consumos
        consumos_data = []
        for c in consumos:
            consumos_data.append({
                "descripcion": c.descripcion,
                "amount": c.cantidad,
                "precio_unitario": float(c.precio_unitario),
                "total": float(c.total),
                "articulo_inventario": c.inventario.nombre if c.inventario else "N/A",
                "fecha": str(c.fecha_consumo.date()) if c.fecha_consumo else ""
            })

        try:
            # Llamar al servicio
            analisis_str = GeminiService.analyze_sales_and_promotions(reservas_data, consumos_data)
            analisis_json = json.loads(analisis_str)
            return ApiResponse.success(data=analisis_json, message="Análisis de ventas y promociones con IA generado exitosamente")
        except Exception as e:
            return ApiResponse.error(
                message=f"Error al generar análisis de promociones: {str(e)}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

# ================================================================
# CONSUMOS EXTRA EN HABITACIÓN
# ================================================================

class ConsumoExtraListCreateView(generics.ListCreateAPIView):
    queryset = ConsumoExtra.objects.all().order_by('-fecha_consumo')
    serializer_class = ConsumoExtraSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        reserva_id = self.request.query_params.get('reserva_id')
        if reserva_id:
            queryset = queryset.filter(estadia__reserva_id=reserva_id)
        return queryset

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        reserva_id = request.data.get('reserva')
        if not reserva_id:
            return ApiResponse.error(
                message="Debe especificar el ID de la reserva ('reserva').",
                status_code=status.HTTP_400_BAD_REQUEST
            )
            
        try:
            reserva = Reserva.objects.get(id=reserva_id)
        except Reserva.DoesNotExist:
            return ApiResponse.error(
                message=f"La reserva con ID {reserva_id} no existe.",
                status_code=status.HTTP_404_NOT_FOUND
            )

        # Buscar o crear la estadía asociada a la reserva
        try:
            estadia = Estadia.objects.get(reserva=reserva)
        except Estadia.DoesNotExist:
            estadia = Estadia.objects.create(
                reserva=reserva,
                fecha_checkin=timezone.now(),
                registrado_por=request.user
            )

        # Clonamos data para asociar el id de estadía antes del guardado
        data = request.data.copy()
        data['estadia'] = estadia.id

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        
        # Validar y descontar stock del inventario
        inventario_item = serializer.validated_data.get('inventario')
        cantidad = serializer.validated_data.get('cantidad', 1)
        
        if inventario_item:
            if inventario_item.stock_actual < cantidad:
                return ApiResponse.error(
                    message=f"Stock insuficiente para '{inventario_item.nombre}'. Stock disponible: {inventario_item.stock_actual}",
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            
            # Descontar del inventario
            inventario_item.stock_actual -= cantidad
            inventario_item.save()
            
            # Asignar precio unitario por defecto del inventario si no se envió
            if not serializer.validated_data.get('precio_unitario'):
                serializer.validated_data['precio_unitario'] = inventario_item.precio_unitario

        self.perform_create(serializer)
        
        return ApiResponse.success(
            data=serializer.data,
            message="Consumo extra registrado exitosamente",
            status_code=status.HTTP_201_CREATED
        )

# ================================================================
# OPERACIONES DE CHECK-IN Y CHECK-OUT
# ================================================================

class CheckInView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request, pk):
        try:
            reserva = Reserva.objects.select_related('habitacion').get(pk=pk)
        except Reserva.DoesNotExist:
            return ApiResponse.error(
                message="Reserva no encontrada.",
                status_code=status.HTTP_404_NOT_FOUND
            )

        if reserva.estado not in ['PENDIENTE', 'CONFIRMADA']:
            return ApiResponse.error(
                message=f"No se puede hacer check-in. Estado actual: {reserva.get_estado_display()}",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        if Estadia.objects.filter(reserva=reserva).exists():
            return ApiResponse.error(
                message="Ya existe una estadía registrada para esta reserva.",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        # Crear la estadía
        estadia = Estadia.objects.create(
            reserva=reserva,
            fecha_checkin=timezone.now(),
            registrado_por=request.user,
            observaciones=request.data.get('observaciones', '')
        )

        # Actualizar estado de reserva y habitación
        reserva.estado = 'EN_CURSO'
        reserva.save()

        habitacion = reserva.habitacion
        habitacion.estado = 'OCUPADA'
        habitacion.save()

        return ApiResponse.success(
            data={
                "estadia_id": estadia.id,
                "fecha_checkin": estadia.fecha_checkin,
                "habitacion": habitacion.numero,
                "huesped": f"{reserva.huesped.nombre} {reserva.huesped.apellido}",
            },
            message=f"Check-in realizado exitosamente. Habitación {habitacion.numero} ahora OCUPADA.",
            status_code=status.HTTP_201_CREATED
        )

class CheckOutView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request, pk):
        try:
            reserva = Reserva.objects.select_related('habitacion').get(pk=pk)
        except Reserva.DoesNotExist:
            return ApiResponse.error(
                message="Reserva no encontrada.",
                status_code=status.HTTP_404_NOT_FOUND
            )

        if reserva.estado != 'EN_CURSO':
            return ApiResponse.error(
                message=f"No se puede hacer check-out. Estado actual: {reserva.get_estado_display()}",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        try:
            estadia = Estadia.objects.get(reserva=reserva)
        except Estadia.DoesNotExist:
            return ApiResponse.error(
                message="No existe una estadía activa para esta reserva.",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        if estadia.fecha_checkout:
            return ApiResponse.error(
                message="El check-out ya fue registrado anteriormente.",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        # Cerrar la estadía
        estadia.fecha_checkout = timezone.now()
        estadia.checkout_registrado_por = request.user
        estadia.observaciones = request.data.get('observaciones', estadia.observaciones)
        estadia.save()

        # Actualizar estado de reserva y habitación
        reserva.estado = 'COMPLETADA'
        reserva.save()

        habitacion = reserva.habitacion
        habitacion.estado = 'SUCIA'
        habitacion.save()

        return ApiResponse.success(
            data={
                "estadia_id": estadia.id,
                "fecha_checkin": estadia.fecha_checkin,
                "fecha_checkout": estadia.fecha_checkout,
                "habitacion": habitacion.numero,
                "huesped": f"{reserva.huesped.nombre} {reserva.huesped.apellido}",
            },
            message=f"Check-out realizado. Habitación {habitacion.numero} marcada para limpieza.",
        )

# ================================================================
# COMPROBANTES FISCALES Y EMISIÓN DE COMPROBANTES
# ================================================================

class ComprobanteListCreateView(generics.ListCreateAPIView):
    queryset = Comprobante.objects.all().order_by('-fecha_emision')
    serializer_class = ComprobanteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        reserva_id = self.request.query_params.get('reserva_id')
        if reserva_id:
            queryset = queryset.filter(reserva_id=reserva_id)
        return queryset

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        reserva_id = request.data.get('reserva')
        if not reserva_id:
            return ApiResponse.error(
                message="Debe especificar el ID de la reserva ('reserva').",
                status_code=status.HTTP_400_BAD_REQUEST
            )
            
        try:
            reserva = Reserva.objects.get(id=reserva_id)
        except Reserva.DoesNotExist:
            return ApiResponse.error(
                message=f"La reserva con ID {reserva_id} no existe.",
                status_code=status.HTTP_404_NOT_FOUND
            )

        # Evitar duplicados de comprobantes para una misma reserva
        existente = Comprobante.objects.filter(reserva=reserva).first()
        if existente:
            serializer = self.get_serializer(existente)
            return ApiResponse.success(
                data=serializer.data,
                message=f"Ya existe un comprobante emitido para esta reserva: {existente.numero_completo}"
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        comprobante = serializer.save()
        
        # Transición de estado de reserva y habitación si está EN_CURSO
        if reserva.estado == 'EN_CURSO':
            reserva.estado = 'COMPLETADA'
            reserva.save()
            
            # Asegurar estadía cerrada
            estadia, created = Estadia.objects.get_or_create(
                reserva=reserva,
                defaults={
                    'fecha_checkin': timezone.now(),
                    'registrado_por': request.user
                }
            )
            estadia.fecha_checkout = timezone.now()
            estadia.checkout_registrado_por = request.user
            estadia.save()
            
            # Habitación en mantenimiento de limpieza
            habitacion = reserva.habitacion
            if habitacion:
                habitacion.estado = 'SUCIA'
                habitacion.save()

        return ApiResponse.success(
            data=serializer.data,
            message=f"Comprobante {comprobante.numero_completo} emitido exitosamente",
            status_code=status.HTTP_201_CREATED
        )

class ComprobanteDetailView(generics.RetrieveAPIView):
    queryset = Comprobante.objects.all()
    serializer_class = ComprobanteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return ApiResponse.success(data=serializer.data)

class ComprobantePDFView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk, *args, **kwargs):
        import io
        from django.http import HttpResponse
        from reportlab.lib.pagesizes import letter
        from reportlab.lib import colors
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

        try:
            comprobante = Comprobante.objects.get(pk=pk)
        except Comprobante.DoesNotExist:
            return Response({"error": "Comprobante no encontrado"}, status=status.HTTP_404_NOT_FOUND)

        reserva = comprobante.reserva
        huesped = reserva.huesped
        habitacion = reserva.habitacion

        noches = max(1, (reserva.fecha_salida - reserva.fecha_entrada).days)
        room_total = float(reserva.tarifa_aplicada) * noches
        
        try:
            estadia = reserva.estadia
            consumos = estadia.consumos_extra.all()
        except Exception:
            consumos = []
            
        consumos_total = sum(float(c.cantidad * c.precio_unitario) for c in consumos)
        total_amount = float(comprobante.monto_total)
        
        concept = "TODO"
        if abs(total_amount - room_total) < 0.05 and abs(total_amount - (room_total + consumos_total)) > 0.05:
            concept = "HABITACION"
        elif abs(total_amount - consumos_total) < 0.05 and abs(total_amount - (room_total + consumos_total)) > 0.05:
            concept = "CONSUMOS"

        # Configuración del documento PDF
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36
        )

        styles = getSampleStyleSheet()
        
        subtitle_style = ParagraphStyle(
            'InvoiceSubtitle',
            parent=styles['Normal'],
            fontSize=9,
            leading=12,
            textColor=colors.HexColor('#555555'),
            fontName='Helvetica'
        )
        
        receipt_box_style = ParagraphStyle(
            'ReceiptBoxText',
            parent=styles['Normal'],
            fontSize=11,
            leading=15,
            textColor=colors.white,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )

        body_style = ParagraphStyle(
            'Body',
            parent=styles['Normal'],
            fontSize=9,
            leading=12,
            textColor=colors.HexColor('#333333'),
            fontName='Helvetica'
        )

        bold_style = ParagraphStyle(
            'Bold',
            parent=body_style,
            fontName='Helvetica-Bold'
        )

        th_style = ParagraphStyle(
            'TableHeader',
            parent=styles['Normal'],
            fontSize=9,
            leading=11,
            textColor=colors.white,
            fontName='Helvetica-Bold'
        )

        story = []

        # ----------------- SECCIÓN CABECERA -----------------
        hotel_info = (
            "<font size=14 color='#031c46'><b>HOTEL ASTURIAS S.A.C</b></font><br/>"
            "R.U.C. 20492837482<br/>"
            "Av. Larco 1024, Miraflores - Lima<br/>"
            "Teléfono: (01) 444-5566 | contacto@hotelasturias.com"
        )
        
        type_str = "BOLETA DE VENTA ELECTRÓNICA" if comprobante.tipo_comprobante == "BOLETA" else "FACTURA ELECTRÓNICA"
        receipt_badge_text = (
            f"<font size=11>{type_str}</font><br/>"
            f"<font size=15><b>N° {comprobante.numero_completo}</b></font>"
        )

        header_data = [
            [Paragraph(hotel_info, subtitle_style), Paragraph(receipt_badge_text, receipt_box_style)]
        ]
        
        header_table = Table(header_data, colWidths=[340, 200])
        header_table.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('BACKGROUND', (1,0), (1,0), colors.HexColor('#031c46')),
            ('ALIGN', (1,0), (1,0), 'CENTER'),
            ('BOTTOMPADDING', (1,0), (1,0), 12),
            ('TOPPADDING', (1,0), (1,0), 12),
            ('BOX', (1,0), (1,0), 1.5, colors.HexColor('#031c46')),
        ]))
        story.append(header_table)
        story.append(Spacer(1, 20))

        # ----------------- DATOS DEL ADQUIRIENTE -----------------
        info_data = [
            [
                Paragraph("<b>ADQUIRIENTE:</b>", body_style),
                Paragraph(comprobante.nombre_cliente, body_style),
                Paragraph("<b>FECHA EMISIÓN:</b>", body_style),
                Paragraph(comprobante.fecha_emision.strftime("%d/%m/%Y %H:%M:%S"), body_style),
            ],
            [
                Paragraph("<b>DNI / RUC:</b>", body_style),
                Paragraph(comprobante.documento_cliente, body_style),
                Paragraph("<b>MÉTODO PAGO:</b>", body_style),
                Paragraph(comprobante.get_metodo_pago_display(), body_style),
            ],
            [
                Paragraph("<b>RESERVA:</b>", body_style),
                Paragraph(reserva.codigo_reserva, body_style),
                Paragraph("<b>HABITACIÓN:</b>", body_style),
                Paragraph(f"Hab. {habitacion.numero if habitacion else 'N/A'}", body_style),
            ],
        ]
        
        info_table = Table(info_data, colWidths=[90, 180, 90, 180])
        info_table.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
            ('TOPPADDING', (0,0), (-1,-1), 6),
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8f9fa')),
            ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#e9ecef')),
            ('INNERGRID', (0,0), (-1,-1), 0.25, colors.HexColor('#e9ecef')),
            ('PADDING', (0,0), (-1,-1), 8),
        ]))
        story.append(info_table)
        story.append(Spacer(1, 20))

        # ----------------- TABLA DE ÍTEMS DETALLADOS -----------------
        table_data = [
            [
                Paragraph("<b>DESCRIPCIÓN</b>", th_style),
                Paragraph("<b>CANT.</b>", th_style),
                Paragraph("<b>P. UNITARIO</b>", th_style),
                Paragraph("<b>TOTAL</b>", th_style)
            ]
        ]
        
        # 1. Habitación stay item
        if concept in ["HABITACION", "TODO"]:
            table_data.append([
                Paragraph(f"Hospedaje Habitación {habitacion.numero if habitacion else 'N/A'} (x{noches} noches)", body_style),
                Paragraph(str(noches), body_style),
                Paragraph(f"S/. {float(reserva.tarifa_aplicada):.2f}", body_style),
                Paragraph(f"S/. {room_total:.2f}", body_style)
            ])
            
        # 2. Consumos extras consumidos
        if concept in ["CONSUMOS", "TODO"]:
            for item in consumos:
                item_total = float(item.cantidad * item.precio_unitario)
                table_data.append([
                    Paragraph(item.descripcion, body_style),
                    Paragraph(str(item.cantidad), body_style),
                    Paragraph(f"S/. {float(item.precio_unitario):.2f}", body_style),
                    Paragraph(f"S/. {item_total:.2f}", body_style)
                ])

        items_table = Table(table_data, colWidths=[280, 50, 100, 110])
        items_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#031c46')),
            ('ALIGN', (1,0), (-1,-1), 'RIGHT'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 8),
            ('TOPPADDING', (0,0), (-1,-1), 8),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f8f9fa')]),
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#dee2e6')),
            ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#dee2e6')),
        ]))
        story.append(items_table)
        story.append(Spacer(1, 15))

        # ----------------- DESGLOSE TOTALES -----------------
        total_val = float(comprobante.monto_total)
        subtotal_val = total_val / 1.18
        igv_val = total_val - subtotal_val
        
        totals_data = [
            [Paragraph("<b>SUBTOTAL (SIN IGV)</b>", body_style), Paragraph(f"S/. {subtotal_val:.2f}", bold_style)],
            [Paragraph("<b>I.G.V. (18%)</b>", body_style), Paragraph(f"S/. {igv_val:.2f}", bold_style)],
            [Paragraph("<b>TOTAL GENERAL</b>", body_style), Paragraph(f"S/. {total_val:.2f}", bold_style)],
        ]
        
        totals_table = Table(totals_data, colWidths=[130, 100])
        totals_table.setStyle(TableStyle([
            ('ALIGN', (0,0), (-1,-1), 'RIGHT'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 5),
            ('TOPPADDING', (0,0), (-1,-1), 5),
            ('LINEBELOW', (0,0), (-1,-1), 0.5, colors.HexColor('#e9ecef')),
            ('BACKGROUND', (0,2), (1,2), colors.HexColor('#ebf3fc')),
        ]))
        
        outer_totals_data = [
            ["", totals_table]
        ]
        outer_totals_table = Table(outer_totals_data, colWidths=[310, 230])
        outer_totals_table.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('ALIGN', (1,0), (1,0), 'RIGHT'),
        ]))
        story.append(outer_totals_table)
        story.append(Spacer(1, 30))

        # ----------------- FOOTER LEYENDA SUNAT -----------------
        footer_text = (
            "Representación impresa de comprobante electrónico.<br/>"
            "Autorizado mediante la resolución de SUNAT.<br/>"
            "<b>¡GRACIAS POR SU PREFERENCIA Y ESPERAMOS VERLE PRONTO EN HOTEL ASTURIAS!</b>"
        )
        footer_para = Paragraph(footer_text, ParagraphStyle(
            'FooterText',
            parent=styles['Normal'],
            fontSize=8,
            leading=11,
            textColor=colors.HexColor('#777777'),
            alignment=TA_CENTER
        ))
        story.append(footer_para)

        doc.build(story)
        buffer.seek(0)
        
        filename = f"{comprobante.numero_completo}.pdf"
        response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response

# ================================================================
# REGISTRO DE RESERVAS EN ÁREAS COMUNES
# ================================================================

class RegistroAforoListView(generics.ListCreateAPIView):
    serializer_class = RegistroAforoSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        qs = RegistroAforoAreaComun.objects.select_related(
            'huesped', 'area_comun', 'registrado_por'
        ).order_by('-fecha_ingreso_programada')
        area_id = self.request.query_params.get('area_comun')
        if area_id:
            qs = qs.filter(area_comun_id=area_id)
        return qs

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return ApiResponse.success(data=serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(registrado_por=request.user)
        return ApiResponse.success(
            data=serializer.data,
            message="Reserva de aforo creada exitosamente",
            status_code=status.HTTP_201_CREATED
        )

class RegistroAforoDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = RegistroAforoAreaComun.objects.all()
    serializer_class = RegistroAforoSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', True)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return ApiResponse.success(
            data=serializer.data,
            message="Reserva actualizada exitosamente"
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return ApiResponse.success(message="Reserva eliminada exitosamente")

class AforoCheckInView(generics.GenericAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, pk):
        try:
            registro = RegistroAforoAreaComun.objects.select_related('area_comun').get(pk=pk)
        except RegistroAforoAreaComun.DoesNotExist:
            return ApiResponse.error(message="Registro no encontrado", status_code=404)

        if registro.estado not in ['PENDIENTE', 'CONFIRMADA']:
            return ApiResponse.error(message="Solo se puede hacer check-in desde estado Pendiente o Confirmada")

        area = registro.area_comun
        if area.aforo_actual >= area.capacidad_maxima:
            return ApiResponse.error(
                message=f"Aforo máximo alcanzado ({area.capacidad_maxima} personas)"
            )

        registro.estado = 'EN_CURSO'
        registro.fecha_ingreso_real = timezone.now()
        registro.save()

        area.aforo_actual += 1
        area.save()

        return ApiResponse.success(
            data=RegistroAforoSerializer(registro).data,
            message="Check-in realizado exitosamente"
        )

class AforoCheckOutView(generics.GenericAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, pk):
        try:
            registro = RegistroAforoAreaComun.objects.select_related('area_comun').get(pk=pk)
        except RegistroAforoAreaComun.DoesNotExist:
            return ApiResponse.error(message="Registro no encontrado", status_code=404)

        if registro.estado != 'EN_CURSO':
            return ApiResponse.error(message="Solo se puede hacer check-out desde estado En Curso")

        registro.estado = 'COMPLETADA'
        registro.fecha_salida_real = timezone.now()
        registro.save()

        area = registro.area_comun
        if area.aforo_actual > 0:
            area.aforo_actual -= 1
            area.save()

        return ApiResponse.success(
            data=RegistroAforoSerializer(registro).data,
            message="Check-out realizado exitosamente"
        )

# ================================================================
# TEMPORADAS (CALENDARIOS Y TARIFAS DINÁMICAS)
# ================================================================

class TemporadaListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        queryset = Temporada.objects.all().order_by('fecha_inicio')
        serializer = TemporadaSerializer(queryset, many=True)
        return Response({
            "status": "success",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = TemporadaSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "status": "success",
                "message": "Temporada dinámica registrada correctamente en el calendario.",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)
            
        return Response({
            "status": "error",
            "message": "Error en la validación de los rangos de fechas.",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

class TemporadaDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        try:
            temporada = Temporada.objects.get(pk=pk)
            serializer = TemporadaSerializer(temporada, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    "status": "success",
                    "message": "Temporada actualizada correctamente en el sistema."
                }, status=status.HTTP_200_OK)
            
            return Response({
                "status": "error",
                "message": "Datos inválidos",
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        except Temporada.DoesNotExist:
            return Response({
                "status": "error",
                "message": "La temporada seleccionada no existe."
            }, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, pk):
        try:
            temporada = Temporada.objects.get(pk=pk)
            temporada.delete()
            return Response({
                "status": "success",
                "message": "Temporada removida del sistema con éxito."
            }, status=status.HTTP_200_OK)
        except Temporada.DoesNotExist:
            return Response({
                "status": "error",
                "message": "La temporada seleccionada no existe o ya fue eliminada."
            }, status=status.HTTP_404_NOT_FOUND)

# ==============================================================================
# 🚀 RECOMENDACIÓN PERSONALIZADA PARA EL HUÉSPED (API GEMINI)
# ==============================================================================

class RecomendacionIAView(APIView):
    """
    Endpoint para obtener recomendaciones personalizadas de servicios del hotel
    basadas en el perfil de un huésped utilizando la API de Gemini.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            perfil_data = request.data
            
            # Validación de entrada
            if not perfil_data:
                return Response({
                    "status": "error",
                    "message": "Falta la información del perfil del huésped."
                }, status=status.HTTP_400_BAD_REQUEST)

            # Consumimos el método estructurado de tu GeminiService
            response_json_str = GeminiService.recommend_services_for_guest(perfil_data)
            
            # Desempaquetamos el string JSON devuelto por Gemini a un diccionario de Python
            resultado = json.loads(response_json_str)
            
            return Response({
                "status": "success",
                "message": "Recomendaciones generadas con éxito por la IA.",
                "data": resultado
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                "status": "error",
                "message": f"Error al procesar con Gemini: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# ==============================================================================
# VISTAS TEMPORALES PARA EVITAR ERRORES DE IMPORTACIÓN (A REEMPLAZAR POR TUS COMPAÑEROS)
# ==============================================================================

class ChatbotStaffView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        return Response({"message": "Chatbot Staff Temporal"}, status=status.HTTP_200_OK)

class DynamicPricingIAView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        return Response({"message": "Dynamic Pricing Temporal"}, status=status.HTTP_200_OK)

class UpdateBasePricesView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        return Response({"message": "Update Base Prices Temporal"}, status=status.HTTP_200_OK)