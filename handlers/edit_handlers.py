# Created by Selutario <selutario@gmail.com>.
# This program is a free software; you can redistribute it and/or modify it under the terms of GPLv3

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, InputMediaVideo
from telegram.ext import ConversationHandler, CommandHandler, MessageHandler, Filters, CallbackQueryHandler

from handlers.common_handlers import cancel
from utils import utils
from utils.common import settings

EDIT_GET_ID, EDIT_MENU, EDIT_CHOSEN_OPTION, EDIT_TITLE, EDIT_DESC, EDIT_KEYWORDS, EDIT_VIDEO = range(7)


def edit_start(update, context):
    if (settings['edit_enabled'] and update.effective_user.username not in settings['banned_usernames']) or \
            update.effective_user.username in settings['admin_usernames']:
        context.bot.send_message(chat_id=update.effective_chat.id, text=_("edit_start"))
        return EDIT_GET_ID
    else:
        return ConversationHandler.END


def edit_get_id(update, context):
    common_query = """
    SELECT video_data.id, video_data.title, video_data.description, video_data.keywords, video_data.file_id, 
    video_data.user_id, video_data.user_name, channel_messages.msg_id, channel_messages.chat_id FROM video_data 
    LEFT JOIN channel_messages ON video_data.id=channel_messages.video_id WHERE 
    """

    if update['message']['video']:
        result = utils.execute_read_query(
            query=common_query+"video_data.file_unique_id = ?",
            parameters=(update['message']['video']['file_unique_id'],)
        )
    elif update['message']['text']:
        result = utils.execute_read_query(query=common_query+"video_data.id = ?", parameters=(update['message']['text'],))
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text=_("need_video_or_id"))
        return

    if result:
        dict_result = dict(result[0])
        context.user_data.update(
            {
                'edit': {
                    'id': dict_result['id'],
                    'title': dict_result['title'],
                    'description': dict_result['description'],
                    'keywords': dict_result['keywords'],
                    'file_id': dict_result['file_id'],
                    'user_id': dict_result['user_id'],
                    'user_name': dict_result['user_name'],
                    'msg_id': dict_result['msg_id'],
                    'chat_id': dict_result['chat_id'],
                }
            }
        )
        if str(update.effective_user.id) != context.user_data['edit']['user_id'] and \
                str(update.effective_user.username) not in settings['admin_usernames']:
            context.bot.send_message(chat_id=update.effective_chat.id, text=_("edit_no_permissions"))
            return ConversationHandler.END
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text=_("error_video_not_found"))
        return ConversationHandler.END

    context.bot.send_video(chat_id=update.effective_chat.id,
                           video=context.user_data['edit']['file_id'],
                           caption=_("video_info").format(context.user_data['edit']['id'],
                                                          context.user_data['edit']['title'],
                                                          context.user_data['edit']['description'],
                                                          context.user_data['edit']['keywords']),
                           parse_mode="HTML")

    menu_opt = [[InlineKeyboardButton(_("video"), callback_data='video'),
                InlineKeyboardButton(_("title"), callback_data='title')],
                [InlineKeyboardButton(_("description"), callback_data='desc'),
                InlineKeyboardButton(_("keywords"), callback_data='keywords')],
                [InlineKeyboardButton(_("cancel"), callback_data='cancel')]]
    context.bot.send_message(chat_id=update.effective_chat.id, text=_("edit_choose_option"),
                             reply_markup=InlineKeyboardMarkup(menu_opt))
    return EDIT_CHOSEN_OPTION


def on_chosen_edit_option(update, context):
    update.callback_query.answer()
    if update.callback_query.data == 'title':
        update.callback_query.edit_message_text(_("title"))
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text=_("edit_send_title").format(settings["max_title_length"]))
        return EDIT_TITLE
    elif update.callback_query.data == 'desc':
        update.callback_query.edit_message_text(_("description"))
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text=_("edit_send_desc").format(settings["max_desc_length"]))
        return EDIT_DESC
    elif update.callback_query.data == 'keywords':
        update.callback_query.edit_message_text(_("keywords"))
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text=_("edit_send_keywords").format(settings["max_kwords_length"]))
        return EDIT_KEYWORDS
    elif update.callback_query.data == 'video':
        update.callback_query.edit_message_text(_("video"))
        context.bot.send_message(chat_id=update.effective_chat.id, text=_("edit_send_video"))
        return EDIT_VIDEO
    elif update.callback_query.data == 'cancel':
        update.callback_query.edit_message_text(_("cancel"))
        return ConversationHandler.END
    else:
        update.callback_query.edit_message_text(chat_id=update.effective_chat.id, text=_("unknown_command"))
        return ConversationHandler.END


def edit_title(update, context):
    if update['message']['text'] and len(update['message']['text']) <= settings["max_title_length"]:
        if utils.execute_query(query="UPDATE video_data SET title = ? WHERE id = ?",
                         parameters=(update['message']['text'], context.user_data['edit']['id'])):
            utils.videos_info.update_model()
            context.bot.send_message(chat_id=update.effective_chat.id, text=_("edit_title_ok"))
        else:
            context.bot.send_message(chat_id=update.effective_chat.id, text=_("error"))
        return ConversationHandler.END
    else:
        if not update['message']['text']:
            context.bot.send_message(chat_id=update.effective_chat.id, text=_("edit_need_title"))
        else:
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text=_("error_title_length").format(len(update['message']['text']),
                                                                         settings['max_title_length']))


