# Created by Selutario <selutario@gmail.com>.
# This program is a free software; you can redistribute it and/or modify it under the terms of GPLv3

import logging

from telegram.ext import ConversationHandler
from videogram.utils.common import settings, LOGS_PATH

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s: %(message)s',
                    level=logging.DEBUG if settings['logs_debug'] else logging.INFO, filename=LOGS_PATH)
logger = logging.getLogger(__name__)


async def start(update, context):
    """Send a message when the command /start is issued."""
    await update.message.reply_text(_("start_command").format(settings['bot_name']), parse_mode="HTML")


async def unknown(update, context):
    await context.bot.send_message(chat_id=update.effective_chat.id, text=_("unknown_command"))


async def cancel(update, context):
    await context.bot.send_message(chat_id=update.effective_chat.id, text=_("cancel_command"))
    return ConversationHandler.END


async def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)
