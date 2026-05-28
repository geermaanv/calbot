import os
from telegram import Update
from telegram.ext import ContextTypes

from services import sheets_client, users_store

ADMIN_USER_IDS = [int(x) for x in os.environ.get("ADMIN_USER_IDS", "").split(",") if x.strip()]

WELCOME_MSG = (
    "Hola! Soy CalBot, tu asistente de registro calórico.\n\n"
    "Para registrarte mandá:\n"
    "/registro"
)


async def handle_unknown_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(WELCOME_MSG)


async def handle_registro(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.username or str(user_id)

    if users_store.is_approved(user_id):
        await update.message.reply_text("Ya estás registrado. Podés empezar a usar el bot.")
        return

    if users_store.is_pending(user_id):
        await update.message.reply_text(
            "Tu solicitud está pendiente de aprobación. Te avisamos cuando esté lista."
        )
        return

    await update.message.reply_text("Creando tu hoja de registro...")

    try:
        tab_name = username
        sheets_client.create_user_tab(tab_name)
    except Exception as e:
        await update.message.reply_text(
            "Hubo un error al crear tu hoja. Intentá de nuevo en unos minutos."
        )
        return

    users_store.approve(user_id)

    await update.message.reply_text(
        "Listo! Ya podés empezar a registrar lo que comés.\n\n"
        "Escribime directamente lo que comiste, por ejemplo:\n"
        "_almorcé milanesa con puré_",
        parse_mode="Markdown",
    )
