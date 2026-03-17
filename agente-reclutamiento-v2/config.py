# ============================================================
# config.py — Configuración mínima para conexión a Gemini
# Migrado desde agente-reclutamiento-v0
# ============================================================

import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Config:
    """Configuración del agente de reclutamiento v2"""

    # --- Conexión a Gemini (estrictamente necesario) ---
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
    TEMPERATURE: float = float(os.getenv("GEMINI_TEMPERATURE", "0.1"))
    TOP_K: int = int(os.getenv("GEMINI_TOP_K", "20"))
    TOP_P: float = float(os.getenv("GEMINI_TOP_P", "0.9"))

    def validate(self) -> bool:
        """Valida que la conexión a Gemini sea posible"""
        if not self.GEMINI_API_KEY or self.GEMINI_API_KEY == "tu_api_key_aqui":
            print("⚠️ GEMINI_API_KEY no configurada en .env")
            return False
        return True


config = Config()
