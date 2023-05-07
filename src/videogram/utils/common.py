# Created by Selutario <selutario@gmail.com>.
# This program is a free software; you can redistribute it and/or modify it under the terms of GPLv3

import gettext
import os
import shutil
import sys
from pathlib import Path

from appdirs import site_config_dir
from ruamel.yaml import YAML

yaml = YAML()

APP_NAME = 'videogram'
BOT_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BOT_PATH, 'data')
DEFAULT_SETTINGS_PATH = os.path.join(DATA_PATH, 'settings.yaml')

LOGS_PATH = os.path.join(DATA_PATH, 'bot.log')

CONFIG_DIR = site_config_dir(APP_NAME)
SETTINGS_DIR = os.path.join(CONFIG_DIR, 'settings')
DB_DIR = os.path.join(CONFIG_DIR, 'databases')

SETTINGS_PATH = os.path.join(SETTINGS_DIR, 'settings.yaml')
DB_PATH = os.path.join(DB_DIR, 'videogram.db')

try:
    not os.path.exists(SETTINGS_DIR) and Path(SETTINGS_DIR).mkdir(parents=True, exist_ok=True)
    not os.path.exists(DB_DIR) and Path(DB_DIR).mkdir(parents=True, exist_ok=True)
    if not os.path.exists(SETTINGS_PATH):
        shutil.copyfile(DEFAULT_SETTINGS_PATH, SETTINGS_PATH)

    with open(SETTINGS_PATH, 'r') as f:
        settings = yaml.load(f)
except Exception as e:
    print(f"There was an error while creating or accessing the data folder: {e}")
    sys.exit(1)

results_limit = min(settings['results_limit'], 50)
empty_query_videos = min(settings['empty_query_videos'], 50)

locale_path = os.path.join(BOT_PATH, 'locale')
language = gettext.translation(settings['language'], locale_path, [settings['language']])
language.install()

INVALID_MIME_TYPES = [
    'video/quicktime'
]
