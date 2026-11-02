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
    if not frequencies:
        return '-'
    ave = sum(frequencies, datetime.timedelta()) / len(frequencies)
    return ave.days



def timeedit(time):#動画時間(ISO8601 例: PT1H2M3S, P1DT2H)を秒に変換する
    match = re.fullmatch(r'P(?:(\d+)D)?(?:T(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?)?', time or '')
    if not match:
        return 0
    days, hours, minutes, seconds = (int(g) if g else 0 for g in match.groups())
    return days * 86400 + hours * 3600 + minutes * 60 + seconds

def m_s_convert(time):#timeedit関数変換したデータを分秒の形に変換する
     minutes = time // 60
     seconds = time % 60
     
     time_convert = str(minutes) + "分" + str(seconds) + "秒"
     return time_convert
     




def commaformat(count):#カンマ付け
    count = '{:,}'.format(int(count))
    return count



