from django.urls import path
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
    ReservaListCreateView,      # ← AGREGAR ESTA
    ReservaDetailView,
    DashboardStatsView,
    InventarioListView,
    InventarioDetailView,
    InventarioIAPredictionView,
    PromocionesIAView,
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
    
    # ========== RF-09: HUÉSPEDES ==========
    path('huespedes', HuespedListCreateView.as_view(), name='huesped-list'),
    path('huespedes/<int:pk>', HuespedDetailView.as_view(), name='huesped-detail'),
    
    # ========== RF-10: HABITACIONES ==========
    path('habitaciones', HabitacionListCreateView.as_view(), name='habitacion-list'),
    path('habitaciones/<int:pk>', HabitacionDetailView.as_view(), name='habitacion-detail'),
    
    # ========== PLANTAS ==========
    path('plantas', PlantaListView.as_view(), name='planta-list'),
    path('plantas/<int:pk>', PlantaDetailView.as_view(), name='planta-detail'),
    
    # ========== ÁREAS COMUNES ==========
    path('areas-comunes', AreaComunListView.as_view(), name='area-comun-list'),
    path('areas-comunes/<int:pk>', AreaComunDetailView.as_view(), name='area-comun-detail'),
    path('limpiezas', RegistroLimpiezaListView.as_view(), name='limpieza-list'),
    path('limpiezas/<int:pk>', RegistroLimpiezaDetailView.as_view(), name='limpieza-detail'),
    path('incidencias', IncidenciaListView.as_view(), name='incidencia-list'),
    path('incidencias/<int:pk>', IncidenciaDetailView.as_view(), name='incidencia-detail'),
    path('incidencia', IncidenciaListView.as_view(), name='incidencia-list-singular'),
    path('incidencia/<int:pk>', IncidenciaDetailView.as_view(), name='incidencia-detail-singular'),
    path('personal-limpieza', PersonalLimpiezaListView.as_view(), name='personal-limpieza'),
    path('personal-mantenimiento', PersonalMantenimientoListView.as_view(), name='personal-mantenimiento'),
    path('select-data', SelectDataView.as_view(), name='select-data'),
    path('reservas', ReservaListView.as_view(), name='reserva-list'),
    path('reservas/<int:pk>', ReservaDetailView.as_view(), name='reserva-detail'),
    path('dashboard/stats', DashboardStatsView.as_view(), name='dashboard-stats'),
    path('inventarios', InventarioListView.as_view(), name='inventario-list'),
    path('inventarios/<int:pk>', InventarioDetailView.as_view(), name='inventario-detail'),
    
    # ========== RF-10: RESERVAS ==========
    path('reservas', ReservaListCreateView.as_view(), name='reserva-list-create'),
    path('reservas/<int:pk>', ReservaDetailView.as_view(), name='reserva-detail'),  # ← AGREGAR ESTA LÍNEA
    
    # ========== ESTADÍSTICAS ==========
    path('dashboard/stats', DashboardStatsView.as_view(), name='dashboard-stats'),
    
    # ========== DATOS PARA SELECTS ==========
    path('select-data', SelectDataView.as_view(), name='select-data'),
    
    # ========== INTEGRACIÓN GEMINI AI ==========
    path('inventarios/analisis-ia', InventarioIAPredictionView.as_view(), name='inventario-analisis-ia'),
    path('promociones/analisis-ia', PromocionesIAView.as_view(), name='promociones-analisis-ia'),
]