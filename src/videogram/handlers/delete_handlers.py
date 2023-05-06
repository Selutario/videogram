# Created by Selutario <selutario@gmail.com>.
# This program is a free software; you can redistribute it and/or modify it under the terms of GPLv3

import html

import videogram.utils.orm as orm
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ConversationHandler, MessageHandler, CommandHandler, Filters, CallbackQueryHandler
from videogram.handlers.common_handlers import cancel
from videogram.utils import utils
from videogram.utils.common import *

DELETE_GET_ID, DELETE_CHOSEN_OPTION = range(2)


def delete_start(update, context):
    if not utils.initialized():
        context.bot.send_message(chat_id=update.effective_chat.id, text=_("init_required"))
        return ConversationHandler.END
    elif (update.effective_user.username in settings['admin_usernames'] or
            (settings['delete_enabled'] and update.effective_user.username not in settings['banned_usernames'] and
             (not settings['closed_circle'] or update.effective_user.username in settings['closed_circle']))):
        context.bot.send_message(chat_id=update.effective_chat.id, text=_("delete_start"))
        return DELETE_GET_ID
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text=_("delete_disabled"))
        return ConversationHandler.END


def delete_get_id(update, context):
    if update['message']['video']:
        result = orm.session.query(orm.VideoData, orm.ChannelMessages).join(orm.ChannelMessages, isouter=True).filter(
            orm.VideoData.file_unique_id == update['message']['video']['file_unique_id']).first()
    elif update['message']['text']:
        result = orm.session.query(orm.VideoData, orm.ChannelMessages).join(orm.ChannelMessages, isouter=True).filter(
            orm.VideoData.id == update['message']['text']).first()
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text=_("need_video_or_id"))
        return

    if result:
        context.user_data.update({
            'video': result[0],
            'channel_message': result[1]
        })

        if str(update.effective_user.id) != context.user_data['video'].user_id and \
                str(update.effective_user.username) not in settings['admin_usernames']:
            context.bot.send_message(chat_id=update.effective_chat.id, text=_("delete_no_permissions"))
            return ConversationHandler.END

        menu_opt = [[InlineKeyboardButton('✅', callback_data='yes'),
                     InlineKeyboardButton('❌', callback_data='no')]]
        context.bot.send_video(chat_id=update.effective_chat.id, video=context.user_data['video'].file_id,
                               caption=_("delete_confirm").format(html.escape(context.user_data['video'].title),
                                                                  html.escape(context.user_data['video'].description)),
                               parse_mode="HTML", reply_markup=InlineKeyboardMarkup(menu_opt))
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text=_("error_video_not_found"))

    return DELETE_CHOSEN_OPTION


def on_chosen_delete_option(update, context):
    update.callback_query.answer()
    if update.callback_query.data == 'yes':
        try:
            orm.session.delete(context.user_data['video'])
            orm.session.delete(context.user_data['channel_message'])

            if context.user_data['channel_message'].msg_id:
                context.bot.delete_message(chat_id=context.user_data['channel_message'].chat_id,
                                           message_id=context.user_data['channel_message'].msg_id)

            orm.session.commit()
            update.callback_query.edit_message_caption(_("delete_ok"))
        except Exception:
            update.callback_query.edit_message_caption(_("error"))

    elif update.callback_query.data == 'no':
        update.callback_query.edit_message_caption(_("cancel_command"))
    else:
        update.callback_query.edit_message_caption(_("unknown_command"))
    return ConversationHandler.END


# Conversation handler
delete_conv_handler = ConversationHandler(
    entry_points=[CommandHandler('delete', delete_start)],
    states={
        DELETE_GET_ID: [MessageHandler((Filters.text | Filters.video) & (~Filters.command), delete_get_id)],
        DELETE_CHOSEN_OPTION: [CallbackQueryHandler(on_chosen_delete_option, pattern='^(yes|no)$')],
    },
    fallbacks=[CommandHandler('cancel', cancel)],
    allow_reentry=True
)
