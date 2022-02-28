-- Created by Selutario <selutario@gmail.com>.
-- This program is a free software; you can redistribute it and/or modify it under the terms of GPLv3

CREATE TABLE IF NOT EXISTS video_data (
      private_id INTEGER PRIMARY KEY AUTOINCREMENT,
      id TEXT UNIQUE NOT NULL,
      title TEXT NOT NULL,
      description TEXT,
      keywords TEXT NOT NULL,
      file_id TEXT NOT NULL,
      duration INTEGER,
      file_size INTEGER,
      file_unique_id TEXT,
      height INTEGER,
      width INTEGER,
      thumb_file_id TEXT,
      thumb_file_size INTEGER,
      thumb_file_unique_id TEXT,
      thumb_height INTEGER,
      thumb_width INTEGER,
      user_id TEXT,
      FOREIGN KEY (user_id) REFERENCES users (id)
);
CREATE INDEX IF NOT EXISTS id ON video_data (id);

CREATE TABLE IF NOT EXISTS sent_videos (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          query TEXT,
          video_id TEXT REFERENCES video_data(id) ON DELETE CASCADE,
          user_id TEXT NOT NULL,
          date DATE,
          FOREIGN KEY (user_id) REFERENCES users (id)
);

CREATE TABLE IF NOT EXISTS channel_messages (
    msg_id TEXT UNIQUE,
    chat_id TEXT,
    video_id TEXT UNIQUE,
    PRIMARY KEY (msg_id, video_id),
    FOREIGN KEY (video_id) REFERENCES video_data (id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS video_id ON channel_messages (video_id);

CREATE TABLE IF NOT EXISTS sent_random (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          title TEXT,
          video_id TEXT,
          user_id TEXT NOT NULL,
          date DATE,
          FOREIGN KEY (video_id) REFERENCES video_data (id) ON DELETE CASCADE,
          FOREIGN KEY (user_id) REFERENCES users (id)
);

CREATE TABLE IF NOT EXISTS users (
          id TEXT PRIMARY KEY,
          user_name TEXT,
          first_name TEXT,
          last_name TEXT
);
