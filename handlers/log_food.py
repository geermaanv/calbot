from telegram import Update
from telegram.ext import ContextTypes

from services import claude_client, sheets_client, users_store


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()

    sheet_id = users_store.get_sheet_id(user_id)
    if not sheet_id:
        await update.message.reply_text(
            "No encontré tu hoja de registro. Escribí cualquier cosa para iniciar el registro."
        )
        return

    # Clasificar intención
    try:
        intent = claude_client.classify(text)
    except Exception:
        await update.message.reply_text(
            "Hubo un error procesando tu mensaje. Intentá de nuevo."
        )
        return

    if intent == "comida":
        await _log_food(update, text, sheet_id)
    elif intent == "correccion":
        await _correct_entry(update, text, sheet_id)
    else:
        await update.message.reply_text(
            "No entendí eso como una comida. Contame qué comiste y lo registro."
        )


async def _log_food(update: Update, text: str, sheet_id: str):
    try:
        result = claude_client.estimate_calories(text)
    except Exception:
        await update.message.reply_text(
            "No pude estimar las calorías. Intentá describir la comida con más detalle."
        )
        return

    plato = result["plato"]
    calorias = result["calorias"]

    try:
        sheets_client.append_entry(sheet_id, text, plato, calorias)
        total = sheets_client.get_daily_total(sheet_id)
    except Exception:
        await update.message.reply_text(
            "Estimé las calorías pero no pude guardar el registro. Intentá de nuevo."
        )
        return

    await update.message.reply_text(
        f"{plato} — {calorias} kcal  |  Total hoy: {total:,} kcal".replace(",", ".")
    )


async def _correct_entry(update: Update, text: str, sheet_id: str):
    last = sheets_client.get_last_entry(sheet_id)
    if not last:
        await update.message.reply_text(
            "No encontré ninguna entrada anterior para corregir."
        )
        return

    try:
        result = claude_client.correct_entry(last["texto_usuario"], text)
    except Exception:
        await update.message.reply_text(
            "No pude procesar la corrección. Intentá de nuevo."
        )
        return

    plato = result["plato"]
    calorias = result["calorias"]

    try:
        sheets_client.update_last_entry(sheet_id, plato, calorias)
        total = sheets_client.get_daily_total(sheet_id)
    except Exception:
        await update.message.reply_text(
            "No pude guardar la corrección. Intentá de nuevo."
        )
        return

    await update.message.reply_text(
        f"Corregido: {plato} — {calorias} kcal  |  Total hoy: {total:,} kcal".replace(",", ".")
    )
