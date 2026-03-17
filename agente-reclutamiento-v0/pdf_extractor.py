# ============================================================
# pdf_extractor.py — Extractor de texto de archivos PDF
# Reconstruido desde bytecode (cpython-311.pyc)
# Fuente original: G:\Mi unidad\Alex\Trabajo\24-Hoy-Datastar\IA\reclutamiento\pdf_extractor.py
# Compilado: 2026-02-04 10:35:45
# ============================================================

import pdfplumber
from pathlib import Path
from typing import Tuple, List, Optional
from PIL import Image
import io


class PDFExtractor:
    """
    Clase para extraer texto de archivos PDF.
    Detecta si el PDF contiene texto digital o es una imagen escaneada.
    """

    MIN_TEXT_LENGTH = 50

    def __init__(self, pdf_path: str):
        self.pdf_path = Path(pdf_path)
        self.text_content: str = ""
        self.pages_as_images: List[Image.Image] = []
        self.is_image_based: bool = False
        self.page_count: int = 0
        self.error: str = ""

    def extract(self) -> Tuple[bool, str]:
        """
        Intenta extraer texto del PDF.

        Returns:
            Tuple[bool, str]: (éxito, texto_o_mensaje_error)
        """
        try:
            with pdfplumber.open(self.pdf_path) as pdf:
                self.page_count = len(pdf.pages)
                all_text = []

                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        all_text.append(page_text)

                self.text_content = "\n\n".join(all_text).strip()

                if len(self.text_content) < self.MIN_TEXT_LENGTH:
                    self.is_image_based = True
                    return True, self.text_content

                return True, self.text_content

        except Exception as e:
            self.error = str(e)
            return False, f"ERROR: No se pudo abrir el PDF - {e}"

    def get_pages_as_images(self, dpi: int = 150) -> List[Image.Image]:
        """
        Convierte las páginas del PDF en imágenes para OCR visual.

        Args:
            dpi: Resolución de las imágenes generadas

        Returns:
            Lista de objetos PIL.Image
        """
        images = []
        try:
            with pdfplumber.open(self.pdf_path) as pdf:
                for page in pdf.pages:
                    img = page.to_image(resolution=dpi)
                    pil_img = img.original
                    images.append(pil_img)

            self.pages_as_images = images
        except Exception as e:
            self.error = str(e)

        return images

    def get_image_bytes(self, image: Image.Image, format: str = "PNG") -> bytes:
        """
        Convierte una imagen PIL a bytes para enviar a Gemini.

        Args:
            image: Imagen PIL
            format: Formato de imagen (PNG, JPEG)

        Returns:
            Bytes de la imagen
        """
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format=format)
        img_byte_arr.seek(0)
        return img_byte_arr.getvalue()


def extract_text_from_pdf(pdf_path: str) -> Tuple[bool, str, bool]:
    """
    Función de conveniencia para extraer texto de un PDF.

    Args:
        pdf_path: Ruta al archivo PDF

    Returns:
        Tuple[bool, str, bool]: (éxito, contenido, es_imagen)
    """
    extractor = PDFExtractor(pdf_path)
    success, content = extractor.extract()
    return success, content, extractor.is_image_based
