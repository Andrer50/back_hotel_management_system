import uuid
# pyrefly: ignore [missing-import]
from django.db import models
# pyrefly: ignore [missing-import]
from django.contrib.auth.models import AbstractUser, Group

# ==============================================================================
# MÓDULO A: ADMINISTRACIÓN Y SEGURIDAD (Y CONFIGURACIÓN GLOBAL)
# ==============================================================================

class Sede(models.Model):
    """
    Representa una sede física del Hotel Asturias (ej. San Isidro, Miraflores).
    """
    nombre = models.CharField(
        max_length=100, 
        unique=True, 
        verbose_name='Nombre de la sede'
    )
    direccion = models.CharField(
        max_length=255, 
        verbose_name='Dirección'
    )
    telefono = models.CharField(
        max_length=20, 
        blank=True, 
        null=True, 
        verbose_name='Teléfono'
    )

    class Meta:
        verbose_name = 'Sede'
        verbose_name_plural = 'Sedes'

    def __str__(self):
        return self.nombre


class Usuario(AbstractUser):
    """
    Modelo de usuario personalizado que extiende la autenticación básica de Django
    para incorporar la gestión de roles internos del personal del hotel y su
    sede asignada.
    """
    role = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='usuarios',
        verbose_name='Rol del usuario'
    )
    sede_asignada = models.ForeignKey(
        Sede,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='personal',
        verbose_name='Sede asignada'
    )
    telefono = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name='Teléfono'
    )
    status = models.CharField(
        max_length=20,
        choices=[('ACTIVE', 'Activo'), ('INACTIVE', 'Inactivo')],
        default='ACTIVE',
        verbose_name='Estado registrado'
    )

    def save(self, *args, **kwargs):
        # Sincronizamos is_active con nuestro status
        self.is_active = (self.status == 'ACTIVE')
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        permissions = [
            ("can_clean_rooms", "Can clean rooms"),
            ("can_do_maintenance", "Can do maintenance"),
            ("can_manage_users", "Can manage users"),
            ("can_manage_roles", "Can manage roles"),
            ("can_manage_inventory", "Can manage inventory"),
            ("can_manage_reservations", "Can manage reservations"),
            ("can_view_reports", "Can view reports"),
            ("can_manage_rooms", "Can manage rooms"),
        ]

    def __str__(self):
        fullname = self.get_full_name()
        display_name = fullname if fullname else self.username
        return f"{display_name} ({self.role.name if self.role else 'Sin Rol'})"


# ==============================================================================
# MÓDULO B: OPERACIONES (ESPACIOS, LOGÍSTICA Y MANTENIMIENTO)
# ==============================================================================

class Planta(models.Model):
    """
    Representa un piso o planta física del hotel.
    """
    nombre = models.CharField(max_length=50, verbose_name='Nombre de la planta') # Ej: "Planta 1", "Ático"
    numero = models.PositiveIntegerField(unique=True, verbose_name='Número de planta') # Ej: 1, 2, 3

    class Meta:
        verbose_name = 'Planta'
        verbose_name_plural = 'Plantas'
        ordering = ['numero']

    def __str__(self):
        return self.nombre

