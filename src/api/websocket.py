"""WebSocket support for real-time signal delivery."""

from typing import Set
from fastapi import WebSocket, WebSocketDisconnect
from loguru import logger
import json


class ConnectionManager:
    """Manage WebSocket connections."""

    def __init__(self):
        """Initialize connection manager."""
        self.active_connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket) -> None:
        """
        Accept new WebSocket connection.

        Args:
            websocket: WebSocket connection

        Example:
            >>> await manager.connect(websocket)
        """
        await websocket.accept()
        self.active_connections.add(websocket)
        logger.info(f"WebSocket connected. Total: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket) -> None:
        """
        Remove WebSocket connection.

        Args:
            websocket: WebSocket connection
        """
        self.active_connections.discard(websocket)
        logger.info(f"WebSocket disconnected. Total: {len(self.active_connections)}")

    async def send_personal_message(self, message: dict, websocket: WebSocket) -> None:
        """
        Send message to specific connection.

        Args:
            message: Message data
            websocket: Target WebSocket
        """
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"Send message error: {e}")

    async def broadcast(self, message: dict) -> None:
        """
        Broadcast message to all connections.

        Args:
            message: Message to broadcast

        Example:
            >>> await manager.broadcast({"type": "signal", "data": signal_data})
        """
        disconnected = set()

        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Broadcast error: {e}")
                disconnected.add(connection)

        # Remove disconnected clients
        for connection in disconnected:
            self.disconnect(connection)

    async def broadcast_signal(self, signal_data: dict) -> None:
        """
        Broadcast trading signal to all connections.

        Args:
            signal_data: Signal data dictionary

        Example:
            >>> await manager.broadcast_signal({
            ...     "symbol": "EURUSD",
            ...     "action": "BUY",
            ...     "entry_price": 1.1000
            ... })
        """
        message = {
            "type": "trading_signal",
            "data": signal_data,
            "timestamp": str(__import__("datetime").datetime.utcnow()),
        }

        await self.broadcast(message)
        logger.info(f"Signal broadcasted: {signal_data.get('symbol')}")


# Global connection manager instance
manager = ConnectionManager()
