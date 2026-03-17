import os

IMAP_SERVER = "outlook.office365.com"
IMAP_PORT = 993
IMAP_USE_SSL = True

INBOX_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "inbox")
VALID_EXTENSIONS = {".pdf", ".doc", ".docx"}

EMAIL_USER = os.environ.get("EMAIL_USER", "")
EMAIL_PASS = os.environ.get("EMAIL_PASS", "")
