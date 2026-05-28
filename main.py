"""
CalBot — Bot de Telegram para registro calórico.
Dependencias: python-telegram-bot, anthropic, gspread

Arrancar:
    python main.py
"""
import os
import re
from dotenv import load_dotenv

load_dotenv()

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
)

from handlers import log_food, onboarding, admin, commands
from services import users_store

TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
ADMIN_USER_IDS = [int(x) for x in os.environ.get("ADMIN_USER_IDS", "").split(",") if x.strip()]


def build_app() -> Application:
    app = Application.builder().token(TOKEN).build()

    # --- Filtros ---
    admin_filter = filters.User(user_id=ADMIN_USER_IDS)

    def approved_filter():
        """Filtro dinámico: recalcula en cada mensaje."""
        return filters.User(user_ids=users_store.get_approved_ids())

    # --- Handlers de admin (comandos dinámicos /aprobar_ID y /rechazar_ID) ---
    app.add_handler(MessageHandler(
        admin_filter & filters.Regex(re.compile(r"^/aprobar_\d+$")),
        admin.handle_approve,
    ))
    app.add_handler(MessageHandler(
        admin_filter & filters.Regex(re.compile(r"^/rechazar_\d+$")),
        admin.handle_reject,
    ))

    # --- /start y /ayuda ---
    app.add_handler(CommandHandler("start", admin.handle_start_admin, filters=admin_filter))
    app.add_handler(CommandHandler("start", commands.handle_start))
    app.add_handler(CommandHandler("ayuda", commands.handle_ayuda))
    app.add_handler(CommandHandler("resumen", commands.handle_resumen))

    # --- Onboarding ---
    app.add_handler(CommandHandler("registro", onboarding.handle_registro))

    # --- Registro calórico (usuarios aprobados, mensajes de texto) ---
    # Nota: approved_filter() se evalúa en tiempo de ejecución para reflejar
    # usuarios recién aprobados sin reiniciar el proceso.
    async def route_message(update: Update, context):
        user_id = update.effective_user.id
        if users_store.is_approved(user_id):
            await log_food.handle_message(update, context)
        elif users_store.is_pending(user_id):
            await update.message.reply_text(
                "Tu solicitud está pendiente de aprobación. Te avisamos cuando esté lista."
            )
        else:
            await onboarding.handle_unknown_user(update, context)

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, route_message))

    return app


if __name__ == "__main__":
    print("CalBot iniciando...")
    app = build_app()
    app.run_polling()
