# Created by Selutario <selutario@gmail.com>.
# This program is a free software; you can redistribute it and/or modify it under the terms of GPLv3

from datetime import datetime, timezone

from telegram import InlineQueryResultCachedVideo

from utils import utils
from utils.common import settings


def inline_search(update, context):
    query = update.inline_query.query
    inline_results = list()

    if query:
        # Search requested videos
        result = utils.get_similar_videos(
            str(utils.cleaner(query)),
            utils.videos_info.desc_kwds_df,
            utils.videos_info.desc_kwds_vt,
            len(utils.videos_info)
        )

        for idx in result:
            if len(inline_results) >= min(settings['results_limit'], 50):
                break
            inline_results.append(
                InlineQueryResultCachedVideo(id=utils.videos_info.videos_info_list[idx]['id'],
                                             video_file_id=utils.videos_info.videos_info_list[idx]['file_id'],
                                             title=utils.videos_info.videos_info_list[idx]['title'],
                                             description=utils.videos_info.videos_info_list[idx]['description']))

        context.bot.answer_inline_query(update.inline_query.id, inline_results)


def on_chosen_video(update, context):
    query = "INSERT INTO sent_videos (user_id, query, video_id, user_name, date) VALUES (?, ?, ?, ?, ?)"
    params = (update.chosen_inline_result.from_user.id, update.chosen_inline_result.query,
              update.chosen_inline_result.result_id, update.chosen_inline_result.from_user.username,
              datetime.now(timezone.utc))
    utils.execute_query(query=query, parameters=params)
