# Created by Selutario <selutario@gmail.com>.
# This program is a free software; you can redistribute it and/or modify it under the terms of GPLv3

import logging
from datetime import datetime, timezone
from random import choice

from telegram.ext import ConversationHandler

from utils import utils
from utils.common import settings

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s: %(message)s',
                    level=logging.DEBUG if settings['logs_debug'] else logging.INFO, filename=utils.LOGS_PATH)
logger = logging.getLogger(__name__)


def start(update, context):
    """Send a message when the command /start is issued."""
    update.message.reply_text(_("start_command").format(settings['bot_name']))
    utils.store_user_details(update)


def unknown(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text=_("unknown_command"))


def cancel(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text=_("cancel_command"))
    return ConversationHandler.END


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def get_random_video(update, context):
    if not (update.effective_user.username in settings['admin_usernames'] or not settings['closed_circle'] or
            update.effective_user.username in settings['closed_circle']):
        return

    random_result = choice(utils.videos_info.videos_info_list)

    if not utils.store_user_details(update):
        context.bot.send_message(chat_id=update.effective_chat.id, text=_("error"))
        return ConversationHandler.END

    query = "INSERT INTO sent_random (video_id, title, user_id, date) VALUES (?, ?, ?, ?)"
    params = (random_result['id'], random_result['title'], update.effective_user.id, datetime.now(timezone.utc))
    if not utils.execute_query(query, params):
        context.bot.send_message(chat_id=update.effective_chat.id, text=_("error"))

    context.bot.send_video(chat_id=update.effective_chat.id, video=random_result['file_id'])
