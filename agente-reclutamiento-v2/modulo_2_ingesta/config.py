import os

# ──────────────────────────────────────────────
# Carpeta de destino
# ──────────────────────────────────────────────
INBOX_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "inbox")
VALID_EXTENSIONS = {".pdf", ".doc", ".docx"}

# ──────────────────────────────────────────────
# Método de conexión: "graph" (OAuth2) o "imap" (Basic Auth)
# ──────────────────────────────────────────────
EMAIL_METHOD = os.environ.get("EMAIL_METHOD", "graph")

# ──────────────────────────────────────────────
# Microsoft Graph — OAuth2 (método recomendado)
# ──────────────────────────────────────────────
# Obtener de Azure Portal → Entra ID → App Registrations
GRAPH_CLIENT_ID = os.environ.get("GRAPH_CLIENT_ID", "")
GRAPH_TENANT_ID = os.environ.get("GRAPH_TENANT_ID", "common")
GRAPH_SCOPES = ["Mail.Read"]
GRAPH_TOKEN_CACHE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), ".token_cache.json"
)
GRAPH_API_BASE = "https://graph.microsoft.com/v1.0"

# ──────────────────────────────────────────────
# IMAP — Basic Auth (fallback / entornos legacy)
# ──────────────────────────────────────────────
IMAP_SERVER = "outlook.office365.com"
IMAP_PORT = 993
EMAIL_USER = os.environ.get("EMAIL_USER", "")
EMAIL_PASS = os.environ.get("EMAIL_PASS", "")
