# Created by Selutario <selutario@gmail.com>.
# This program is a free software; you can redistribute it and/or modify it under the terms of GPLv3

import html

import videogram.utils.orm as orm
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, InputMediaVideo
from telegram.ext import ConversationHandler, CommandHandler, MessageHandler, filters, CallbackQueryHandler
from videogram.handlers.common_handlers import cancel
from videogram.utils import utils
from videogram.utils.common import settings, INVALID_MIME_TYPES

EDIT_GET_ID, EDIT_MENU, EDIT_CHOSEN_OPTION, EDIT_TITLE, EDIT_DESC, EDIT_KEYWORDS, EDIT_VIDEO = range(7)


async def edit_start(update, context):
    if not utils.initialized():
        await context.bot.send_message(chat_id=update.effective_chat.id, text=_("init_required"))
        return ConversationHandler.END
    elif (update.effective_user.username in settings['admin_usernames'] or
          (settings['edit_enabled'] and update.effective_user.username not in settings['banned_usernames'] and
           (not settings['closed_circle'] or update.effective_user.username in settings['closed_circle']))):
        await context.bot.send_message(chat_id=update.effective_chat.id, text=_("edit_start"))
        return EDIT_GET_ID
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=_("edit_disabled"))
        return ConversationHandler.END


async def edit_get_id(update, context):
    if update['message']['video']:
        result = orm.session.query(orm.VideoData, orm.ChannelMessages, orm.Users).join(
            orm.ChannelMessages, isouter=True).join(orm.Users, isouter=True).filter(
            orm.VideoData.file_unique_id == update['message']['video']['file_unique_id']).first()
    elif update['message']['text']:
        result = orm.session.query(orm.VideoData, orm.ChannelMessages, orm.Users).join(
            orm.ChannelMessages, isouter=True).join(orm.Users, isouter=True).filter(
            orm.VideoData.id == update['message']['text']).first()
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=_("need_video_or_id"))
        return

    if result:
        context.user_data.update({
            'video': result[0],
            'channel_message': result[1],
            'user': result[2]
        })

        if str(update.effective_user.id) != context.user_data['user'].id and \
                str(update.effective_user.username) not in settings['admin_usernames']:
            await context.bot.send_message(chat_id=update.effective_chat.id, text=_("edit_no_permissions"))
            return ConversationHandler.END
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=_("error_video_not_found"))
        return ConversationHandler.END

    await context.bot.send_video(chat_id=update.effective_chat.id,
                                 video=context.user_data['video'].file_id,
                                 caption=_("video_info").format(context.user_data['video'].id,
                                                                html.escape(context.user_data['video'].title),
                                                                html.escape(context.user_data['video'].description),
                                                                html.escape(context.user_data['video'].keywords)),
                                 parse_mode="HTML")

    menu_opt = [[InlineKeyboardButton(_("video"), callback_data='video'),
                 InlineKeyboardButton(_("title"), callback_data='title')],
                [InlineKeyboardButton(_("description"), callback_data='desc'),
                 InlineKeyboardButton(_("keywords"), callback_data='keywords')],
                [InlineKeyboardButton(_("cancel"), callback_data='cancel')]]
    await context.bot.send_message(chat_id=update.effective_chat.id, text=_("edit_choose_option"),
                                   reply_markup=InlineKeyboardMarkup(menu_opt))
    return EDIT_CHOSEN_OPTION


async def on_chosen_edit_option(update, context):
    await update.callback_query.answer()

    if update.callback_query.data == 'title':
        await update.callback_query.edit_message_text(_("title"))
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text=_("edit_send_title").format(settings["max_title_length"]))
        return EDIT_TITLE
    elif update.callback_query.data == 'desc':
        await update.callback_query.edit_message_text(_("description"))
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text=_("edit_send_desc").format(settings["max_desc_length"]))
        return EDIT_DESC
    elif update.callback_query.data == 'keywords':
        await update.callback_query.edit_message_text(_("keywords"))
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text=_("edit_send_keywords").format(settings["max_kwords_length"]))
        return EDIT_KEYWORDS
    elif update.callback_query.data == 'video':
        await update.callback_query.edit_message_text(_("video"))
        await context.bot.send_message(chat_id=update.effective_chat.id, text=_("edit_send_video"))
        return EDIT_VIDEO
    elif update.callback_query.data == 'cancel':
        await update.callback_query.edit_message_text(_("cancel"))
        return ConversationHandler.END
    else:
        await update.callback_query.edit_message_text(chat_id=update.effective_chat.id, text=_("unknown_command"))
        return ConversationHandler.END


async def edit_title(update, context):
    if update['message']['text'] and len(update['message']['text']) <= settings["max_title_length"]:
        try:
            context.user_data['video'].title = update['message']['text']
            orm.session.add(context.user_data['video'])
            orm.session.commit()

            utils.videos_info.update_model()
            await context.bot.send_message(chat_id=update.effective_chat.id, text=_("edit_title_ok"))
        except Exception:
            await context.bot.send_message(chat_id=update.effective_chat.id, text=_("error"))

        return ConversationHandler.END
    else:
        if not update['message']['text']:
            await context.bot.send_message(chat_id=update.effective_chat.id, text=_("edit_need_title"))
        else:
            await context.bot.send_message(chat_id=update.effective_chat.id,
                                           text=_("error_title_length").format(len(update['message']['text']),
                                                                               settings['max_title_length']))
        return EDIT_TITLE


