<p align="center">
  <img src="https://user-images.githubusercontent.com/23361101/156668909-02ef8410-d8ed-4fac-b354-75facb9f84d0.png" alt="Videogram" height="200"/>
</p>


## Description
Telegram bot to search and send videos in any chat (inline, like [@gif](https://telegram.me/gif)). Users can upload/edit/delete their own videos.

## How to install
1. Get a Telegram API key at [@BotFather](https://t.me/botfather) via Telegram:
   ```
   /newbot
   ```
2. Enable inline mode for your bot at [@BotFather](https://t.me/botfather) via Telegram:
   ```
   /setinline
   ```
3. Clone this repository in your host:
   ```
   $ git clone https://github.com/Selutario/Videogram.git
   ```
4. *[Optional]* Create a virtual env:
   ```
   $ cd Videogram/ && mkdir venv && python3 -m venv ./venv && source ./venv/bin/activate
   ```
5. Run the installer and follow the instructions:
   ```
   $ make setup
   ```
6. Run the bot:
   ```
   $ make run
   ```
