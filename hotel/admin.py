from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario, Sede, Habitacion, Huesped, Reserva

# Registrar Usuario con el admin personalizado de Django
admin.site.register(Usuario, UserAdmin)

# Registrar los demás modelos
@admin.register(Sede)
class SedeAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'direccion', 'telefono')
    search_fields = ('nombre',)

@admin.register(Habitacion)
class HabitacionAdmin(admin.ModelAdmin):
    list_display = ('id', 'numero', 'sede', 'tipo', 'capacidad', 'precio_base', 'estado')
    list_filter = ('sede', 'tipo', 'estado')
    search_fields = ('numero',)

@admin.register(Huesped)
class HuespedAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'apellido', 'email', 'documento')
    search_fields = ('nombre', 'apellido', 'email', 'documento')

@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ('id', 'codigo_reserva', 'huesped', 'habitacion', 'fecha_entrada', 'fecha_salida', 'estado')
    list_filter = ('estado', 'origen')
    search_fields = ('codigo_reserva',)