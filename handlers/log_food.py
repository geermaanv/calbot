import logging
from telegram import Update
from telegram.ext import ContextTypes

from services import ai_client, sheets_client, users_store

logger = logging.getLogger(__name__)


def _tab_name(update: Update) -> str:
    return update.effective_user.username or str(update.effective_user.id)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    tab = _tab_name(update)

    try:
        intent = ai_client.classify(text)
    except Exception as e:
        logger.error("Error clasificando mensaje de %s: %s", tab, e)
        await update.message.reply_text(
            "Hubo un error procesando tu mensaje. Intentá de nuevo."
        )
        return

    if intent == "comida":
        await _log_food(update, text, tab)
    elif intent == "correccion":
        await _correct_entry(update, text, tab)
    elif intent == "skip":
        await update.message.reply_text("Ok, anotado. Si después comés algo, avisame.")
    else:
        await update.message.reply_text(
            "No entendí eso como una comida. Contame qué comiste y lo registro."
        )


async def _log_food(update: Update, text: str, tab: str):
    try:
        result = ai_client.estimate_calories(text)
    except Exception as e:
        logger.error("Error estimando calorías para %s: %s", tab, e)
        await update.message.reply_text(
            "No pude estimar las calorías. Intentá describir la comida con más detalle."
        )
        return

    plato = result["plato"]
    calorias = result["calorias"]
    fecha = result.get("fecha")
    logger.info("Registro: %s | %s | %s kcal | fecha: %s", tab, plato, calorias, fecha)

    try:
        sheets_client.append_entry(tab, text, plato, calorias, fecha)
        total = sheets_client.get_daily_total(tab, fecha)
    except Exception as e:
        logger.error("Error guardando registro de %s: %s", tab, e)
        await update.message.reply_text(
            "Estimé las calorías pero no pude guardar el registro. Intentá de nuevo."
        )
        return

    from datetime import datetime
    hoy = datetime.now().strftime("%d/%m/%Y")
    dia_label = "hoy" if not fecha or fecha == hoy else fecha
    await update.message.reply_text(
        f"{plato} — {calorias} kcal  |  Total {dia_label}: {total:,} kcal".replace(",", ".")
    )


async def _correct_entry(update: Update, text: str, tab: str):
    last = sheets_client.get_last_entry(tab)
    if not last:
        await update.message.reply_text(
            "No encontré ninguna entrada anterior para corregir."
        )
        return

    try:
        result = ai_client.correct_entry(last["texto_usuario"], text)
    except Exception:
        await update.message.reply_text(
            "No pude procesar la corrección. Intentá de nuevo."
        )
        return

    plato = result["plato"]
    calorias = result["calorias"]

    try:
        sheets_client.update_last_entry(tab, plato, calorias)
        total = sheets_client.get_daily_total(tab)
    except Exception:
        await update.message.reply_text(
            "No pude guardar la corrección. Intentá de nuevo."
        )
        return

    await update.message.reply_text(
        f"Corregido: {plato} — {calorias} kcal  |  Total hoy: {total:,} kcal".replace(",", ".")
    )
