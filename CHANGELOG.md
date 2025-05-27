# 変更履歴

## [1.0.0] - 2025-05-27

### 追加
- 🎮 初回リリース
- 🔍 RiotID (ゲーム名#タグライン) 対応
- 🌍 全リージョン対応 (KR, EUW1, NA1, JP1, etc.)
- ⚡ リアルタイムソロランク監視
- 📊 観戦データ自動ダウンロード
- 🖥️ Web UI インターフェース
- 💻 CLI インターフェース
- 📁 JSONフォーマットでのデータ保存
- 🎯 プロプレイヤー一括追加機能
- ⚙️ 設定ファイル対応
- 🚀 自動インストールスクリプト

### 機能詳細
- Account-v1 API使用でPUUID取得
- Spectator-v4 API使用でライブゲーム監視
- ソロランク (queueId: 420) 自動検出
- 10秒間隔での監視 (設定可能)
- レート制限考慮済み
- マルチスレッド対応
- CORS対応のFlask Webサーバー
- レスポンシブWebデザイン

### サポート地域
- 🇰🇷 Korea (kr)
- 🇪🇺 Europe West (euw1)
- 🇪🇺 Europe Nordic East (eun1)
- 🇺🇸 North America (na1)
- 🇯🇵 Japan (jp1)
- 🇧🇷 Brazil (br1)
- 🌎 Latin America North (la1)
- 🌎 Latin America South (la2)
- 🇦🇺 Oceania (oc1)
- 🇹🇷 Turkey (tr1)
- 🇷🇺 Russia (ru)

### API制限
- Personal API Key: 100 requests/2分
- Production API Key: より高い制限 (申請要)
- 適切な待機時間でレート制限回避

### セキュリティ
- API Key を環境変数・設定ファイルで管理
- .gitignore でAPI Key除外
- セキュアな設定ファイル管理

### ファイル構成
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
├── install.sh             # インストールスクリプト
├── run.sh                 # 起動スクリプト
├── spectator_data/        # 観戦データ保存フォルダ
├── .gitignore             # Git除外設定
├── CHANGELOG.md           # 変更履歴
└── README.md              # ドキュメント
```

### 今後の予定
- [ ] データベース連携 (SQLite/PostgreSQL)
- [ ] Discord通知機能
- [ ]統計ダッシュボード
- [ ] モバイルアプリ
- [ ] 複数プレイヤー同時監視最適化
- [ ] Webhook通知対応
- [ ] Docker対応
- [ ] クラウドデプロイ対応