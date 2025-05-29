import requests
import time
import json
import os
import sqlite3
from datetime import datetime, timedelta
import threading
from typing import Dict, List, Optional, Callable

try:
    from config import RIOT_API_KEY, MONITOR_INTERVAL, DATA_DIR, DATABASE_PATH, RATE_LIMIT_CALLS, RATE_LIMIT_SECONDS
except ImportError:
    RIOT_API_KEY = None
    MONITOR_INTERVAL = 10
    DATA_DIR = "spectator_data"
    DATABASE_PATH = "spectator_data/spectator_data.db"
    RATE_LIMIT_CALLS = 100
    RATE_LIMIT_SECONDS = 120

class RiotAPISpectatorTool:
    def __init__(self, api_key: str = None):
        """Riot API Spectator Tool初期化"""
        self.api_key = api_key or RIOT_API_KEY
        if not self.api_key:
            raise ValueError("API keyが設定されていません")
        
        # API制限管理
        self.rate_limit_calls = RATE_LIMIT_CALLS
        self.rate_limit_seconds = RATE_LIMIT_SECONDS
        self.api_calls = []
        
        # 監視関連
        self.monitored_players = []
        self.current_games = {}
        self.monitoring = False
        self.monitor_thread = None
        
        # コールバック関数
        self.on_game_start = None
        self.on_game_end = None
        
        # データディレクトリ作成
        os.makedirs(DATA_DIR, exist_ok=True)
        
        # データベース初期化
        self.init_database()
        
        # 地域とクラスターのマッピング
        self.regional_urls = {
            "br1": "br1.api.riotgames.com",
            "eun1": "eun1.api.riotgames.com", 
            "euw1": "euw1.api.riotgames.com",
            "jp1": "jp1.api.riotgames.com",
            "kr": "kr.api.riotgames.com",
            "la1": "la1.api.riotgames.com",
            "la2": "la2.api.riotgames.com",
            "na1": "na1.api.riotgames.com",
            "oc1": "oc1.api.riotgames.com",
            "tr1": "tr1.api.riotgames.com",
            "ru": "ru.api.riotgames.com"
        }
        
        self.region_to_cluster = {
            "br1": "americas",
            "eun1": "europe",
            "euw1": "europe", 
            "jp1": "asia",
            "kr": "asia",
            "la1": "americas",
            "la2": "americas",
            "na1": "americas",
            "oc1": "asia",
            "tr1": "europe",
            "ru": "europe"
        }
        
        # プロプレイヤーデータ（例）
        self.pro_players = {
            "LCK": [
                ("Faker", "KR1", "kr"),
                ("Canyon", "KR1", "kr"),
                ("Showmaker", "KR1", "kr"),
                ("Keria", "KR1", "kr"),
                ("Gumayusi", "KR1", "kr"),
            ],
            "LPL": [
                ("Uzi", "CN1", "kr"),  # 多くの中国プレイヤーは韓国サーバーでプレイ
                ("Knight", "CN1", "kr"),
                ("JackeyLove", "CN1", "kr"),
            ],
            "LCS": [
                ("Doublelift", "NA1", "na1"),
                ("Bjergsen", "NA1", "na1"),
                ("CoreJJ", "NA1", "na1"),
            ],
            "LEC": [
                ("Caps", "EUW", "euw1"),
                ("Rekkles", "EUW", "euw1"),
                ("Jankos", "EUW", "euw1"),
            ]
        }
        
    def init_database(self):
        """データベース初期化"""
        try:
            conn = sqlite3.connect(DATABASE_PATH)
            cursor = conn.cursor()
            
            # ゲームデータテーブル
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS game_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    puuid TEXT,
                    game_name TEXT,
                    tag_line TEXT,
                    game_id TEXT,
                    game_start_time INTEGER,
                    game_end_time INTEGER,
                    game_duration INTEGER,
                    participants TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 監視プレイヤーテーブル
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS monitored_players (
                    puuid TEXT PRIMARY KEY,
                    game_name TEXT,
                    tag_line TEXT,
                    region TEXT,
                    cluster TEXT,
                    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"データベース初期化エラー: {e}")
    
    def check_rate_limit(self):
        """レート制限チェック"""
        now = time.time()
        # 古いAPIコール記録を削除
        self.api_calls = [call_time for call_time in self.api_calls 
                         if now - call_time < self.rate_limit_seconds]
        
        if len(self.api_calls) >= self.rate_limit_calls:
            sleep_time = self.rate_limit_seconds - (now - self.api_calls[0])
            if sleep_time > 0:
                print(f"レート制限に達しました。{sleep_time:.1f}秒待機...")
                time.sleep(sleep_time)
        
        self.api_calls.append(now)
    
    def make_api_request(self, url: str, params: dict = None) -> dict:
        """API リクエスト実行"""
        self.check_rate_limit()
        
        headers = {"X-Riot-Token": self.api_key}
        
        try:
            response = requests.get(url, headers=headers, params=params, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                return None
            elif response.status_code == 429:
                print("レート制限エラー")
                time.sleep(10)
                return None
            else:
                print(f"API エラー: {response.status_code}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"リクエストエラー: {e}")
            return None
    
    def test_api_connection(self) -> bool:
        """API接続テスト"""
        test_url = "https://kr.api.riotgames.com/lol/summoner/v4/summoners/by-name/test"
        try:
            headers = {"X-Riot-Token": self.api_key}
            response = requests.get(test_url, headers=headers, timeout=5)
            # 401以外なら API key は有効（404は正常、プレイヤーが存在しないだけ）
            return response.status_code != 401
        except:
            return False
    
    def get_account_by_riot_id(self, game_name: str, tag_line: str, cluster: str) -> dict:
        """Riot IDでアカウント情報取得"""
        cluster_urls = {
            "americas": "americas.api.riotgames.com",
            "asia": "asia.api.riotgames.com", 
            "europe": "europe.api.riotgames.com"
        }
        
        base_url = cluster_urls.get(cluster, "asia.api.riotgames.com")
        url = f"https://{base_url}/riot/account/v1/accounts/by-riot-id/{game_name}/{tag_line}"
        
        return self.make_api_request(url)
    
    def get_summoner_by_puuid(self, puuid: str, region: str) -> dict:
        """PUUIDでサモナー情報取得"""
        base_url = self.regional_urls.get(region, "kr.api.riotgames.com")
        url = f"https://{base_url}/lol/summoner/v4/summoners/by-puuid/{puuid}"
        
        return self.make_api_request(url)
    
    def get_current_game(self, puuid: str, region: str) -> dict:
        """現在のゲーム情報取得"""
        base_url = self.regional_urls.get(region, "kr.api.riotgames.com")
        url = f"https://{base_url}/lol/spectator/v4/active-games/by-summoner/{puuid}"
        
        return self.make_api_request(url)
    
    def get_recent_match_history(self, puuid: str, cluster: str, count: int = 10) -> list:
        """最近のマッチ履歴取得"""
        cluster_urls = {
            "americas": "americas.api.riotgames.com",
            "asia": "asia.api.riotgames.com",
            "europe": "europe.api.riotgames.com"
        }
        
        base_url = cluster_urls.get(cluster, "asia.api.riotgames.com")
        url = f"https://{base_url}/lol/match/v5/matches/by-puuid/{puuid}/ids"
        
        match_ids = self.make_api_request(url, {"count": count})
        if not match_ids:
            return []
        
        matches = []
        for match_id in match_ids[:5]:  # 最新5試合のみ詳細取得
            match_url = f"https://{base_url}/lol/match/v5/matches/{match_id}"
            match_data = self.make_api_request(match_url)
            if match_data:
                matches.append(match_data)
        
        return matches
    
    def add_player_to_monitor(self, game_name: str, tag_line: str, region: str, cluster: str) -> bool:
        """プレイヤーを監視対象に追加"""
        try:
            # アカウント情報取得
            account = self.get_account_by_riot_id(game_name, tag_line, cluster)
            if not account:
                print(f"プレイヤー {game_name}#{tag_line} が見つかりません")
                return False
            
            puuid = account['puuid']
            
            # 既に追加済みかチェック
            for player in self.monitored_players:
                if player['puuid'] == puuid:
                    print(f"プレイヤー {game_name}#{tag_line} は既に監視対象です")
                    return False
            
            # サモナー情報取得
            summoner = self.get_summoner_by_puuid(puuid, region)
            if not summoner:
                print(f"サモナー情報の取得に失敗しました")
                return False
            
            player_data = {
                'puuid': puuid,
                'game_name': game_name,
                'tag_line': tag_line,
                'region': region,
                'cluster': cluster,
                'summoner_id': summoner['id'],
                'summoner_name': summoner['name'],
                'summoner_level': summoner['summonerLevel']
            }
            
            self.monitored_players.append(player_data)
            
            # データベースに保存
            try:
                conn = sqlite3.connect(DATABASE_PATH)
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO monitored_players 
                    (puuid, game_name, tag_line, region, cluster)
                    VALUES (?, ?, ?, ?, ?)
                ''', (puuid, game_name, tag_line, region, cluster))
                conn.commit()
                conn.close()
            except Exception as e:
                print(f"データベース保存エラー: {e}")
            
            print(f"プレイヤー {game_name}#{tag_line} を監視対象に追加しました")
            return True
            
        except Exception as e:
            print(f"プレイヤー追加エラー: {e}")
            return False
    
    def remove_player_from_monitor(self, game_name: str, tag_line: str) -> bool:
        """プレイヤーを監視対象から削除"""
        for i, player in enumerate(self.monitored_players):
            if player['game_name'] == game_name and player['tag_line'] == tag_line:
                removed_player = self.monitored_players.pop(i)
                
                # データベースからも削除
                try:
                    conn = sqlite3.connect(DATABASE_PATH)
                    cursor = conn.cursor()
                    cursor.execute('DELETE FROM monitored_players WHERE puuid = ?', 
                                 (removed_player['puuid'],))
                    conn.commit()
                    conn.close()
                except Exception as e:
                    print(f"データベース削除エラー: {e}")
                
                print(f"プレイヤー {game_name}#{tag_line} を監視対象から削除しました")
                return True
        
        print(f"プレイヤー {game_name}#{tag_line} が見つかりません")
        return False
    
    def list_monitored_players(self):
        """監視対象プレイヤー一覧表示"""
        if not self.monitored_players:
            print("監視対象プレイヤーはいません")
            return
        
        print("\n=== 監視対象プレイヤー ===")
        for i, player in enumerate(self.monitored_players, 1):
            status = "ゲーム中" if player['puuid'] in self.current_games else "待機中"
            print(f"{i}. {player['game_name']}#{player['tag_line']} ({player['region']}) - {status}")
    
    def add_pro_players_by_region(self, region: str) -> int:
        """地域別プロプレイヤー一括追加"""
        if region not in self.pro_players:
            print(f"地域 {region} のプロプレイヤーデータがありません")
            return 0
        
        added_count = 0
        for game_name, tag_line, server_region in self.pro_players[region]:
            cluster = self.region_to_cluster.get(server_region, "asia")
            if self.add_player_to_monitor(game_name, tag_line, server_region, cluster):
                added_count += 1
        
        print(f"{region} から {added_count} 人のプロプレイヤーを追加しました")
        return added_count
    
    def set_game_callbacks(self, on_game_start: Callable = None, on_game_end: Callable = None):
        """ゲーム開始/終了時のコールバック設定"""
        self.on_game_start = on_game_start
        self.on_game_end = on_game_end
    
    def monitor_players(self):
        """プレイヤー監視メインループ"""
        print(f"監視開始: {len(self.monitored_players)} 人のプレイヤーを監視中...")
        
        while self.monitoring:
            try:
                for player in self.monitored_players:
                    if not self.monitoring:
                        break
                    
                    puuid = player['puuid']
                    region = player['region']
                    
                    # 現在のゲーム状況取得
                    current_game = self.get_current_game(puuid, region)
                    
                    if current_game:
                        # ゲーム中
                        if puuid not in self.current_games:
                            # 新しいゲーム開始
                            self.current_games[puuid] = current_game
                            print(f"🎮 {player['game_name']}#{player['tag_line']} がゲームを開始しました")
                            
                            # データベースに保存
                            self.save_game_data(player, current_game, "start")
                            
                            # コールバック呼び出し
                            if self.on_game_start:
                                self.on_game_start(player, current_game)
                    else:
                        # ゲーム中ではない
                        if puuid in self.current_games:
                            # ゲーム終了
                            finished_game = self.current_games.pop(puuid)
                            print(f"🏁 {player['game_name']}#{player['tag_line']} のゲームが終了しました")
                            
                            # データベースに保存
                            self.save_game_data(player, finished_game, "end")
                            
                            # コールバック呼び出し
                            if self.on_game_end:
                                self.on_game_end(player)
                
                time.sleep(MONITOR_INTERVAL)
                
            except Exception as e:
                print(f"監視エラー: {e}")
                time.sleep(MONITOR_INTERVAL)
    
    def save_game_data(self, player: dict, game_data: dict, event_type: str):
        """ゲームデータをデータベースに保存"""
        try:
            conn = sqlite3.connect(DATABASE_PATH)
            cursor = conn.cursor()
            
            game_id = game_data.get('gameId')
            game_start_time = game_data.get('gameStartTime', 0)
            participants = json.dumps(game_data.get('participants', []))
            
            if event_type == "start":
                cursor.execute('''
                    INSERT INTO game_data 
                    (puuid, game_name, tag_line, game_id, game_start_time, participants)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (player['puuid'], player['game_name'], player['tag_line'], 
                     game_id, game_start_time, participants))
            else:  # end
                game_end_time = int(time.time() * 1000)
                game_duration = game_end_time - game_start_time
                cursor.execute('''
                    UPDATE game_data 
                    SET game_end_time = ?, game_duration = ?
                    WHERE game_id = ? AND puuid = ?
                ''', (game_end_time, game_duration, game_id, player['puuid']))
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"データ保存エラー: {e}")
    
    def start_monitoring(self):
        """監視開始"""
        if self.monitoring:
            print("既に監視中です")
            return
        
        if not self.monitored_players:
            print("監視対象プレイヤーがいません")
            return
        
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self.monitor_players, daemon=True)
        self.monitor_thread.start()
    
    def stop_monitoring(self):
        """監視停止"""
        if not self.monitoring:
            print("監視は開始されていません")
            return
        
        print("監視を停止中...")
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        self.current_games.clear()
        print("監視を停止しました")
    
    def get_analytics_data(self) -> dict:
        """分析データ取得"""
        try:
            conn = sqlite3.connect(DATABASE_PATH)
            cursor = conn.cursor()
            
            # 基本統計
            cursor.execute('SELECT COUNT(*) FROM game_data WHERE game_end_time IS NOT NULL')
            total_games = cursor.fetchone()[0]
            
            cursor.execute('SELECT AVG(game_duration/1000) FROM game_data WHERE game_duration IS NOT NULL')
            avg_duration = cursor.fetchone()[0] or 0
            
            cursor.execute('SELECT COUNT(DISTINCT puuid) FROM game_data')
            unique_players = cursor.fetchone()[0]
            
            # プレイヤー別統計
            cursor.execute('''
                SELECT game_name, tag_line, COUNT(*) as games_played
                FROM game_data 
                WHERE game_end_time IS NOT NULL
                GROUP BY puuid, game_name, tag_line
                ORDER BY games_played DESC
            ''')
            player_stats = [
                {'game_name': row[0], 'tag_line': row[1], 'games_played': row[2]}
                for row in cursor.fetchall()
            ]
            
            conn.close()
            
            return {
                'basic_stats': {
                    'total_games': total_games,
                    'avg_duration': round(avg_duration, 1),
                    'unique_players': unique_players
                },
                'player_stats': player_stats
            }
            
        except Exception as e:
            return {'error': str(e)}

