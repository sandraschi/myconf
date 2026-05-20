import { NextResponse } from "next/server";

const startTime = Date.now();
let requestCount = 0;

export async function GET() {
  requestCount++;

  const metrics = [
    "# HELP web_uptime_milliseconds Web dashboard uptime",
    "# TYPE web_uptime_milliseconds gauge",
    `web_uptime_milliseconds ${Date.now() - startTime}`,
    "",
    "# HELP web_requests_total Total API requests served",
    "# TYPE web_requests_total counter",
    `web_requests_total ${requestCount}`,
    "",
    "# HELP web_node_env Node environment",
    "# TYPE web_node_env gauge",
    `web_node_env{env="${process.env.NODE_ENV ?? "development"}"} 1`,
    "",
  ].join("\n");

  return new NextResponse(metrics, {
    headers: { "Content-Type": "text/plain; version=0.0.4" },
  });
}
