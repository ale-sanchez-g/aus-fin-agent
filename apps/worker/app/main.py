"""Worker service - runs periodic sync tasks."""
import asyncio
import signal
import structlog
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread
from app.core.config import settings
from app.core.logging import configure_logging
from app.tasks.sync_providers import sync_all_providers
from app.tasks.sync_products import sync_all_products
from app.tasks.cleanup import cleanup_old_records

configure_logging()
log = structlog.get_logger()
_shutdown = asyncio.Event()


class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/health":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"status":"ok","service":"worker"}')
        else:
            self.send_response(404)
            self.end_headers()
    def log_message(self, *args): pass


def start_health_server():
    server = HTTPServer(("0.0.0.0", 8001), HealthHandler)
    Thread(target=server.serve_forever, daemon=True).start()
    log.info("health_server_started", port=8001)


async def run_sync_cycle():
    log.info("sync_cycle_start")
    provider_result = await sync_all_providers()
    product_result = await sync_all_products()
    log.info("sync_cycle_complete", providers=provider_result, products=product_result)


async def main():
    start_health_server()

    def handle_signal(*args):
        log.info("shutdown_signal_received")
        _shutdown.set()

    signal.signal(signal.SIGTERM, handle_signal)
    signal.signal(signal.SIGINT, handle_signal)

    log.info("worker_start", sync_interval_hours=settings.SYNC_INTERVAL_HOURS)
    await run_sync_cycle()

    cycle = 0
    while not _shutdown.is_set():
        try:
            await asyncio.wait_for(
                asyncio.shield(asyncio.sleep(settings.SYNC_INTERVAL_HOURS * 3600)),
                timeout=settings.SYNC_INTERVAL_HOURS * 3600,
            )
        except (asyncio.TimeoutError, asyncio.CancelledError):
            pass

        if _shutdown.is_set():
            break

        await run_sync_cycle()
        cycle += 1
        if cycle % 4 == 0:
            await cleanup_old_records()

    log.info("worker_shutdown")


if __name__ == "__main__":
    asyncio.run(main())
