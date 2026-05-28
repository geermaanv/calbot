from telegram import Update
from telegram.ext import ContextTypes

from services import users_store, sheets_client

AYUDA_MSG = (
    "📋 *Cómo usar CalBot*\n\n"
    "*Registrar una comida:*\n"
    "Escribí lo que comiste en lenguaje natural:\n"
    "_almorcé milanesa con puré_\n"
    "_desayuné dos tostadas con manteca y café con leche_\n\n"
    "*Registrar en otra fecha:*\n"
    "_ayer cené empanadas de carne_\n"
    "_el lunes almorcé un sándwich_\n"
    "_27/05 comí pizza_\n\n"
    "*Corregir el último registro:*\n"
    "_en realidad era milanesa de pollo_\n"
    "_me equivoqué, fueron 3 empanadas, no 5_\n\n"
    "*Comandos:*\n"
    "/resumen — calorías de hoy, semana y mes\n"
    "/ayuda — este mensaje"
)


async def handle_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if users_store.is_approved(user_id):
        await update.message.reply_text(
            "Hola! Escribime lo que comiste y lo registro.\n"
            "Por ejemplo: _almorcé milanesa con puré_\n\n"
            "Usá /ayuda para ver todas las opciones.",
            parse_mode="Markdown",
        )


async def handle_ayuda(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(AYUDA_MSG, parse_mode="Markdown")


async def handle_resumen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not users_store.is_approved(user_id):
        return
    tab = update.effective_user.username or str(user_id)
    try:
        r = sheets_client.get_resumen(tab)
    except Exception:
        await update.message.reply_text("No pude obtener el resumen. Intentá de nuevo.")
        return
    dias_semana = r["dias_semana"] or 1
    dias_mes = r["dias_mes"] or 1
    prom_semana = r["semana"] // dias_semana
    prom_mes = r["mes"] // dias_mes

    lineas = (
        f"📊 Tu resumen calórico\n\n"
        f"Hoy:    {r['hoy']:,} kcal\n"
        f"Semana: {prom_semana:,} kcal/día ({r['semana']:,} kcal en {dias_semana} días)\n"
        f"Mes:    {prom_mes:,} kcal/día ({r['mes']:,} kcal en {dias_mes} días)"
    ).replace(",", ".")
    await update.message.reply_text(f"```\n{lineas}\n```", parse_mode="Markdown")
