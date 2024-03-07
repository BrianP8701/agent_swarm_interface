"""
This is responsible for sending messages to clients over
websocket connections to update the UI.
"""
from typing import Dict
from fastapi import WebSocket
from pydantic import BaseModel


class WebsocketEvent(BaseModel):
    type: str
    data: dict


"""
type: "update_swarm"
data: {swarm: UserSwarm}

type: "append_message_to_chat"
data: {message: SwarmMessage} 
"""

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, user_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[user_id] = websocket

    def disconnect(self, user_id: str):
        if user_id in self.active_connections:
            del self.active_connections[user_id]

    def is_connected(self, user_id: str) -> bool:
        return user_id in self.active_connections

    async def send_personal_message(
        self, websocket_event: WebsocketEvent, user_id: str
    ):
        """
        Client id is username
        """
        print(f"\n\nSending message {websocket_event} to {user_id}\n\n")
        if type(websocket_event) is dict:
            websocket_event = WebsocketEvent.model_validate(websocket_event)
        if user_id in self.active_connections:
            websocket = self.active_connections[user_id]
            try:
                await websocket.send_json(websocket_event.model_dump())
            except Exception as e:
                print(f"Error sending message: {e}")
                # Disconnect the WebSocket connection
                self.disconnect(user_id)

    async def broadcast(self, message: dict):
        for user_id, connection in list(self.active_connections.items()):
            try:
                await connection.send_json(message)
            except Exception as e:
                print(f"Error broadcasting message: {e}")
                # Disconnect the WebSocket connection
                self.disconnect(user_id)
                
manager = ConnectionManager()