class Habitacion(models.Model):
    """
    Representa una habitación física dentro de una sede del hotel.
    """
    class Tipo(models.TextChoices):
        INDIVIDUAL = 'INDIVIDUAL', 'Individual'
        DOBLE = 'DOBLE', 'Doble'
        SUITE = 'SUITE', 'Suite'
        FAMILIAR = 'FAMILIAR', 'Familiar'

    class Estado(models.TextChoices):
        DISPONIBLE = 'DISPONIBLE', 'Disponible'
        OCUPADA = 'OCUPADA', 'Ocupada'
        MANTENIMIENTO = 'MANTENIMIENTO', 'En Mantenimiento'
        SUCIA = 'SUCIA', 'Sucia / Limpieza requerida'

    sede = models.ForeignKey(
        Sede,
        on_delete=models.CASCADE,
        related_name='habitaciones',
        null=True,
        blank=True,
        verbose_name='Sede'
    )
    planta = models.ForeignKey(
        Planta,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='habitaciones',
        verbose_name='Planta/Piso'
    )
    numero = models.CharField(
        max_length=10,
        verbose_name='Número de habitación'
    )
    tipo = models.CharField(
        max_length=20,
        choices=Tipo.choices,
        default=Tipo.INDIVIDUAL,
        verbose_name='Tipo de habitación'
    )
    capacidad = models.PositiveIntegerField(
        verbose_name='Capacidad de huéspedes'
    )
    precio_base = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Precio base por noche'
    )
    estado = models.CharField(
        max_length=20,
        choices=Estado.choices,
        default=Estado.DISPONIBLE,
        verbose_name='Estado de la habitación'
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name='¿Habitación activa?'
    )

    class Meta:
        verbose_name = 'Habitación'
        verbose_name_plural = 'Habitaciones'
        # unique_together = ('sede', 'numero')

    def __str__(self):
        sede_nombre = self.sede.nombre if self.sede else "Sin Sede"
        return f"Hab. {self.numero} ({self.get_tipo_display()}) - {sede_nombre}"


class AreaComun(models.Model):
    """
    Áreas compartidas de las sedes (ej: piscina, gimnasio, restaurante, sala de reuniones).
    """
    class Estado(models.TextChoices):
        DISPONIBLE = 'DISPONIBLE', 'Disponible'
        OCUPADA = 'OCUPADA', 'Ocupada'
        MANTENIMIENTO = 'MANTENIMIENTO', 'En Mantenimiento'
        SUCIA = 'SUCIA', 'Sucia / Limpieza requerida'
        RESTRINGIDO = 'RESTRINGIDO', 'Restringido'

    sede = models.ForeignKey(
        Sede,
        on_delete=models.CASCADE,
        related_name='areas_comunes',
        verbose_name='Sede'
    )
    nombre = models.CharField(
        max_length=100,
        verbose_name='Nombre del área común'
    )
    capacidad_maxima = models.PositiveIntegerField(
        verbose_name='Aforo máximo permitido'
    )
    aforo_actual = models.PositiveIntegerField(
        default=0,
        verbose_name='Aforo actual'
    )
    imagen = models.ImageField(
        upload_to='areas/',
        null=True,
        blank=True,
        verbose_name='Imagen del área'
    )
    categoria = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name='Categoría'
    )
    descripcion = models.TextField(
        blank=True,
        null=True,
        verbose_name='Descripción'
    )
    estado = models.CharField(
        max_length=20,
        choices=Estado.choices,
        default=Estado.DISPONIBLE,
        verbose_name='Estado'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='¿Área activa?'
    )

    class Meta:
        verbose_name = 'Área Común'
        verbose_name_plural = 'Áreas Comunes'
        unique_together = ('sede', 'nombre')

    def __str__(self):
        return f"{self.nombre} ({self.sede.nombre})"


class Inventario(models.Model):
    """
    Control de suministros, insumos de limpieza y amenities del hotel.
    Sirve también como catálogo para consumos extra en estadías.
    """
    class Tipo(models.TextChoices):
        SUMINISTRO = 'SUMINISTRO', 'Suministro'
        INVENTARIO = 'INVENTARIO', 'Inventario'

    sede = models.ForeignKey(
        Sede,
        on_delete=models.CASCADE,
        related_name='inventarios',
        verbose_name='Sede'
    )
    nombre = models.CharField(
        max_length=100,
        verbose_name='Nombre del suministro / artículo'
    )
    descripcion = models.TextField(
        blank=True,
        null=True,
        verbose_name='Descripción'
    )
    stock_actual = models.PositiveIntegerField(
        default=0,
        verbose_name='Stock actual'
    )
    stock_minimo = models.PositiveIntegerField(
        default=5,
        verbose_name='Stock mínimo (alerta de reabastecimiento)'
    )
    precio_unitario = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        verbose_name='Precio de venta unitario (para cargos extra)'
    )
    tipo = models.CharField(
        max_length=20,
        choices=Tipo.choices,
        default=Tipo.SUMINISTRO,
        verbose_name='Tipo de artículo'
    )

    class Meta:
        verbose_name = 'Inventario / Suministro'
        verbose_name_plural = 'Inventarios / Suministros'
        unique_together = ('sede', 'nombre')

    def __str__(self):
        return f"{self.nombre} ({self.sede.nombre}) - Stock: {self.stock_actual}"


