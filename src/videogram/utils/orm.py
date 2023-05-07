# Created by Selutario <selutario@gmail.com>.
# This program is a free software; you can redistribute it and/or modify it under the terms of GPLv3


import datetime

from sqlalchemy import create_engine, Column, Integer, Text, DateTime, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base
from videogram.utils.common import DB_PATH

Base = declarative_base()

engine = create_engine(f'sqlite:///{DB_PATH}')
Session = sessionmaker(bind=engine)
session = Session()


class VideoData(Base):
    __tablename__ = 'video_data'

    private_id = Column(Integer, primary_key=True)
    id = Column(Text, unique=True, nullable=False, index=True)
    title = Column(Text, nullable=False)
    description = Column(Text, nullable=False)
    keywords = Column(Text, nullable=False)
    file_id = Column(Text, nullable=False)
    file_unique_id = Column(Text)
    height = Column(Integer)
    width = Column(Integer)
    duration = Column(Integer)
    user_id = Column(Text, ForeignKey('users.id'))

    def __init__(self, video_id: str = None, title: str = None, description: str = None, keywords: str = None,
                 file_id: str = None, file_unique_id: str = None, height: int = None, width: int = None,
                 duration: int = None, user_id: str = None):
        """Class constructor.

        Parameters
        ----------
        video_id : str
            Internal ID of the video resource.
        title : str
            Title of the video.
        description : str
            Description of the video.
        keywords : str
            Keywords of the video.
        file_id : str
            Telegram file ID of the video.
        file_unique_id : str
            Telegram file unique ID of the video.
        height : int
            Height of the video.
        width : int
            Width of the video.
        duration : int
            Duration of the video.
        user_id : str
            Telegram user ID of the video uploader.
        """
        self.id = video_id
        self.title = title
        self.description = description
        self.keywords = keywords
        self.file_id = file_id
        self.file_unique_id = file_unique_id
        self.height = height
        self.width = width
        self.duration = duration
        self.user_id = user_id

    def __repr__(self):
        return f'Video({self.private_id}, {self.title})'


class SentVideos(Base):
    __tablename__ = 'sent_videos'

    id = Column(Integer, primary_key=True)
    query = Column(Text)
    date = Column(DateTime)
    user_id = Column(Text, ForeignKey('users.id'))
    video_id = Column(Text, ForeignKey('video_data.id', ondelete='CASCADE'), index=True)

    def __init__(self, query: str = '', user_id: str = '', video_id: str = '', date: DateTime = None):
        """Class constructor.

        Parameters
        ----------
        query : str
            Query used to search the video.
        user_id : str
            Telegram user ID of the user who requested the video.
        video_id : str
            Internal ID of the video resource.
        date : DateTime
            Date when the video was sent.
        """
        self.query = query
        self.user_id = user_id
        self.video_id = video_id
        self.date = date or datetime.datetime.utcnow()

    def __repr__(self):
        return f'SentVideo({self.id}, {self.query})'


class ChannelMessages(Base):
    __tablename__ = 'channel_messages'

    msg_id = Column(Text, primary_key=True, unique=True)
    video_id = Column(Text, ForeignKey('video_data.id', ondelete='CASCADE'), primary_key=True, unique=True)
    chat_id = Column(Text)

    def __init__(self, msg_id: str, video_id: str, chat_id: str = ''):
        """Class constructor.

        Parameters
        ----------
        msg_id : str
            Telegram message ID of the video.
        video_id : str
            Internal ID of the video resource.
        chat_id : str
            Telegram chat ID of the channel.
        """
        self.msg_id = msg_id
        self.video_id = video_id
        self.chat_id = chat_id

    def __repr__(self):
        return f'ChannelMessage({self.msg_id}, {self.video_id})'


class Users(Base):
    __tablename__ = 'users'

    id = Column(Text, primary_key=True)
    user_name = Column(Text)
    first_name = Column(Text)
    last_name = Column(Text)

    def __init__(self, user_id: str, user_name: str = '', first_name: str = '', last_name: str = ''):
        """Class constructor.

        Parameters
        ----------
        user_id : str
            Telegram user ID of the user.
        user_name : str
            Telegram username of the user.
        first_name : str
            Telegram first name of the user.
        last_name : str
            Telegram last name of the user.
        """
        self.id = user_id
        self.user_name = user_name
        self.first_name = first_name
        self.last_name = last_name

    def __repr__(self):
        return f'User({self.id}, {self.first_name})'


Base.metadata.create_all(engine)
