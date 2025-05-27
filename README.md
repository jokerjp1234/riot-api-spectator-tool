# 🎮 Riot API ソロランク監視ツール

League of Legends プロプレイヤーのソロランクを監視して、観戦データを自動取得するツールです。

![Tool Screenshot](https://img.shields.io/badge/League%20of%20Legends-Riot%20API-blue)
![Python](https://img.shields.io/badge/Python-3.7+-green)
![HTML5](https://img.shields.io/badge/HTML5-CSS3-orange)

## ✨ 主要機能

- **リアルタイム監視**: プロプレイヤーのソロランク開始を自動検出
- **観戦データ取得**: ゲーム開始と同時に観戦データをダウンロード
- **マルチリージョン対応**: 韓国、欧州、北米、日本など全リージョン
- **WebUI**: 使いやすいブラウザインターフェース
- **RiotID対応**: ゲーム名#タグライン形式でプレイヤー検索

## 🚀 セットアップ

### 1. リポジトリクローン
```bash
git clone https://github.com/jokerjp1234/riot-api-spectator-tool.git
cd riot-api-spectator-tool
```

### 2. 依存関係インストール
```bash
pip install -r requirements.txt
```

### 3. API Key設定

#### Riot Developer PortalでKey取得
1. [Riot Developer Portal](https://developer.riotgames.com/) にアクセス
2. Personal API Keyを取得（24時間有効）
3. `config.py.example` を `config.py` にコピー
4. API Keyを設定

```python
# config.py
RIOT_API_KEY = "your_api_key_here"
```

### 4. 実行方法

#### Web UI版（推奨）
```bash
python app.py
```
ブラウザで `http://localhost:5000` にアクセス

#### CLI版
```bash
python riot_api_tool.py
```

## 📖 使用方法

### Web UI版
1. ブラウザでアプリにアクセス
2. API Keyを入力
3. プレイヤー追加（例: `Faker#KR1`）
4. 監視開始ボタンをクリック
5. ソロランク開始時に自動でデータダウンロード

### CLI版
1. スクリプト実行
2. メニューからプレイヤー追加
3. 監視開始
4. ログでリアルタイム状況確認

## 🌍 対応リージョン

- **KR**: Korea (韓国)
- **EUW1**: Europe West (欧州西)
- **EUN1**: Europe Nordic East (欧州北東)
- **NA1**: North America (北米)
- **JP1**: Japan (日本)
- **BR1**: Brazil (ブラジル)
- **LA1**: Latin America North (中南米北)
- **LA2**: Latin America South (中南米南)
- **OC1**: Oceania (オセアニア)
- **TR1**: Turkey (トルコ)
- **RU**: Russia (ロシア)

## 📁 プロジェクト構成

```
riot-api-spectator-tool/
├── app.py                 # Flask Webアプリ
├── riot_api_tool.py       # CLIツール本体
├── templates/
│   └── index.html         # WebUIテンプレート
├── static/
│   ├── style.css          # スタイルシート
│   └── script.js          # JavaScript
├── config.py.example      # 設定ファイルテンプレート
├── requirements.txt       # Python依存関係
├── spectator_data/        # 観戦データ保存フォルダ
└── README.md
```

## 📊 取得できるデータ

### ライブゲーム情報
- ゲームID
- 参加者リスト
- チャンピオン情報
- ゲーム開始時刻
- マップ・モード情報

### 試合詳細データ
- KDA統計
- アイテムビルド
- ルーン設定
- ダメージ統計
- ゲーム進行データ

## ⚠️ 注意事項

### API制限
- **Personal Key**: 100 requests/2分
- **Production Key**: より高い制限（申請必要）
- 監視間隔: 10秒（制限考慮済み）

### セキュリティ
- API Keyは環境変数や設定ファイルで管理
- GitHubにAPI Keyをコミットしない
- `.gitignore`で`config.py`を除外

## 🔧 カスタマイズ

### プロプレイヤーリスト追加
`riot_api_tool.py`の`pro_players`辞書を編集:

```python
self.pro_players = {
    "kr": [
        {"game_name": "Hide on bush", "tag_line": "KR1"},  # Faker
        {"game_name": "Your Player", "tag_line": "TAG1"},   # 追加
    ]
}
```

### 監視間隔変更
`_monitor_loop()`メソッドの`time.sleep(10)`を変更

## 🐛 トラブルシューティング

### API Key エラー
```
403 Forbidden: API key expired
```
→ Personal API Keyは24時間で期限切れ。新しいキーを取得

### プレイヤーが見つからない
```
404 Not Found: Summoner not found
```
→ ゲーム名・タグライン・リージョンを確認

### レート制限エラー
```
429 Too Many Requests
```
→ 監視間隔を長くする（15秒以上推奨）

## 📝 ライセンス

MIT License

## 🤝 コントリビューション

Pull Request歓迎！以下の改善アイデア：

- [ ] データベース連携
- [ ] Discord通知機能
- [ ] 統計ダッシュボード
- [ ] モバイルアプリ
- [ ] 複数プレイヤー同時監視最適化

## 📞 サポート

Issuesでバグ報告・機能要望をお願いします。

---

**免責事項**: このツールはRiot Games公式APIを使用していますが、Riot Gamesの公式製品ではありません。