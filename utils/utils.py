# Created by Selutario <selutario@gmail.com>.
# This program is a free software; you can redistribute it and/or modify it under the terms of GPLv3

import re
import string
from datetime import datetime, timezone
from sqlite3 import connect, Row, Error

from numpy import dot
from numpy.linalg import norm
from pandas import DataFrame
from sklearn.feature_extraction.text import TfidfVectorizer

from utils.common import *


def execute_query(query, parameters=None):
    with connect(DB_PATH) as connection:
        connection.row_factory = Row
        cursor = connection.cursor()
        cursor.execute("PRAGMA foreign_keys = ON")

        try:
            cursor.execute(query, parameters) if parameters else cursor.execute(query)
            connection.commit()
            return True
        except Error as e:
            return False


def execute_read_query(query, parameters=None):
    with connect(DB_PATH) as connection:
        connection.row_factory = Row
        cursor = connection.cursor()
        try:
            cursor.execute(query, parameters) if parameters else cursor.execute(query)
            result = cursor.fetchall()
            return result
        except Error as e:
            print(f"The error '{e}' occurred")


def cleaner(query):
    document_test = query.replace('á', 'a').replace('é', 'e').replace('í', 'i').replace('ó', 'o').replace('ú', 'u')\
        .replace('ñ', 'n').replace('ü', 'u').replace('1', 'one').replace('2', 'two').replace('3', 'three').\
        replace('4', 'four').replace('5', 'five').replace('6', 'six').replace('7', 'seven').replace('8', 'eight').\
        replace('9', 'nine').replace('0', 'zero')
    # Remove Unicode
    document_test = re.sub(r'[^\x00-\x7F]+', ' ', document_test)
    # Remove Mentions
    document_test = re.sub(r'@\w+', '', document_test)
    # Lowercase the document
    document_test = document_test.lower()
    # Remove punctuations
    document_test = re.sub(r'[%s]' % re.escape(string.punctuation), ' ', document_test)
    # Lowercase the numbers
    document_test = re.sub(r'[0-9]', '', document_test)
    # Remove the doubled space
    return re.sub(r'\s{2,}', ' ', document_test)


def clean_documents(documents):
    documents_clean = []
    for key, value in documents.items():
        cleaned = cleaner(value)
        documents[key] = cleaned
        documents_clean.append(cleaned)

    return documents_clean


def create_df(documents):
    vt = TfidfVectorizer()  # It fits the data and transform it as a vector
    x = vt.fit_transform(documents)  # Convert the X as transposed matrix
    x = x.T.toarray()  # Create a DataFrame and set the vocabulary as the index
    return DataFrame(x, index=vt.get_feature_names()), vt


def get_similar_videos(q, df, vt, n_videos, sensitivity=settings['sensitivity']):
    if n_videos:
        q = [q]
        result = list()
        q_vec = vt.transform(q).toarray().reshape(df.shape[0], )
        sim = {}  # Calculate the similarity

        for i in range(n_videos):
            sim[i] = dot(df.loc[:, i].values, q_vec) / norm(df.loc[:, i]) * norm(q_vec)

        # Sort the values
        sim_sorted = sorted(sim.items(), key=lambda x: x[1], reverse=True)  # Print the articles and their similarity values
        for k, v in sim_sorted:
            if v > sensitivity:
                result.append(k)
        return result


def store_user_details(update):
    """Save user data (name, username and chat id if not in a group).

    Parameters
    ----------
    update : telegram.update.Update
        Object representing incoming update with request data.

    Returns
    -------
    bool
        SQL query result.
    """
    if getattr(update, 'effective_chat') and update.effective_chat.type == 'private':
        query = f"INSERT IGNORE INTO users (id, user_name, first_name, last_name, chat_id) VALUES(?, ?, ?, ?, ?)"
        params = (update.effective_user.id, update.effective_user.username, update.effective_user.first_name,
                  update.effective_user.last_name, update.effective_chat.id)
    else:
        query = "INSERT IGNORE INTO users (id, user_name, first_name, last_name) VALUES(?, ?, ?, ?)"
        params = (update.effective_user.id, update.effective_user.username, update.effective_user.first_name,
                  update.effective_user.last_name)

    return execute_query(query, params)


class VideosInfo:
    def __init__(self):
        # Full video items from the DB
        self.videos_info_list = list()

        # Description field
        self.desc_list = list()
        self.desc_df = None
        self.desc_vt = None

        # Description + keywords fields
        self.desc_kwds_list = list()
        self.desc_kwds_df = None
        self.desc_kwds_vt = None

        self.update_model()

    def update_model(self):
        db_result = execute_read_query('select id, title, description, file_id, keywords from video_data')

        if db_result:
            self.videos_info_list = list()
            self.desc_list = list()
            self.desc_kwds_list = list()

            for row in db_result:
                row_dict = dict(row)
                self.videos_info_list.append(row_dict)
                self.desc_list.append(cleaner(row_dict['description']))
                self.desc_kwds_list.append(cleaner(row_dict['description'] + ' ' + row_dict['keywords']))

            self.desc_df, self.desc_vt = create_df(self.desc_list)
            self.desc_kwds_df, self.desc_kwds_vt = create_df(self.desc_kwds_list)

    def __len__(self):
        return len(self.videos_info_list)


videos_info = VideosInfo()
