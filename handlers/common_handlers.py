# Created by Selutario <selutario@gmail.com>.
# This program is a free software; you can redistribute it and/or modify it under the terms of GPLv3

import logging
from datetime import datetime, timezone
from random import choice

from telegram.ext import ConversationHandler

from utils import utils
from utils.common import settings

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s: %(message)s',
                    level=logging.DEBUG if settings['logs_debug'] else logging.INFO,
                    filename=utils.LOGS_PATH)
logger = logging.getLogger(__name__)


def start(update, context):
    """Send a message when the command /start is issued."""
    update.message.reply_text(_("start_command").format(settings['bot_name']))


def unknown(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text=_("unknown_command"))


def cancel(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text=_("cancel_command"))
    return ConversationHandler.END


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def get_random_video(update, context):
    random_result = choice(utils.videos_info.videos_info_list)

    query = "INSERT INTO sent_random (video_id, title, user_id, user_name, date) VALUES (?, ?, ?, ?, ?)"
    params = (random_result['id'], random_result['title'], update.effective_user.id, update.effective_user.username,
              datetime.now(timezone.utc))
    utils.execute_query(query=query, parameters=params)
    context.bot.send_video(chat_id=update.effective_chat.id, video=random_result['file_id'])