class RegistroLimpieza(models.Model):
    """
    Seguimiento del estado de limpieza de las habitaciones en tiempo real.
    """
    class Estado(models.TextChoices):
        EN_PROGRESO = 'EN_PROGRESO', 'En Progreso'
        COMPLETADO = 'COMPLETADO', 'Completado'
        INSPECCIONADO = 'INSPECCIONADO', 'Inspeccionado y Aprobado'

    habitacion = models.ForeignKey(
        Habitacion,
        on_delete=models.CASCADE,
        related_name='registros_limpieza',
        verbose_name='Habitación'
    )
    personal_limpieza = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={'role__permissions__codename': 'can_clean_rooms'},
        related_name='limpiezas_asignadas',
        verbose_name='Personal de limpieza'
    )
    fecha_inicio = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de inicio'
    )
    fecha_fin = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Fecha de finalización'
    )
    estado = models.CharField(
        max_length=20,
        choices=Estado.choices,
        default=Estado.EN_PROGRESO,
        verbose_name='Estado'
    )
    observaciones = models.TextField(
        blank=True,
        null=True,
        verbose_name='Observaciones'
    )

    class Meta:
        verbose_name = 'Registro de Limpieza'
        verbose_name_plural = 'Registros de Limpieza'
        ordering = ['-fecha_inicio']

    def __str__(self):
        sede_nombre = self.habitacion.sede.nombre if self.habitacion.sede else "Sin Sede"
        return f"Limpieza Hab. {self.habitacion.numero} - Sede: {sede_nombre} ({self.get_estado_display()})"


class Incidencia(models.Model):
    """
    Registro y control de daños, averías y problemas de mantenimiento.
    """
    class Prioridad(models.TextChoices):
        ALTA = 'ALTA', 'Alta'
        MEDIA = 'MEDIA', 'Media'
        BAJA = 'BAJA', 'Baja'

    class Estado(models.TextChoices):
        PENDIENTE = 'PENDIENTE', 'Pendiente'
        EN_PROGRESO = 'EN_PROGRESO', 'En Progreso'
        RESUELTO = 'RESUELTO', 'Resuelto'
        CANCELADO = 'CANCELADO', 'Cancelado'

    titulo = models.CharField(
        max_length=150,
        verbose_name='Título / Resumen de la incidencia'
    )
    descripcion = models.TextField(
        verbose_name='Descripción detallada'
    )
    habitacion = models.ForeignKey(
        Habitacion,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='incidencias',
        verbose_name='Habitación afectada'
    )
    area_comun = models.ForeignKey(
        AreaComun,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='incidencias',
        verbose_name='Área común afectada'
    )
    reportado_por = models.ForeignKey(
        Usuario,
        on_delete=models.PROTECT,
        related_name='incidencias_reportadas',
        verbose_name='Reportado por'
    )
    asignado_a = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        limit_choices_to={'role__permissions__codename': 'can_do_maintenance'},
        related_name='incidencias_asignadas',
        verbose_name='Asignado a (Personal de Mantenimiento)'
    )
    fecha_reporte = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de reporte'
    )
    fecha_resolucion = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Fecha de resolución'
    )
    prioridad = models.CharField(
        max_length=10,
        choices=Prioridad.choices,
        default=Prioridad.MEDIA,
        verbose_name='Prioridad'
    )
    estado = models.CharField(
        max_length=20,
        choices=Estado.choices,
        default=Estado.PENDIENTE,
        verbose_name='Estado de la incidencia'
    )

    class Meta:
        verbose_name = 'Incidencia de Mantenimiento'
        verbose_name_plural = 'Incidencias de Mantenimiento'
        ordering = ['-prioridad', 'fecha_reporte']

    def __str__(self):
        ubicacion = f"Hab. {self.habitacion.numero}" if self.habitacion else f"Área: {self.area_comun.nombre}"
        return f"{self.titulo} en {ubicacion} - ({self.get_estado_display()})"


