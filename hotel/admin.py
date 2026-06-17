from django.contrib import admin
from .models import Incidencia
from django.contrib.auth.admin import UserAdmin
from .models import Usuario, Sede, Habitacion, Huesped, Reserva, Comprobante

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
admin.site.register(Incidencia)

@admin.register(Comprobante)
class ComprobanteAdmin(admin.ModelAdmin):
    list_display = ('id', 'numero_completo', 'reserva', 'tipo_comprobante', 'monto_total', 'fecha_emision')
    list_filter = ('tipo_comprobante', 'metodo_pago')
    search_fields = ('reserva__codigo_reserva', 'nombre_cliente', 'documento_cliente')