def main():
    """メイン関数（コマンドライン用）"""
    print("🎮 Riot API ソロランク監視ツール v2.0")
    print("=" * 50)
    
    if not RIOT_API_KEY:
        api_key = input("Riot API Key を入力してください: ").strip()
        if not api_key:
            print("API Keyが必要です")
            return
    else:
        api_key = RIOT_API_KEY
    
    try:
        tool = RiotAPISpectatorTool(api_key)
    except ValueError as e:
        print(f"エラー: {e}")
        return
    
    # API接続テスト
    if not tool.test_api_connection():
        print("❌ API接続に失敗しました。API Keyを確認してください。")
        return
    
    print("✅ API接続成功!")
    
    while True:
        print("\n" + "=" * 50)
        print("1. プレイヤー追加")
        print("2. プレイヤー削除") 
        print("3. 監視対象プレイヤー一覧")
        print("4. プロプレイヤー一括追加")
        print("5. 監視開始")
        print("6. 監視停止")
        print("7. 利用可能地域表示")
        print("8. 分析データ表示")
        print("9. 終了")
        print("=" * 50)
        
        choice = input("選択してください (1-9): ").strip()
        
        if choice == "9":
            tool.stop_monitoring()
            print("ツールを終了します")
            break
        
        elif choice == "1":
            game_name = input("ゲーム名を入力: ").strip()
            tag_line = input("タグラインを入力: ").strip()
            
            print("\n利用可能地域:")
            available_regions = list(tool.regional_urls.keys())
            for i, region in enumerate(available_regions):
                print(f"{i+1}. {region}")
            
            try:
                region_idx = int(input(f"地域を選択 (1-{len(available_regions)}): ")) - 1
                region = available_regions[region_idx]
                cluster = tool.region_to_cluster.get(region, "asia")
                tool.add_player_to_monitor(game_name, tag_line, region, cluster)
            except (ValueError, IndexError):
                print("無効な選択です")

        elif choice == "2":
            game_name = input("削除するゲーム名を入力: ").strip()
            tag_line = input("削除するタグラインを入力: ").strip()
            tool.remove_player_from_monitor(game_name, tag_line)

        elif choice == "3":
            tool.list_monitored_players()

        elif choice == "4":
            print("\n利用可能地域:")
            available_regions = list(tool.pro_players.keys())
            for i, region in enumerate(available_regions):
                print(f"{i+1}. {region}")

            try:
                region_idx = int(input(f"地域を選択 (1-{len(available_regions)}): ")) - 1
                region = available_regions[region_idx]
                tool.add_pro_players_by_region(region)
            except (ValueError, IndexError):
                print("無効な選択です")

        elif choice == "5":
            tool.start_monitoring()
            print("\n監視を開始しました。Ctrl+C で停止できます。")
            try:
                while tool.monitoring:
                    time.sleep(1)
            except KeyboardInterrupt:
                tool.stop_monitoring()

        elif choice == "6":
            tool.stop_monitoring()

        elif choice == "7":
            print("\n=== 利用可能地域 ===")
            for region, url in tool.regional_urls.items():
                cluster = tool.region_to_cluster.get(region, "不明")
                print(f"{region}: {cluster} クラスター")

        elif choice == "8":
            analytics = tool.get_analytics_data()
            if 'error' in analytics:
                print(f"エラー: {analytics['error']}")
            else:
                print("\n=== 分析データ ===")
                print(f"総ゲーム数: {analytics['basic_stats']['total_games']}")
                print(f"平均ゲーム時間: {analytics['basic_stats']['avg_duration']} 秒")
                print(f"監視プレイヤー数: {analytics['basic_stats']['unique_players']}")
                
                if analytics['player_stats']:
                    print("\n=== プレイヤー統計 ===")
                    for stat in analytics['player_stats']:
                        print(f"{stat['game_name']}#{stat['tag_line']}: {stat['games_played']} ゲーム")

if __name__ == "__main__":
    main()
