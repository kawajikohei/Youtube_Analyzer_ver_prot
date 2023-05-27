import datetime
import re
#ISO8601フォーマット形式になっているデータを変換する


def dateedit(date):#公開日付を年月日形式に変換する
    datefomat = '%Y年%m月%d日%H時'
    try:#データにミリ秒まである場合
        s = datetime.datetime.strptime(date,'%Y-%m-%dT%H:%M:%S.%fZ')
        d = s.strftime(datefomat)
    except:#
         s = datetime.datetime.strptime(date,'%Y-%m-%dT%H:%M:%SZ')
         d = s.strftime(datefomat)
    return d

def date_frequency(dates):
    date_format = '%Y年%m月%d日%H時'
    frequencies = []
    for i in range(len(dates) - 1):
        freq = datetime.datetime.strptime(dates[i+1], date_format) - datetime.datetime.strptime(dates[i], date_format)
        frequencies.append(freq)
    ave = sum(frequencies, datetime.timedelta()) / len(frequencies)
    return ave.days



def timeedit(time):#動画時間を秒に変換する
        pattern = r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?'

    # 正規表現パターンに一致するグループを取得
        match = re.match(pattern, time)

        # 時間、分、秒の値を取得
        hours = match.group(1)
        minutes = match.group(2)
        seconds = match.group(3)

        # 分に変換
        total_seconds = 0
        if hours:
            total_seconds += int(hours) * 3600
        if minutes:
            total_seconds += int(minutes)*60
        if seconds:
            total_seconds += int(seconds)

        # フォーマットされた文字列を生成
        #formatted_data = str(total_minutes) + "分"
        return total_seconds

def m_s_convert(time):#timeedit関数変換したデータを分秒の形に変換する
     minutes = time // 60
     seconds = time % 60
     
     time_convert = str(minutes) + "分" + str(seconds) + "秒"
     return time_convert
     




def commaformat(count):#カンマ付け
    count = '{:,}'.format(int(count))
    return count



