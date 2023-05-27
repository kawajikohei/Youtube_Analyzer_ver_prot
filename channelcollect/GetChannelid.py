import requests
from PIL import Image
from io import BytesIO
import urllib.request
import os
import base64
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

def idlist(apilist,search_word):
    for deveLoperKey in apilist:
        try:
            deveLoperKey = deveLoperKey.strip()
            youtube =  build("youtube","v3",developerKey = deveLoperKey)

            search = youtube.search().list(
                q = search_word,
                part = "snippet",
                type = "channel",
                maxResults = 20
            ).execute()

            channel_ids = []
            for search_result in search.get('items', []):
                if search_result['id']['kind'] == 'youtube#channel':
                    channel_id = search_result['id']['channelId']
                    channel_ids.append(channel_id)

            channels = []


            for channel_id in channel_ids:
                channels_data = youtube.channels().list(
                part='snippet',
                id=channel_id
                ).execute()
                channel = channels_data['items'][0]
                # チャンネル情報をリストに追加
                channels.append((image_get(channel['snippet']['thumbnails']['default']['url']),#チャンネルアイコン
                                channel['snippet']['title'],#チャンネル名
                                channel_id)) #チャンネルID 
            
            return channels
        except HttpError:
            if deveLoperKey == apilist[-1]:
                break
            else:
                continue




#画像は入手方法ひな形k
#response = requests.get(profile_image_url)
#img = Image.open(BytesIO(response.content))
#img.save('profile.jpg', 'JPEG')

def  image_dl4(image):
    response = requests.get(image)
    img = Image.open(BytesIO(response.content))
    img.save('profile.jpg', 'JPEG')
    image_list = [
        f for f in os.listdir()
        if f.endswith((".jpg"))
    ]
    # 画像ファイル名を削除する
    return image_list[0]

def image_get(image_url):
    response = requests.get(image_url)
    img = Image.open(BytesIO(response.content))
    img_bytes = BytesIO()
    img.save(img_bytes, format='JPEG')
    img_bytes.seek(0)
    return base64.b64encode(img_bytes.read()).decode('utf-8')
    
#BytesIO(img.save(profile.jpg,'JPEG'))
#一度saveして次の文でカレントディレクトリから生成した画像を取り出して変数に入れる。そして削除する
