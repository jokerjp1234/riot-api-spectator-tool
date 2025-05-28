from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import json
import os
from datetime import datetime, timedelta
from riot_api_tool import RiotAPISpectatorTool
import threading
import time

try:
    from config import HOST, PORT, DEBUG, SECRET_KEY
except ImportError:
    HOST = "127.0.0.1"
    PORT = 5000
    DEBUG = True
    SECRET_KEY = "your-secret-key-here"

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
CORS(app)  # CORS対応
socketio = SocketIO(app, cors_allowed_origins="*")

# グローバル変数でツールインスタンスを管理
tool_instance = None
connected_clients = set()

@app.route('/')
def index():
    """メインページ"""
    return render_template('index.html')

@app.route('/analytics')
def analytics():
    """分析ページ"""
    return render_template('analytics.html')

@socketio.on('connect')
def handle_connect():
    """WebSocket接続"""
    connected_clients.add(request.sid)
    print(f"クライアント接続: {request.sid}")
    
    # 現在の状態を送信
    if tool_instance:
        emit('players_updated', {
            'players': get_monitored_players_data(),
            'monitoring': tool_instance.monitoring
        })

@socketio.on('disconnect')
def handle_disconnect():
    """WebSocket切断"""
    connected_clients.discard(request.sid)
    print(f"クライアント切断: {request.sid}")

def broadcast_update(event, data):
    """全クライアントに更新を送信"""
    if connected_clients:
        socketio.emit(event, data)

@app.route('/api/set_api_key', methods=['POST'])
def set_api_key():
    """API Keyを設定"""
    global tool_instance
    
    try:
        data = request.get_json()
        api_key = data.get('api_key', '').strip()
        
        if not api_key:
            return jsonify({'success': False, 'error': 'API Keyが入力されていません'})
        
        if len(api_key) < 30:
            return jsonify({'success': False, 'error': 'API Keyの形式が正しくありません'})
        
        # 既存のツールがある場合は監視を停止
        if tool_instance:
            tool_instance.stop_monitoring()
        
        tool_instance = RiotAPISpectatorTool(api_key)
        
        # API Keyの有効性をテスト
        test_result = tool_instance.test_api_connection()
        if not test_result:
            tool_instance = None
            return jsonify({'success': False, 'error': 'API Keyが無効です。Riot Developer Portalで確認してください。'})
        
        broadcast_update('api_key_set', {'success': True})
        return jsonify({'success': True, 'message': 'API Keyが正常に設定されました'})
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'API Key設定エラー: {str(e)}'})

@app.route('/api/add_player', methods=['POST'])
def add_player():
    """プレイヤーを監視対象に追加"""
    if not tool_instance:
        return jsonify({'success': False, 'error': 'API Keyを先に設定してください'})
    
    try:
        data = request.get_json()
        game_name = data.get('game_name', '').strip()
        tag_line = data.get('tag_line', '').strip()
        region = data.get('region', '').strip()
        
        if not all([game_name, tag_line, region]):
            return jsonify({'success': False, 'error': 'すべてのフィールドを入力してください'})
        
        cluster = tool_instance.region_to_cluster.get(region, 'asia')
        success = tool_instance.add_player_to_monitor(game_name, tag_line, region, cluster)
        
        if success:
            players_data = get_monitored_players_data()
            broadcast_update('players_updated', {
                'players': players_data,
                'monitoring': tool_instance.monitoring
            })
            
            return jsonify({
                'success': True, 
                'message': f'プレイヤー {game_name}#{tag_line} を追加しました',
                'players': players_data
            })
        else:
            return jsonify({'success': False, 'error': 'プレイヤーの追加に失敗しました。名前やタグライン、地域を確認してください。'})
            
    except Exception as e:
        return jsonify({'success': False, 'error': f'プレイヤー追加エラー: {str(e)}'})

@app.route('/api/remove_player', methods=['POST'])
def remove_player():
    """プレイヤーを監視対象から削除"""
    if not tool_instance:
        return jsonify({'success': False, 'error': 'API Keyを先に設定してください'})
    
    try:
        data = request.get_json()
        game_name = data.get('game_name', '').strip()
        tag_line = data.get('tag_line', '').strip()
        
        success = tool_instance.remove_player_from_monitor(game_name, tag_line)
        
        if success:
            players_data = get_monitored_players_data()
            broadcast_update('players_updated', {
                'players': players_data,
                'monitoring': tool_instance.monitoring
            })
            
            return jsonify({
                'success': True,
                'message': f'プレイヤー {game_name}#{tag_line} を削除しました',
                'players': players_data
            })
        else:
            return jsonify({'success': False, 'error': 'プレイヤーが見つかりません'})
            
    except Exception as e:
        return jsonify({'success': False, 'error': f'プレイヤー削除エラー: {str(e)}'})

