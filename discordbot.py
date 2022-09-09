# インストールした discord.py を読み込む
import discord
from discord.ext import tasks
import datetime
import tempfile

# Slackに接続してチャンネル一覧を取得
from slack import Slack
slack = Slack('<ここにSlackのUser OAuth Tokenを記入>')
slack_ch = slack.getChannels()

# 自分のBotのアクセストークンに置き換えてください
TOKEN = '<ここにDiscord Botのトークンを記入>'

# 接続に必要なオブジェクトを生成
intents = discord.Intents.default()
#intents.message_content = True
client = discord.Client(intents=intents)

## 起動時に動作する処理
@client.event
async def on_ready():
    # 接続できたらメッセージ表示
    print('サーバに接続しました')
    loop.start()

## 30分ごとに同期処理実行
@tasks.loop(minutes=30)
async def loop():
    print('定期実行!!', datetime.datetime.now())

    # 指定の名前のカテゴリのIDを取得
    category_id = 0
    for ch in client.get_all_channels():
        if ch.name == 'Slackバックアップ':
            category_id = ch.id

    # 指定カテゴリ内のテキストチャンネル一覧
    category = client.get_channel(category_id)
    channels={}
    for ch in category.channels:
        channels[ch.name] = ch.id

    # Slackにあって、Discordの「Slackバックアップ」にないチャンネル
    #for ch in slack_ch:
    #    if ch not in channels:
    #        print(ch)

    # slack_chのチャンネルすべてを処理
    for target in slack_ch:

        # 移行先のテキストチャンネルがなければ作成する
        if target not in channels:
            ch = await category.create_text_channel(name=target)
            channels[target] = ch.id

        # 移行先テキストチャンネルの過去メッセージを最大5000件取得
        target_ch=client.get_channel(channels[target])
        msgs=[]
        async for m in target_ch.history(limit=5000):
            msgs.append(m.content)

        # 移行元チャンネルのメッセージを取得に、未投稿ならば投稿（20件ずつ）
        count = 0
        for m in slack.getMessages(slack_ch[target]):
            if m['type']=='message' and ('subtype' not in m or m['subtype']!='channel_join'):
                dt = datetime.datetime.fromtimestamp(float(m['ts']))
                s = dt.strftime('%Y/%m/%d %H:%M:%S')
                msg = m['user']+': '+m['text']+' ('+s+')'
                if not msg in msgs:
                    try:
                        if 'files' in m:
                            files=[]
                            for f in m['files']:
                                #print(f['name'],f['mimetype'],f['filetype'],f['size'])
                                if 'url_private_download' in f:
                                    t=tempfile.TemporaryDirectory()
                                    slack.downloadFile(f['url_private_download'], t.name + '/' + f['name'])
                                    files.append(discord.File(t.name + '/' + f['name'], filename=f['name']))
                            if len(files)>1:
                                print('multiple files:', target, msg)
                            await target_ch.send(msg, files=files)
                        else:
                            await target_ch.send(msg)
                    except Exception as e:
                        # Discordの投稿サイズ制限などによりエラー発生した場合
                        print('---')
                        print('#' + target, m['user'], '('+s+')', 'length=' + str(len(m['text'])))
                        print(e)
                        print(type(e))
                    count += 1
                    # 各チャンネル毎回最大20件ずつ
                    if count >= 20:
                        break
    print('定期実行終了!', datetime.datetime.now())

# Botの起動とDiscordサーバーへの接続
client.run(TOKEN)
