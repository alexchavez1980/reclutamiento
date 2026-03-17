# ============================================================
# gemini_client.py — Cliente de conexión a Google Gemini
# Migrado desde agente-reclutamiento-v0/gemini_analyzer.py
# Solo la conexión, sin lógica de análisis de CVs
# ============================================================

from google import genai
from google.genai import types

from config import config


def get_client() -> genai.Client:
    """Crea y retorna un cliente autenticado de Gemini"""
    return genai.Client(api_key=config.GEMINI_API_KEY)


def get_generation_config() -> types.GenerateContentConfig:
    """Retorna la configuración de generación"""
    return types.GenerateContentConfig(
        temperature=config.TEMPERATURE,
        top_p=config.TOP_P,
        top_k=config.TOP_K,
        max_output_tokens=8192,
    )


def test_connection() -> bool:
    """
    Verifica que la conexión a Gemini funcione correctamente.
    Retorna True si la API responde.
    """
    try:
        client = get_client()
        response = client.models.generate_content(
            model=config.GEMINI_MODEL,
            contents="Responde solo con la palabra OK",
            config=get_generation_config(),
        )
        if response.text:
            print(f"✅ Conexión exitosa a Gemini ({config.GEMINI_MODEL})")
            print(f"   Respuesta: {response.text.strip()}")
            return True
        else:
            print("⚠️ Gemini respondió pero sin contenido")
            return False
    except Exception as e:
        print(f"❌ Error conectando a Gemini: {e}")
        return False


if __name__ == "__main__":
    if config.validate():
        test_connection()
