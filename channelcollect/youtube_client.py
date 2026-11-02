"""YouTube Data API v3 の呼び出しをまとめたモジュール。

クォータ消費(1日10,000ユニット)を抑えるため、重い search.list(100ユニット)は
キーワード検索だけに使い、動画一覧はアップロード再生リスト(playlistItems.list, 1ユニット)から取る。
"""
import os
import re

from googleapiclient.discovery import build

from channelcollect import cache

_youtube = None


def client():
    global _youtube
    if _youtube is None:
        api_key = os.getenv('YOUTUBE_API_KEY', '').strip()
        if not api_key:
            raise RuntimeError('YOUTUBE_API_KEY が設定されていません')
        _youtube = build('youtube', 'v3', developerKey=api_key, cache_discovery=False)
    return _youtube


def search_channels(keyword, max_results=10):
    """キーワードでチャンネルを検索する(約101ユニット、結果はキャッシュ)。"""
    key = f'search:{keyword.strip().lower()}:{max_results}'
    cached = cache.get(key)
    if cached is not None:
        return cached
    yt = client()
    found = yt.search().list(q=keyword, part='id', type='channel', maxResults=max_results).execute()
    ids = [item['id']['channelId'] for item in found.get('items', [])]
    channels = []
    if ids:
        res = yt.channels().list(part='snippet', id=','.join(ids), maxResults=50).execute()
        by_id = {c['id']: c for c in res.get('items', [])}
        for cid in ids:  # 検索順を保つ
            c = by_id.get(cid)
            if c:
                channels.append({
                    'id': cid,
                    'title': c['snippet']['title'],
                    'icon': c['snippet']['thumbnails']['default']['url'],
                })
    cache.set(key, channels)
    return channels


_CHANNEL_ID_RE = re.compile(r'(UC[0-9A-Za-z_-]{22})')
_HANDLE_RE = re.compile(r'(?:youtube\.com/)?(@[0-9A-Za-z_.\-]+)')


def resolve_channel_id(text):
    """URL・@ハンドル・チャンネルIDならチャンネルIDを返す(1ユニット)。キーワードなら None。"""
    text = text.strip()
    m = _CHANNEL_ID_RE.search(text)
    if m:
        return m.group(1)
    m = _HANDLE_RE.search(text) if ('youtube.com' in text or text.startswith('@')) else None
    if m:
        res = client().channels().list(part='id', forHandle=m.group(1)).execute()
        items = res.get('items', [])
        if items:
            return items[0]['id']
    return None


def fetch_channel(channel_id, max_videos=50):
    """チャンネル情報と新着動画を取得する(50本で約3ユニット、結果はキャッシュ)。

    戻り値: {'channel': channels.list の item, 'videos': videos.list の item のリスト(新しい順)}
    """
    key = f'channel:{channel_id}:{max_videos}'
    cached = cache.get(key)
    if cached is not None:
        return cached
    yt = client()
    res = yt.channels().list(part='snippet,statistics,contentDetails', id=channel_id).execute()
    items = res.get('items', [])
    if not items:
        raise LookupError('チャンネルが見つかりませんでした')
    channel = items[0]
    uploads = channel['contentDetails']['relatedPlaylists']['uploads']

    # アップロード再生リストは重複なしで新しい順に並ぶ(README の課題①の解決)
    video_ids, page_token = [], None
    while len(video_ids) < max_videos:
        page = yt.playlistItems().list(part='contentDetails', playlistId=uploads,
                                       maxResults=min(50, max_videos - len(video_ids)),
                                       pageToken=page_token).execute()
        video_ids += [it['contentDetails']['videoId'] for it in page.get('items', [])]
        page_token = page.get('nextPageToken')
        if not page_token:
            break

    videos = []
    for i in range(0, len(video_ids), 50):  # videos.list は50件まとめて1ユニット
        res = yt.videos().list(part='snippet,statistics,contentDetails', id=','.join(video_ids[i:i + 50])).execute()
        videos += res.get('items', [])
    videos.sort(key=lambda v: v['snippet']['publishedAt'], reverse=True)

    result = {'channel': channel, 'videos': videos}
    cache.set(key, result)
    return result
