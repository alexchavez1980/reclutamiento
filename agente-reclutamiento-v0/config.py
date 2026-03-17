# ============================================================
# config.py — Configuración centralizada del sistema
# Reconstruido desde bytecode (cpython-311.pyc)
# Fuente original: G:\Mi unidad\Alex\Trabajo\24-Hoy-Datastar\IA\reclutamiento\config.py
# Compilado: 2026-02-04 16:40:01
# ============================================================

import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Config:
    """Configuración centralizada del sistema de extracción de CVs"""

    CV_SOURCE_PATH: str = os.getenv(
        "CV_SOURCE_PATH",
        r"C:\Users\achavez\DATASTAR ARGENTINA SA\share01 - CVs\Ciberseguridad",
    )
    OUTPUT_FILE: str = os.getenv("OUTPUT_FILE", "resumen_reclutamiento.xlsx")
    PROCESSED_LOG: str = os.getenv("PROCESSED_LOG", "archivos_procesados.json")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
    TEMPERATURE: float = float(os.getenv("GEMINI_TEMPERATURE", "0.1"))
    TOP_K: int = int(os.getenv("GEMINI_TOP_K", "20"))
    TOP_P: float = float(os.getenv("GEMINI_TOP_P", "0.9"))
    COLUMNS: list = None

    def __post_init__(self):
        self.COLUMNS = [
            "Archivo",
            "Extensión",
            "Nombre",
            "Apellido",
            "Email",
            "Teléfono",
            "Educación",
            "Idiomas",
            "Trabajo más reciente",
            "Crecimiento",
            "Contradicciones",
            "Herramientas",
            "Estado",
            "Observaciones",
        ]

    def validate(self) -> bool:
        """Valida que la configuración sea correcta"""
        errors = []

        if not self.GEMINI_API_KEY or self.GEMINI_API_KEY == "tu_api_key_aqui":
            errors.append("⚠️ GEMINI_API_KEY no configurada en .env")

        if not os.path.exists(self.CV_SOURCE_PATH):
            errors.append(f"⚠️ Carpeta de CVs no encontrada: {self.CV_SOURCE_PATH}")

        for error in errors:
            print(error)

        return len(errors) == 0


config = Config()
