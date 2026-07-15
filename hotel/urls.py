from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    RegisterView,
    UserProfileView,
    RoleListCreateView,
    RoleDetailView,
    PermissionListView,
    UserListView,
    UserDetailView,
    HuespedListCreateView,
    HuespedDetailView,
    HabitacionListCreateView,
    HabitacionDetailView,
    PlantaListView,
    PlantaDetailView,
    AreaComunListView,
    AreaComunDetailView,
    RegistroLimpiezaListView,
    RegistroLimpiezaDetailView,
    IncidenciaListView,
    IncidenciaDetailView,
    PersonalLimpiezaListView,
    PersonalMantenimientoListView,
    SelectDataView,
    ReservaListView,
    ReservaListCreateView,     
    ReservaDetailView,
    DashboardStatsView,
    InventarioListView,
    InventarioDetailView,
    InventarioIAPredictionView,
    PromocionesIAView,
    ConsumoExtraListCreateView,
    ComprobanteListCreateView,
    ComprobanteDetailView,
    ComprobantePDFView,
    # 🔥 PARCHE DE IMPORTACIONES: Aquí conectamos las vistas que Django reclamaba
    CheckInView,
    CheckOutView,
    RegistroAforoListView,
    RegistroAforoDetailView,
    # 📈 TU MÓDULO: Conexión con tus vistas de temporadas corregidas
    TemporadaListView,
    TemporadaDetailView
)
from .auth_views import MyTokenObtainPairView

urlpatterns = [
    # ========== AUTENTICACIÓN ==========
    path('register', RegisterView.as_view(), name='register'),
    path('login', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh', TokenRefreshView.as_view(), name='token_refresh'),
    path('profile', UserProfileView.as_view(), name='profile'),
    
    # ========== USUARIOS ==========
    path('users', UserListView.as_view(), name='user-list'),
    path('users/<int:pk>', UserDetailView.as_view(), name='user-detail'),
    
    # ========== ROLES Y PERMISOS ==========
    path('roles', RoleListCreateView.as_view(), name='role-list-create'),
    path('roles/<int:pk>', RoleDetailView.as_view(), name='role-detail'),
    path('permissions', PermissionListView.as_view(), name='permission-list'),
    
    # ========== FINANZAS Y COMPROBANTES ==========
    path('consumos-extra', ConsumoExtraListCreateView.as_view(), name='consumo-extra-list-create'),
    path('comprobantes', ComprobanteListCreateView.as_view(), name='comprobante-list-create'),
    path('comprobantes/<int:pk>', ComprobanteDetailView.as_view(), name='comprobante-detail'),
    path('comprobantes/<int:pk>/pdf', ComprobantePDFView.as_view(), name='comprobante-pdf'),
    
    # ========== HUÉSPEDES ==========
    path('huespedes', HuespedListCreateView.as_view(), name='huesped-list'),
    path('huespedes/<int:pk>', HuespedDetailView.as_view(), name='huesped-detail'),
    
    # ========== HABITACIONES ==========
    path('habitaciones', HabitacionListCreateView.as_view(), name='habitacion-list'),
    path('habitaciones/<int:pk>', HabitacionDetailView.as_view(), name='habitacion-detail'),
    
    # ========== PLANTAS ==========
    path('plantas', PlantaListView.as_view(), name='planta-list'),
    path('plantas/<int:pk>', PlantaDetailView.as_view(), name='planta-detail'),
    
    # ========== ÁREAS COMUNES Y AFOROS ==========
    path('areas-comunes', AreaComunListView.as_view(), name='area-comun-list'),
    path('areas-comunes/<int:pk>', AreaComunDetailView.as_view(), name='area-comun-detail'),
    path('aforos', RegistroAforoListView.as_view(), name='aforo-list-create'),
    path('aforos/<int:pk>', RegistroAforoDetailView.as_view(), name='aforo-detail'),
    
    # ========== LOGÍSTICA, LIMPIEZA E INCIDENCIAS ==========
    path('limpiezas', RegistroLimpiezaListView.as_view(), name='limpieza-list'),
    path('limpiezas/<int:pk>', RegistroLimpiezaDetailView.as_view(), name='limpieza-detail'),
    path('incidencias', IncidenciaListView.as_view(), name='incidencia-list'),
    path('incidencias/<int:pk>', IncidenciaDetailView.as_view(), name='incidencia-detail'),
    path('incidencia', IncidenciaListView.as_view(), name='incidencia-list-singular'),
    path('incidencia/<int:pk>', IncidenciaDetailView.as_view(), name='incidencia-detail-singular'),
    path('personal-limpieza', PersonalLimpiezaListView.as_view(), name='personal-limpieza'),
    path('personal-mantenimiento', PersonalMantenimientoListView.as_view(), name='personal-mantenimiento'),
    path('inventarios', InventarioListView.as_view(), name='inventario-list'),
    path('inventarios/<int:pk>', InventarioDetailView.as_view(), name='inventario-detail'),
    
    # ========== RESERVAS ==========
    path('reservas/list', ReservaListView.as_view(), name='reserva-list-only'),
    path('reservas', ReservaListCreateView.as_view(), name='reserva-list-create'),
    path('reservas/<int:pk>', ReservaDetailView.as_view(), name='reserva-detail'),
    path('reservas/<int:pk>/checkin', CheckInView.as_view(), name='reserva-checkin'),
    path('reservas/<int:pk>/checkout', CheckOutView.as_view(), name='reserva-checkout'),
    
    # ========== MANTENIMIENTO DE TEMPORADAS (TU CRUD) ==========
    path('temporadas', TemporadaListView.as_view(), name='temporada-list-create'),
    path('temporadas/<int:pk>', TemporadaDetailView.as_view(), name='temporada-detail'),
    
    # ========== PANEL Y SELECTS (LIMPIADOS DE DUPLICADOS) ==========
    path('dashboard/stats', DashboardStatsView.as_view(), name='dashboard-stats'),
    path('select-data', SelectDataView.as_view(), name='select-data'),
    
    # ========== INTEGRACIÓN GEMINI AI ==========
    path('inventarios/analisis-ia', InventarioIAPredictionView.as_view(), name='inventario-analisis-ia'),
    path('promociones/analisis-ia', PromocionesIAView.as_view(), name='promociones-analisis-ia'),
]
# Rutas del módulo de reseñas (HU-18)
urlpatterns += [
    path('', include('hotel.resenas.urls')),
]