@app.route('/api/start_monitoring', methods=['POST'])
def start_monitoring():
    """監視を開始"""
    if not tool_instance:
        return jsonify({'success': False, 'error': 'API Keyを先に設定してください'})
    
    if not tool_instance.monitored_players:
        return jsonify({'success': False, 'error': '監視対象プレイヤーがいません'})
    
    try:
        # カスタムコールバックを設定
        tool_instance.set_game_callbacks(
            on_game_start=on_player_game_start,
            on_game_end=on_player_game_end
        )
        
        tool_instance.start_monitoring()
        
        broadcast_update('monitoring_started', {
            'monitoring': True,
            'players': get_monitored_players_data()
        })
        
        return jsonify({
            'success': True,
            'message': f'{len(tool_instance.monitored_players)} 人のプレイヤーの監視を開始しました'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': f'監視開始エラー: {str(e)}'})

@app.route('/api/stop_monitoring', methods=['POST'])
def stop_monitoring():
    """監視を停止"""
    if not tool_instance:
        return jsonify({'success': False, 'error': 'API Keyを先に設定してください'})
    
    try:
        tool_instance.stop_monitoring()
        
        broadcast_update('monitoring_stopped', {
            'monitoring': False,
            'players': get_monitored_players_data()
        })
        
        return jsonify({'success': True, 'message': '監視を停止しました'})
    except Exception as e:
        return jsonify({'success': False, 'error': f'監視停止エラー: {str(e)}'})

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
    
    try:
        data = request.get_json()
        region = data.get('region', '').strip()
        
        if not region:
            return jsonify({'success': False, 'error': 'リージョンを選択してください'})
        
        added_count = tool_instance.add_pro_players_by_region(region)
        
        players_data = get_monitored_players_data()
        broadcast_update('players_updated', {
            'players': players_data,
            'monitoring': tool_instance.monitoring
        })
        
        return jsonify({
            'success': True,
            'message': f'{region} から {added_count} 人のプロプレイヤーを追加しました',
            'players': players_data
        })
    except Exception as e:
        return jsonify({'success': False, 'error': f'プロプレイヤー追加エラー: {str(e)}'})

@app.route('/api/get_analytics_data')
def get_analytics_data():
    """分析データを取得"""
    if not tool_instance:
        return jsonify({'error': 'API Keyを先に設定してください'})
    
    try:
        analytics_data = tool_instance.get_analytics_data()
        return jsonify(analytics_data)
    except Exception as e:
        return jsonify({'error': f'分析データ取得エラー: {str(e)}'})

@app.route('/api/get_recent_games/<puuid>')
def get_recent_games(puuid):
    """特定プレイヤーの最近のゲーム履歴を取得"""
    if not tool_instance:
        return jsonify({'error': 'API Keyを先に設定してください'})
    
    try:
        # プレイヤー情報を取得
        player = None
        for p in tool_instance.monitored_players:
            if p['puuid'] == puuid:
                player = p
                break
        
        if not player:
            return jsonify({'error': 'プレイヤーが見つかりません'})
        
        recent_games = tool_instance.get_recent_match_history(puuid, player['cluster'])
        return jsonify({'games': recent_games})
        
    except Exception as e:
        return jsonify({'error': f'ゲーム履歴取得エラー: {str(e)}'})

def on_player_game_start(player, game_data):
    """プレイヤーのゲーム開始時コールバック"""
    broadcast_update('game_started', {
        'player': {
            'game_name': player['game_name'],
            'tag_line': player['tag_line'],
            'puuid': player['puuid']
        },
        'game_info': {
            'gameId': game_data.get('gameId'),
            'gameStartTime': game_data.get('gameStartTime'),
            'participants': len(game_data.get('participants', []))
        },
        'players': get_monitored_players_data()
    })

def on_player_game_end(player):
    """プレイヤーのゲーム終了時コールバック"""
    broadcast_update('game_ended', {
        'player': {
            'game_name': player['game_name'],
            'tag_line': player['tag_line'],
            'puuid': player['puuid']
        },
        'players': get_monitored_players_data()
    })

def get_monitored_players_data():
    """監視対象プレイヤーのデータを取得"""
    if not tool_instance:
        return []
    
    players_data = []
    for player in tool_instance.monitored_players:
        is_playing = player['puuid'] in tool_instance.current_games
        game_info = None
        
        if is_playing:
            game_data = tool_instance.current_games[player['puuid']]
            game_info = {
                'gameId': game_data.get('gameId'),
                'gameLength': game_data.get('gameLength', 0),
                'participants': len(game_data.get('participants', []))
            }
        
        players_data.append({
            'game_name': player['game_name'],
            'tag_line': player['tag_line'],
            'region': player['region'],
            'status': 'playing' if is_playing else 'waiting',
            'puuid': player['puuid'],
            'game_info': game_info
        })
    
    return players_data

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    print("🎮 Riot API ソロランク監視ツール Web Server v2.0")
    print(f"🌐 アクセス URL: http://{HOST}:{PORT}")
    print("📊 新機能:")
    print("  • リアルタイム更新 (WebSocket)")
    print("  • データ分析ダッシュボード")
    print("  • エラーハンドリング強化")
    print("  • パフォーマンス最適化")
    print("\n📝 使用方法:")
    print("  1. Personal API Key を入力")
    print("  2. プレイヤー追加 (例: Faker#KR1)")
    print("  3. 監視開始")
    print("  4. リアルタイムでゲーム状況を確認")
    print("\n⚠️  注意: config.py でAPI Keyを設定してください")
    
    socketio.run(app, host=HOST, port=PORT, debug=DEBUG)
