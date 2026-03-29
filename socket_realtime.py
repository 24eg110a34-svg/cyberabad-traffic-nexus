"""
CYBERABAD TRAFFIC NEXUS - Socket Programming Module
Real-time bidirectional communication for live traffic updates
"""

import socket
import threading
import json
import time
from datetime import datetime
from collections import defaultdict
import queue

class TrafficSocketServer:
    """WebSocket-like server for real-time traffic updates"""
    
    def __init__(self, host='127.0.0.1', port=5555):
        self.host = host
        self.port = port
        self.server_socket = None
        self.clients = {}
        self.client_lock = threading.Lock()
        self.running = False
        self.message_queue = queue.Queue()
        self.subscriptions = defaultdict(set)  # client_id -> set of topics
        self.callbacks = {}
    
    def start(self):
        """Start the socket server"""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            self.running = True
            
            # Start accept thread
            accept_thread = threading.Thread(target=self._accept_connections)
            accept_thread.daemon = True
            accept_thread.start()
            
            # Start message sender thread
            sender_thread = threading.Thread(target=self._send_messages)
            sender_thread.daemon = True
            sender_thread.start()
            
            print(f"Socket server started on {self.host}:{self.port}")
            return True
        except Exception as e:
            print(f"Failed to start server: {e}")
            return False
    
    def stop(self):
        """Stop the socket server"""
        self.running = False
        with self.client_lock:
            for client_id, client_data in list(self.clients.items()):
                try:
                    client_data['socket'].close()
                except:
                    pass
            self.clients.clear()
        
        if self.server_socket:
            self.server_socket.close()
    
    def _accept_connections(self):
        """Accept incoming connections"""
        while self.running:
            try:
                self.server_socket.settimeout(1.0)
                try:
                    client_socket, address = self.server_socket.accept()
                    client_id = f"{address[0]}:{address[1]}"
                    
                    with self.client_lock:
                        self.clients[client_id] = {
                            'socket': client_socket,
                            'address': address,
                            'connected_at': datetime.now(),
                            'topics': set()
                        }
                    
                    # Start handler thread
                    handler_thread = threading.Thread(
                        target=self._handle_client,
                        args=(client_id, client_socket)
                    )
                    handler_thread.daemon = True
                    handler_thread.start()
                    
                    print(f"Client connected: {client_id}")
                    
                    # Send welcome message
                    self.send_to_client(client_id, {
                        'type': 'welcome',
                        'client_id': client_id,
                        'timestamp': datetime.now().isoformat()
                    })
                    
                except socket.timeout:
                    continue
            except Exception as e:
                if self.running:
                    print(f"Accept error: {e}")
    
    def _handle_client(self, client_id, client_socket):
        """Handle client communication"""
        while self.running:
            try:
                client_socket.settimeout(0.5)
                data = client_socket.recv(4096)
                
                if not data:
                    break
                
                message = data.decode('utf-8')
                self._process_message(client_id, message)
                
            except socket.timeout:
                continue
            except Exception as e:
                if self.running:
                    print(f"Client handler error ({client_id}): {e}")
                break
        
        # Cleanup
        with self.client_lock:
            if client_id in self.clients:
                try:
                    self.clients[client_id]['socket'].close()
                except:
                    pass
                del self.clients[client_id]
        
        print(f"Client disconnected: {client_id}")
    
    def _process_message(self, client_id, message):
        """Process incoming message from client"""
        try:
            data = json.loads(message)
            msg_type = data.get('type', 'unknown')
            
            if msg_type == 'subscribe':
                topics = data.get('topics', [])
                with self.client_lock:
                    if client_id in self.clients:
                        self.clients[client_id]['topics'].update(topics)
                self.send_to_client(client_id, {
                    'type': 'subscribed',
                    'topics': topics
                })
            
            elif msg_type == 'unsubscribe':
                topics = data.get('topics', [])
                with self.client_lock:
                    if client_id in self.clients:
                        self.clients[client_id]['topics'].difference_update(topics)
            
            elif msg_type == 'ping':
                self.send_to_client(client_id, {'type': 'pong'})
            
            elif msg_type == 'traffic_update':
                # Process traffic update from client
                self._trigger_callback('traffic_update', data)
            
            elif msg_type == 'alert':
                # Process alert from client
                self._trigger_callback('alert', data)
            
        except json.JSONDecodeError:
            print(f"Invalid JSON from {client_id}")
    
    def _send_messages(self):
        """Send queued messages to clients"""
        while self.running:
            try:
                message = self.message_queue.get(timeout=1.0)
                topic = message.get('topic')
                data = message.get('data')
                
                with self.client_lock:
                    for client_id, client_data in self.clients.items():
                        if topic in client_data['topics']:
                            try:
                                client_data['socket'].sendall(
                                    json.dumps(data).encode('utf-8')
                                )
                            except Exception as e:
                                print(f"Send error to {client_id}: {e}")
                
                self.message_queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Sender error: {e}")
    
    def send_to_client(self, client_id, data):
        """Send message to specific client"""
        with self.client_lock:
            if client_id in self.clients:
                try:
                    self.clients[client_id]['socket'].sendall(
                        json.dumps(data).encode('utf-8')
                    )
                    return True
                except Exception as e:
                    print(f"Send error: {e}")
        return False
    
    def broadcast(self, topic, data):
        """Broadcast message to all clients subscribed to topic"""
        self.message_queue.put({
            'topic': topic,
            'data': data
        })
    
    def broadcast_traffic_update(self, traffic_data):
        """Broadcast traffic update"""
        self.broadcast('traffic', {
            'type': 'traffic_update',
            'timestamp': datetime.now().isoformat(),
            'data': traffic_data
        })
    
    def broadcast_alert(self, alert):
        """Broadcast traffic alert"""
        self.broadcast('alerts', {
            'type': 'alert',
            'timestamp': datetime.now().isoformat(),
            'data': alert
        })
    
    def broadcast_signal_change(self, junction_id, signal_state):
        """Broadcast signal change"""
        self.broadcast('signals', {
            'type': 'signal_change',
            'timestamp': datetime.now().isoformat(),
            'junction_id': junction_id,
            'state': signal_state
        })
    
    def register_callback(self, event_type, callback):
        """Register callback for events"""
        self.callbacks[event_type] = callback
    
    def _trigger_callback(self, event_type, data):
        """Trigger registered callback"""
        if event_type in self.callbacks:
            try:
                self.callbacks[event_type](data)
            except Exception as e:
                print(f"Callback error: {e}")
    
    def get_client_count(self):
        """Get number of connected clients"""
        with self.client_lock:
            return len(self.clients)
    
    def get_client_info(self, client_id):
        """Get client information"""
        with self.client_lock:
            if client_id in self.clients:
                return {
                    'id': client_id,
                    'address': self.clients[client_id]['address'],
                    'connected_at': self.clients[client_id]['connected_at'].isoformat(),
                    'topics': list(self.clients[client_id]['topics'])
                }
        return None


