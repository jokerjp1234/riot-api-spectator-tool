#!/bin/bash

# Riot API Spectator Tool インストールスクリプト

echo "🎮 Riot API Spectator Tool セットアップを開始します..."
echo ""

# Python バージョンチェック
if command -v python3 &> /dev/null; then
    PYTHON_CMD=python3
elif command -v python &> /dev/null; then
    PYTHON_CMD=python
else
    echo "❌ Python が見つかりません。Python 3.7+ をインストールしてください。"
    exit 1
fi

echo "✓ Python が見つかりました: $($PYTHON_CMD --version)"

# pip バージョンチェック
if command -v pip3 &> /dev/null; then
    PIP_CMD=pip3
elif command -v pip &> /dev/null; then
    PIP_CMD=pip
else
    echo "❌ pip が見つかりません。pip をインストールしてください。"
    exit 1
fi

echo "✓ pip が見つかりました"

# 依存関係インストール
echo ""
echo "📦 依存関係をインストール中..."
$PIP_CMD install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✓ 依存関係のインストールが完了しました"
else
    echo "❌ 依存関係のインストールに失敗しました"
    exit 1
fi

# 設定ファイル作成
echo ""
echo "⚙️ 設定ファイルを作成中..."

if [ ! -f config.py ]; then
    cp config.py.example config.py
    echo "✓ config.py を作成しました"
    echo "📝 config.py を編集してAPI Keyを設定してください"
else
    echo "⚠️ config.py は既に存在します"
fi

# データディレクトリ作成
echo ""
echo "📁 データディレクトリを作成中..."
mkdir -p spectator_data
echo "✓ spectator_data ディレクトリを作成しました"

# 実行権限付与
echo ""
echo "🔧 実行権限を設定中..."
chmod +x install.sh
chmod +x run.sh
echo "✓ 実行権限を設定しました"

echo ""
echo "🎉 セットアップが完了しました!"
echo ""
echo "📋 次の手順:"
echo "  1. Riot Developer Portal でAPI Keyを取得"
echo "     https://developer.riotgames.com/"
echo "  2. config.py を編集してAPI Keyを設定"
echo "  3. ./run.sh でツールを起動"
echo ""
echo "💡 使用方法:"
echo "  CLI版:    python3 riot_api_tool.py"
echo "  Web版:    python3 app.py"
echo "  簡単起動: ./run.sh"
echo ""