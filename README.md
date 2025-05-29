# 🎮 Riot API ソロランク監視ツール v2.0

League of Legends プロプレイヤーのソロランクを自動監視し、観戦データを取得・分析するツールです。

## ✨ 新機能 (v2.0)

### 🚀 大幅な機能向上
- **リアルタイム更新**: WebSocket通信によるリアルタイムな状態更新
- **データ分析ダッシュボード**: 統計情報とチャートによる可視化
- **改善されたUI**: モダンで直感的なWebインターフェース
- **データベース統合**: SQLiteによる履歴データの永続化
- **API制限管理**: インテリジェントなレート制限処理
- **エラーハンドリング**: 堅牢なエラー処理と復旧機能

### 📊 分析機能
- プレイヤー別ゲーム統計
- 日別ゲーム数推移
- 平均ゲーム時間分析
- リアルタイム監視状況表示

### 🎨 UI/UX改善
- レスポンシブデザイン
- ダークテーマ対応
- リアルタイム通知システム
- キーボードショートカット対応
- モバイルフレンドリー

## 🛠️ 主な機能

### 🔍 監視機能
- **自動プレイヤー監視**: 指定プレイヤーのソロランク開始を自動検出
- **リアルタイム通知**: ゲーム開始/終了を即座に通知
- **観戦データ取得**: ライブゲームデータの自動ダウンロード
- **プロプレイヤー対応**: 有名プロプレイヤーの一括追加機能

### 📈 データ管理
- **データベース保存**: 全ゲーム履歴の永続化
- **JSON出力**: 構造化されたゲームデータ
- **分析レポート**: 統計情報の自動生成
- **データエクスポート**: CSV/JSON形式での出力

### 🌐 Web インターフェース
- **直感的な操作**: ドラッグ&ドロップ対応
- **リアルタイム更新**: 自動画面更新
- **多言語対応**: 日本語完全対応
- **モバイル対応**: スマートフォンでも利用可能

## 📋 必要な環境

- Python 3.8以上
- Riot API Personal Key
- インターネット接続

## 🚀 クイックスタート

### 1. リポジトリをクローン
```bash
git clone https://github.com/jokerjp1234/riot-api-spectator-tool.git
cd riot-api-spectator-tool
```

### 2. 依存関係をインストール
```bash
pip install -r requirements.txt
```

### 3. 設定ファイルを作成
```bash
cp config.py.example config.py
```

### 4. API Keyを設定
`config.py` を編集してRiot API Keyを設定：
```python
RIOT_API_KEY = "あなたのAPI_KEYをここに入力"
```

> 💡 **API Key取得方法**: [Riot Developer Portal](https://developer.riotgames.com/) でPersonal API Keyを取得

### 5. アプリケーションを起動
```bash
python app.py
```

### 6. ブラウザでアクセス
http://127.0.0.1:5000 にアクセス

## 📱 使い方

### 基本的な使用方法

1. **API Key設定**
   - Personal API Keyを入力して設定ボタンをクリック

2. **プレイヤー追加**
   - ゲーム名、タグライン、リージョンを入力
   - 「プレイヤー追加」ボタンでリストに追加

3. **監視開始**
   - 「監視開始」ボタンで自動監視を開始
   - ソロランク開始時に自動でデータを取得

### 🌟 プロプレイヤー機能

有名プロプレイヤーを一括追加できます：

- **Korea**: Faker, Zeus, Oner, Gumayusi, Keria等
- **Europe**: Caps, Jankos, Rekkles等  
- **North America**: Doublelift, Bjergsen等

### 📊 分析ダッシュボード

右下の📊アイコンから分析ページにアクセス：

- **基本統計**: 総ゲーム数、平均時間、プレイヤー数
- **日別推移**: ゲーム数の時系列チャート
- **プレイヤー分析**: 個別プレイヤーの詳細統計

## ⌨️ キーボードショートカット

- `Ctrl + Enter`: プレイヤー追加
- `Ctrl + M`: 監視開始/停止切り替え
- `Enter`: 各フィールドで次の入力へ移動

## 🔧 設定オプション

`config.py` で以下の設定が可能：

```python
# 監視間隔 (秒)
MONITOR_INTERVAL = 10

# サーバー設定
HOST = "127.0.0.1"
PORT = 5000

# データ保存先
DATA_DIR = "spectator_data"

# API制限設定
RATE_LIMIT_CALLS = 100
RATE_LIMIT_SECONDS = 120
```

## 📁 ファイル構成

```
riot-api-spectator-tool/
├── app.py                 # メインWebアプリケーション
├── riot_api_tool.py       # コアAPIツール
├── config.py.example      # 設定ファイルテンプレート
├── requirements.txt       # Python依存関係
├── templates/
│   ├── index.html        # メインページ
│   └── analytics.html    # 分析ダッシュボード
├── static/               # 静的ファイル
├── spectator_data/       # データ保存ディレクトリ
│   ├── spectator_data.db # SQLiteデータベース
│   └── [region]/[player]/ # プレイヤー別データ
└── README.md
```

## 📊 データ形式

### ライブゲームデータ
```json
{
  "target_player": {
    "game_name": "Hide on bush",
    "tag_line": "KR1",
    "puuid": "...",
    "region": "kr"
  },
  "download_time": "2025-05-29T10:30:00",
  "game_data": {
    "gameId": 123456789,
    "gameStartTime": 1234567890,
    "participants": [...],
    "bannedChampions": [...]
  }
}
```

### データベーススキーマ
- `game_records`: ゲーム履歴テーブル
- `player_stats`: プレイヤー統計テーブル

## 🐛 トラブルシューティング

### よくある問題

1. **API Key エラー**
   ```
   解決方法: Riot Developer PortalでAPI Keyを再取得
   ```

2. **プレイヤーが見つからない**
   ```
   解決方法: ゲーム名・タグライン・リージョンを確認
   ```

3. **ポートエラー**
   ```
   解決方法: config.pyでPORTを変更 (例: 5001)
   ```

### ログの確認
```bash
# アプリケーションログ
tail -f spectator_data/app.log

# コンソール出力で詳細確認
python app.py
```

## 🔒 プライバシーとセキュリティ

- API Keyはローカルに保存されます
- 取得データは個人利用目的のみ
- Riot Games利用規約に準拠
- パブリックAPIのみ使用

## 🤝 コントリビューション

プルリクエストや課題報告を歓迎します！

1. フォークしてください
2. 機能ブランチを作成 (`git checkout -b feature/amazing-feature`)
3. 変更をコミット (`git commit -m 'Add amazing feature'`)
4. ブランチにプッシュ (`git push origin feature/amazing-feature`)
5. プルリクエストを開いてください

## 📄 ライセンス

このプロジェクトはMITライセンスの下で公開されています。

## ⚠️ 免責事項

- このツールはRiot Games公式製品ではありません
- Riot Games API利用規約に従って使用してください
- 過度なAPI呼び出しはお控えください
- 個人利用目的でのみご使用ください

## 🔗 関連リンク

- [Riot Developer Portal](https://developer.riotgames.com/)
- [Riot Games API Documentation](https://developer.riotgames.com/apis)
- [League of Legends](https://www.leagueoflegends.com/)

## 💡 今後の予定

- [ ] チャンピオン別分析
- [ ] ランク変動追跡
- [ ] 試合結果自動取得
- [ ] Discord通知機能
- [ ] 複数リージョン同時監視
- [ ] データ可視化強化

---

**楽しいプロゲーム観戦を！** 🎮✨