def edit_desc(update, context):
    if update['message']['text'] and len(update['message']['text']) <= settings["max_desc_length"]:
        context.user_data['edit'].update({'description': update['message']['text']})

        if utils.execute_query(query="UPDATE video_data SET description = ? WHERE id = ?",
                               parameters=(update['message']['text'], context.user_data['edit']['id'])):
            utils.videos_info.update_model()
            context.bot.send_message(chat_id=update.effective_chat.id, text=_("edit_desc_ok"))
            if context.user_data['edit']['msg_id']:
                context.bot.edit_message_caption(
                    chat_id=context.user_data['edit']['chat_id'], message_id=context.user_data['edit']['msg_id'],
                    caption=_("channel_info_caption").format(context.user_data['edit']['id'],
                                                             context.user_data['edit']['user_name'],
                                                             context.user_data['edit']['description'],
                                                             context.user_data['edit']['keywords']),
                    parse_mode="HTML")
        else:
            context.bot.send_message(chat_id=update.effective_chat.id, text=_("error"))
        return ConversationHandler.END
    else:
        if not update['message']['text']:
            context.bot.send_message(chat_id=update.effective_chat.id, text=_("edit_need_desc"))
        else:
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text=_("error_desc_length").format(len(update['message']['text']),
                                                                        settings['max_desc_length']))


def edit_keywords(update, context):
    if update['message']['text'] and len(update['message']['text']) <= settings["max_kwords_length"]:
        context.user_data['edit'].update({'keywords': update['message']['text']})
        if utils.execute_query(query="UPDATE video_data SET keywords = ? WHERE id = ?",
                               parameters=(context.user_data['edit']['keywords'], context.user_data['edit']['id'])):
            utils.videos_info.update_model()
            context.bot.send_message(chat_id=update.effective_chat.id, text=_("edit_keywords_ok"))
            if context.user_data['edit']['msg_id']:
                context.bot.edit_message_caption(
                    chat_id=context.user_data['edit']['chat_id'], message_id=context.user_data['edit']['msg_id'],
                    caption=_("channel_info_caption").format(context.user_data['edit']['id'],
                                                             context.user_data['edit']['user_name'],
                                                             context.user_data['edit']['description'],
                                                             context.user_data['edit']['keywords']),
                    parse_mode="HTML")
        else:
            context.bot.send_message(chat_id=update.effective_chat.id, text=_("error"))
        return ConversationHandler.END
    else:
        if not update['message']['text']:
            context.bot.send_message(chat_id=update.effective_chat.id, text=_("edit_need_keywords"))
        else:
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text=_("error_keywords_length").format(len(update['message']['text']),
                                                                            settings['max_kwords_length']))


def edit_video(update, context):
    if update['message']['video']:
        query = "UPDATE video_data SET file_id = ?, file_unique_id = ?, width = ?, height = ?, duration = ? WHERE id = ?"
        params = (update['message']['video']['file_id'], update['message']['video']['file_unique_id'],
                  update['message']['video']['width'], update['message']['video']['height'],
                  update['message']['video']['duration'], context.user_data['edit']['id'])

        if utils.execute_query(query=query, parameters=params):
            utils.videos_info.update_model()
            context.bot.send_message(chat_id=update.effective_chat.id, text=_("edit_video_ok"))
            if context.user_data['edit']['msg_id']:
                context.bot.edit_message_media(
                    chat_id=context.user_data['edit']['chat_id'], message_id=context.user_data['edit']['msg_id'],
                    media=InputMediaVideo(
                        update['message']['video']['file_id'],
                        caption=_("channel_info_caption").format(context.user_data['edit']['id'],
                                                                 context.user_data['edit']['user_name'],
                                                                 context.user_data['edit']['description'],
                                                                 context.user_data['edit']['keywords']),
                        parse_mode="HTML"))
        else:
            context.bot.send_message(chat_id=update.effective_chat.id, text=_("error"))
        return ConversationHandler.END
    else:
        if not update['message']['video']:
            context.bot.send_message(chat_id=update.effective_chat.id, text=_("edit_need_video"))


# Conversation handler
edit_conv_handler = ConversationHandler(
    entry_points=[CommandHandler('edit', edit_start)],
    states={
        EDIT_GET_ID: [MessageHandler((Filters.text | Filters.video) & (~Filters.command), edit_get_id)],
        EDIT_CHOSEN_OPTION: [CallbackQueryHandler(on_chosen_edit_option, pattern='^(video|title|desc|keywords|cancel)$')],
        EDIT_TITLE: [MessageHandler((Filters.text & ~Filters.command), edit_title)],
        EDIT_DESC: [MessageHandler((Filters.text & ~Filters.command), edit_desc)],
        EDIT_KEYWORDS: [MessageHandler((Filters.text & ~Filters.command), edit_keywords)],
        EDIT_VIDEO: [MessageHandler((Filters.video & ~Filters.command), edit_video)],
    },
    fallbacks=[CommandHandler('cancel', cancel)],
    allow_reentry=True
)
