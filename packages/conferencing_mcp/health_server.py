"""
packages/conferencing_mcp/health_server.py — Health endpoint + Prometheus metrics.
"""

import json
import logging
import time
from http.server import BaseHTTPRequestHandler, HTTPServer

from myconf.health import check_ollama, check_tcp_port, health_response

logger = logging.getLogger("conferencing-health")


class MetricsHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/health":
            checks = {
                "livekit": check_tcp_port("localhost", 15580),
                "ollama": check_ollama(),
                "mcp_server": {"status": "ALIVE"},
            }
            resp = health_response("conferencing-mcp", checks)
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(resp).encode())

        elif self.path == "/metrics":
            lk = check_tcp_port("localhost", 15580)
            ol = check_ollama()
            metrics = (
                "# HELP livekit_up LiveKit server reachability\n"
                "# TYPE livekit_up gauge\n"
                f"livekit_up {1 if lk.get('status') == 'ALIVE' else 0}\n"
                "# HELP livekit_latency_ms LiveKit connection latency\n"
                "# TYPE livekit_latency_ms gauge\n"
                f"livekit_latency_ms {lk.get('latency_ms', -1)}\n"
                "# HELP ollama_up Ollama server reachability\n"
                "# TYPE ollama_up gauge\n"
                f"ollama_up {1 if ol.get('status') == 'ALIVE' else 0}\n"
                "# HELP ollama_models_count Number of installed Ollama models\n"
                "# TYPE ollama_models_count gauge\n"
                f"ollama_models_count {len(ol.get('models', []))}\n"
                "# HELP mcp_uptime_seconds MCP server uptime\n"
                "# TYPE mcp_uptime_seconds gauge\n"
                f"mcp_uptime_seconds {time.time() - self._start_time:.0f}\n"
                "# HELP mcp_requests_total Total requests served\n"
                "# TYPE mcp_requests_total counter\n"
                f"mcp_requests_total {getattr(self, '_request_count', 0)}\n"
            )
            self._request_count = getattr(self, "_request_count", 0) + 1
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; version=0.0.4")
            self.end_headers()
            self.wfile.write(metrics.encode())

        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        logger.debug(format, *args)


def run_health_server(port: int = 10721):
    server = HTTPServer(("0.0.0.0", port), MetricsHandler)  # noqa: S104
    MetricsHandler._start_time = time.time()
    MetricsHandler._request_count = 0
    logger.info(f"Health + metrics endpoint on port {port}")
    server.serve_forever()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run_health_server()
