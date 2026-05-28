# CalBot

Bot de Telegram para registro calórico por texto libre.

## Stack

- Python 3.11+
- python-telegram-bot
- Anthropic API (Claude)
- Google Sheets (gspread)

## Setup

```bash
# 1. Clonar
git clone https://github.com/<usuario>/calbot.git && cd calbot

# 2. Entorno virtual
python3 -m venv .venv && source .venv/bin/activate

# 3. Dependencias
pip install -r requirements.txt

# 4. Variables de entorno
cp .env.example .env
# Editar .env con los valores reales

# 5. Estado inicial de usuarios
cp users.json.example users.json

# 6. Correr
python main.py
```

## Variables de entorno

| Variable | Descripción |
|---|---|
| `TELEGRAM_BOT_TOKEN` | Token del bot (@BotFather) |
| `ANTHROPIC_API_KEY` | API key de Anthropic |
| `GOOGLE_CREDENTIALS_JSON` | Contenido del credentials.json como string |
| `ADMIN_USER_IDS` | Telegram user IDs de admins, separados por coma |
| `SERVICE_ACCOUNT_EMAIL` | Email de la service account de Google |

## Deploy en servidor (systemd)

Ver documentación en el design doc.
