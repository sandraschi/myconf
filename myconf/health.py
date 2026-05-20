"""
myconf/health.py — Shared health check utilities for all AG-Visio services.
"""

import logging
import socket
import time
from typing import Any

logger = logging.getLogger("ag-visio-health")


def check_tcp_port(host: str, port: int, timeout: float = 0.5) -> dict[str, Any]:
    start = time.perf_counter()
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(timeout)
            if s.connect_ex((host, port)) == 0:
                return {
                    "status": "ALIVE",
                    "host": host,
                    "port": port,
                    "latency_ms": int((time.perf_counter() - start) * 1000),
                }
            return {"status": "DEAD", "host": host, "port": port, "latency_ms": -1}
    except Exception as e:
        return {"status": "ERROR", "host": host, "port": port, "error": str(e)}


def check_ollama(timeout: float = 1.0) -> dict[str, Any]:
    try:
        import aiohttp
    except ImportError:
        return {"status": "UNKNOWN", "error": "aiohttp not installed"}
    import asyncio

    async def _probe():
        start = time.perf_counter()
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(
                    "http://localhost:11434/api/tags", timeout=aiohttp.ClientTimeout(total=timeout)
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return {
                            "status": "ALIVE",
                            "models": [m["name"] for m in data.get("models", [])],
                            "latency_ms": int((time.perf_counter() - start) * 1000),
                        }
                    return {"status": f"DEGRADED ({resp.status})"}
            except Exception:
                return {"status": "OFFLINE"}

    return asyncio.run(_probe())


def health_response(service: str, checks: dict[str, Any]) -> dict[str, Any]:
    all_alive = all(v.get("status") == "ALIVE" for v in checks.values() if isinstance(v, dict))
    return {
        "service": service,
        "status": "PASS" if all_alive else "DEGRADED",
        "checks": checks,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
