# Created by Selutario <selutario@gmail.com>.
# This program is a free software; you can redistribute it and/or modify it under the terms of GPLv3

import logging
from random import choice

import videogram.utils.orm as orm
from telegram.ext import ConversationHandler
from videogram.utils import utils
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


async def get_random_video(update, context):
    if not (update.effective_user.username in settings['admin_usernames'] or not settings['closed_circle'] or
            update.effective_user.username in settings['closed_circle']):
        return

    random_result = choice(utils.videos_info.videos_info_list)

    user = orm.Users(
        user_id=update.effective_user.id,
        user_name=update.effective_user.username,
        first_name=update.effective_user.first_name,
        last_name=update.effective_user.last_name
    )

    sent_video = orm.SentVideos(
        user_id=update.effective_user.id,
        query='/random',
        video_id=random_result.id
    )

    orm.session.merge(user)
    orm.session.add(sent_video)
    orm.session.commit()

    await context.bot.send_video(chat_id=update.effective_chat.id, video=random_result.file_id)
