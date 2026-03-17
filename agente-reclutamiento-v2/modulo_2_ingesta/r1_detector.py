"""
Responsabilidad 1 — Detección de nuevos CVs por Email (IMAP)

Conecta a Outlook vía IMAP/SSL, lee emails no leídos,
descarga adjuntos .pdf/.doc/.docx en la carpeta inbox/.
"""

import imaplib
import email
from email.header import decode_header
import os
import logging
from pathlib import Path

from config import (
    IMAP_SERVER,
    IMAP_PORT,
    INBOX_DIR,
    VALID_EXTENSIONS,
    EMAIL_USER,
    EMAIL_PASS,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger("r1_detector")


def _decode_header_value(raw: str | None) -> str:
    """Decodifica un header MIME que puede tener encoding RFC 2047."""
    if raw is None:
        return "(sin asunto)"
    parts = decode_header(raw)
    decoded = []
    for fragment, charset in parts:
        if isinstance(fragment, bytes):
            decoded.append(fragment.decode(charset or "utf-8", errors="replace"))
        else:
            decoded.append(fragment)
    return "".join(decoded)


def _safe_filename(name: str, dest_dir: str) -> str:
    """
    Genera un nombre de archivo seguro y sin colisiones.
    Si 'CV - Juan.pdf' ya existe, produce 'CV - Juan (1).pdf', etc.
    """
    name = name.replace("/", "_").replace("\\", "_").replace("\x00", "")
    path = Path(dest_dir) / name
    if not path.exists():
        return str(path)

    stem = path.stem
    suffix = path.suffix
    counter = 1
    while True:
        candidate = Path(dest_dir) / f"{stem} ({counter}){suffix}"
        if not candidate.exists():
            return str(candidate)
        counter += 1


def _connect() -> imaplib.IMAP4_SSL:
    """Establece conexión IMAP autenticada contra Outlook."""
    if not EMAIL_USER or not EMAIL_PASS:
        raise RuntimeError(
            "Variables de entorno EMAIL_USER y EMAIL_PASS no configuradas."
        )

    log.info("Conectando a %s:%d como %s …", IMAP_SERVER, IMAP_PORT, EMAIL_USER)
    conn = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
    conn.login(EMAIL_USER, EMAIL_PASS)
    log.info("Autenticación exitosa.")
    return conn


def _fetch_unseen_ids(conn: imaplib.IMAP4_SSL) -> list[bytes]:
    """Selecciona INBOX y devuelve los IDs de emails no leídos."""
    conn.select("INBOX")
    status, data = conn.search(None, "UNSEEN")
    if status != "OK":
        log.warning("Búsqueda UNSEEN devolvió status: %s", status)
        return []

    ids = data[0].split()
    log.info("Emails no leídos encontrados: %d", len(ids))
    return ids


def _process_email(conn: imaplib.IMAP4_SSL, msg_id: bytes) -> int:
    """
    Descarga y procesa un email individual.
    Retorna la cantidad de adjuntos válidos descargados.
    """
    status, msg_data = conn.fetch(msg_id, "(RFC822)")
    if status != "OK":
        log.error("No se pudo obtener el email ID %s", msg_id.decode())
        return 0

    raw = msg_data[0][1]
    msg = email.message_from_bytes(raw)

    subject = _decode_header_value(msg.get("Subject"))
    sender = _decode_header_value(msg.get("From"))
    log.info("── Email: '%s'  de: %s", subject, sender)

    downloaded = 0

    for part in msg.walk():
        if part.get_content_maintype() == "multipart":
            continue

        raw_filename = part.get_filename()
        if raw_filename is None:
            continue

        filename = _decode_header_value(raw_filename)
        ext = Path(filename).suffix.lower()

        if ext not in VALID_EXTENSIONS:
            log.info("   Adjunto ignorado (extensión %s): %s", ext, filename)
            continue

        payload = part.get_payload(decode=True)
        if payload is None:
            log.warning("   Adjunto vacío: %s", filename)
            continue

        dest_path = _safe_filename(filename, INBOX_DIR)
        with open(dest_path, "wb") as f:
            f.write(payload)

        log.info("   ✅ Descargado: %s (%d bytes)", os.path.basename(dest_path), len(payload))
        downloaded += 1

    if downloaded == 0:
        log.info("   Sin adjuntos válidos — email ignorado.")

    return downloaded


def run() -> dict:
    """
    Ejecuta el ciclo completo de detección:
    conectar → buscar no leídos → descargar adjuntos → desconectar.

    Retorna un resumen con totales.
    """
    os.makedirs(INBOX_DIR, exist_ok=True)

    summary = {"emails_leidos": 0, "adjuntos_descargados": 0, "errores": 0}
    conn = None

    try:
        conn = _connect()
        msg_ids = _fetch_unseen_ids(conn)

        for msg_id in msg_ids:
            try:
                count = _process_email(conn, msg_id)
                summary["emails_leidos"] += 1
                summary["adjuntos_descargados"] += count
            except Exception:
                summary["errores"] += 1
                log.exception("Error procesando email ID %s", msg_id.decode())

    except Exception:
        log.exception("Error fatal en la conexión IMAP")
        raise
    finally:
        if conn:
            try:
                conn.close()
                conn.logout()
            except Exception:
                pass

    log.info(
        "Resumen: %d emails leídos, %d adjuntos descargados, %d errores",
        summary["emails_leidos"],
        summary["adjuntos_descargados"],
        summary["errores"],
    )
    return summary


if __name__ == "__main__":
    run()
