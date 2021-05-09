# Created by Selutario <selutario@gmail.com>.
# This program is a free software; you can redistribute it and/or modify it under the terms of GPLv3

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ConversationHandler, MessageHandler, CommandHandler, Filters, CallbackQueryHandler

from handlers.common_handlers import cancel
from utils import utils
from utils.common import *

DELETE_GET_ID, DELETE_CHOSEN_OPTION = range(2)


def delete_start(update, context):
    if (settings['delete_enabled'] and update.effective_user.username not in settings['banned_usernames']) or \
            update.effective_user.username in settings['admin_usernames']:
        context.bot.send_message(chat_id=update.effective_chat.id, text=_("delete_start"))
        return DELETE_GET_ID
    else:
        return ConversationHandler.END


def delete_get_id(update, context):
    common_query = """
    SELECT video_data.id, video_data.title, video_data.description, video_data.file_id, channel_messages.msg_id, 
    channel_messages.chat_id FROM video_data LEFT JOIN channel_messages ON video_data.id=channel_messages.video_id WHERE 
    """

    if update['message']['video']:
        result = utils.execute_read_query(
            query=common_query+"video_data.file_unique_id = ?", parameters=(update['message']['video']['file_unique_id'],))
    elif update['message']['text']:
        result = utils.execute_read_query(query=common_query+"video_data.id = ?", parameters=(update['message']['text'],))
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text=_("need_video_or_id"))
        return

    if result:
        dict_result = dict(result[0])
        context.user_data.update({
            'delete': {
                'id': dict_result['id'],
                'chat_id': dict_result['chat_id'],
                'msg_id': dict_result['msg_id']
            }
        })
        menu_opt = [[InlineKeyboardButton('✅', callback_data='yes'),
                     InlineKeyboardButton('❌', callback_data='no')]]
        context.bot.send_video(chat_id=update.effective_chat.id, video=dict_result['file_id'],
                               caption=_("delete_confirm").format(dict_result['title'], dict_result['description']),
                               parse_mode="HTML", reply_markup=InlineKeyboardMarkup(menu_opt))
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text=_("error_video_not_found"))

    return DELETE_CHOSEN_OPTION


def on_chosen_delete_option(update, context):
    update.callback_query.answer()
    if update.callback_query.data == 'yes':
        if utils.execute_query(query="DELETE FROM video_data WHERE id = ?", parameters=(context.user_data['delete']['id'],)):
            utils.videos_info.update_model()
            if context.user_data['delete']['msg_id']:
                context.bot.delete_message(chat_id=context.user_data['delete']['chat_id'],
                                           message_id=context.user_data['delete']['msg_id'])
            update.callback_query.edit_message_caption(_("delete_ok"))
        else:
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
