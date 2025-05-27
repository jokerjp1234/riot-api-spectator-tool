// アプリケーション状態
let apiKeySet = false;
let monitoredPlayers = [];
let monitoring = false;
let updateInterval = null;

// ログ出力
function addLog(message, type = 'info') {
    const timestamp = new Date().toLocaleTimeString();
    const logContainer = document.getElementById('logContainer');
    const logEntry = document.createElement('div');
    logEntry.className = `log-entry log-${type}`;
    logEntry.textContent = `[${timestamp}] ${message}`;
    logContainer.appendChild(logEntry);
    logContainer.scrollTop = logContainer.scrollHeight;
}

// API Key設定
async function setApiKey() {
    const keyInput = document.getElementById('apiKey');
    const apiKey = keyInput.value.trim();
    
    if (!apiKey) {
        document.getElementById('apiStatus').innerHTML = 
            '<span style="color: #e74c3c;">✗ API Keyが入力されていません</span>';
        addLog('API Keyの設定に失敗しました', 'error');
        return;
    }
    
    try {
        const response = await fetch('/api/set_api_key', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ api_key: apiKey })
        });
        
        const data = await response.json();
        
        if (data.success) {
            apiKeySet = true;
            document.getElementById('apiStatus').innerHTML = 
                '<span style="color: #27ae60;">✓ API Key設定完了</span>';
            addLog('API Keyが設定されました', 'success');
        } else {
            document.getElementById('apiStatus').innerHTML = 
                `<span style="color: #e74c3c;">✗ ${data.error}</span>`;
            addLog(`API Key設定エラー: ${data.error}`, 'error');
        }
    } catch (error) {
        addLog(`API呼び出しエラー: ${error.message}`, 'error');
    }
}

// プレイヤー追加
async function addPlayer() {
    if (!apiKeySet) {
        addLog('API Keyを先に設定してください', 'error');
        return;
    }

    const gameName = document.getElementById('gameName').value.trim();
    const tagLine = document.getElementById('tagLine').value.trim();
    const region = document.getElementById('region').value;

    if (!gameName || !tagLine || !region) {
        addLog('すべてのフィールドを入力してください', 'error');
        return;
    }

    addLog(`プレイヤー ${gameName}#${tagLine} を検索中...`, 'info');
    
    try {
        const response = await fetch('/api/add_player', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                game_name: gameName,
                tag_line: tagLine,
                region: region
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            monitoredPlayers = data.players;
            updatePlayerList();
            addLog(data.message, 'success');
            
            // フォームクリア
            document.getElementById('gameName').value = '';
            document.getElementById('tagLine').value = '';
        } else {
            addLog(`プレイヤー追加エラー: ${data.error}`, 'error');
        }
    } catch (error) {
        addLog(`API呼び出しエラー: ${error.message}`, 'error');
    }
}

// プロプレイヤー一括追加
async function addProPlayers() {
    if (!apiKeySet) {
        addLog('API Keyを先に設定してください', 'error');
        return;
    }

    const region = document.getElementById('region').value;
    if (!region) {
        addLog('リージョンを選択してください', 'error');
        return;
    }

    addLog(`${region} のプロプレイヤーを追加中...`, 'info');
    
    try {
        const response = await fetch('/api/add_pro_players', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ region: region })
        });
        
        const data = await response.json();
        
        if (data.success) {
            monitoredPlayers = data.players;
            updatePlayerList();
            addLog(data.message, 'success');
        } else {
            addLog(`プロプレイヤー追加エラー: ${data.error}`, 'error');
        }
    } catch (error) {
        addLog(`API呼び出しエラー: ${error.message}`, 'error');
    }
}

// プレイヤーリスト更新
function updatePlayerList() {
    const container = document.getElementById('playerList');
    const countElement = document.getElementById('playerCount');
    
    countElement.textContent = monitoredPlayers.length;
    
    if (monitoredPlayers.length === 0) {
        container.innerHTML = '<p style="color: #888; text-align: center; margin: 20px 0;">監視対象プレイヤーがいません</p>';
        return;
    }

    container.innerHTML = monitoredPlayers.map((player, index) => {
        const statusClass = player.status === 'playing' ? 'status-playing' : 'status-waiting';
        const statusText = player.status === 'playing' ? 'ゲーム中' : '待機中';
        
        return `
            <div class="player-item">
                <div class="player-info">
                    <div class="player-status ${statusClass}"></div>
                    <div>
                        <strong>${player.game_name}#${player.tag_line}</strong>
                        <div style="font-size: 0.9em; color: #888;">${player.region.toUpperCase()} - ${statusText}</div>
                    </div>
                </div>
                <button class="btn btn-danger" onclick="removePlayer('${player.game_name}', '${player.tag_line}')" style="margin: 0;">削除</button>
            </div>
        `;
    }).join('');
}

