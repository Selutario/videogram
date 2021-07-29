# Created by Selutario <selutario@gmail.com>.
# This program is a free software; you can redistribute it and/or modify it under the terms of GPLv3

from os.path import join, dirname, abspath
from yaml import safe_load
import gettext
from locale import getdefaultlocale

BOT_PATH = dirname(dirname(abspath(__file__)))
DATA_PATH = join(BOT_PATH, 'data')
SCHEMA_PATH = join(DATA_PATH, 'schema_db.sql')
DB_PATH = join(DATA_PATH, 'bot.db')
DB_BACKUP_SCRIPT = join(BOT_PATH, 'scripts', 'db_backup.py')
LOGS_PATH = join(DATA_PATH, 'bot.log')
SETTINGS_PATH = join(DATA_PATH, 'settings.yaml')

locale_path = join(BOT_PATH, 'locale')
current_locale, encoding = getdefaultlocale()
language = gettext.translation(current_locale, locale_path, [current_locale])
language.install()

with open(SETTINGS_PATH, 'r') as f:
    settings = safe_load(f)
