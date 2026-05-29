import os
import logging

REQUIRED_VARS = [
    "TELEGRAM_BOT_TOKEN",
    "OPENROUTER_API_KEY",
    "GOOGLE_CREDENTIALS_JSON",
    "GOOGLE_SHEET_ID",
    "ADMIN_USER_IDS",
]


def validate():
    missing = [v for v in REQUIRED_VARS if not os.environ.get(v)]
    if missing:
        raise EnvironmentError(
            f"Variables de entorno faltantes: {', '.join(missing)}\n"
            "Copiá .env.example a .env y completá los valores."
        )


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%d/%m/%Y %H:%M:%S",
    )
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("apscheduler").setLevel(logging.WARNING)
