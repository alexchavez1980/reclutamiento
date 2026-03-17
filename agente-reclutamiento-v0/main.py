# ============================================================
# main.py — Orquestador principal del sistema
# NOTA: Este archivo NO tenía .pyc en __pycache__, fue
# reconstruido a partir de la lógica de los demás módulos,
# el .env, y el archivos_procesados.json
# ============================================================

import os
import sys
import time
from pathlib import Path

from config import config
from file_manager import ProcessedFilesManager
from pdf_extractor import PDFExtractor
from word_extractor import WordExtractor
from gemini_analyzer import GeminiCVAnalyzer
from excel_exporter import ExcelExporter


# Extensiones soportadas
SUPPORTED_EXTENSIONS = {".pdf", ".doc", ".docx"}


def find_cv_files(source_path: str) -> list:
    """
    Busca todos los archivos de CV soportados en la carpeta fuente.

    Args:
        source_path: Ruta a la carpeta con los CVs

    Returns:
        Lista de rutas absolutas a los archivos
    """
    files = []
    source = Path(source_path)

    for file_path in source.rglob("*"):
        if file_path.is_file() and file_path.suffix.lower() in SUPPORTED_EXTENSIONS:
            files.append(str(file_path))

    return sorted(files)


def extract_text(file_path: str) -> tuple:
    """
    Extrae texto de un archivo según su extensión.

    Args:
        file_path: Ruta al archivo

    Returns:
        Tuple[éxito: bool, texto: str, es_imagen: bool, extensión: str]
    """
    ext = Path(file_path).suffix.lower()

    if ext == ".pdf":
        extractor = PDFExtractor(file_path)
        success, content = extractor.extract()
        return success, content, extractor.is_image_based, ext

    elif ext in (".doc", ".docx"):
        extractor = WordExtractor(file_path)
        success, content = extractor.extract()
        return success, content, False, ext

    else:
        return False, f"Extensión no soportada: {ext}", False, ext


def process_single_cv(
    file_path: str,
    analyzer: GeminiCVAnalyzer,
    file_manager: ProcessedFilesManager,
) -> list:
    """
    Procesa un único archivo de CV.

    Args:
        file_path: Ruta al archivo
        analyzer: Instancia del analizador Gemini
        file_manager: Gestor de archivos procesados

    Returns:
        Lista de registros extraídos
    """
    filename = Path(file_path).name
    print(f"\n📄 Procesando: {filename}")

    # 1. Extraer texto
    success, content, is_image_based, extension = extract_text(file_path)

    if not success:
        print(f"   ❌ Error extrayendo texto: {content}")
        record = analyzer.create_empty_record()
        record["Archivo"] = filename
        record["Extensión"] = extension
        record["Estado"] = "Error"
        record["Observaciones"] = content
        file_manager.mark_as_processed(file_path, success=False, candidates_count=0)
        return [record]

    # 2. Analizar con Gemini
    if is_image_based:
        print("   🖼️  PDF basado en imagen — usando OCR visual...")
        pdf_extractor = PDFExtractor(file_path)
        images = pdf_extractor.get_pages_as_images()
        if images:
            candidates, error = analyzer.analyze_images(images)
        else:
            candidates, error = None, "No se pudieron generar imágenes del PDF"
    else:
        if not content or len(content.strip()) < 10:
            print("   ⚠️  Contenido insuficiente para análisis")
            record = analyzer.create_empty_record()
            record["Archivo"] = filename
            record["Extensión"] = extension
            record["Estado"] = "Sin contenido"
            record["Observaciones"] = "El archivo no contiene texto suficiente"
            file_manager.mark_as_processed(file_path, success=False, candidates_count=0)
            return [record]

        candidates, error = analyzer.analyze_text(content)

    # 3. Procesar resultados
    if candidates:
        records = []
        for candidate in candidates:
            record = analyzer.create_empty_record()
            record["Archivo"] = filename
            record["Extensión"] = extension
            record["Estado"] = "OK"
            record["Observaciones"] = ""

            # Mapear campos del JSON de Gemini al registro
            for key, value in candidate.items():
                if key in record:
                    record[key] = value

            records.append(record)

        print(f"   ✅ {len(records)} candidato(s) extraído(s)")
        file_manager.mark_as_processed(
            file_path, success=True, candidates_count=len(records)
        )
        return records
    else:
        print(f"   ❌ Error: {error}")
        record = analyzer.create_empty_record()
        record["Archivo"] = filename
        record["Extensión"] = extension
        record["Estado"] = "Error Gemini"
        record["Observaciones"] = error or "Error desconocido"
        file_manager.mark_as_processed(file_path, success=False, candidates_count=0)
        return [record]


def main():
    """Función principal del sistema de extracción de CVs"""
    print("=" * 60)
    print("  🤖 Sistema de Extracción Automatizada de CVs")
    print("=" * 60)

    # Validar configuración
    if not config.validate():
        print("\n❌ Configuración inválida. Revisa el archivo .env")
        sys.exit(1)

    print(f"\n📁 Carpeta de CVs: {config.CV_SOURCE_PATH}")
    print(f"📊 Archivo de salida: {config.OUTPUT_FILE}")
    print(f"🧠 Modelo: {config.GEMINI_MODEL}")

    # Inicializar componentes
    file_manager = ProcessedFilesManager()
    analyzer = GeminiCVAnalyzer()
    exporter = ExcelExporter()

    # Buscar archivos
    all_files = find_cv_files(config.CV_SOURCE_PATH)
    print(f"\n📋 Total de archivos encontrados: {len(all_files)}")

    # Filtrar solo nuevos
    new_files = file_manager.get_new_files(all_files)
    print(f"🆕 Archivos nuevos a procesar: {len(new_files)}")

    if not new_files:
        print("\n✅ No hay archivos nuevos para procesar.")
        stats = file_manager.get_stats()
        print(f"   Estadísticas: {stats['total']} procesados, "
              f"{stats['successful']} exitosos, "
              f"{stats['total_candidates']} candidatos extraídos")
        return

    # Procesar cada archivo
    all_records = []
    total = len(new_files)

    for i, file_path in enumerate(new_files, 1):
        print(f"\n{'─' * 40}")
        print(f"  [{i}/{total}]")

        try:
            records = process_single_cv(file_path, analyzer, file_manager)
            all_records.extend(records)
        except Exception as e:
            print(f"   💥 Error inesperado: {e}")
            record = analyzer.create_empty_record()
            record["Archivo"] = Path(file_path).name
            record["Extensión"] = Path(file_path).suffix.lower()
            record["Estado"] = "Error Fatal"
            record["Observaciones"] = str(e)
            all_records.append(record)
            file_manager.mark_as_processed(file_path, success=False, candidates_count=0)

        # Pausa entre llamadas a la API para evitar rate limiting
        if i < total:
            time.sleep(1)

    # Exportar resultados
    print(f"\n{'=' * 40}")
    print(f"  📊 Exportando {len(all_records)} registros...")

    success = exporter.export(all_records, append=True)

    # Estadísticas finales
    print(f"\n{'=' * 60}")
    print("  📈 RESUMEN FINAL")
    print(f"{'=' * 60}")
    stats = file_manager.get_stats()
    print(f"  Total procesados: {stats['total']}")
    print(f"  Exitosos: {stats['successful']}")
    print(f"  Fallidos: {stats['failed']}")
    print(f"  Candidatos extraídos: {stats['total_candidates']}")
    print(f"  Registros en Excel: {exporter.get_current_count()}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
