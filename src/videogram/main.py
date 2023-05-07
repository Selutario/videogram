#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Created by Selutario <selutario@gmail.com>.
# This program is a free software; you can redistribute it and/or modify it under the terms of GPLv3

import os

from telegram.ext import CommandHandler, InlineQueryHandler, ChosenInlineResultHandler, ChatMemberHandler, Application
from videogram.handlers import common_handlers, search_handlers, admin_handlers
from videogram.handlers.delete_handlers import delete_conv_handler
from videogram.handlers.edit_handlers import edit_conv_handler
from videogram.handlers.upload_handlers import upload_conv_handler


def main():
    # Start bot
    try:
        application = Application.builder().token(os.environ['TOKEN']).build()
    except Exception as e:
        print(f'Could not find the bot token. Please set the environment variable "TOKEN": {e}')
        exit(1)

    # Admin handlers
    application.add_handler(ChatMemberHandler(admin_handlers.init, 'MY_CHAT_MEMBER'))
    application.add_handler(CommandHandler("get_sent_videos", admin_handlers.get_sent_videos))
    application.add_handler(CommandHandler("get_db_backup", admin_handlers.send_db_backup))

    # Common handlers
    application.add_handler(CommandHandler("start", common_handlers.start))

    # Conversation handlers
    application.add_handler(upload_conv_handler)
    application.add_handler(edit_conv_handler)
    application.add_handler(delete_conv_handler)

    # Search & send video
    application.add_handler(InlineQueryHandler(search_handlers.inline_search))
    application.add_handler(ChosenInlineResultHandler(search_handlers.on_chosen_video))

    # Log all errors
    application.add_error_handler(common_handlers.error)

    # Run the bot until the user presses Ctrl-C
    application.run_polling()


if __name__ == '__main__':
    main()
