"""
Server-Sent Events (SSE) Manager.

Manages SSE connections and broadcasts workflow events to connected clients.
"""

import asyncio
import json
from collections import deque
from datetime import datetime
from typing import Dict, List, Any, AsyncGenerator

from api.config import APIConfig


class SSEManager:
    """
    Manages SSE connections and event broadcasting.

    Features:
    - Multiple clients per workflow
    - Event buffering for reconnections (last 100 events)
    - Automatic cleanup of disconnected clients
    """

    def __init__(self):
        """Initialize SSE manager."""
        # Active connections: workflow_id -> list of queues
        self.connections: Dict[str, List[asyncio.Queue]] = {}

        # Event buffer: workflow_id -> deque of events (max 100)
        self.event_buffer: Dict[str, deque] = {}

        # Max events to buffer per workflow
        self.max_buffer_size = 100

    async def connect(self, workflow_id: str) -> AsyncGenerator[str, None]:
        """
        Create SSE connection for a workflow.

        Args:
            workflow_id: Workflow UUID

        Yields:
            SSE-formatted event strings
        """
        # Create queue for this connection
        queue: asyncio.Queue = asyncio.Queue(maxsize=100)

        # Register connection
        if workflow_id not in self.connections:
            self.connections[workflow_id] = []
        self.connections[workflow_id].append(queue)

        try:
            # Send buffered events first (for reconnections)
            if workflow_id in self.event_buffer:
                for event in self.event_buffer[workflow_id]:
                    yield self._format_sse(event)

            # Stream new events
            while True:
                event = await queue.get()

                # Check for termination signal
                if event is None:
                    break

                yield self._format_sse(event)

        except asyncio.CancelledError:
            # Client disconnected
            pass
        finally:
            # Cleanup connection
            if workflow_id in self.connections:
                try:
                    self.connections[workflow_id].remove(queue)
                    if not self.connections[workflow_id]:
                        # No more connections for this workflow
                        del self.connections[workflow_id]
                except ValueError:
                    pass

    def emit(self, workflow_id: str, event_type: str, data: Dict[str, Any]) -> None:
        """
        Emit SSE event to all connected clients.

        Args:
            workflow_id: Workflow UUID
            event_type: Event type (node_started, node_completed, etc.)
            data: Event payload
        """
        event = {
            "type": event_type,
            "data": data,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }

        # Buffer event for reconnections
        if workflow_id not in self.event_buffer:
            self.event_buffer[workflow_id] = deque(maxlen=self.max_buffer_size)
        self.event_buffer[workflow_id].append(event)

        # DEBUG: Log event emission
        print(f"[SSE] Emitting {event_type} for workflow {workflow_id[:8]}... to {len(self.connections.get(workflow_id, []))} clients")

        # Emit to active connections
        if workflow_id in self.connections:
            disconnected = []
            for queue in self.connections[workflow_id]:
                try:
                    # Non-blocking put
                    queue.put_nowait(event)
                except asyncio.QueueFull:
                    # Client is slow, mark for disconnect
                    disconnected.append(queue)

            # Remove slow clients
            for queue in disconnected:
                try:
                    self.connections[workflow_id].remove(queue)
                except ValueError:
                    pass

    def close_connection(self, workflow_id: str) -> None:
        """
        Close all connections for a workflow.

        Sends termination signal to all clients.

        Args:
            workflow_id: Workflow UUID
        """
        if workflow_id in self.connections:
            for queue in self.connections[workflow_id]:
                try:
                    queue.put_nowait(None)  # Termination signal
                except asyncio.QueueFull:
                    pass

            # Clear connections
            del self.connections[workflow_id]

    def cleanup_workflow(self, workflow_id: str) -> None:
        """
        Cleanup workflow resources.

        Removes event buffer but keeps connections open.
        Call this after workflow completion to free memory.

        Args:
            workflow_id: Workflow UUID
        """
        if workflow_id in self.event_buffer:
            del self.event_buffer[workflow_id]

    def _format_sse(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format event as SSE message.

        Args:
            event: Event dictionary

        Returns:
            SSE-formatted dictionary
        """
        return {
            "event": event['type'],
            "data": json.dumps(event['data'])
        }

    def get_connection_count(self, workflow_id: str) -> int:
        """
        Get number of active connections for a workflow.

        Args:
            workflow_id: Workflow UUID

        Returns:
            Number of active connections
        """
        return len(self.connections.get(workflow_id, []))

    def get_buffer_size(self, workflow_id: str) -> int:
        """
        Get number of buffered events for a workflow.

        Args:
            workflow_id: Workflow UUID

        Returns:
            Number of buffered events
        """
        return len(self.event_buffer.get(workflow_id, []))


# Global SSE manager instance
_sse_manager: SSEManager = None


def get_sse_manager() -> SSEManager:
    """
    Get global SSE manager instance.

    Returns:
        SSEManager singleton
    """
    global _sse_manager
    if _sse_manager is None:
        _sse_manager = SSEManager()
    return _sse_manager