# ==============================================================================
# MÓDULO C: RECEPCIÓN (HUÉSPEDES, RESERVAS Y ESTADÍAS)
# ==============================================================================

class Huesped(models.Model):
    """
    Datos de identificación, perfil e historial de preferencias del cliente.
    """
    class TipoDocumento(models.TextChoices):
        DNI = 'DNI', 'DNI (Documento Nacional de Identidad)'
        PASAPORTE = 'PASAPORTE', 'Pasaporte'
        CE = 'CE', 'Carné de Extranjería'

    nombre = models.CharField(
        max_length=100,
        verbose_name='Nombre(s)'
    )
    apellido = models.CharField(
        max_length=100,
        verbose_name='Apellido(s)'
    )
    tipo_documento = models.CharField(
        max_length=20,
        choices=TipoDocumento.choices,
        default=TipoDocumento.DNI,
        verbose_name='Tipo de Documento'
    )
    documento = models.CharField(
        max_length=20,
        unique=True,
        verbose_name='Número de Documento'
    )
    email = models.EmailField(
        verbose_name='Correo Electrónico'
    )
    telefono = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name='Teléfono'
    )
    preferencias_notas = models.TextField(
        blank=True,
        null=True,
        verbose_name='Preferencias / Notas Especiales'
    )
    status = models.CharField(
        max_length=20,
        choices=[('ACTIVE', 'Activo'), ('INACTIVE', 'Inactivo')],
        default='ACTIVE',
        verbose_name='Estado'
    )

    class Meta:
        verbose_name = 'Huésped'
        verbose_name_plural = 'Huéspedes'

    def __str__(self):
        return f"{self.nombre} {self.apellido} ({self.get_tipo_documento_display()}: {self.documento})"


class Reserva(models.Model):
    """
    Reserva de una habitación por parte de un huésped, incluyendo fechas e ingresos estimados.
    """
    class Estado(models.TextChoices):
        PENDIENTE = 'PENDIENTE', 'Pendiente / Pago Pendiente'
        CONFIRMADA = 'CONFIRMADA', 'Confirmada'
        EN_CURSO = 'EN_CURSO', 'En Curso (Hospedado)'
        COMPLETADA = 'COMPLETADA', 'Completada / Check-out'
        CANCELADA = 'CANCELADA', 'Cancelada'

    class Origen(models.TextChoices):
        DIRECTO = 'DIRECTO', 'Reserva Directa'
        OTA_BOOKING = 'BOOKING', 'Booking.com'
        OTA_EXPEDIA = 'EXPEDIA', 'Expedia'
        OTA_AIRBNB = 'AIRBNB', 'Airbnb'

    codigo_reserva = models.CharField(
        max_length=20,
        unique=True,
        verbose_name='Código de Reserva'
    )
    huesped = models.ForeignKey(
        Huesped,
        on_delete=models.PROTECT,
        related_name='reservas',
        verbose_name='Huésped'
    )
    habitacion = models.ForeignKey(
        Habitacion,
        on_delete=models.PROTECT,
        related_name='reservas',
        verbose_name='Habitación'
    )
    fecha_entrada = models.DateField(
        verbose_name='Fecha de Entrada (Check-in)'
    )
    fecha_salida = models.DateField(
        verbose_name='Fecha de Salida (Check-out)'
    )
    fecha_reserva = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de Reserva'
    )
    estado = models.CharField(
        max_length=20,
        choices=Estado.choices,
        default=Estado.PENDIENTE,
        verbose_name='Estado de la reserva'
    )
    tarifa_aplicada = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Tarifa total aplicada (Precio pactado)'
    )
    origen = models.CharField(
        max_length=20,
        choices=Origen.choices,
        default=Origen.DIRECTO,
        verbose_name='Origen de la reserva (OTA)'
    )

    class Meta:
        verbose_name = 'Reserva'
        verbose_name_plural = 'Reservas'

    def save(self, *args, **kwargs):
        # Autogeneración de un código de reserva seguro en mayúsculas si no existe
        if not self.codigo_reserva:
            self.codigo_reserva = f"AST-{uuid.uuid4().hex[:6].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        sede_nombre = self.habitacion.sede.nombre if self.habitacion.sede else "Sin Sede"
        return f"Reserva {self.codigo_reserva} | {self.huesped.apellido} (Hab: {self.habitacion.numero} - {sede_nombre})"


