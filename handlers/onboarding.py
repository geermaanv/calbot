import os
from telegram import Update
from telegram.ext import ContextTypes

from services import sheets_client, users_store

SERVICE_ACCOUNT_EMAIL = os.environ.get("SERVICE_ACCOUNT_EMAIL", "")
ADMIN_USER_IDS = [int(x) for x in os.environ.get("ADMIN_USER_IDS", "").split(",") if x.strip()]

WELCOME_MSG = (
    "Hola! Soy CalBot, tu asistente de registro calórico.\n\n"
    "Para empezar necesitás crear tu hoja de registro en Google Sheets:\n\n"
    "1. Abrí sheets.new y creá una hoja nueva\n"
    "2. Compartila con esta dirección como *Editor*:\n"
    f"`{SERVICE_ACCOUNT_EMAIL}`\n\n"
    "3. Copiá el ID de la hoja (la parte entre /d/ y /edit en la URL)\n"
    "4. Mandámelo así:\n"
    "`/registro TU_SHEET_ID`"
)


async def handle_unknown_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler para usuarios no registrados ni pendientes."""
    user_id = update.effective_user.id

    if users_store.is_pending(user_id):
        await update.message.reply_text(
            "Tu solicitud está pendiente de aprobación. Te avisamos cuando esté lista."
        )
        return

    await update.message.reply_text(WELCOME_MSG, parse_mode="Markdown")


async def handle_registro(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler para /registro <sheet_id>."""
    user_id = update.effective_user.id
    username = update.effective_user.username or str(user_id)

    if users_store.is_approved(user_id):
        await update.message.reply_text("Ya estás registrado. Podés empezar a usar el bot.")
        return

    if not context.args:
        await update.message.reply_text(
            "Usá el comando así: `/registro TU_SHEET_ID`", parse_mode="Markdown"
        )
        return

    sheet_id = context.args[0].strip()

    # Validar acceso a la Sheet
    await update.message.reply_text("Verificando acceso a tu hoja...")
    try:
        sheets_client.init_sheet(sheet_id)
    except Exception:
        await update.message.reply_text(
            "No pude acceder a esa hoja. Verificá que:\n"
            f"• La compartiste con `{SERVICE_ACCOUNT_EMAIL}` como Editor\n"
            "• El ID es correcto (la parte entre /d/ y /edit en la URL)\n\n"
            "Intentá de nuevo con `/registro TU_SHEET_ID`",
            parse_mode="Markdown",
        )
        return

    # Guardar como pendiente
    users_store.add_pending(user_id, sheet_id)

    await update.message.reply_text(
        "Perfecto, tu hoja está lista. Enviamos la solicitud al administrador para aprobación. "
        "Te avisamos cuando esté todo listo."
    )

    # Notificar a todos los admins
    for admin_id in ADMIN_USER_IDS:
        try:
            await context.bot.send_message(
                chat_id=admin_id,
                text=(
                    f"Solicitud de registro:\n"
                    f"Usuario: @{username} ({user_id})\n"
                    f"Sheet ID: `{sheet_id}`\n\n"
                    f"/aprobar_{user_id}\n"
                    f"/rechazar_{user_id}"
                ),
                parse_mode="Markdown",
            )
        except Exception:
            pass
