#!/usr/bin/env python3
# Created by Selutario <selutario@gmail.com>.
# This program is a free software; you can redistribute it and/or modify it under the terms of GPLv3

from pathlib import Path

from telegram import Bot

from videogram.utils.common import settings, DB_PATH

def send_backup():
    bot = Bot(token=Path(settings['token_path']).read_text().rstrip())
    bot.sendDocument(chat_id=settings['backup_user_id'], document=open(DB_PATH, 'rb'))


if __name__ == '__main__':
    send_backup()
