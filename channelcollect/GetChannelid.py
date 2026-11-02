from channelcollect import youtube_client


def idlist(search_word):
    """キーワードからチャンネル候補を (アイコンURL, チャンネル名, チャンネルID) のリストで返す。"""
    return [(c['icon'], c['title'], c['id']) for c in youtube_client.search_channels(search_word)]
