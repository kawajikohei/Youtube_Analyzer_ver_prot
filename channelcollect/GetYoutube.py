import statistics

import pandas as pd

from channelcollect import Format, youtube_client

HIDDEN_LIKES = '非公開'


class AnalyzeYoutube:
    """取得したチャンネル・動画データを画面表示用の形に整える。"""

    def procoll(self, channel_id):
        """チャンネルのプロフィール情報を1行の DataFrame で返す。"""
        info = youtube_client.fetch_channel(channel_id)['channel']
        stats = info['statistics']
        subscribers = '非公開' if stats.get('hiddenSubscriberCount') else Format.commaformat(stats.get('subscriberCount', 0))
        return pd.DataFrame([[
            info['snippet']['title'],
            Format.commaformat(stats.get('videoCount', 0)),
            subscribers,
            Format.commaformat(stats.get('viewCount', 0)),
            Format.dateedit(info['snippet']['publishedAt']),
        ]], columns=['チャンネル名', '動画投稿数', 'チャンネル登録者数', '総再生数', 'チャンネル創設日時'])

    def vdcoll(self, channel_id):
        """新着動画の一覧と、動画時間の平均・中央値、平均投稿間隔(日)を返す。"""
        items = youtube_client.fetch_channel(channel_id)['videos']
        videos, urls, durations = [], [], []
        for v in items:
            stats = v.get('statistics', {})
            thumbs = v['snippet']['thumbnails']
            thumb = (thumbs.get('medium') or thumbs.get('default') or {}).get('url', '')
            videos.append([
                thumb,
                v['snippet']['title'],
                stats.get('viewCount', 0),
                stats.get('likeCount', HIDDEN_LIKES),  # 高評価を非公開にしている動画は「非公開」と表示(課題②)
                Format.dateedit(v['snippet']['publishedAt']),
            ])
            urls.append(f"https://www.youtube.com/watch?v={v['id']}")
            duration = v.get('contentDetails', {}).get('duration')
            if duration:
                durations.append(Format.timeedit(duration))

        video = pd.DataFrame(videos, columns=['サムネイル', 'タイトル', '再生数', '高評価数', 'アップ時間'])
        mean = Format.m_s_convert(round(statistics.mean(durations))) if durations else '-'
        median = Format.m_s_convert(round(statistics.median(durations))) if durations else '-'
        day_average = Format.date_frequency(video['アップ時間'].loc[::-1].tolist()) if len(video) >= 2 else '-'
        return video, urls, mean, median, day_average