async def edit_desc(update, context):
    if update['message']['text'] and len(update['message']['text']) <= settings["max_desc_length"]:
        try:
            context.user_data['video'].description = update['message']['text']
            orm.session.add(context.user_data['video'])
            orm.session.commit()
            utils.videos_info.update_model()

            if context.user_data['channel_message'].msg_id:
                await context.bot.edit_message_caption(
                    chat_id=context.user_data['channel_message'].chat_id,
                    message_id=context.user_data['channel_message'].msg_id,
                    caption=_("channel_info_caption").format(context.user_data['video'].id,
                                                             html.escape(context.user_data['user'].user_name or
                                                                         context.user_data['user'].last_name),
                                                             html.escape(context.user_data['video'].description),
                                                             html.escape(context.user_data['video'].keywords)),
                    parse_mode="HTML")

            await context.bot.send_message(chat_id=update.effective_chat.id, text=_("edit_desc_ok"))
        except Exception:
            await context.bot.send_message(chat_id=update.effective_chat.id, text=_("error"))
        return ConversationHandler.END

    else:
        if not update['message']['text']:
            await context.bot.send_message(chat_id=update.effective_chat.id, text=_("edit_need_desc"))
        else:
            await context.bot.send_message(chat_id=update.effective_chat.id,
                                           text=_("error_desc_length").format(len(update['message']['text']),
                                                                              settings['max_desc_length']))
        return EDIT_DESC


async def edit_keywords(update, context):
    if update['message']['text'] and len(update['message']['text']) <= settings["max_kwords_length"]:
        try:
            context.user_data['video'].keywords = update['message']['text']
            orm.session.add(context.user_data['video'])
            orm.session.commit()
            utils.videos_info.update_model()

            if context.user_data['channel_message'].msg_id:
                await context.bot.edit_message_caption(
                    chat_id=context.user_data['channel_message'].chat_id,
                    message_id=context.user_data['channel_message'].msg_id,
                    caption=_("channel_info_caption").format(context.user_data['video'].id,
                                                             html.escape(context.user_data['user'].user_name or
                                                                         context.user_data['user'].last_name),
                                                             html.escape(context.user_data['video'].description),
                                                             html.escape(context.user_data['video'].keywords)),
                    parse_mode="HTML")

            await context.bot.send_message(chat_id=update.effective_chat.id, text=_("edit_keywords_ok"))
        except Exception:
            await context.bot.send_message(chat_id=update.effective_chat.id, text=_("error"))
        return ConversationHandler.END

    else:
        if not update['message']['text']:
            await context.bot.send_message(chat_id=update.effective_chat.id, text=_("edit_need_keywords"))
        else:
            await context.bot.send_message(chat_id=update.effective_chat.id,
                                           text=_("error_keywords_length").format(len(update['message']['text']),
                                                                                  settings['max_kwords_length']))
        return EDIT_KEYWORDS


async def edit_video(update, context):
    if update['message']['video']:
        if update['message']['video']['duration'] > settings['max_video_length']:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=_("error_video_length").format(update['message']['video']['duration'],
                                                    settings['max_video_length']))
            return EDIT_VIDEO
        elif update['message']['video']['mime_type'] in INVALID_MIME_TYPES:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=_("error_video_type").format(update['message']['video']['mime_type']))
            return EDIT_VIDEO
        else:
            try:
                context.user_data['video'].file_id = update['message']['video']['file_id']
                context.user_data['video'].file_unique_id = update['message']['video']['file_unique_id']
                context.user_data['video'].width = update['message']['video']['width']
                context.user_data['video'].height = update['message']['video']['height']
                context.user_data['video'].duration = update['message']['video']['duration']
                orm.session.add(context.user_data['video'])
                orm.session.commit()
                utils.videos_info.update_model()

                if context.user_data['channel_message'].msg_id:
                    await context.bot.edit_message_media(
                        chat_id=context.user_data['channel_message'].chat_id,
                        message_id=context.user_data['channel_message'].msg_id,
                        media=InputMediaVideo(
                            update['message']['video']['file_id'],
                            caption=_("channel_info_caption").format(context.user_data['video'].id,
                                                                     html.escape(context.user_data['user'].user_name or
                                                                                 context.user_data['user'].last_name),
                                                                     html.escape(
                                                                         context.user_data['video'].description),
                                                                     html.escape(context.user_data['video'].keywords)),
                            parse_mode="HTML"))

                await context.bot.send_message(chat_id=update.effective_chat.id, text=_("edit_video_ok"))
            except Exception:
                await context.bot.send_message(chat_id=update.effective_chat.id, text=_("error"))

            return ConversationHandler.END
    else:
        if not update['message']['video']:
            await context.bot.send_message(chat_id=update.effective_chat.id, text=_("edit_need_video"))
        return EDIT_VIDEO


# Conversation handler
edit_conv_handler = ConversationHandler(
    entry_points=[CommandHandler('edit', edit_start)],
    states={
        EDIT_GET_ID: [MessageHandler((filters.TEXT | filters.VIDEO) & (~filters.COMMAND), edit_get_id)],
        EDIT_CHOSEN_OPTION: [
            CallbackQueryHandler(on_chosen_edit_option, pattern='^(video|title|desc|keywords|cancel)$')],
        EDIT_TITLE: [MessageHandler((filters.TEXT & ~filters.COMMAND), edit_title)],
        EDIT_DESC: [MessageHandler((filters.TEXT & ~filters.COMMAND), edit_desc)],
        EDIT_KEYWORDS: [MessageHandler((filters.TEXT & ~filters.COMMAND), edit_keywords)],
        EDIT_VIDEO: [MessageHandler((filters.VIDEO & ~filters.COMMAND), edit_video)],
    },
    fallbacks=[CommandHandler('cancel', cancel)],
    allow_reentry=True
)
