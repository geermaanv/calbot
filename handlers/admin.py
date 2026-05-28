import os
from telegram import Update
from telegram.ext import ContextTypes

from services import users_store

ADMIN_USER_IDS = [int(x) for x in os.environ.get("ADMIN_USER_IDS", "").split(",") if x.strip()]


def _is_admin(user_id: int) -> bool:
    return user_id in ADMIN_USER_IDS


async def handle_approve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler para /aprobar_<user_id>."""
    admin_id = update.effective_user.id
    if not _is_admin(admin_id):
        return

    # Extraer user_id del comando: /aprobar_123456789
    command = update.message.text.split("_", 1)
    if len(command) < 2:
        await update.message.reply_text("Formato inválido. Usá /aprobar_USER_ID")
        return

    try:
        target_id = int(command[1])
    except ValueError:
        await update.message.reply_text("ID inválido.")
        return

    approved = users_store.approve(target_id)
    if not approved:
        await update.message.reply_text(f"No encontré solicitud pendiente para {target_id}.")
        return

    # Notificar al usuario aprobado
    try:
        await context.bot.send_message(
            chat_id=target_id,
            text=(
                "Bienvenido a CalBot! Ya podés empezar a registrar lo que comés.\n\n"
                "Escribime directamente lo que comiste, por ejemplo:\n"
                "_almorcé milanesa con puré_"
            ),
            parse_mode="Markdown",
        )
    except Exception:
        pass

    await update.message.reply_text(f"Usuario {target_id} aprobado.")


async def handle_reject(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler para /rechazar_<user_id>."""
    admin_id = update.effective_user.id
    if not _is_admin(admin_id):
        return

    command = update.message.text.split("_", 1)
    if len(command) < 2:
        await update.message.reply_text("Formato inválido. Usá /rechazar_USER_ID")
        return

    try:
        target_id = int(command[1])
    except ValueError:
        await update.message.reply_text("ID inválido.")
        return

    existed = users_store.reject(target_id)
    if not existed:
        await update.message.reply_text(f"No encontré solicitud pendiente para {target_id}.")
        return

    try:
        await context.bot.send_message(
            chat_id=target_id,
            text="Tu solicitud de registro no fue aprobada. Contactá al administrador para más información.",
        )
    except Exception:
        pass

    await update.message.reply_text(f"Solicitud de {target_id} rechazada.")


async def handle_start_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler de /start para admins."""
    await update.message.reply_text(
        "Hola! Sos administrador de CalBot.\n"
        "Cuando alguien solicite registrarse, te llegará una notificación con los comandos de aprobación."
    )
