# Created by Selutario <selutario@gmail.com>.
# This program is a free software; you can redistribute it and/or modify it under the terms of GPLv3

import html
from uuid import uuid4

import videogram.utils.orm as orm
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ConversationHandler, CommandHandler, filters, MessageHandler, CallbackQueryHandler
from videogram.handlers.common_handlers import cancel
from videogram.utils import utils
from videogram.utils.common import settings, INVALID_MIME_TYPES

UPLD_GET_VID, UPLD_TITLE, UPLD_DESC, UPLD_KEYWORDS, UPLD_CHECK_SAME = range(5)


async def upld_start(update, context):
    if not utils.initialized():
        await context.bot.send_message(chat_id=update.effective_chat.id, text=_("init_required"))
        return ConversationHandler.END
    elif (update.effective_user.username in settings['admin_usernames'] or
          (settings['upload_enabled'] and update.effective_user.username not in settings['banned_usernames'] and
           (not settings['closed_circle'] or update.effective_user.username in settings['closed_circle']))):
        await  context.bot.send_message(chat_id=update.effective_chat.id, text=_("upld_send_video"))
        return UPLD_GET_VID
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=_("upload_disabled"))
        return ConversationHandler.END


async def upld_video(update, context):
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
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=_("error_video_length").format(context.user_data['upld']['duration'], settings['max_video_length']))
    elif update['message']['video']['mime_type'] in INVALID_MIME_TYPES:
        await  context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=_("error_video_type").format(update['message']['video']['mime_type']))
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text=_("upld_send_title").format(settings['max_title_length']))
        return UPLD_TITLE


async def upld_title(update, context):
    if len(update['message']['text']) <= settings['max_title_length']:
        context.user_data['upld'].update({'title': update['message']['text']})
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text=_("upld_send_desc").format(settings["max_desc_length"]))
        return UPLD_DESC
    else:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=_("error_title_length").format(len(update['message']['text']), settings['max_title_length']))


async def upld_desc(update, context):
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
            await context.bot.send_video(chat_id=update.effective_chat.id,
                                         video=utils.videos_info.videos_info_list[result[0]].file_id,
                                         caption=_("upld_same_video_form"), reply_markup=InlineKeyboardMarkup(menu_opt))
            return UPLD_CHECK_SAME
        else:
            await context.bot.send_message(
                chat_id=update.effective_chat.id, text=_("upld_send_keywords").format(settings['max_kwords_length']))
            return UPLD_KEYWORDS
    else:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=_("error_desc_length").format(len(update['message']['text']), settings['max_desc_length']))


async def upld_keywords(update, context):
    if len(update['message']['text']) <= settings['max_kwords_length']:
        context.user_data['upld'].update({'keywords': update['message']['text']})

        if context.user_data['upld']['user_name']:
            user = context.user_data['upld']['user_name']
        else:
            user = context.user_data['upld']['first_name']

        video_msg = await context.bot.send_video(
            chat_id=settings['channel_id'], video=context.user_data['upld']['file_id'],
            caption=_("channel_info_caption").format(context.user_data['upld']['id'],
                                                     html.escape(user),
                                                     html.escape(context.user_data['upld']['desc']),
                                                     html.escape(context.user_data['upld']['keywords'])),
            parse_mode="HTML")

        try:
            user = orm.Users(
                user_id=update.effective_user.id,
                user_name=update.effective_user.username,
                first_name=update.effective_user.first_name,
                last_name=update.effective_user.last_name
            )
            orm.session.merge(user)

            video = orm.VideoData(
                video_id=context.user_data['upld']['id'],
                title=context.user_data['upld']['title'],
                description=context.user_data['upld']['desc'],
                keywords=context.user_data['upld']['keywords'],
                file_id=video_msg['video']['file_id'],
                file_unique_id=video_msg['video']['file_unique_id'],
                width=video_msg['video']['width'],
                height=video_msg['video']['height'],
                duration=video_msg['video']['duration'],
                user_id=context.user_data['upld']['user_id']
            )
            orm.session.add(video)

            channel_message = orm.ChannelMessages(
                msg_id=video_msg['message_id'],
                chat_id=video_msg['chat']['id'],
                video_id=context.user_data['upld']['id']
            )
            orm.session.add(channel_message)
            orm.session.commit()

            utils.videos_info.update_model()
            await context.bot.send_message(
                chat_id=update.effective_chat.id, text=_("upld_video_ok").format(context.user_data['upld']['id']),
                parse_mode="HTML")

        except Exception:
            await context.bot.send_message(chat_id=update.effective_chat.id, text=_("error"))
            return ConversationHandler.END

        return ConversationHandler.END
    else:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=_("error_keywords_length").format(len(update['message']['text']), settings['max_kwords_length']))


async def upld_on_chosen_option(update, context):
    await update.callback_query.answer()

    if update.callback_query.data == 'same':
        await update.callback_query.edit_message_caption(_("upld_same_video"))
        await cancel(update, context)
    elif update.callback_query.data == 'different':
        await update.callback_query.edit_message_caption(_("upld_diff_video"))
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=_("upld_send_keywords").format(settings['max_kwords_length']))
        return UPLD_KEYWORDS


# Conversation handler
upload_conv_handler = ConversationHandler(
    entry_points=[CommandHandler('upload', upld_start)],
    states={
        UPLD_GET_VID: [MessageHandler(filters.VIDEO, upld_video)],
        UPLD_TITLE: [MessageHandler((filters.TEXT & ~filters.COMMAND), upld_title)],
        UPLD_DESC: [MessageHandler((filters.TEXT & ~filters.COMMAND), upld_desc)],
        UPLD_CHECK_SAME: [CallbackQueryHandler(upld_on_chosen_option, pattern='^(same|different)$')],
        UPLD_KEYWORDS: [MessageHandler((filters.TEXT & ~filters.COMMAND), upld_keywords)]
    },
    fallbacks=[CommandHandler('cancel', cancel)],
    allow_reentry=True
)
