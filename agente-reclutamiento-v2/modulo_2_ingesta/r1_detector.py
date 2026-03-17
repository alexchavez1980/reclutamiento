"""
Responsabilidad 1 — Detección de nuevos CVs por Email

Dos backends:
  - "graph" → Microsoft Graph API con OAuth2 (recomendado)
  - "imap"  → IMAP/SSL con Basic Auth (fallback legacy)

Seleccionar con la variable de entorno EMAIL_METHOD (default: graph).
"""

import imaplib
import email as email_lib
from email.header import decode_header
import os
import logging
from pathlib import Path

import requests

from config import (
    EMAIL_METHOD,
    INBOX_DIR,
    VALID_EXTENSIONS,
    GRAPH_API_BASE,
    IMAP_SERVER,
    IMAP_PORT,
    EMAIL_USER,
    EMAIL_PASS,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger("r1_detector")


# ──────────────────────────────────────────────
#  Utilidades comunes
# ──────────────────────────────────────────────

def _safe_filename(name: str, dest_dir: str) -> str:
    """Nombre seguro sin colisiones. 'CV.pdf' → 'CV (1).pdf' si ya existe."""
    name = name.replace("/", "_").replace("\\", "_").replace("\x00", "")
    path = Path(dest_dir) / name
    if not path.exists():
        return str(path)
    stem, suffix = path.stem, path.suffix
    counter = 1
    while True:
        candidate = Path(dest_dir) / f"{stem} ({counter}){suffix}"
        if not candidate.exists():
            return str(candidate)
        counter += 1


def _is_valid_cv(filename: str) -> bool:
    return Path(filename).suffix.lower() in VALID_EXTENSIONS


# ──────────────────────────────────────────────
#  Backend: Microsoft Graph API (OAuth2)
# ──────────────────────────────────────────────

def _graph_run() -> dict:
    from graph_auth import get_access_token

    token = get_access_token()
    headers = {"Authorization": f"Bearer {token}"}
    summary = {"emails_leidos": 0, "adjuntos_descargados": 0, "errores": 0}

    # Obtener emails no leídos con adjuntos
    url = (
        f"{GRAPH_API_BASE}/me/messages"
        "?$filter=isRead eq false and hasAttachments eq true"
        "&$select=id,subject,from"
        "&$top=50"
        "&$orderby=receivedDateTime desc"
    )

    response = requests.get(url, headers=headers)
    response.raise_for_status()
    messages = response.json().get("value", [])

    log.info("Emails no leídos con adjuntos: %d", len(messages))

    for msg in messages:
        msg_id = msg["id"]
        subject = msg.get("subject", "(sin asunto)")
        sender = msg.get("from", {}).get("emailAddress", {}).get("address", "?")
        log.info("── Email: '%s'  de: %s", subject, sender)

        try:
            att_url = f"{GRAPH_API_BASE}/me/messages/{msg_id}/attachments"
            att_resp = requests.get(att_url, headers=headers)
            att_resp.raise_for_status()
            attachments = att_resp.json().get("value", [])

            downloaded = 0
            for att in attachments:
                filename = att.get("name", "")
                if not _is_valid_cv(filename):
                    log.info("   Adjunto ignorado (%s): %s",
                             Path(filename).suffix.lower(), filename)
                    continue

                content_bytes = att.get("contentBytes")
                if not content_bytes:
                    log.warning("   Adjunto sin contenido: %s", filename)
                    continue

                import base64
                data = base64.b64decode(content_bytes)
                dest_path = _safe_filename(filename, INBOX_DIR)

                with open(dest_path, "wb") as f:
                    f.write(data)

                log.info("   ✅ Descargado: %s (%d bytes)",
                         os.path.basename(dest_path), len(data))
                downloaded += 1

            if downloaded == 0:
                log.info("   Sin adjuntos válidos — email ignorado.")

            summary["emails_leidos"] += 1
            summary["adjuntos_descargados"] += downloaded

        except Exception:
            summary["errores"] += 1
            log.exception("Error procesando email '%s'", subject)

    return summary


# ──────────────────────────────────────────────
#  Backend: IMAP Basic Auth (fallback)
# ──────────────────────────────────────────────

def _decode_header_value(raw: str | None) -> str:
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


def _imap_run() -> dict:
    if not EMAIL_USER or not EMAIL_PASS:
        raise RuntimeError("EMAIL_USER y EMAIL_PASS no configurados.")

    summary = {"emails_leidos": 0, "adjuntos_descargados": 0, "errores": 0}
    conn = None

    try:
        log.info("Conectando via IMAP a %s:%d como %s …",
                 IMAP_SERVER, IMAP_PORT, EMAIL_USER)
        conn = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
        conn.login(EMAIL_USER, EMAIL_PASS)
        log.info("Autenticación IMAP exitosa.")

        conn.select("INBOX")
        status, data = conn.search(None, "UNSEEN")
        if status != "OK":
            log.warning("Búsqueda UNSEEN devolvió status: %s", status)
            return summary

        msg_ids = data[0].split()
        log.info("Emails no leídos: %d", len(msg_ids))

        for msg_id in msg_ids:
            try:
                status, msg_data = conn.fetch(msg_id, "(RFC822)")
                if status != "OK":
                    summary["errores"] += 1
                    continue

                raw = msg_data[0][1]
                msg = email_lib.message_from_bytes(raw)
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
                    if not _is_valid_cv(filename):
                        log.info("   Adjunto ignorado (%s): %s",
                                 Path(filename).suffix.lower(), filename)
                        continue

                    payload = part.get_payload(decode=True)
                    if payload is None:
                        log.warning("   Adjunto vacío: %s", filename)
                        continue

                    dest_path = _safe_filename(filename, INBOX_DIR)
                    with open(dest_path, "wb") as f:
                        f.write(payload)

                    log.info("   ✅ Descargado: %s (%d bytes)",
                             os.path.basename(dest_path), len(payload))
                    downloaded += 1

                if downloaded == 0:
                    log.info("   Sin adjuntos válidos — email ignorado.")

                summary["emails_leidos"] += 1
                summary["adjuntos_descargados"] += downloaded

            except Exception:
                summary["errores"] += 1
                log.exception("Error procesando email ID %s", msg_id.decode())

    except Exception:
        log.exception("Error fatal en conexión IMAP")
        raise
    finally:
        if conn:
            try:
                conn.close()
                conn.logout()
            except Exception:
                pass

    return summary


# ──────────────────────────────────────────────
#  Punto de entrada
# ──────────────────────────────────────────────

def run() -> dict:
    """
    Ejecuta R1: detectar emails no leídos → descargar adjuntos CV.
    El backend se elige con la variable EMAIL_METHOD ('graph' o 'imap').
    """
    os.makedirs(INBOX_DIR, exist_ok=True)
    log.info("Método de conexión: %s", EMAIL_METHOD)

    if EMAIL_METHOD == "graph":
        summary = _graph_run()
    elif EMAIL_METHOD == "imap":
        summary = _imap_run()
    else:
        raise ValueError(f"EMAIL_METHOD no válido: '{EMAIL_METHOD}'. Usar 'graph' o 'imap'.")

    log.info(
        "Resumen: %d emails, %d adjuntos descargados, %d errores",
        summary["emails_leidos"],
        summary["adjuntos_descargados"],
        summary["errores"],
    )
    return summary


if __name__ == "__main__":
    run()