// プレイヤー削除
async function removePlayer(gameName, tagLine) {
    try {
        const response = await fetch('/api/remove_player', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                game_name: gameName,
                tag_line: tagLine
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            monitoredPlayers = data.players;
            updatePlayerList();
            addLog(data.message, 'info');
        } else {
            addLog(`プレイヤー削除エラー: ${data.error}`, 'error');
        }
    } catch (error) {
        addLog(`API呼び出しエラー: ${error.message}`, 'error');
    }
}

// 全プレイヤー削除
function clearPlayers() {
    if (monitoredPlayers.length === 0) {
        addLog('削除するプレイヤーがいません', 'warning');
        return;
    }
    
    // 全プレイヤーを順次削除
    const playersToDelete = [...monitoredPlayers];
    playersToDelete.forEach(player => {
        removePlayer(player.game_name, player.tag_line);
    });
}

// 監視開始
async function startMonitoring() {
    if (!apiKeySet) {
        addLog('API Keyを先に設定してください', 'error');
        return;
    }

    if (monitoredPlayers.length === 0) {
        addLog('監視対象プレイヤーがいません', 'error');
        return;
    }

    try {
        const response = await fetch('/api/start_monitoring', {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (data.success) {
            monitoring = true;
            document.getElementById('monitoringStatus').className = 'monitoring-status status-active';
            document.getElementById('monitoringStatus').textContent = '監視中';
            addLog(data.message, 'success');
            
            // 定期的にプレイヤーリストを更新
            startPlayerStatusUpdates();
        } else {
            addLog(`監視開始エラー: ${data.error}`, 'error');
        }
    } catch (error) {
        addLog(`API呼び出しエラー: ${error.message}`, 'error');
    }
}

// 監視停止
async function stopMonitoring() {
    try {
        const response = await fetch('/api/stop_monitoring', {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (data.success) {
            monitoring = false;
            document.getElementById('monitoringStatus').className = 'monitoring-status status-inactive';
            document.getElementById('monitoringStatus').textContent = '監視停止中';
            addLog(data.message, 'info');
            
            // 定期更新を停止
            stopPlayerStatusUpdates();
        } else {
            addLog(`監視停止エラー: ${data.error}`, 'error');
        }
    } catch (error) {
        addLog(`API呼び出しエラー: ${error.message}`, 'error');
    }
}

// プレイヤーステータス更新開始
function startPlayerStatusUpdates() {
    if (updateInterval) {
        clearInterval(updateInterval);
    }
    
    // 5秒ごとにプレイヤーリストを更新
    updateInterval = setInterval(async () => {
        if (!monitoring) return;
        
        try {
            const response = await fetch('/api/get_players');
            const data = await response.json();
            
            if (data.players) {
                const oldPlayers = [...monitoredPlayers];
                monitoredPlayers = data.players;
                
                // ステータス変更をチェック
                checkStatusChanges(oldPlayers, monitoredPlayers);
                
                updatePlayerList();
            }
        } catch (error) {
            console.error('Player status update error:', error);
        }
    }, 5000);
}

// プレイヤーステータス更新停止
function stopPlayerStatusUpdates() {
    if (updateInterval) {
        clearInterval(updateInterval);
        updateInterval = null;
    }
}

// ステータス変更チェック
function checkStatusChanges(oldPlayers, newPlayers) {
    newPlayers.forEach(newPlayer => {
        const oldPlayer = oldPlayers.find(p => p.puuid === newPlayer.puuid);
        
        if (oldPlayer && oldPlayer.status !== newPlayer.status) {
            if (newPlayer.status === 'playing') {
                addLog(`🎮 ${newPlayer.game_name}#${newPlayer.tag_line} がソロランクを開始しました！`, 'success');
            } else if (newPlayer.status === 'waiting') {
                addLog(`🏁 ${newPlayer.game_name}#${newPlayer.tag_line} のゲームが終了しました`, 'info');
            }
        }
    });
}

// 初期化
document.addEventListener('DOMContentLoaded', function() {
    updatePlayerList();
    addLog('ツールが起動しました', 'info');
    
    // 定期的にプレイヤーリストを取得
    setInterval(async () => {
        if (!apiKeySet) return;
        
        try {
            const response = await fetch('/api/get_players');
            const data = await response.json();
            
            if (data.players) {
                monitoredPlayers = data.players;
                monitoring = data.monitoring;
                
                // 監視状態の更新
                if (monitoring) {
                    document.getElementById('monitoringStatus').className = 'monitoring-status status-active';
                    document.getElementById('monitoringStatus').textContent = '監視中';
                } else {
                    document.getElementById('monitoringStatus').className = 'monitoring-status status-inactive';
                    document.getElementById('monitoringStatus').textContent = '監視停止中';
                }
                
                updatePlayerList();
            }
        } catch (error) {
            console.error('Periodic update error:', error);
        }
    }, 10000); // 10秒ごと
});