class Estadia(models.Model):
    """
    Vínculo físico real de hospedaje que registra las horas de Check-In y Check-Out
    y asocia todos los consumos extra y eventos de aforo.
    """
    reserva = models.OneToOneField(
        Reserva,
        on_delete=models.PROTECT,
        related_name='estadia',
        verbose_name='Reserva Asociada'
    )
    fecha_checkin = models.DateTimeField(
        verbose_name='Fecha y hora de Check-in real'
    )
    fecha_checkout = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Fecha y hora de Check-out real'
    )
    registrado_por = models.ForeignKey(
        Usuario,
        on_delete=models.PROTECT,
        related_name='checkins_registrados',
        verbose_name='Registrado por (Recepción)'
    )
    checkout_registrado_por = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='checkouts_registrados',
        verbose_name='Check-out registrado por'
    )
    observaciones = models.TextField(
        blank=True,
        null=True,
        verbose_name='Observaciones / Estado del cliente'
    )

    class Meta:
        verbose_name = 'Estadía'
        verbose_name_plural = 'Estadías'

    def __str__(self):
        return f"Estadía de {self.reserva.huesped.nombre} {self.reserva.huesped.apellido} (Hab: {self.reserva.habitacion.numero})"


class RegistroAforoAreaComun(models.Model):
    class Estado(models.TextChoices):
        PENDIENTE = 'PENDIENTE', 'Pendiente'
        CONFIRMADA = 'CONFIRMADA', 'Confirmada'
        EN_CURSO = 'EN_CURSO', 'En Curso'
        COMPLETADA = 'COMPLETADA', 'Completada'
        CANCELADA = 'CANCELADA', 'Cancelada'

    area_comun = models.ForeignKey(
        AreaComun,
        on_delete=models.CASCADE,
        related_name='registros_aforo',
        verbose_name='Área Común'
    )
    huesped = models.ForeignKey(
        Huesped,
        on_delete=models.CASCADE,
        related_name='registros_aforo',
        verbose_name='Huésped'
    )
    registrado_por = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='aforos_registrados',
        verbose_name='Registrado por'
    )
    fecha_ingreso_programada = models.DateTimeField(
        null=True, blank=True,
        verbose_name='Fecha y hora de ingreso programada'
    )
    fecha_salida_programada = models.DateTimeField(
        null=True, blank=True,
        verbose_name='Fecha y hora de salida programada'
    )
    fecha_ingreso_real = models.DateTimeField(
        blank=True, null=True,
        verbose_name='Fecha y hora de ingreso real'
    )
    fecha_salida_real = models.DateTimeField(
        blank=True, null=True,
        verbose_name='Fecha y hora de salida real'
    )
    estado = models.CharField(
        max_length=20,
        choices=Estado.choices,
        default=Estado.PENDIENTE,
        verbose_name='Estado'
    )
    notas = models.TextField(
        blank=True, null=True,
        verbose_name='Notas'
    )

    class Meta:
        verbose_name = 'Registro de Aforo'
        verbose_name_plural = 'Registros de Aforo'
        ordering = ['-fecha_ingreso_programada']

    def __str__(self):
        return f"{self.huesped.nombre} en {self.area_comun.nombre} ({self.get_estado_display()})"


