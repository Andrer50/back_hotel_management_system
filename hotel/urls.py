from django.urls import path
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)
from .views import (
    RegisterView, 
    UserProfileView,
    RoleListCreateView,
    RoleDetailView,
    PermissionListView,
    UserListView,
    UserDetailView,
    HuespedListView,
    HuespedDetailView,
    HabitacionListView,
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
    PersonalMantenimientoListView
)
from .auth_views import MyTokenObtainPairView

urlpatterns = [
    path('register', RegisterView.as_view(), name='register'),
    path('login', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh', TokenRefreshView.as_view(), name='token_refresh'),
    path('profile', UserProfileView.as_view(), name='profile'),
    path('users', UserListView.as_view(), name='user-list'),
    path('users/<int:pk>', UserDetailView.as_view(), name='user-detail'),
    path('huespedes', HuespedListView.as_view(), name='huesped-list'),
    path('huespedes/<int:pk>', HuespedDetailView.as_view(), name='huesped-detail'),
    path('habitaciones', HabitacionListView.as_view(), name='habitacion-list'),
    path('habitaciones/<int:pk>', HabitacionDetailView.as_view(), name='habitacion-detail'),
    path('plantas', PlantaListView.as_view(), name='planta-list'),
    path('plantas/<int:pk>', PlantaDetailView.as_view(), name='planta-detail'),
    path('areas-comunes', AreaComunListView.as_view(), name='area-comun-list'),
    path('areas-comunes/<int:pk>', AreaComunDetailView.as_view(), name='area-comun-detail'),
    path('limpiezas', RegistroLimpiezaListView.as_view(), name='limpieza-list'),
    path('limpiezas/<int:pk>', RegistroLimpiezaDetailView.as_view(), name='limpieza-detail'),
    path('incidencias', IncidenciaListView.as_view(), name='incidencia-list'),
    path('incidencias/<int:pk>', IncidenciaDetailView.as_view(), name='incidencia-detail'),
    path('personal-limpieza', PersonalLimpiezaListView.as_view(), name='personal-limpieza'),
    path('personal-mantenimiento', PersonalMantenimientoListView.as_view(), name='personal-mantenimiento'),
    
    # Roles y Permisos
    path('roles', RoleListCreateView.as_view(), name='role-list-create'),
    path('roles/<int:pk>', RoleDetailView.as_view(), name='role-detail'),
    path('permissions', PermissionListView.as_view(), name='permission-list'),
]