class TrafficSocketClient:
    """Socket client for connecting to traffic server"""
    
    def __init__(self, host='127.0.0.1', port=5555):
        self.host = host
        self.port = port
        self.socket = None
        self.connected = False
        self.reconnect_delay = 5
        self.subscriptions = set()
        self.callbacks = {}
        self.listener_thread = None
        self.running = False
    
    def connect(self):
        """Connect to server"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            self.connected = True
            
            # Start listener thread
            self.running = True
            self.listener_thread = threading.Thread(target=self._listen)
            self.listener_thread.daemon = True
            self.listener_thread.start()
            
            print(f"Connected to server {self.host}:{self.port}")
            return True
        except Exception as e:
            print(f"Connection failed: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from server"""
        self.running = False
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
        self.connected = False
    
    def _listen(self):
        """Listen for incoming messages"""
        while self.running and self.connected:
            try:
                self.socket.settimeout(1.0)
                data = self.socket.recv(4096)
                
                if not data:
                    break
                
                message = json.loads(data.decode('utf-8'))
                self._handle_message(message)
                
            except socket.timeout:
                continue
            except Exception as e:
                if self.running:
                    print(f"Listen error: {e}")
                break
        
        self.connected = False
        print("Disconnected from server")
    
    def _handle_message(self, message):
        """Handle incoming message"""
        msg_type = message.get('type', 'unknown')
        
        if msg_type in self.callbacks:
            self.callbacks[msg_type](message)
    
    def send(self, data):
        """Send message to server"""
        if self.connected:
            try:
                self.socket.sendall(json.dumps(data).encode('utf-8'))
                return True
            except Exception as e:
                print(f"Send error: {e}")
                return False
        return False
    
    def subscribe(self, topics):
        """Subscribe to topics"""
        if isinstance(topics, str):
            topics = [topics]
        self.subscriptions.update(topics)
        return self.send({
            'type': 'subscribe',
            'topics': list(topics)
        })
    
    def unsubscribe(self, topics):
        """Unsubscribe from topics"""
        if isinstance(topics, str):
            topics = [topics]
        self.subscriptions.difference_update(topics)
        return self.send({
            'type': 'unsubscribe',
            'topics': list(topics)
        })
    
    def ping(self):
        """Send ping to server"""
        return self.send({'type': 'ping'})
    
    def register_callback(self, event_type, callback):
        """Register callback for events"""
        self.callbacks[event_type] = callback


# Global socket server instance
_socket_server = None

def get_socket_server():
    """Get global socket server instance"""
    global _socket_server
    if _socket_server is None:
        _socket_server = TrafficSocketServer()
    return _socket_server


# Test socket module
if __name__ == "__main__":
    print("Traffic Socket Module")
    print("=" * 50)
    
    # Start server
    server = TrafficSocketServer()
    if server.start():
        print("Server started successfully")
        time.sleep(2)
        print(f"Connected clients: {server.get_client_count()}")
        server.stop()
    
    print("Test complete")
