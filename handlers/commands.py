from telegram import Update
from telegram.ext import ContextTypes

from services import users_store


async def handle_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /start para usuarios registrados muestra bienvenida.
    Para usuarios desconocidos el flujo lo maneja onboarding.handle_unknown_user.
    """
    user_id = update.effective_user.id
    if users_store.is_approved(user_id):
        await update.message.reply_text(
            "Hola! Escribime lo que comiste y lo registro.\n"
            "Por ejemplo: _almorcé milanesa con puré_",
            parse_mode="Markdown",
        )
