import os
import logging
from typing import Any, Dict, List, Optional, Type
from google import genai
from google.genai import types
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

# ==============================================================================
# ESQUEMAS DE PREDICCIÓN DE INVENTARIO
# ==============================================================================

class InventoryAlert(BaseModel):
    id: int
    nombre: str
    razon: str
    nivel_urgencia: str  # 'ALTA', 'MEDIA', 'BAJA'

class ReorderRecommendation(BaseModel):
    id: int
    nombre: str
    cantidad_sugerida: int
    justificacion: str

class SlowMovingSuggestion(BaseModel):
    id: int
    nombre: str
    sugerencia: str

class InventoryAnalysisSchema(BaseModel):
    alertas_criticas: List[InventoryAlert] = Field(
        description="Artículos que están por debajo o cerca del stock mínimo y requieren reabastecimiento inmediato."
    )
    recomendaciones_reabastecimiento: List[ReorderRecommendation] = Field(
        description="Sugerencias de reabastecimiento con cantidades estimadas y justificaciones de negocio."
    )
    sugerencias_exceso_stock: List[SlowMovingSuggestion] = Field(
        description="Artículos con stock excesivo o baja rotación que se sugiere dejar de comprar o disminuir sus pedidos."
    )

# ==============================================================================
# ESQUEMAS DE ANÁLISIS DE VENTAS Y PROMOCIONES
# ==============================================================================

class ProfitabilityAnalysis(BaseModel):
    habitaciones_mas_rentables: List[str] = Field(
        description="Habitaciones o tipos de habitación que han demostrado mayor volumen de ventas o ingresos."
    )
    servicios_mas_vendidos: List[str] = Field(
        description="Servicios extras o insumos de inventario que tienen mayor consumo registrado."
    )
    observaciones: str = Field(
        description="Análisis de comportamiento e insights de ventas deducidos de los datos."
    )

class PromotionProposal(BaseModel):
    nombre: str = Field(description="Nombre comercial y llamativo para la promoción.")
    descripcion: str = Field(description="Descripción del paquete, oferta o descuento planteado.")
    descuento_sugerido: str = Field(description="Descuento sugerido (ej. '15% de descuento', '2x1 en amenities').")
    justificacion: str = Field(description="Razón comercial de la propuesta basada en los datos analizados.")

class SalesAnalysisSchema(BaseModel):
    analisis_rentabilidad: ProfitabilityAnalysis
    propuestas_promocionales: List[PromotionProposal]


# ==============================================================================
# SERVICIO PRINCIPAL DE GEMINI AI
# ==============================================================================

