from flask import Flask, render_template, url_for, request
from channelcollect.GetYoutube import AnalyzeYoutube
from channelcollect import GetChannelid
from dotenv import load_dotenv
import os

load_dotenv()
apilist = os.getenv('APIS_LIST', '').split(',')
analyze = AnalyzeYoutube(apilist)

app = Flask(__name__)
app.jinja_env.globals.update(zip=zip)


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        search_word = request.form['search_word']
        content = GetChannelid.idlist(apilist, search_word)
        try:
            return render_template('home.html',
                                   title='Analyze Youtube Neighbors',
                                   message="気になるyoutuberの名前やキーワードを入力してください",
                                   select_candidate=content
                                   )
        except Exception as e:
            return render_template('error.html',
                                   error_content=e
                                   )
    else:
        return render_template('home.html',
                               title='Analyze Youtube Neighbors',
                               message="気になるyoutuberの名前やキーワードを入力してください"
                               )


@app.route('/test', methods=['GET'])
def index():
    try:
        channel_name = request.args.get('channel_name')
        channel_id = request.args.get('channel_id')
        channel = analyze.procoll(channel_id)
        video, urls, mean, median, day_average = analyze.vdcoll(channel_id)
        print(day_average)
        return render_template('test.html',
                               title='Analyze Youtube Neighbors',
                               message="気になるyoutuberの名前やキーワードを入力してください",
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
        return render_template('error.html',
                               error_content=e
                               )


if __name__ == '__main__':
    app.debug = True
    app.run(host='localhost')
