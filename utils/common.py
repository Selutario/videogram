# Created by Selutario <selutario@gmail.com>.
# This program is a free software; you can redistribute it and/or modify it under the terms of GPLv3

from os.path import join, dirname, abspath
from yaml import safe_load
import gettext

BOT_PATH = dirname(dirname(abspath(__file__)))
DATA_PATH = join(BOT_PATH, 'data')
SCHEMA_PATH = join(DATA_PATH, 'schema_db.sql')
DB_PATH = join(DATA_PATH, 'bot.db')
DB_BACKUP_SCRIPT = join(BOT_PATH, 'scripts', 'db_backup.py')
LOGS_PATH = join(DATA_PATH, 'bot.log')
SETTINGS_PATH = join(DATA_PATH, 'settings.yaml')

with open(SETTINGS_PATH, 'r') as f:
    settings = safe_load(f)

results_limit = min(settings['results_limit'], 50)
empty_query_videos = min(settings['empty_query_videos'], 50)

locale_path = join(BOT_PATH, 'locale')
language = gettext.translation(settings['language'], locale_path, [settings['language']])
language.install()

INVALID_MIME_TYPES = [
    'video/quicktime'
]
