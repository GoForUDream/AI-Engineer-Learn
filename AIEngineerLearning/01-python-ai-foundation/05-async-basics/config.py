import sys

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")  # type: ignore

API_BASE_URL = "https://wttr.in"
API_TIMEOUT_SECONDS = 5.0
