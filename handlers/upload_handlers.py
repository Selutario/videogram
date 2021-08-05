# Created by Selutario <selutario@gmail.com>.
# This program is a free software; you can redistribute it and/or modify it under the terms of GPLv3

from uuid import uuid4

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ConversationHandler, CommandHandler, Filters, MessageHandler, CallbackQueryHandler

from handlers.common_handlers import cancel
from utils import utils
from utils.common import settings

UPLD_GET_VID, UPLD_TITLE, UPLD_DESC, UPLD_KEYWORDS, UPLD_CHECK_SAME = range(5)


def upld_start(update, context):
    if (update.effective_user.username in settings['admin_usernames'] or
            (settings['upload_enabled'] and update.effective_user.username not in settings['banned_usernames'] and
             (not settings['closed_circle'] or update.effective_user.username in settings['closed_circle']))):
        context.bot.send_message(chat_id=update.effective_chat.id, text=_("upld_send_video"))

        if not utils.store_user_details(update):
            context.bot.send_message(chat_id=update.effective_chat.id, text=_("error"))
            return ConversationHandler.END

        return UPLD_GET_VID
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text=_("upload_disabled"))
        return ConversationHandler.END


def upld_video(update, context):
    context.user_data.update({
        'upld': {
            'id': str(uuid4()),
            'file_id': update['message']['video']['file_id'],
            'file_unique_id': update['message']['video']['file_unique_id'],
            'width': update['message']['video']['width'],
            'height': update['message']['video']['height'],
            'duration': update['message']['video']['duration'],
            'user_id': update.effective_user.id,
            'user_name': update.effective_user.username,
            'first_name': update.effective_user.first_name,
        }
    })

    if context.user_data['upld']['duration'] > settings['max_video_length']:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=_("error_video_length").format(context.user_data['upld']['duration'], settings['max_video_length']))
    else:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text=_("upld_send_title").format(settings['max_title_length']))
        return UPLD_TITLE


def upld_title(update, context):
    if len(update['message']['text']) <= settings['max_title_length']:
        context.user_data['upld'].update({'title': update['message']['text']})
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text=_("upld_send_desc").format(settings["max_desc_length"]))
        return UPLD_DESC
    else:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=_("error_title_length").format(len(update['message']['text']), settings['max_title_length']))


def upld_desc(update, context):
    if len(update['message']['text']) <= settings['max_desc_length']:
        context.user_data['upld'].update({'desc': update['message']['text']})
        result = utils.get_similar_videos(
            utils.cleaner(context.user_data['upld']['desc']),
            utils.videos_info.desc_df,
            utils.videos_info.desc_vt,
            len(utils.videos_info),
            0.60)

        if result:
            menu_opt = [[InlineKeyboardButton(_("upld_diff_video"), callback_data='different')],
                        [InlineKeyboardButton(_("upld_same_video"), callback_data='same')]]
            context.bot.send_video(chat_id=update.effective_chat.id,
                                   video=utils.videos_info.videos_info_list[result[0]]['file_id'],
                                   caption=_("upld_same_video_form"), reply_markup=InlineKeyboardMarkup(menu_opt))
            return UPLD_CHECK_SAME
        else:
            context.bot.send_message(
                chat_id=update.effective_chat.id, text=_("upld_send_keywords").format(settings['max_kwords_length']))
            return UPLD_KEYWORDS
    else:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=_("error_desc_length").format(len(update['message']['text']), settings['max_desc_length']))


def upld_keywords(update, context):
    if len(update['message']['text']) <= settings['max_kwords_length']:
        context.user_data['upld'].update({'keywords': update['message']['text']})

        if context.user_data['upld']['user_name']:
            user = context.user_data['upld']['user_name']
        else:
            user = context.user_data['upld']['first_name']

        video_msg = context.bot.send_video(
            chat_id=settings['channel_id'], video=context.user_data['upld']['file_id'],
            caption=_("channel_info_caption").format(context.user_data['upld']['id'],
                                                     user,
                                                     context.user_data['upld']['desc'],
                                                     context.user_data['upld']['keywords']),
            parse_mode="HTML")

        query = "INSERT INTO video_data (id, title, description, keywords, file_id, file_unique_id, width, height, " \
                "duration, user_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
        params = (context.user_data['upld']['id'], context.user_data['upld']['title'],
                  context.user_data['upld']['desc'], context.user_data['upld']['keywords'],
                  video_msg['video']['file_id'], video_msg['video']['file_unique_id'], video_msg['video']['width'],
                  video_msg['video']['height'], video_msg['video']['duration'], context.user_data['upld']['user_id'])
        if not utils.execute_query(query, params):
            context.bot.send_message(chat_id=update.effective_chat.id, text=_("error"))
            return ConversationHandler.END

        query = "INSERT INTO channel_messages (msg_id, chat_id, video_id) VALUES (?, ?, ?)"
        params = (video_msg['message_id'], video_msg['chat']['id'], context.user_data['upld']['id'])
        if utils.execute_query(query, params):
            utils.videos_info.update_model()
            context.bot.send_message(
                chat_id=update.effective_chat.id, text=_("upld_video_ok").format(context.user_data['upld']['id']),
                parse_mode="HTML")
        else:
            context.bot.send_message(chat_id=update.effective_chat.id, text=_("error"))
        return ConversationHandler.END
    else:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=_("error_keywords_length").format(len(update['message']['text']), settings['max_kwords_length']))


def upld_on_chosen_option(update, context):
    update.callback_query.answer()
    if update.callback_query.data == 'same':
        update.callback_query.edit_message_caption(_("upld_same_video"))
        cancel(update, context)
    elif update.callback_query.data == 'different':
        update.callback_query.edit_message_caption(_("upld_diff_video"))
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=_("upld_send_keywords").format(settings['max_kwords_length']))
        return UPLD_KEYWORDS


# Conversation handler
upload_conv_handler = ConversationHandler(
    entry_points=[CommandHandler('upload', upld_start)],
    states={
        UPLD_GET_VID: [MessageHandler(Filters.video, upld_video)],
        UPLD_TITLE: [MessageHandler((Filters.text & ~Filters.command), upld_title)],
        UPLD_DESC: [MessageHandler((Filters.text & ~Filters.command), upld_desc)],
        UPLD_CHECK_SAME: [CallbackQueryHandler(upld_on_chosen_option, pattern='^(same|different)$')],
        UPLD_KEYWORDS: [MessageHandler((Filters.text & ~Filters.command), upld_keywords)]
    },
    fallbacks=[CommandHandler('cancel', cancel)],
    allow_reentry=True
)
