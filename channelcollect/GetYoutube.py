import csv
import pandas as pd
import itertools
import statistics
from channelcollect import Format
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
#classにする:

class AnalyzeYoutube:
   
   def __init__(self, apilist):
        self.apilist = apilist


   def procoll(self,channel_id):
      for deveLoperKey in self.apilist:
          try:
            DEVELOPER_KEY = deveLoperKey
            CHANNEL_ID = channel_id
            channel_info = []#チャンネル情報を入れる配列

            youtube =  build("youtube","v3",developerKey = DEVELOPER_KEY)

            #取得したrequestはdict型である
            request = youtube.channels().list(
                part = 'snippet,statistics',
                id = CHANNEL_ID
                ).execute()



            #requestで入手した情報の中からほしいデータをinfoとして取り出して配列channel_infoに入れる
            for info in request.get("items",[]):
              if info["kind"] != "youtube#video":
                channel_info.append([info["snippet"]["title"],#チャンネルタイトル
                                    Format.commaformat(info["statistics"]["videoCount"]),#チャンネルのアップロード数
                                    Format.commaformat(info["statistics"]["subscriberCount"]),#チャンネルの登録者数
                                    Format.commaformat(info["statistics"]["viewCount"]),#チャンネルの総再生数
                                    Format.dateedit(info["snippet"]["publishedAt"])])#チャンネルの作成日時

            #配列channel_infoのデータをデータフレーム化してcsvファイルとして出力する
            channel = pd.DataFrame(channel_info,columns = ["チャンネル名","動画投稿数","チャンネル登録者数","総再生数","チャンネル創設日時"])
            #chanellist = list(itertools.chain.from_iterable(channel.values.tolist()))
            return channel
            #channel.to_csv("channel.csv",index = False)
            #print(channel)
          except HttpError:
              if deveLoperKey == self.apilist[-1]:
                  break
              else:
                  continue
              

              
   def vdcoll(self,channel_id):#動画一覧を出す
      for deveLoperKey in self.apilist:
        try:
          DEVELOPER_KEY = deveLoperKey
          CHANNEL_ID = channel_id
          search_info = []#動画のIDを入れる配列
          videos = []
          urls = []
          video_times = []
          

          youtube =  build("youtube","v3",developerKey = DEVELOPER_KEY)

          while True:#動画収集は200件までに制限
            search_request =  youtube.search().list(
                part="snippet",
                channelId = CHANNEL_ID,
                maxResults = 50,
                order = "date",
            ).execute()

            for search_result in search_request.get("items", []):
                if search_result["id"]["kind"] == "youtube#video":
                  search_info.append(search_result["id"]["videoId"])#各動画のvideoidをリストに保存
                  urls.append(f'https://www.youtube.com/watch?v={search_result["id"]["videoId"]}')#各動画のリンクをリストに保存
              


            for info in search_info:#動画リストから必要情報を抜き取っていく
              video_info = youtube.videos().list(
                  part = "snippet,statistics,contentDetails",
                  id = info
              ).execute()
              for video_search in video_info.get("items",[]):
                if video_search["kind"] == "youtube#video":
                  try:
                    videos.append([
                              str(video_search["snippet"]["thumbnails"]["medium"]["url"]),#サムネイル
                              video_search["snippet"]["title"],#動画タイトル
                              video_search["statistics"]["viewCount"],#動画の再生数
                              video_search["statistics"]["likeCount"],#動画の高評価数
                              Format.dateedit(video_search["snippet"]["publishedAt"])#投稿日時
                              ])
                  except:#高評価を非公開にしている動画用対策
                      videos.append([
                              video_search["snippet"]["thumbnails"]["medium"]["url"],
                              video_search["snippet"]["title"],
                              video_search["statistics"]["viewCount"],
                              0,
                              Format.dateedit(video_search["snippet"]["publishedAt"])
                              ])
                  video_times.append(Format.timeedit(video_search["contentDetails"]["duration"]))
            


          #print(videos)
            video = pd.DataFrame(videos,columns = ["サムネイル","タイトル","再生数","高評価数","アップ時間"])
            mean = Format.m_s_convert(round(statistics.mean(video_times)))
            median = Format.m_s_convert(round(statistics.median(video_times)))
            day_average = Format.date_frequency(video["アップ時間"].loc[::-1].tolist())
          
            return video,urls,mean,median,day_average
          #video.to_csv("videos.csv",index = False)
        except HttpError:
              if deveLoperKey == self.apilist[-1]:
                  break
              else:
                  continue
          
          

  #def avetime(times):
    
    