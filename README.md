<p align="center">
  <img src="https://user-images.githubusercontent.com/23361101/156668909-02ef8410-d8ed-4fac-b354-75facb9f84d0.png" alt="Videogram" height="200"/>
</p>


# Description
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
3. Also enable inline feedback for your bot at [@BotFather](https://t.me/botfather) via Telegram:
   ```
   /setinlinefeedback
   ```
3. Clone this repository in your host:
   ```
   git clone https://github.com/Selutario/videogram.git
   cd videogram
   ```
4. Create `.env` file:
   ```
   cp .env.example .env
   ```
5. Run this to get your UID and GID:
   ```
   id
   ```
   or
   ```
   id -u # UID
   id -g # GID
   ```
6. Edit the `.env` file to add the token obtained in step `1.` and the UID and GID in step `5.`. For example:
   ```
   VIDEOGRAM_TOKEN=6092251042:AAGxRqK5QlZN7AlhBgVQIzSKAEy7nigsW_8
   UID=1000
   GID=1000
   ```
7. Build and run the container using docker-compose:
   ```
   docker compose up -d
   ```

## Usage

The bot is finally running. In order to use it for the first time, you will need to create a Telegram channel where the bot will publish all the new uploaded videos. It doesn't mind whether it is public or private. Then, add the bot to the channel (it must be administrator). Once it is added, a message like this one should appear:
<details>
<summary>Image</summary>

![image](https://user-images.githubusercontent.com/23361101/236672171-bd34fce2-e423-4690-aaa1-cf2f44cb5fd5.png)

</details>

Now is time to upload your first video. Talk to your bot and send `/upload` command. It will ask you for some extra information:

<details>
<summary>Image</summary>

![image](https://user-images.githubusercontent.com/23361101/236672154-318e3921-25d2-46a3-8f95-cd134fe08372.png)

</details>

All the uploaded videos will be published in the channel that you created before. 

<details>
<summary>Image</summary>

![image](https://user-images.githubusercontent.com/23361101/236672221-3e03bf7c-6560-477f-ac6a-127edc6881ec.png)

</details>

Everybody can now query the bot in all conversations to search and send any of the uploaded videos:

<details>
<summary>Image</summary>

![image](https://user-images.githubusercontent.com/23361101/236672332-1194b3d5-3ba3-4a8f-a6fb-5da4fed35f3c.png)

</details>

## Available commands

The bot will answers to these commands:
- `/random`: Get a randomly chosen video.
- `/upload`: Upload a new video.
- `/edit`: Edit the file, title, description or keywords of any previously uploaded video. Only administrator or the user who uploaded the video can edit it.
- `/delete`: Delete any video. Only administrators can delete videos by default.
- `/get_sent_videos`: Get history of the videos sent by all users.
- `/get_db_backup`: Get a backup of the database file.

## Configuration

The configuration file will allow you to modify the administrator users, ban users, change language, enable or disable the uploading, editing or deleting of videos, etc.

The file can be found in the repository under this path:
```
config/settings/settings.yaml
```