import asyncio
import json
import logging
from collections.abc import AsyncGenerator
from typing import Any

logger = logging.getLogger(__name__)


class SSEBroker:
    def __init__(self):
        self._subscribers: set[asyncio.Queue] = set()
        self._lock = asyncio.Lock()

    async def subscribe(self) -> asyncio.Queue:
        queue: asyncio.Queue = asyncio.Queue()
        async with self._lock:
            self._subscribers.add(queue)
            logger.info(f"New SSE client connected. Active connections: {len(self._subscribers)}")
        return queue

    async def unsubscribe(self, queue: asyncio.Queue) -> None:
        async with self._lock:
            self._subscribers.discard(queue)
            logger.info(f"SSE client disconnected. Active connections: {len(self._subscribers)}")

    async def publish(self, event: str, data: Any) -> None:
        if not self._subscribers:
            return

        payload = f"event: {event}\ndata: {json.dumps(data)}\n\n"
        async with self._lock:
            disconnected = []
            for q in self._subscribers:
                try:
                    q.put_nowait(payload)
                except asyncio.QueueFull:
                    disconnected.append(q)

            for q in disconnected:
                self._subscribers.discard(q)

    async def sse_generator(self, queue: asyncio.Queue) -> AsyncGenerator[str, None]:
        try:
            # Yield initial connection confirmation
            yield f"event: status\ndata: {json.dumps({'status': 'connected'})}\n\n"

            while True:
                try:
                    # Wait for message with 15s timeout for ping keepalive
                    msg = await asyncio.wait_for(queue.get(), timeout=15.0)
                    yield msg
                except TimeoutError:
                    # Send periodic ping keepalive to prevent proxy timeout
                    yield ": ping\n\n"
        except asyncio.CancelledError:
            pass
        finally:
            await self.unsubscribe(queue)


# Global singleton broker
sse_broker = SSEBroker()
