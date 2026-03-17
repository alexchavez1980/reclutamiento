# ============================================================
# word_extractor.py — Extractor de texto de archivos Word
# Reconstruido desde bytecode (cpython-311.pyc)
# Fuente original: G:\Mi unidad\Alex\Trabajo\24-Hoy-Datastar\IA\reclutamiento\word_extractor.py
# Compilado: 2026-02-04 16:40:11
# ============================================================

import os
from pathlib import Path
from typing import Tuple, Optional
import docx
import win32com.client
import pythoncom


class WordExtractor:
    """
    Clase para extraer texto de archivos Word.
    Soporta .docx (vía python-docx) y .doc (vía win32com).
    """

    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        self.extension = self.file_path.suffix.lower()

    def extract(self) -> Tuple[bool, str]:
        """
        Extrae el texto del archivo según su extensión.

        Returns:
            Tuple[éxito (bool), contenido o mensaje de error (str)]
        """
        if not self.file_path.exists():
            return False, f"El archivo no existe: {self.file_path}"

        if self.extension == ".docx":
            return self._extract_docx()
        elif self.extension == ".doc":
            return self._extract_doc()
        else:
            return False, f"Extensión no soportada por WordExtractor: {self.extension}"

    def _extract_docx(self) -> Tuple[bool, str]:
        """Extrae texto de archivos .docx usando python-docx"""
        try:
            doc = docx.Document(self.file_path)
            full_text = []
            for para in doc.paragraphs:
                full_text.append(para.text)
            content = "\n".join(full_text).strip()
            return True, content
        except Exception as e:
            return False, f"Error leyendo .docx: {str(e)}"

    def _extract_doc(self) -> Tuple[bool, str]:
        """Extrae texto de archivos .doc usando win32com (requiere Word instalado)"""
        word = None
        try:
            pythoncom.CoInitialize()
            word = win32com.client.Dispatch("Word.Application")
            word.Visible = False
            abs_path = str(self.file_path.absolute())
            doc = word.Documents.Open(abs_path)
            content = doc.Content.Text
            doc.Close(False)
            word.Quit()
            content = content.replace("\r", "\n").strip()
            return True, content
        except Exception as e:
            return False, f"Error leyendo .doc (Asegúrate de tener Word instalado): {str(e)}"
        finally:
            pythoncom.CoUninitialize()
