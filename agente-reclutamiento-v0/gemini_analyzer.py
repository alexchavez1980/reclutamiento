# ============================================================
# gemini_analyzer.py — Analizador de CVs con Google Gemini
# Reconstruido desde bytecode (cpython-311.pyc)
# Fuente original: G:\Mi unidad\Alex\Trabajo\24-Hoy-Datastar\IA\reclutamiento\gemini_analyzer.py
# Compilado: 2026-02-04 13:17:17
# ============================================================

from google import genai
from google.genai import types
from typing import Dict, List, Optional, Tuple
from PIL import Image
import json
import io

from config import config


class GeminiCVAnalyzer:
    """
    Clase para analizar CVs usando Google Gemini 2.0 Flash.
    Soporta tanto texto digital como OCR visual de imágenes.
    Usa el nuevo SDK google-genai.
    """

    def __init__(self):
        self.client = genai.Client(api_key=config.GEMINI_API_KEY)
        self.model_name = config.GEMINI_MODEL
        self.generation_config = types.GenerateContentConfig(
            temperature=config.TEMPERATURE,
            top_p=config.TOP_P,
            top_k=config.TOP_K,
            max_output_tokens=8192,
        )

    def _build_extraction_prompt(self, text_content: str) -> str:
        """
        Construye el prompt para extracción de datos del CV.

        Args:
            text_content: Texto del CV

        Returns:
            Prompt formateado
        """
        return (
            'Eres un experto en análisis de Recursos Humanos. Analiza el siguiente currículum y extrae la información en formato JSON estricto.\n\n'
            'INSTRUCCIONES CRÍTICAS:\n'
            '1. Responde ÚNICAMENTE con un JSON válido, sin texto adicional.\n'
            '2. Si algún dato no está disponible o no se puede inferir, usa "N/A".\n'
            '3. NUNCA inventes datos. Solo extrae lo que está presente.\n'
            '4. Si hay múltiples candidatos en el documento, devuelve un array de objetos.\n\n'
            'CAMPOS A EXTRAER:\n'
            '{\n'
            '  "Nombre": "Primer nombre (sin títulos)",\n'
            '  "Apellido": "Apellido(s)",\n'
            '  "Email": "Correo electrónico personal más relevante",\n'
            '  "Teléfono": "Número de teléfono limpio, sin texto extra",\n'
            '  "Educación": "Resumen de estudios: tipo, institución, período. Máximo 2-3 líneas",\n'
            '  "Idiomas": "Lista de idiomas con nivel. Ej: \'Español (nativo), Inglés (avanzado B2)\'",\n'
            '  "Trabajo más reciente": "Cargo, empresa, funciones principales. Máximo 2 líneas",\n'
            '  "Crecimiento": "Evolución profesional: de dónde viene y hacia dónde ha progresado. Máximo 2 líneas",\n'
            '  "Contradicciones": "Inconsistencias encontradas (fechas superpuestas, brechas inexplicadas, etc.) o \'N/A\'",\n'
            '  "Herramientas": "Tecnologías/software mencionados CON CONTEXTO de uso. No listas simples"\n'
            '}\n\n'
            'CONTENIDO DEL CV:\n'
            '---\n'
            f'{text_content}\n'
            '---\n\n'
            'Responde SOLO con el JSON:'
        )

    def _build_ocr_prompt(self) -> str:
        """
        Construye el prompt para OCR visual + extracción.

        Returns:
            Prompt formateado
        """
        return (
            'Eres un experto en análisis de Recursos Humanos con capacidad de lectura visual.\n\n'
            'TAREA: Observa esta imagen de un CV y extrae TODA la información visible. Luego estructúrala en JSON.\n\n'
            'INSTRUCCIONES CRÍTICAS:\n'
            '1. Lee cuidadosamente TODO el texto visible en la imagen.\n'
            '2. Responde ÚNICAMENTE con un JSON válido, sin explicaciones.\n'
            '3. Si algún dato no es visible o legible, usa "N/A".\n'
            '4. NUNCA inventes datos. Solo extrae lo que puedes ver.\n\n'
            'CAMPOS A EXTRAER:\n'
            '{\n'
            '  "Nombre": "Primer nombre (sin títulos)",\n'
            '  "Apellido": "Apellido(s)",\n'
            '  "Email": "Correo electrónico personal",\n'
            '  "Teléfono": "Número de teléfono",\n'
            '  "Educación": "Resumen de estudios",\n'
            '  "Idiomas": "Lista de idiomas con nivel",\n'
            '  "Trabajo más reciente": "Cargo, empresa, funciones. Máximo 2 líneas",\n'
            '  "Crecimiento": "Evolución profesional. Máximo 2 líneas",\n'
            '  "Contradicciones": "Inconsistencias encontradas o \'N/A\'",\n'
            '  "Herramientas": "Tecnologías/software CON CONTEXTO de uso"\n'
            '}\n\n'
            'Responde SOLO con el JSON:'
        )

    def _parse_json_response(self, response_text: str) -> List[Dict]:
        """
        Parsea la respuesta JSON de Gemini.

        Args:
            response_text: Texto de respuesta del modelo

        Returns:
            Lista de diccionarios con los datos extraídos
        """
        try:
            cleaned = response_text.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]  # Quita ```json
            if cleaned.startswith("```"):
                cleaned = cleaned[3:]  # Quita ```
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]  # Quita ``` final

            parsed = json.loads(cleaned.strip())

            if isinstance(parsed, dict):
                return [parsed]
            elif isinstance(parsed, list):
                return parsed
            else:
                return []

        except json.JSONDecodeError as e:
            print(f"⚠️  Error parseando JSON: {e}")
            print(f"    Respuesta recibida: {response_text[:200]}...")
            return []

    def _image_to_part(self, image: Image.Image) -> types.Part:
        """
        Convierte una imagen PIL a un Part para el API de Gemini.

        Args:
            image: Imagen PIL

        Returns:
            Part con los datos de la imagen
        """
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format="PNG")
        img_byte_arr.seek(0)
        return types.Part.from_bytes(data=img_byte_arr.getvalue(), mime_type="image/png")

    def analyze_text(self, text_content: str) -> Tuple[Optional[List[Dict]], Optional[str]]:
        """
        Analiza el texto de un CV y extrae información estructurada.

        Args:
            text_content: Texto del CV

        Returns:
            Tuple[Lista de candidatos, mensaje de error o None]
        """
        try:
            prompt = self._build_extraction_prompt(text_content)
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=self.generation_config,
            )

            if response.text:
                candidates = self._parse_json_response(response.text)
                if candidates:
                    return candidates, None
                else:
                    return None, "Gemini: La respuesta no contenía datos estructurados válidos"
            else:
                return None, "Gemini: El modelo no devolvió respuesta para este documento"

        except Exception as e:
            error_str = str(e)
            print(f"⚠️ Error en análisis con Gemini: {error_str[:100]}")

            if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
                return None, "Gemini: Límite de cuota de API alcanzado (Error 429). Intentar más tarde."
            elif "404" in error_str:
                return None, "Gemini: Modelo no encontrado. Verificar configuración."
            elif "400" in error_str:
                return None, "Gemini: Solicitud inválida. El contenido puede ser demasiado largo o contener caracteres no soportados."
            else:
                return None, f"Gemini: Error de API - {error_str}"

    def analyze_images(self, images: List[Image.Image]) -> Tuple[Optional[List[Dict]], Optional[str]]:
        """
        Analiza imágenes de un CV usando OCR visual de Gemini.

        Args:
            images: Lista de imágenes PIL de las páginas del CV

        Returns:
            Tuple[Lista de candidatos, mensaje de error o None]
        """
        if not images:
            return None, "No hay imágenes para analizar"

        try:
            contents = [self._build_ocr_prompt()]
            for img in images:
                contents.append(self._image_to_part(img))

            response = self.client.models.generate_content(
                model=self.model_name,
                contents=contents,
                config=self.generation_config,
            )

            if response.text:
                candidates = self._parse_json_response(response.text)
                if candidates:
                    return candidates, None
                else:
                    return None, (
                        "OCR Gemini: No se pudo extraer información estructurada de las imágenes. "
                        "El documento puede contener texto ilegible o formato no reconocible."
                    )
            else:
                return None, "OCR Gemini: El modelo no devolvió respuesta para las imágenes del documento"

        except Exception as e:
            error_str = str(e)
            print(f"⚠️ Error en OCR con Gemini: {error_str[:100]}")

            if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
                return None, "Gemini OCR: Límite de cuota de API alcanzado (Error 429). Intentar más tarde."
            else:
                return None, f"Gemini OCR: Error de API - {error_str}"

    def create_empty_record(self) -> Dict:
        """
        Crea un registro vacío con todos los campos en N/A.

        Returns:
            Diccionario con campos vacíos
        """
        return {col: "N/A" for col in config.COLUMNS}


def get_analyzer() -> GeminiCVAnalyzer:
    """Obtiene una instancia del analizador Gemini"""
    return GeminiCVAnalyzer()
