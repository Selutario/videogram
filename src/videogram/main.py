#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Created by Selutario <selutario@gmail.com>.
# This program is a free software; you can redistribute it and/or modify it under the terms of GPLv3

import os

from telegram.ext import Updater, CommandHandler, InlineQueryHandler, ChosenInlineResultHandler, ChatMemberHandler

from videogram.handlers import common_handlers, search_handlers
from videogram.handlers.delete_handlers import delete_conv_handler
from videogram.handlers.edit_handlers import edit_conv_handler
from videogram.handlers.upload_handlers import upload_conv_handler

def main():
    # Start bot
    try:
        updater = Updater(token=os.environ['TOKEN'], use_context=True)
        dp = updater.dispatcher
    except Exception as e:
        print(f'Could not find the bot token. Please set the environment variable "TOKEN": {e}')
        exit(1)

    dp.add_handler(ChatMemberHandler(common_handlers.init, 'MY_CHAT_MEMBER'))

    # Common commands - answer in Telegram
    dp.add_handler(CommandHandler("start", common_handlers.start))
    dp.add_handler(CommandHandler("sent_videos", common_handlers.get_sent_videos))

    # Conversation handlers
    dp.add_handler(upload_conv_handler)
    dp.add_handler(edit_conv_handler)
    dp.add_handler(delete_conv_handler)

    # Search & send video
    dp.add_handler(InlineQueryHandler(search_handlers.inline_search))
    dp.add_handler(ChosenInlineResultHandler(search_handlers.on_chosen_video))

    # log all errors
    dp.add_error_handler(common_handlers.error)

    # Start the Bot
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
