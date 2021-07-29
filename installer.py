# Created by Selutario <selutario@gmail.com>.
# This program is a free software; you can redistribute it and/or modify it under the terms of GPLv3

# Simple installer script

from os import getcwd, path
from pathlib import Path
from sqlite3 import connect
from threading import Thread

from ruamel.yaml import YAML
from telegram import ext, error

from utils.common import DB_PATH, SCHEMA_PATH, DB_BACKUP_SCRIPT

telegram_inst_step = 0
yaml = YAML()
with open('settings.yaml', 'r') as f:
    settings = yaml.load(f)


def shutdown():
    updater.stop()
    updater.is_idle = False


def start(update, context):
    global telegram_inst_step

    if telegram_inst_step == 0:
        try:
            if update.message.chat.type == 'private':
                print(f"\033[92mOk\033[0m (User ID {update.message['chat']['id']})")
                print("\n6. Join the bot to a channel (public or private) as administrator, and post a message in it.")
                settings['backup_user_id'] = update.message['chat']['id']
                settings['admin_usernames'] = list([update.message['chat']['username']])
                telegram_inst_step += 1
        except Exception:
            print(f"There has been an error. Make sure to send a message directly to the bot.")
    elif telegram_inst_step == 1:
        try:
            print(f"\033[92mOk\033[0m (Channel ID: {update['channel_post']['chat']['id']})")
            settings['channel_id'] = update['channel_post']['chat']['id']
            with open('settings.yaml', 'w') as f:
                yaml.dump(settings, f)

            print("\n\nPlease wait... ")
            Thread(target=shutdown).start()
        except Exception :
            print(f"There has been an error. Make sure to put the bot on a channel and post a message on that channel.")


def create_cronjob_backup(backup_hour):
    from crontab import CronTab
    cron = CronTab(user=True)
    job = cron.new(command=f'python3 {DB_BACKUP_SCRIPT}')
    job.setall(f"0 {backup_hour} * * 6")
    cron.write()
    print(f'\033[92mOk\033[0m (The bot will send you a backup every saturday at {backup_hour}h. You can modify this with "crontab -e")')


if __name__ == '__main__':

    print(f"PATH: {path.join(getcwd(), DB_BACKUP_SCRIPT)}")

    print("\n1. Creating DB... ")
    with open(SCHEMA_PATH, 'r') as f:
        with connect(DB_PATH) as connection:
            cursor = connection.cursor()
            try:
                sql_as_string = f.read()
                cursor.executescript(sql_as_string)
                print('\033[92mOk\033[0m')
            except Exception as e:
                print(f"Error: {e}")

    response = input("\n2. Do you want the bot to send you a backup of the DB every day? (yes/no) [yes]: ") or 'yes'
    if response == 'yes':
        while True:
            try:
                backup_hour = int(input("Choose the time (0-23) at which the backup will be sent to you [4]: ") or 4)
                if backup_hour in range(24):
                    create_cronjob_backup(backup_hour)
                    break
            except ValueError:
                print("The value is not an integer.")
    else:
        print('\033[92mOk\033[0m')

    settings['bot_name'] = input("\n3. Enter the name of your bot [@Videos_bot]: ").replace('@', '').replace(' ', '_') or 'videos_bot'
    print('\033[92mOk\033[0m')

    while True:
        try:
            settings['token_path'] = input("\n4. Save your bot's token in a file and enter its "
                                           "absolute path: ").replace("'", "").replace('"', '')
            updater = ext.Updater(token=Path(settings['token_path']).read_text().rstrip(), use_context=True)
            dp = updater.dispatcher
            print("\033[92mOk\033[0m\n\n5. Write anything to your bot via Telegram.")
            break
        except error.InvalidToken:
            print("The token is not valid.")
        except Exception as e:
            print(f"I could not access the token: {e}")

    dp.add_handler(ext.MessageHandler(ext.Filters.text, start))

    updater.start_polling()
    updater.idle()
