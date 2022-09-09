# slack2discord

## 必要なもの
- Slack の User OAuth Token
- Discord Bot の トークン
- Discordサーバ の ID (要らなかったかも)

## Slack API側設定
- User Token Scopes
  - channels.history
  - channels.read
  - files.read
  - users.read
  - プライベートチャンネルもコピーするなら groups.history と groups.read も

## Discord Bot側設定
- SCOPES (詳細不明)
  - bot
  - applications.commands
- Bot Permissions (もっと少なくて良さそう)
  - Manage Channels
  - Read Messages/View Channels
  - Send Messages
  - Create Public Threads
  - Create Private Threads
  - Send Messages in Threads
  - Manage Messages
  - Manage Threads
  - Attach Files
  - Add Reactions

## 準備
- Slack の User OAuth Token を取得し、slack.pyの <ここにSlackのUser OAuth Tokenを記入> と、discordbot.pyの <ここにSlackのUser OAuth Tokenを記入> に記入する
- Discord Botのトークンを取得し、discordbot.pyの <ここにDiscord Botのトークンを記入> に記入する
- Discordサーバに Slackバックアップ というカテゴリーを作成し、Discord Bot用のアカウントでText Channel作成可能かつ投稿可能に設定する

## 動作確認(Slack側のみ)
- slack.py を実行し、チャンネル一覧と、#random チャンネルのメッセージ20件が表示されるか確認する

## 実行
- discordbot.py を実行する
  - Slack側の対象チャンネルすべてに対し、Discordサーバの Slackバックアップ カテゴリに同名のチャンネルを作成、各チャンネル最大20件ずつ投稿がコピーされます
  - Slack側のスレッドは、Discord側にはスレッドを展開した状態でコピーされます
  - Slack側の添付ファイルは、Discord側にも添付ファイルとしてコピーされます
  - Discord側のサイズ制限により、長い投稿、大きな添付ファイルはコピーされません(エラー表示あり)
  - 対象チャンネル全部を処理したのち、30分経過すると最初から再び実行します(そのまま放置しておけばすべてコピーされる想定)
- 1回ずつのコピー件数や、定期実行の時間間隔は、必要があれば discordbot.py の中を適当に書き換えて調整してください。

## 不具合や機能制限
- Discord側のサイズ制限により、長い投稿、大きな添付ファイルはコピーされません。実行時にエラー表示しますが、Discord側には何も残りません
- Slack側のスレッドはDiscord側のスレッドになりません
- ときどき、Slack側の1つの投稿がDiscord側に複数投稿されることがあります
- Slackのprivateチャンネルは設定次第でコピーされるようにしていますが、ダイレクトメッセージはコピーされません

## 免責
- 必要に迫られて急きょ作ったものです。全面的に自己責任で利用してください。
- Slack Appの設定や、Discord Botの設定については、ご自分で調べてください。
