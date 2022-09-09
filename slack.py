import requests
import json
import re

class Slack:

    def __init__(self, token):
        self.token = token
        self.header = {
            "Authorization": "Bearer {}".format(token)
        }
        # ユーザ一覧を取得して、ID→名前の対応辞書を作る
        self.users={}
        members=self.getUsers()
        for m in members:
            name = m['name']
            if 'display_name' in m and m['display_name'] != '':
                name = m['display_name']
            elif 'real_name' in m and m['real_name'] != '':
                name = m['real_name']
            self.users[m['id']]=name

    ## ユーザ一覧を取得
    def getUsers(self):
        url = 'https://slack.com/api/users.list'
        res = requests.get(url, headers=self.header)
        return res.json()['members']

    ## チャンネル一覧を取得
    def getChannels(self):
        url = 'https://slack.com/api/conversations.list'
        res = requests.get(url, headers=self.header)
        ret = {}
        for ch in res.json()['channels']:
            ret[ch['name']]=ch['id']
        return ret

    ## メッセージ一個出力（デバッグ用）
    def printMessage(self, msg):
        if msg['type']=='message':
            print(msg['user'],msg['text'],msg['ts'])

    ## メンションをIDから名前に変える
    def convertMentions(self, msg):
        for u in self.users:
            msg['text']=msg['text'].replace('<@' + u + '>', '<@' + self.users[u] + '>')
        msg['text']=re.sub(r'<#[0-9A-Z]+\|([^>]+)>',r'#\1',msg['text'])
        msg['text']=re.sub(r'<mailto:[.0-9a-zA-Z@_]+\|([^>]+)>',r'\1',msg['text'])
        return msg


    ## 指定されたチャンネルの(全)メッセージを取得
    def getMessages(self, channel):
        url = 'https://slack.com/api/conversations.history'
        payload = {
            'channel' : channel
        }
        res = requests.get(url, headers=self.header, params=payload)
        ret = []
        for msg in res.json()['messages']:
            if msg['type'] == 'message':
                if 'user' not in msg:
                    msg['user']=''
                elif msg['user'] in self.users:
                    msg['user'] = self.users[msg['user']]
                if 'reply_count' in msg and msg['reply_count'] > 0:
                    ret = self.getReplies(channel, msg['thread_ts']) + ret
                ret.insert(0, self.convertMentions(msg))
        return ret

    ## 所定スレッド内の全メッセージを取得
    def getReplies(self, channel, ts):
        url = "https://slack.com/api/conversations.replies" 
        payload  = {
            "channel" : channel,
            "ts" : ts
        }
        res = requests.get(url, headers=self.header, params=payload)
        ret = []
        count = 0
        for msg in res.json()['messages']:
            if count > 0:
                if msg['user'] in self.users:
                    msg['user'] = self.users[msg['user']]
                ret.append(self.convertMentions(msg))
            count += 1
        return ret

    ## 添付ファイルのダウンロード
    def downloadFile(self, url, path):
        #print('Download ' + url + ' to ' + path)
        res = requests.get(url, headers=self.header)
        #print(res)
        with open(path, 'wb') as f:
            f.write(res.content)

#### Slack側の投稿読み出し確認用 ####
if __name__ == '__main__':
    slack = Slack(token = '<ここにSlackのUser OAuth Tokenを記入>')

    # チャンネル一覧
    ch = slack.getChannels()
    print('channels:', ch)

    # 特定チャンネルのメッセージを出力
    ret = slack.getMessages(ch['random'])
    count = 1
    for m in ret[0:20]:
        if 'files' in m:
            for f in m['files']:
                print(f['name'],f['mimetype'],f['filetype'],f['size'])
                if 'url_private_download' in f:
                    slack.downloadFile(f['url_private_download'], str(count) + f['name'])
                count += 1
        else:
            print(m['user'],m['text'],m['ts'])
        #m['url_private']
        #m['url_private_download']
        #m['permalink']
