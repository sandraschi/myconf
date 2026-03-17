"""
apps/agent/state_bus.py — Inter-Agent Coordination Layer
Uses Redis for cross-agent state synchronization.
"""

import json
import logging

import redis.asyncio as redis

logger = logging.getLogger("ag-visio-agent")


class StateBus:
    def __init__(self, host: str = "localhost", port: int = 6379):
        self._host = host
        self._port = port
        self._redis = None
        self._pubsub = None

    async def connect(self):
        """ESTABLISH DISCOVERY PROTOCOL."""
        try:
            self._redis = redis.Redis(host=self._host, port=self._port, decode_responses=True)
            await self._redis.ping()
            logger.info("SOTA: State Bus connected to Redis at %s:%d", self._host, self._port)
        except Exception as e:
            logger.error("State Bus connection failed: %s", e)

    async def publish_state(self, agent_id: str, state: dict):
        """Broadcast state updates to the fleet."""
        if not self._redis:
            return
        payload = json.dumps({"agent_id": agent_id, "state": state})
        await self._redis.publish("ag_visio_fleet_state", payload)

    async def subscribe_to_fleet(self, callback):
        """Listen for state updates from other agents."""
        if not self._redis:
            return
        self._pubsub = self._redis.pubsub()
        await self._pubsub.subscribe("ag_visio_fleet_state")

        async for message in self._pubsub.listen():
            if message["type"] == "message":
                data = json.loads(message["data"])
                await callback(data)
