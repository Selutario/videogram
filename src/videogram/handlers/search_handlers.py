# Created by Selutario <selutario@gmail.com>.
# This program is a free software; you can redistribute it and/or modify it under the terms of GPLv3

import random
from datetime import datetime, timezone

from telegram import InlineQueryResultCachedVideo

from videogram.utils import utils
from videogram.utils.common import settings, results_limit, empty_query_videos

def inline_search(update, context):
    query = update.inline_query.query
    inline_results = []
    result = []

    if update.effective_user.username in settings['admin_usernames'] or not settings['closed_circle'] or \
            update.effective_user.username in settings['closed_circle']:

        if query:
            # Search requested videos
            result = utils.get_similar_videos(
                str(utils.cleaner(query)),
                utils.videos_info.desc_kwds_df,
                utils.videos_info.desc_kwds_vt,
                len(utils.videos_info)
            )
        else:
            # Obtain random videos
            n_videos = len(utils.videos_info.videos_info_list)
            result = random.sample(range(n_videos), min(empty_query_videos, n_videos))

        for idx in result:
            if len(inline_results) >= results_limit:
                break
            inline_results.append(
                InlineQueryResultCachedVideo(id=utils.videos_info.videos_info_list[idx]['id'],
                                             video_file_id=utils.videos_info.videos_info_list[idx]['file_id'],
                                             title=utils.videos_info.videos_info_list[idx]['title'],
                                             description=utils.videos_info.videos_info_list[idx]['description']))

        context.bot.answer_inline_query(update.inline_query.id, inline_results)


def on_chosen_video(update, context):
    query = "INSERT INTO sent_videos (user_id, query, video_id, date) VALUES (?, ?, ?, ?)"
    params = (update.chosen_inline_result.from_user.id, update.chosen_inline_result.query,
              update.chosen_inline_result.result_id, datetime.now(timezone.utc))
    if not utils.store_user_details(update) or not utils.execute_query(query=query, parameters=params):
        context.bot.send_message(chat_id=update.effective_chat.id, text=_("error"))
