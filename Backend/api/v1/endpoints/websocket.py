"""
WebSocket endpoints for real-time communication in Janus Prop AI Backend

This module provides WebSocket endpoints for real-time updates and communication.
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from fastapi.responses import HTMLResponse

from core.websocket_manager import get_websocket_manager

router = APIRouter()

@router.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """WebSocket endpoint for real-time communication."""
    websocket_manager = get_websocket_manager()
    await websocket_manager.handle_websocket(websocket, client_id)

@router.get("/ws/test")
async def websocket_test_page():
    """Test page for WebSocket connections."""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>WebSocket Test - Janus Prop AI</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            .container { max-width: 800px; margin: 0 auto; }
            .status { padding: 10px; margin: 10px 0; border-radius: 5px; }
            .connected { background-color: #d4edda; color: #155724; }
            .disconnected { background-color: #f8d7da; color: #721c24; }
            .message { background-color: #f8f9fa; border: 1px solid #dee2e6; padding: 10px; margin: 5px 0; border-radius: 3px; }
            button { padding: 10px 20px; margin: 5px; border: none; border-radius: 5px; cursor: pointer; }
            .connect { background-color: #28a745; color: white; }
            .disconnect { background-color: #dc3545; color: white; }
            .subscribe { background-color: #007bff; color: white; }
            .unsubscribe { background-color: #6c757d; color: white; }
            input { padding: 8px; margin: 5px; border: 1px solid #ddd; border-radius: 3px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>WebSocket Test - Janus Prop AI Backend</h1>
            
            <div id="status" class="status disconnected">Disconnected</div>
            
            <div>
                <button id="connectBtn" class="connect" onclick="connect()">Connect</button>
                <button id="disconnectBtn" class="disconnect" onclick="disconnect()" disabled>Disconnect</button>
            </div>
            
            <div style="margin: 20px 0;">
                <input type="text" id="channelInput" placeholder="Channel name (e.g., agent:eden)" value="agent:eden">
                <button id="subscribeBtn" class="subscribe" onclick="subscribe()" disabled>Subscribe</button>
                <button id="unsubscribeBtn" class="unsubscribe" onclick="unsubscribe()" disabled>Unsubscribe</button>
            </div>
            
            <div>
                <h3>Messages:</h3>
                <div id="messages"></div>
            </div>
            
            <div style="margin: 20px 0;">
                <h3>Send Message:</h3>
                <input type="text" id="messageInput" placeholder="Message type (e.g., ping, subscribe)">
                <button onclick="sendMessage()">Send</button>
            </div>
        </div>

        <script>
            let ws = null;
            let clientId = 'test_' + Math.random().toString(36).substr(2, 9);
            
            function updateStatus(connected) {
                const status = document.getElementById('status');
                const connectBtn = document.getElementById('connectBtn');
                const disconnectBtn = document.getElementById('disconnectBtn');
                const subscribeBtn = document.getElementById('subscribeBtn');
                const unsubscribeBtn = document.getElementById('unsubscribeBtn');
                
                if (connected) {
                    status.textContent = 'Connected';
                    status.className = 'status connected';
                    connectBtn.disabled = true;
                    disconnectBtn.disabled = false;
                    subscribeBtn.disabled = false;
                    unsubscribeBtn.disabled = false;
                } else {
                    status.textContent = 'Disconnected';
                    status.className = 'status disconnected';
                    connectBtn.disabled = false;
                    disconnectBtn.disabled = true;
                    subscribeBtn.disabled = true;
                    unsubscribeBtn.disabled = true;
                }
            }
            
            function addMessage(message, type = 'info') {
                const messages = document.getElementById('messages');
                const messageDiv = document.createElement('div');
                messageDiv.className = 'message';
                messageDiv.innerHTML = `<strong>[${new Date().toLocaleTimeString()}] ${type}:</strong> ${message}`;
                messages.appendChild(messageDiv);
                messages.scrollTop = messages.scrollHeight;
            }
            
            function connect() {
                const wsUrl = `ws://${window.location.host}/api/v1/ws/ws/${clientId}`;
                ws = new WebSocket(wsUrl);
                
                ws.onopen = function(event) {
                    updateStatus(true);
                    addMessage('WebSocket connected', 'success');
                };
                
                ws.onmessage = function(event) {
                    try {
                        const data = JSON.parse(event.data);
                        addMessage(JSON.stringify(data, null, 2), 'received');
                    } catch (e) {
                        addMessage(event.data, 'received');
                    }
                };
                
                ws.onclose = function(event) {
                    updateStatus(false);
                    addMessage('WebSocket disconnected', 'warning');
                    ws = null;
                };
                
                ws.onerror = function(error) {
                    addMessage('WebSocket error: ' + error, 'error');
                };
            }
            
            function disconnect() {
                if (ws) {
                    ws.close();
                }
            }
            
            function subscribe() {
                if (ws && ws.readyState === WebSocket.OPEN) {
                    const channel = document.getElementById('channelInput').value;
                    const message = {
                        type: 'subscribe',
                        channel: channel
                    };
                    ws.send(JSON.stringify(message));
                    addMessage(`Subscribed to channel: ${channel}`, 'info');
                }
            }
            
            function unsubscribe() {
                if (ws && ws.readyState === WebSocket.OPEN) {
                    const channel = document.getElementById('channelInput').value;
                    const message = {
                        type: 'unsubscribe',
                        channel: channel
                    };
                    ws.send(JSON.stringify(message));
                    addMessage(`Unsubscribed from channel: ${channel}`, 'info');
                }
            }
            
            function sendMessage() {
                if (ws && ws.readyState === WebSocket.OPEN) {
                    const messageType = document.getElementById('messageInput').value;
                    const message = {
                        type: messageType
                    };
                    
                    if (messageType === 'subscribe' || messageType === 'unsubscribe') {
                        const channel = document.getElementById('channelInput').value;
                        message.channel = channel;
                    }
                    
                    ws.send(JSON.stringify(message));
                    addMessage(`Sent: ${JSON.stringify(message)}`, 'sent');
                }
            }
            
            // Auto-connect on page load
            window.onload = function() {
                connect();
            };
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@router.get("/ws/status")
async def websocket_status():
    """Get WebSocket connection status and statistics."""
    try:
        websocket_manager = get_websocket_manager()
        return {
            "status": "active",
            "connections": websocket_manager.get_connection_count(),
            "subscriptions": {
                "total_channels": len(websocket_manager.connection_manager.subscriptions),
                "channels": list(websocket_manager.connection_manager.subscriptions.keys())
            },
            "timestamp": websocket_manager.connection_manager.active_connections
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "connections": 0,
            "subscriptions": {"total_channels": 0, "channels": []}
        }
