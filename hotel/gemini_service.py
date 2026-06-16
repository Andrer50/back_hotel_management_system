import os
import logging
from typing import Any, Dict, List, Optional, Type
import google.generativeai as genai
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
    def _get_model(cls, system_instruction: Optional[str] = None, response_schema: Optional[Type[BaseModel]] = None) -> genai.GenerativeModel:
        """Configura e inicializa el modelo de Gemini."""
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key or api_key == "your_gemini_api_key_here":
            raise ValueError(
                "La clave GEMINI_API_KEY no está configurada o contiene el valor predeterminado. "
                "Por favor, agrégala en tu archivo .env para habilitar este servicio."
            )
        
        genai.configure(api_key=api_key)
        model_name = os.getenv('GEMINI_MODEL', 'gemini-1.5-flash')
        
        config = {}
        if response_schema:
            config["response_mime_type"] = "application/json"
            config["response_schema"] = response_schema
            
        return genai.GenerativeModel(
            model_name=model_name,
            generation_config=config if config else None,
            system_instruction=system_instruction
        )

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
            model = cls._get_model(system_instruction, response_schema)
            generation_config = {}
            if response_schema:
                generation_config["response_mime_type"] = "application/json"
                generation_config["response_schema"] = response_schema
            if temperature is not None:
                generation_config["temperature"] = temperature
                
            response = model.generate_content(
                prompt,
                generation_config=generation_config if generation_config else None
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
