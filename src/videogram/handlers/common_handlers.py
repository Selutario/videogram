# Created by Selutario <selutario@gmail.com>.
# This program is a free software; you can redistribute it and/or modify it under the terms of GPLv3

import html
import logging
from zoneinfo import ZoneInfo

import videogram.utils.orm as orm
from dateutil import tz
from telegram.ext import ConversationHandler
from videogram.utils import utils
from videogram.utils.common import settings, LOGS_PATH

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s: %(message)s',
                    level=logging.DEBUG if settings['logs_debug'] else logging.INFO, filename=LOGS_PATH)
logger = logging.getLogger(__name__)


async def init(update, context):
    """Extract and store bot, user and channel details."""
    if not utils.initialized() and update.my_chat_member.new_chat_member.status == 'administrator':
        try:
            if update.effective_chat.type != 'channel':
                await context.bot.send_message(chat_id=update.effective_chat.id, text=_("init_required"),
                                               parse_mode="HTML")
            else:
                utils.store_settings('bot_name', context.bot.username)
                utils.store_settings('admin_usernames', [update.effective_user.username])
                utils.store_settings('backup_user_id', update.effective_user.id)
                utils.store_settings('channel_id', update.effective_chat.id)
                await context.bot.send_message(chat_id=update.effective_chat.id, text="🎉", parse_mode="HTML")
                await context.bot.send_message(chat_id=update.effective_chat.id, text=_("init_success"),
                                               parse_mode="HTML")
        except Exception as e:
            await context.bot.send_message(chat_id=update.effective_chat.id, text=_("init_error").format(e),
                                           parse_mode="HTML")
    elif settings['channel_id'] == update.effective_chat.id and \
            update.my_chat_member.new_chat_member.status in ['kicked', 'left']:
        utils.store_settings('bot_name', '')
        utils.store_settings('admin_usernames', [])
        utils.store_settings('backup_user_id', 0)
        utils.store_settings('channel_id', 0)


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


async def get_sent_videos(update, context):
    if update.effective_user.username in settings['admin_usernames']:
        try:
            parameters = int(context.args[0])
        except IndexError:
            parameters = 2

        try:
            sent_videos = orm.session.query(orm.SentVideos, orm.Users, orm.VideoData).filter(
                orm.SentVideos.user_id == orm.Users.id, orm.VideoData.id == orm.SentVideos.video_id).order_by(
                orm.SentVideos.id.desc()).limit(parameters).all()
        except Exception as e:
            print(e)
            return

        if not sent_videos:
            await update.message.reply_text(_("no_sent_videos").format(settings['bot_name']), parse_mode="HTML")
        for sent_video, user, video_data in reversed(sent_videos):
            try:
                date = sent_video.date.replace(tzinfo=ZoneInfo('UTC')).astimezone(
                    tz.gettz(settings['timezone'])).strftime('%H:%M (%d/%m/%Y)')

                await context.bot.send_message(chat_id=update.effective_chat.id,
                                               text=_("get_sent_videos").format(
                                                   sent_video.id,
                                                   user.user_name,
                                                   html.escape(user.first_name),
                                                   date,
                                                   html.escape(sent_video.query),
                                                   html.escape(video_data.title)),
                                               parse_mode="HTML")
            except Exception as e:
                print(f"Error: {sent_videos} | {e}")
