# Created by Selutario <selutario@gmail.com>.
# This program is a free software; you can redistribute it and/or modify it under the terms of GPLv3

import html
import logging
from datetime import datetime, timezone
from random import choice

from telegram.ext import ConversationHandler

from videogram.utils import utils
from videogram.utils.common import settings, LOGS_PATH

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s: %(message)s',
                    level=logging.DEBUG if settings['logs_debug'] else logging.INFO, filename=LOGS_PATH)
logger = logging.getLogger(__name__)

def init(update, context):
    """Extract and store bot, user and channel details."""
    if not utils.initialized() and update.my_chat_member.new_chat_member.status == 'administrator':
        try:
            if update.effective_chat.type != 'channel':
                context.bot.send_message(chat_id=update.effective_chat.id, text=_("init_required"), parse_mode="HTML")
            else:
                utils.store_settings('bot_name', context.bot.username)
                utils.store_settings('admin_usernames', [update.effective_user.username])
                utils.store_settings('backup_user_id', update.effective_user.id)
                utils.store_settings('channel_id', update.effective_chat.id)
                context.bot.send_message(chat_id=update.effective_chat.id, text="🎉", parse_mode="HTML")
                context.bot.send_message(chat_id=update.effective_chat.id, text=_("init_success"), parse_mode="HTML")
        except Exception as e:
            context.bot.send_message(chat_id=update.effective_chat.id, text=_("init_error").format(e),
                                     parse_mode="HTML")
    elif settings['channel_id'] == update.effective_chat.id and \
        update.my_chat_member.new_chat_member.status in ['kicked', 'left']:
        utils.store_settings('bot_name', '')
        utils.store_settings('admin_usernames', [])
        utils.store_settings('backup_user_id', 0)
        utils.store_settings('channel_id', 0)

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

    query = "INSERT INTO sent_random (video_id, title, user_id, date) VALUES (?, ?, ?, ?)"
    params = (random_result['id'], random_result['title'], update.effective_user.id, datetime.now(timezone.utc))
    if not utils.execute_query(query, params):
        context.bot.send_message(chat_id=update.effective_chat.id, text=_("error"))

    context.bot.send_video(chat_id=update.effective_chat.id, video=random_result['file_id'])


def get_sent_videos(update, context):
    if update.effective_user.username in settings['admin_usernames']:
        query = "select sent_videos.id, sent_videos.query, sent_videos.date, sent_videos.user_id, users.user_name, " \
                "users.first_name, video_data.title FROM sent_videos JOIN users ON sent_videos.user_id=users.id " \
                "JOIN video_data ON sent_videos.video_id=video_data.id ORDER BY sent_videos.id DESC LIMIT ?;"
        try:
            parameters = int(context.args[0])
        except IndexError:
            parameters = 2

        for row in reversed(utils.execute_read_query(query=query, parameters=(parameters,))):
            try:
                result = dict(row)

                context.bot.send_message(chat_id=update.effective_chat.id,
                                         text=f"<b>ID:</b> {result['id']}\n"
                                              f"<b>Username:</b> <code>{result['user_name']}</code>\n"
                                              f"<b>Name:</b> {html.escape(result['first_name'])}\n"
                                              f"<b>Date:</b> {result['date']}\n"
                                              f"<b>Query:</b> <code>{html.escape(result['query'])}</code>\n"
                                              f"<b>Title:</b> {html.escape(result['title'])}\n", parse_mode="HTML")

            except Exception as e:
                print(f"Error: {result} | {e}")
