# ============================================================
# file_manager.py — Gestor de archivos procesados
# Reconstruido desde bytecode (cpython-311.pyc)
# Fuente original: G:\Mi unidad\Alex\Trabajo\24-Hoy-Datastar\IA\reclutamiento\file_manager.py
# Compilado: 2026-02-04 10:36:48
# ============================================================

import json
import os
from pathlib import Path
from typing import Set, Dict, List
from datetime import datetime
import hashlib

from config import config


class ProcessedFilesManager:
    """
    Gestiona el registro de archivos ya procesados para evitar
    reprocesar CVs en ejecuciones subsecuentes.
    """

    def __init__(self, log_path: str = None):
        self.log_path = Path(log_path or config.PROCESSED_LOG)
        self.processed_files: Dict = {}
        self._load()

    def _load(self):
        """Carga el registro de archivos procesados"""
        if self.log_path.exists():
            try:
                with open(self.log_path, "r", encoding="utf-8") as f:
                    self.processed_files = json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"⚠️  Error cargando registro: {e}. Iniciando vacío.")
                self.processed_files = {}

    def _save(self):
        """Guarda el registro de archivos procesados"""
        try:
            with open(self.log_path, "w", encoding="utf-8") as f:
                json.dump(self.processed_files, f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"⚠️ Error guardando registro: {e}")

    def _get_file_hash(self, file_path: str) -> str:
        """
        Calcula un hash del archivo para detectar modificaciones.
        Usa tamaño + fecha de modificación para eficiencia.
        """
        stat = os.stat(file_path)
        content = f"{stat.st_size}_{stat.st_mtime}"
        return hashlib.md5(content.encode()).hexdigest()

    def is_processed(self, file_path: str) -> bool:
        """
        Verifica si un archivo ya fue procesado.

        Args:
            file_path: Ruta al archivo

        Returns:
            True si ya fue procesado y no ha cambiado
        """
        path = Path(file_path)
        abs_path = str(path.absolute())

        if abs_path not in self.processed_files:
            return False

        current_hash = self._get_file_hash(file_path)
        stored_hash = self.processed_files[abs_path].get("hash", "")

        return current_hash == stored_hash

    def mark_as_processed(self, file_path: str, success: bool, candidates_count: int):
        """
        Marca un archivo como procesado.

        Args:
            file_path: Ruta al archivo
            success: Si el procesamiento fue exitoso
            candidates_count: Número de candidatos extraídos
        """
        path = Path(file_path)
        abs_path = str(path.absolute())

        self.processed_files[abs_path] = {
            "hash": self._get_file_hash(file_path),
            "processed_at": datetime.now().isoformat(),
            "success": success,
            "candidates_extracted": candidates_count,
        }
        self._save()

    def get_new_files(self, all_files: List[str]) -> List[str]:
        """
        Filtra y devuelve solo los archivos nuevos o modificados.

        Args:
            all_files: Lista de todas las rutas de archivos

        Returns:
            Lista de archivos que necesitan procesamiento
        """
        new_files = []
        for file_path in all_files:
            if not self.is_processed(file_path):
                new_files.append(file_path)
        return new_files

    def get_stats(self) -> Dict:
        """
        Obtiene estadísticas del procesamiento.

        Returns:
            Diccionario con estadísticas
        """
        total = len(self.processed_files)
        successful = sum(1 for f in self.processed_files.values() if f.get("success"))
        failed = total - successful
        total_candidates = sum(
            f.get("candidates_extracted", 0)
            for f in self.processed_files.values()
        )

        return {
            "total": total,
            "successful": successful,
            "failed": failed,
            "total_candidates": total_candidates,
        }

    def clear(self):
        """Limpia el registro (usar con precaución)"""
        self.processed_files = {}
        self._save()
        print("🗑️  Registro de archivos procesados limpiado")