class GeminiService:
    @staticmethod
    def is_configured() -> bool:
        """Verifica si la API Key de Gemini está configurada."""
        api_key = os.getenv('GEMINI_API_KEY')
        return bool(api_key and api_key != "your_gemini_api_key_here")

    @classmethod
    def _get_client(cls) -> genai.Client:
        """Inicializa el cliente de Gemini usando el nuevo SDK google-genai."""
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key or api_key == "your_gemini_api_key_here":
            raise ValueError(
                "La clave GEMINI_API_KEY no está configurada o contiene el valor predeterminado. "
                "Por favor, agrégala en tu archivo .env para habilitar este servicio."
            )
        # El cliente encapsula la conexión a la API de manera orientada a objetos
        return genai.Client(api_key=api_key)

    @classmethod
    def generate_content(
        cls, 
        prompt: str, 
        system_instruction: Optional[str] = None, 
        response_schema: Optional[Type[BaseModel]] = None,
        temperature: float = 0.2
    ) -> str:
        """
        Método genérico para generar contenido usando Gemini.
        Soporta prompts personalizados, instrucciones de sistema y salida estructurada (JSON).
        """
        try:
            client = cls._get_client()
            model_name = os.getenv('GEMINI_MODEL', 'gemini-3.1-flash-lite')
            print(f">>> MODELO USADO: {model_name}")
            # Construimos la configuración usando las clases nativas del nuevo SDK
            config = types.GenerateContentConfig(
                temperature=temperature,
                system_instruction=system_instruction,
            )
            
            if response_schema:
                config.response_mime_type = "application/json"
                config.response_schema = response_schema
                
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=config
            )
            return response.text
        except Exception as e:
            logger.error(f"Error en GeminiService.generate_content: {str(e)}")
            raise e

    @classmethod
    def predict_inventory_needs(cls, inventory_items: List[Dict[str, Any]]) -> str:
        """
        Analiza un listado de inventario y genera predicciones de desabastecimiento/reabastecimiento.
        """
        system_instruction = (
            "Eres un experto en gestión de inventarios y logística para hoteles de primer nivel. "
            "Tu labor consiste en analizar la lista de artículos del inventario brindada y pronosticar qué suministros "
            "están por agotarse (stock_actual muy bajo respecto a stock_minimo), cuáles requieren reordenarse "
            "con cantidades idóneas, y cuáles tienen baja demanda/rotación y deben ser suspendidos o limitados en compras."
        )
        
        prompt = (
            f"Datos del Inventario del Hotel:\n"
            f"{inventory_items}\n\n"
            f"Por favor, analiza detenidamente estos registros de inventario y responde utilizando el formato JSON solicitado "
            f"según el esquema definido."
        )
        
        return cls.generate_content(
            prompt=prompt,
            system_instruction=system_instruction,
            response_schema=InventoryAnalysisSchema,
            temperature=0.1
        )

    @classmethod
    def analyze_sales_and_promotions(cls, reservas: List[Dict[str, Any]], consumos: List[Dict[str, Any]]) -> str:
        """
        Analiza reservas y consumos extra para proponer promociones y reportar rentabilidad comercial.
        """
        system_instruction = (
            "Eres un especialista de Revenue Management y Estrategia de Marketing Hotelero. "
            "Tu meta es analizar el historial de reservas y consumos extra de los huéspedes para encontrar qué tipos de "
            "habitación e insumos generan el mayor impacto financiero y proponer ideas promocionales atractivas, "
            "paquetes conjuntos o descuentos inteligentes."
        )
        
        prompt = (
            f"Historial Reciente de Reservas:\n{reservas}\n\n"
            f"Historial Reciente de Consumos Extra (minibar, lavandería, etc.):\n{consumos}\n\n"
            f"Procesa estos conjuntos de datos y rellena el esquema estructurado de salida de ventas en formato JSON."
        )
        
        return cls.generate_content(
            prompt=prompt,
            system_instruction=system_instruction,
            response_schema=SalesAnalysisSchema,
            temperature=0.2
        )

    # ==============================================================================
    # ASISTENCIA INTERNA PARA EL PERSONAL DEL HOTEL (CHATBOT STAFF)
    # ==============================================================================

    @classmethod
    def responder_asistente_staff(
        cls,
        mensaje_usuario: str,
        role_name: str | None,
        permissions: list[str], # Mantenemos el parámetro por si lo mandas desde el controlador, aunque ya no lo usemos aquí
        contexto_operativo: dict,
        historial: list[dict]
    ) -> str:
        """
        Chatbot interno para el personal del hotel.
        Responde inyectando un prompt fijo basado directamente en el ROL del usuario.
        """

        if not role_name:
            return (
                "No se ha detectado un rol asignado a tu cuenta. "
                "Por favor contacta con el administrador del sistema para que te asigne "
                "un rol antes de poder usar el asistente."
            )

        # ── Mapa directo de ROL → Contexto funcional ──────────────────────────
        CONTEXTO_POR_ROL = {
            "Recepcionista": (
                "MÓDULO: RESERVAS\n"
                "- Ver reservas: Sidebar izquierdo → 'Reservas'. La tabla central muestra todas las reservas.\n"
                "- Nueva reserva: Botón verde '+ Nueva Reserva' (esquina superior derecha). Buscar huésped, seleccionar habitación, ingresar tarifa y origen. Confirmar con botón verde 'Crear Reserva' (esquina inferior derecha del modal).\n"
                "- Modificar reserva: Botón 'Modificar' en columna ACCIONES de la fila. Permite cambiar estado y tarifa. Confirmar con botón naranja 'Actualizar Reserva' (esquina inferior derecha).\n"
                "- Check-In: Solo aparece en reservas PENDIENTE o CONFIRMADA. Botón 'Check-In' en columna ACCIONES. Se abre modal de confirmación con observaciones. Confirmar con botón verde 'Confirmar Check-In'.\n"
                "- Check-Out: Solo aparece en reservas EN_CURSO. Botón 'Check-Out' en columna ACCIONES. Se abre modal de confirmación. Confirmar con botón negro 'Confirmar Check-Out' (esquina inferior derecha).\n"
                "- Consumos extra: Solo en reservas EN_CURSO. Botón '+ Consumos' (texto verde) en columna ACCIONES. Para añadir un artículo usar botón verde '+ Añadir' en la tarjeta del producto. Cerrar con botón azul oscuro 'Cerrar Registro'.\n"
                "- Facturar: Aparece en reservas EN_CURSO o COMPLETADA. Botón 'Facturar' (texto azul) en columna ACCIONES. El modal muestra configuración a la izquierda y vista previa a la derecha. Seleccionar método de pago a la izquierda. Confirmar con botón azul oscuro 'Emitir Comprobante'.\n"
                "- Filtrar reservas: Botones de estado encima de la tabla (Todos, CONFIRMADA, PENDIENTE, EN_CURSO, COMPLETADA, CANCELADA). Búsqueda por nombre, código o habitación en el campo de texto.\n\n"
                "MÓDULO: PAGOS\n"
                "- Ver historial: Sidebar → 'Pagos'. Muestra tarjetas de resumen financiero y tabla de comprobantes emitidos.\n"
                "- Filtrar: Botones de tipo de comprobante y método de pago encima de la tabla. Filtro por rango de fechas en el extremo derecho superior.\n"
                "- Ver detalle de comprobante: Botón azul 'Ver' (ícono de ojo) en la última columna de la tabla.\n"
                "- Reimprimir comprobante: Dentro del modal de detalle → botón azul oscuro 'Reimprimir Comprobante' (esquina inferior derecha). También hay botón 'Descargar' en blanco.\n\n"
                "MÓDULO: HABITACIONES\n"
                "- Ver panel: Sidebar → 'Habitaciones'. Muestra indicadores KPI, grid de tarjetas de habitaciones, sección de limpieza y alertas de mantenimiento.\n"
                "- Nueva habitación: Botón verde '+ Nueva Habitación' (esquina superior derecha). Ingresar número, tipo, planta, capacidad y precio. Confirmar con botón azul 'Guardar Habitación'.\n"
                "- Cambiar estado de habitación: Clic sobre la tarjeta de la habitación → abre 'Panel de Gestión Directa'. Los botones de estado (LISTA, OCUPADA, SUCIA, MTTO) están en la parte superior del modal. IMPORTANTE: siempre presionar el botón negro 'Guardar Cambios' para aplicar el cambio.\n"
                "- Habitación SUCIA: Al hacer clic en su tarjeta se abre el diálogo de asignación de limpieza.\n"
                "- Habitación en MANTENIMIENTO: Al hacer clic en su tarjeta se abre el diálogo para registrar o gestionar la incidencia.\n"
                "- Restricción: El recepcionista puede consultar tareas y reasignar personal, pero NO puede marcar tareas como completadas ni eliminarlas.\n\n"
                "MÓDULO: TEMPORADAS\n"
                "- Ver temporadas: Sidebar → 'Temporadas'. Panel izquierdo para configurar, tabla derecha con temporadas existentes.\n"
                "- Nueva temporada: Llenar datos en el panel izquierdo 'CONFIGURAR RANGO'. Confirmar con botón verde '+ Registrar Temporada' (parte inferior del panel izquierdo).\n"
                "- Editar temporada: Ícono de lápiz azul en la tabla derecha → carga los datos en el formulario izquierdo → confirmar con botón azul 'Guardar Cambios'.\n"
                "- Eliminar temporada: Ícono de papelera roja en la tabla derecha.\n"
                "- Sincronizar: Botón blanco 'Sincronizar' en la esquina superior derecha.\n\n"
                "MÓDULO: ÁREAS COMUNES\n"
                "- Ver áreas: Sidebar → 'Áreas Comunes'. Muestra panel de estado global, filtros por tipo y tarjetas de cada área.\n"
                "- Nueva área: Botón flotante '+' en la esquina inferior derecha de la pantalla → llenar datos y subir foto → confirmar con botón gris 'CREAR ÁREA COMÚN'.\n"
                "- Cambiar estado de área: Clic en la tarjeta del área → 'Panel de Gestión Directa' → seleccionar estado (DISPONIBLE, OCUPADA, SUCIA, MTTO., RESTRINGIDO) → confirmar con botón negro 'GUARDAR CAMBIOS'.\n"
                "- Agendar aforo: En el panel de gestión del área → botón negro 'NUEVA RESERVA' (extremo derecho de la cabecera) → llenar modal 'AGENDAR AFORO' → confirmar con botón gris 'CREAR RESERVA'.\n\n"
                "MÓDULO: ESTADÍSTICAS\n"
                "- Ver estadísticas: Sidebar → 'Estadísticas'. Vista de solo lectura, sin botones de acción.\n"
                "- Contenido: Tarjetas superiores con KPIs (Tasa de Ocupación Promedio, Ingresos Totales, Reservas Activas, Alertas de Stock Bajo). Tabla inferior con métricas de ocupación por sede (habitaciones totales, ocupadas, disponibles y porcentaje de eficiencia).\n"
                "- Esta sección es únicamente informativa, no permite modificar ningún dato."
            ),
            "Limpieza": (
                "MÓDULO: ESTADOS DE LIMPIEZA\n"
                "- Ver panel: Sidebar izquierdo → 'Estados de Limpieza'. Esta vista centraliza el monitoreo en tiempo real exclusivo para actualizar el estado de las habitaciones o áreas comunes que tienes asignadas.\n"
                "- Filtrar y buscar: En la parte superior tienes una barra de búsqueda y botones rápidos para filtrar las tarjetas por estado (Todos, Sucia, En progreso, Inspeccionada).\n"
                "- Marcar como completada: En las tarjetas que se encuentran en estado 'SUCIA' (etiqueta roja), verás un botón azul prominente que dice 'Marcar como Limpia'. Al presionarlo, finalizas la tarea y actualizas el estado para el resto del hotel.\n"
                "- Habitaciones en Mantenimiento: Si una tarjeta está en estado 'MANTENIMIENTO', verás un aviso de 'Incidencia Reportada' indicando que la limpieza se pospone hasta su reparación, y el botón de estado estará deshabilitado.\n"
                "- Consultar áreas listas: Para las habitaciones 'LIMPIAS' o áreas 'DISPONIBLES', cuentas con un enlace en la parte inferior de la tarjeta ('VER DETALLES' o 'DETALLES DEL ÁREA') para consultar más información.\n"
                "- Restricción: Tu rol es estrictamente operativo para la limpieza. No tienes acceso para crear incidencias técnicas, gestionar reservas, ni facturar."
            ),
            "Mantenimiento": (
                "MÓDULO: INCIDENCIAS DE MANTENIMIENTO\n"
                "- Ver panel: Sidebar izquierdo → 'Incidencias'. Muestra tarjetas superiores de resumen (Alta Prioridad, En Progreso, Resueltas) y una lista central con todas las incidencias reportadas.\n"
                "- Filtrar y buscar: Puedes usar la barra de búsqueda por título, los botones de filtro por estado (Pendiente, En Progreso, Resuelto, Cancelado) y prioridad (Alta, Media, Baja). También hay un checkbox para 'Incluir resueltas' a la derecha.\n"
                "- Nueva incidencia: Botón flotante '+' (esquina inferior derecha de la pantalla). Abre el modal rojo 'Nueva Incidencia' donde llenas Título, Ubicación (Habitación o Área común), Prioridad, Personal y Descripción. Confirmar con el botón rojo 'Registrar Incidencia'.\n"
                "- Gestionar incidencia: Haz clic sobre la tarjeta de cualquier incidencia en la lista para abrir su panel de detalle.\n"
                "- Editar y Guardar: Dentro del detalle, puedes modificar el Título, Descripción, Prioridad, Estado (Pendiente, En Progreso, Resuelto, Cancelado), Ubicación y Personal asignado. Para aplicar los ajustes, presiona siempre el botón negro 'Guardar cambios' (esquina inferior derecha).\n"
                "- Resolver rápidamente: Para finalizar la tarea de forma directa, presiona el botón verde ancho 'Marcar como Resuelto' dentro del modal de detalle.\n"
                "- Eliminar: Si la incidencia fue un error o está duplicada, usa el botón de texto rojo 'Eliminar incidencia' en la parte inferior del modal."
            ),
            "Administrador": (
                "MÓDULOS DE ADMINISTRACIÓN GLOBAL\n"
                "Tienes acceso total (Superusuario) a todos los módulos operativos del sistema (Reservas, Pagos, Habitaciones, Temporadas, Áreas Comunes y Estadísticas) con todas las funcionalidades de Recepción, además de los siguientes módulos exclusivos:\n\n"
                "MÓDULO: MANTENIMIENTO DE PERSONAL\n"
                "- Ver panel: Directorio del equipo con indicadores operativos y un panel de 'Optimización de recursos por IA'.\n"
                "- Nuevo usuario: Botón azul '+ Añadir Nuevo Personal' (esquina superior derecha). Se llena el formulario y se confirma con el botón azul 'Guardar Personal'.\n"
                "- Editar usuario: Clic en el ícono de lápiz en la última columna de la tabla. Permite modificar datos básicos, cambiar el rol asignado o desactivar la cuenta. Confirmar con el botón negro 'Actualizar Colaborador'.\n\n"
                "MÓDULO: INVENTARIO Y SUMINISTROS\n"
                "- Ver panel: Control de stock en tiempo real, alertas de reabastecimiento y valoración total.\n"
                "- Añadir artículo: Botón azul '+ Añadir Artículo' (esquina superior derecha). Se define nombre, tipo, stock y precio. Confirmar con el botón azul 'Registrar'.\n"
                "- Editar/Eliminar: Clic en la acción de texto 'Editar' en la fila del producto. El modal permite hacer un 'Ajuste rápido de stock', modificar detalles o usar el botón rojo 'Eliminar'. Confirmar con el botón azul 'Guardar cambios'.\n\n"
                "MÓDULO: ROLES Y PERMISOS\n"
                "- Modificar accesos: Selecciona un rol de la jerarquía izquierda. A la derecha verás los módulos con interruptores (toggles) para encender/apagar permisos. Para aplicar, usa el botón negro 'Guardar Cambios' (arriba a la derecha).\n"
                "- Crear rol: Botón azul '+ Crear Nuevo Rol' (esquina superior derecha). Define el nombre y marca los checkboxes de los accesos permitidos. Confirmar con 'Crear Rol'.\n\n"
                "MÓDULO: GESTIÓN DE HUÉSPEDES (CLIENTES)\n"
                "- Ver panel: Directorio de clientes con KPIs de lealtad, estancias promedio y panel de 'Perspectivas de Inteligencia' con sugerencias de la IA.\n"
                "- Nuevo huésped: Botón azul '+ Nuevo Huésped' (esquina superior derecha).\n"
                "- Editar huésped: Clic en el ícono de lápiz en la tabla. Permite actualizar datos personales, documento y estado del perfil. Confirmar con el botón azul 'Guardar Cambios'."
            )
        }

        # Extraer el contexto del diccionario; si el rol no está, dar un mensaje genérico.
        funciones_str = CONTEXTO_POR_ROL.get(
            role_name, 
            f"Tu rol '{role_name}' es válido, pero actualmente no tengo un manual de funciones específico configurado para ti. Consulta con el Administrador."
        )

        # ── Contexto operativo anónimo según rol ──────────────────────────────
        contexto_str = ""
        if contexto_operativo:
            lineas = [f"  - {clave}: {valor}" for clave, valor in contexto_operativo.items()]
            contexto_str = (
                "\n\nCONTEXTO OPERATIVO ACTUAL (datos anónimos en tiempo real):\n"
                + "\n".join(lineas)
            )

        # ── System instruction ────────────────────────────────────────────────
        system_instruction = (
            f"Eres 'Astur', el asistente interno del sistema de gestión del Hotel Asturias. "
            f"Estás hablando con un miembro del personal con el rol: '{role_name}'.\n\n"
            f"TU MISIÓN:\n"
            f"Ayudar a este usuario a entender y usar las funciones del sistema que tiene "
            f"habilitadas para su rol. Sé claro, directo y práctico. "
            f"Da instrucciones paso a paso cuando te pregunten cómo hacer algo. "
            f"Si el usuario pregunta por algo fuera de sus permisos, indícale amablemente "
            f"que esa función no está disponible para su rol.\n\n"
            f"FUNCIONES DISPONIBLES PARA ESTE USUARIO:\n\n"
            f"{funciones_str}"
            f"{contexto_str}\n\n"
            f"REGLAS ESTRICTAS:\n"
            f"1. NUNCA menciones ni repitas datos personales de huéspedes, DNIs, emails ni códigos de reserva específicos.\n"
            f"2. NUNCA inventes funciones que no estén en la lista de funciones disponibles del usuario.\n"
            f"3. Si no sabes algo, di que no tienes esa información y sugiere contactar al administrador.\n"
            f"4. Responde siempre en español.\n"
            f"5. Sé conciso: máximo 3-4 oraciones por respuesta salvo que el usuario pida detalle."
        )

        # ── Construir historial para la API ───────────────────────────────────
        contents = [
            types.Content(
                role=msg["role"],
                parts=[types.Part(text=msg["text"])]
            ) for msg in historial
        ]
        
        # Añadir el mensaje actual
        contents.append(
            types.Content(
                role="user",
                parts=[types.Part(text=mensaje_usuario)]
            )
        )

        try:
            client = cls._get_client()
            model_name = os.getenv('GEMINI_MODEL', 'gemini-3.1-flash-lite')
            print(f">>> MODELO USADO: {model_name}")
            config = types.GenerateContentConfig(
                temperature=0.3,
                system_instruction=system_instruction,
            )

            response = client.models.generate_content(
                model=model_name,
                contents=contents,
                config=config
            )
            return response.text

        except Exception as e:
            logger.error(f"Error en asistente_staff: {str(e)}")
            raise e