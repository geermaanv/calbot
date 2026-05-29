import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from telegram import Bot

from services import users_store

logger = logging.getLogger(__name__)

TIMEZONE = "America/Argentina/Buenos_Aires"

MENSAJES = [
    (10, 0, "🍳 ¿Ya desayunaste? Registralo acá."),
    (14, 0, "🍽️ ¿Qué almorzaste hoy?"),
    (18, 0, "🫖 Hora de la merienda, ¿comiste algo?"),
    (21, 0, "🌙 Antes de terminar el día, ¿registraste la cena?"),
]


async def _enviar(bot: Bot, mensaje: str):
    for user_id in users_store.get_reminder_ids():
        try:
            await bot.send_message(chat_id=user_id, text=mensaje)
            logger.info("Recordatorio enviado a %s", user_id)
        except Exception as e:
            logger.warning("No se pudo enviar recordatorio a %s: %s", user_id, e)


def setup(bot: Bot) -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler(timezone=TIMEZONE)
    for hora, minuto, mensaje in MENSAJES:
        scheduler.add_job(
            _enviar,
            CronTrigger(hour=hora, minute=minuto, timezone=TIMEZONE),
            args=[bot, mensaje],
        )
    scheduler.start()
    return scheduler
