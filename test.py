from flask import Flask, render_template, url_for, request, redirect
from channelcollect.GetYoutube import AnalyzeYoutube
from channelcollect import GetChannelid, youtube_client
from dotenv import load_dotenv
import os

load_dotenv()
# APIキーは YOUTUBE_API_KEY の1本だけ使う(channelcollect/youtube_client.py で読み込む)。
# 複数キーでのクォータ回避は YouTube API の規約違反になるため行わない。
analyze = AnalyzeYoutube()

app = Flask(__name__)
app.jinja_env.globals.update(zip=zip)

TITLE = 'Analyze Youtube Neighbors'
MESSAGE = "気になるyoutuberの名前、チャンネルURL、@ハンドルを入力してください"
ERROR_MESSAGE = 'データを取得できませんでした。時間をおいて再度お試しください。'


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        search_word = request.form['search_word'].strip()
        if not search_word:
            return redirect(url_for('home'))
        try:
            # URL・@ハンドル・チャンネルIDが入力されたら、検索せずに直接分析へ(クォータ節約)
            channel_id = youtube_client.resolve_channel_id(search_word)
            if channel_id:
                return redirect(url_for('index', channel_id=channel_id))
            content = GetChannelid.idlist(search_word)
            return render_template('home.html',
                                   title=TITLE,
                                   message=MESSAGE,
                                   select_candidate=content
                                   )
        except Exception as e:
            app.logger.exception(e)
            return render_template('error.html', error_content=ERROR_MESSAGE)
    else:
        return render_template('home.html',
                               title=TITLE,
                               message=MESSAGE
                               )


@app.route('/test', methods=['GET'])
def index():
    try:
        channel_id = request.args.get('channel_id')
        channel = analyze.procoll(channel_id)
        channel_name = request.args.get('channel_name') or channel.loc[0, 'チャンネル名']
        video, urls, mean, median, day_average = analyze.vdcoll(channel_id)
        return render_template('test.html',
                               title=TITLE,
                               message=MESSAGE,
                               channelcolumns=channel.columns.values.tolist(),
                               channeldata=channel.loc[0],
                               videocolumns=video.columns,
                               videodata=video.values.tolist(),
                               urls=urls,
                               channel_name=channel_name,
                               mean=mean,
                               median=median,
                               day_average=day_average
                               )
    except Exception as e:
        app.logger.exception(e)
        return render_template('error.html', error_content=ERROR_MESSAGE)


if __name__ == '__main__':
    app.debug = os.getenv('FLASK_DEBUG') == '1'
    app.run(host='localhost')