class ConsumoExtra(models.Model):
    """
    Cargos adicionales a la estadía de un huésped (comidas, bebidas de minibar, lavandería, tours, etc.).
    """
    estadia = models.ForeignKey(
        Estadia,
        on_delete=models.CASCADE,
        related_name='consumos_extra',
        verbose_name='Estadía'
    )
    inventario = models.ForeignKey(
        Inventario,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='consumos_asociados',
        verbose_name='Artículo de Inventario (Suministro consumido)'
    )
    descripcion = models.CharField(
        max_length=255,
        verbose_name='Descripción del cargo o servicio'
    )
    cantidad = models.PositiveIntegerField(
        default=1,
        verbose_name='Cantidad'
    )
    precio_unitario = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Precio Unitario'
    )
    fecha_consumo = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de consumo'
    )
    pagado = models.BooleanField(
        default=False,
        verbose_name='¿Pagado de inmediato?'
    )

    class Meta:
        verbose_name = 'Consumo Extra'
        verbose_name_plural = 'Consumos Extra'

    @property
    def total(self):
        return self.cantidad * self.precio_unitario

    def __str__(self):
        return f"{self.descripcion} (x{self.cantidad}) - Total: S/. {self.total:.2f} - {self.estadia.reserva.huesped.apellido}"


class Comprobante(models.Model):
    class Tipo(models.TextChoices):
        BOLETA = 'BOLETA', 'Boleta'
        FACTURA = 'FACTURA', 'Factura'
        
    class MetodoPago(models.TextChoices):
        EFECTIVO = 'EFECTIVO', 'Efectivo'
        TARJETA = 'TARJETA', 'Tarjeta'
        TRANSFERENCIA = 'TRANSFERENCIA', 'Transferencia'

    reserva = models.ForeignKey(
        Reserva,
        on_delete=models.PROTECT,
        related_name='comprobantes',
        verbose_name='Reserva Asociada'
    )
    tipo_comprobante = models.CharField(
        max_length=10,
        choices=Tipo.choices,
        verbose_name='Tipo de Comprobante'
    )
    serie = models.CharField(
        max_length=4,
        verbose_name='Serie'
    )
    numero = models.PositiveIntegerField(
        verbose_name='Número Correlativo'
    )
    documento_cliente = models.CharField(
        max_length=20,
        verbose_name='Documento del Cliente'
    )
    nombre_cliente = models.CharField(
        max_length=150,
        verbose_name='Nombre del Cliente'
    )
    metodo_pago = models.CharField(
        max_length=20,
        choices=MetodoPago.choices,
        verbose_name='Método de Pago'
    )
    monto_total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Monto Total'
    )
    fecha_emision = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de Emisión'
    )

    class Meta:
        unique_together = ('tipo_comprobante', 'serie', 'numero')
        verbose_name = 'Comprobante de Pago'
        verbose_name_plural = 'Comprobantes de Pago'

    def save(self, *args, **kwargs):
        if not self.id:
            if self.tipo_comprobante == 'BOLETA':
                self.serie = 'B001'
            else:
                self.serie = 'F001'
            
            ultimo = Comprobante.objects.filter(
                tipo_comprobante=self.tipo_comprobante,
                serie=self.serie
            ).order_by('-numero').first()
            
            self.numero = (ultimo.numero + 1) if ultimo else 1
            
        super().save(*args, **kwargs)

    @property
    def numero_completo(self):
        return f"{self.serie}-{self.numero:08d}"

    def __str__(self):
        return f"{self.tipo_comprobante} {self.numero_completo} - S/. {self.monto_total} - Reserva {self.reserva.codigo_reserva}"

# ==============================================================================
# MÓDULO D: GESTIÓN DE TARIFAS Y PLANIFICACIÓN DINÁMICA
# ==============================================================================

class Temporada(models.Model):
    """
    Representa un rango de fechas especial en el calendario (ej. Año Nuevo, Semana Santa)
    donde las tarifas base de las habitaciones sufren variaciones por alta demanda.
    """
    nombre = models.CharField(
        max_length=100,
        verbose_name='Nombre de la temporada / evento'
    )
    fecha_inicio = models.DateField(
        verbose_name='Fecha de Inicio'
    )
    fecha_fin = models.DateField(
        verbose_name='Fecha de Finalización'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='¿Temporada activa?'
    )

    class Meta:
        verbose_name = 'Temporada Dinámica'
        verbose_name_plural = 'Temporadas Dinámicas'
        ordering = ['fecha_inicio']

    def __str__(self):
        return f"{self.nombre} ({self.fecha_inicio} al {self.fecha_fin})"
    
    porcentaje = models.IntegerField(default=0, help_text="Porcentaje de variación")