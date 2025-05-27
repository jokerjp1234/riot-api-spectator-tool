from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import json
import os
from datetime import datetime
from riot_api_tool import RiotAPISpectatorTool

try:
    from config import HOST, PORT, DEBUG
except ImportError:
    HOST = "127.0.0.1"
    PORT = 5000
    DEBUG = True

app = Flask(__name__)
CORS(app)  # CORS対応

# グローバル変数でツールインスタンスを管理
tool_instance = None

@app.route('/')
def index():
    """メインページ"""
    return render_template('index.html')

@app.route('/api/set_api_key', methods=['POST'])
def set_api_key():
    """API Keyを設定"""
    global tool_instance
    
    data = request.get_json()
    api_key = data.get('api_key')
    
    if not api_key:
        return jsonify({'success': False, 'error': 'API Keyが入力されていません'})
    
    try:
        tool_instance = RiotAPISpectatorTool(api_key)
        return jsonify({'success': True, 'message': 'API Keyが設定されました'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/add_player', methods=['POST'])
def add_player():
    """プレイヤーを監視対象に追加"""
    if not tool_instance:
        return jsonify({'success': False, 'error': 'API Keyを先に設定してください'})
    
    data = request.get_json()
    game_name = data.get('game_name')
    tag_line = data.get('tag_line')
    region = data.get('region')
    
    if not all([game_name, tag_line, region]):
        return jsonify({'success': False, 'error': 'すべてのフィールドを入力してください'})
    
    try:
        cluster = tool_instance.region_to_cluster.get(region, 'asia')
        success = tool_instance.add_player_to_monitor(game_name, tag_line, region, cluster)
        
        if success:
            return jsonify({
                'success': True, 
                'message': f'プレイヤー {game_name}#{tag_line} を追加しました',
                'players': get_monitored_players_data()
            })
        else:
            return jsonify({'success': False, 'error': 'プレイヤーの追加に失敗しました'})
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/remove_player', methods=['POST'])
def remove_player():
    """プレイヤーを監視対象から削除"""
    if not tool_instance:
        return jsonify({'success': False, 'error': 'API Keyを先に設定してください'})
    
    data = request.get_json()
    game_name = data.get('game_name')
    tag_line = data.get('tag_line')
    
    try:
        success = tool_instance.remove_player_from_monitor(game_name, tag_line)
        
        if success:
            return jsonify({
                'success': True,
                'message': f'プレイヤー {game_name}#{tag_line} を削除しました',
                'players': get_monitored_players_data()
            })
        else:
            return jsonify({'success': False, 'error': 'プレイヤーが見つかりません'})
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/start_monitoring', methods=['POST'])
def start_monitoring():
    """監視を開始"""
    if not tool_instance:
        return jsonify({'success': False, 'error': 'API Keyを先に設定してください'})
    
    if not tool_instance.monitored_players:
        return jsonify({'success': False, 'error': '監視対象プレイヤーがいません'})
    
    try:
        tool_instance.start_monitoring()
        return jsonify({
            'success': True,
            'message': f'{len(tool_instance.monitored_players)} 人のプレイヤーの監視を開始しました'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/stop_monitoring', methods=['POST'])
def stop_monitoring():
    """監視を停止"""
    if not tool_instance:
        return jsonify({'success': False, 'error': 'API Keyを先に設定してください'})
    
    try:
        tool_instance.stop_monitoring()
        return jsonify({'success': True, 'message': '監視を停止しました'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/get_players')
def get_players():
    """監視対象プレイヤーリストを取得"""
    if not tool_instance:
        return jsonify({'players': [], 'monitoring': False})
    
    return jsonify({
        'players': get_monitored_players_data(),
        'monitoring': tool_instance.monitoring
    })

@app.route('/api/add_pro_players', methods=['POST'])
def add_pro_players():
    """プロプレイヤーを一括追加"""
    if not tool_instance:
        return jsonify({'success': False, 'error': 'API Keyを先に設定してください'})
    
    data = request.get_json()
    region = data.get('region')
    
    if not region:
        return jsonify({'success': False, 'error': 'リージョンを選択してください'})
    
    try:
        tool_instance.add_pro_players_by_region(region)
        return jsonify({
            'success': True,
            'message': f'{region} のプロプレイヤーを追加しました',
            'players': get_monitored_players_data()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

def get_monitored_players_data():
    """監視対象プレイヤーのデータを取得"""
    if not tool_instance:
        return []
    
    players_data = []
    for player in tool_instance.monitored_players:
        is_playing = player['puuid'] in tool_instance.current_games
        players_data.append({
            'game_name': player['game_name'],
            'tag_line': player['tag_line'],
            'region': player['region'],
            'status': 'playing' if is_playing else 'waiting',
            'puuid': player['puuid']
        })
    
    return players_data

if __name__ == '__main__':
    print("🎮 Riot API ソロランク監視ツール Web Server")
    print(f"🌐 アクセス URL: http://{HOST}:{PORT}")
    print("📝 使用方法:")
    print("  1. Personal API Key を入力")
    print("  2. プレイヤー追加 (例: Faker#KR1)")
    print("  3. 監視開始")
    print("  4. ソロランク開始時に自動データダウンロード")
    print("\n⚠️  注意: config.py でAPI Keyを設定してください")
    
    app.run(host=HOST, port=PORT, debug=DEBUG)