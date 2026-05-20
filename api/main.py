import os
import time
import signal
import asyncio
import psutil
from fastapi import FastAPI, HTTPException, Header
from fastapi.responses import JSONResponse
from typing import Optional
import uvicorn
from config import AppSettings, LlamaArgs
from manager import LlamaProcessManager
from auth import verify_api_key

# Logging configuration
import logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger("llama-manager")

# Initialize settings and manager
app_settings = AppSettings()
manager = LlamaProcessManager(app_settings)

app = FastAPI(title="Llama Server Manager")

# ----------------------------------------------------------------------
# Signal handling for graceful shutdown
# ----------------------------------------------------------------------
def _handle_sigterm(signum, frame):
    asyncio.create_task(app.shutdown())

signal.signal(signal.SIGTERM, _handle_sigterm)
signal.signal(signal.SIGINT, _handle_sigterm)

# ----------------------------------------------------------------------
# Lifespan handlers
# ----------------------------------------------------------------------
@app.on_event("startup")
async def startup_event():
    """Start the llama‑server when the FastAPI app starts."""
    default_args = LlamaArgs(
        m=app_settings.default_model,
        host=app_settings.default_host,
        port=app_settings.default_port,
        cache_type_k=app_settings.default_cache_type_k,
        cache_type_v=app_settings.default_cache_type_v,
        n_cpu_moe=app_settings.default_n_cpu_moe,
        ngl=app_settings.default_ngl,
        n_gpu_layers=app_settings.default_n_gpu_layers,
        no_mmap=app_settings.default_no_mmap,
        mlock=app_settings.default_mlock,
        jinja=app_settings.default_jinja,
        ctx_size=app_settings.default_ctx_size,
        np=app_settings.default_np,
    )
    success = manager.start_server(default_args)
    if success:
        logger.info("Llama server started successfully.")
    else:
        logger.error("Failed to start llama server.")

@app.on_event("shutdown")
async def shutdown_event():
    """Stop the llama‑server when the container shuts down."""
    logger.info("Shutting down – stopping llama server.")
    manager.stop_server()

# ----------------------------------------------------------------------
# API endpoints
# ----------------------------------------------------------------------
@app.get("/health")
def health_check():
    """Return health information for both the API and the llama‑server."""
    health = manager.check_health()
    return {"status": health["status"], "message": health["message"]}

@app.get("/metrics")
def metrics():
    """Simple process metrics endpoint."""
    proc = psutil.Process(os.getpid())
    return {
        "pid": proc.pid,
        "status": "running",
        "uptime_seconds": int(time.time() - getattr(proc, "create_time", time.time() - 0)),
    }

@app.get("/restart-status")
def restart_status(x_api_key: Optional[str] = Header(None)):
    verify_api_key(app_settings, x_api_key)
    health = manager.check_health()
    return health

@app.post("/restart-llama")
def restart_llama(new_args: LlamaArgs, x_api_key: Optional[str] = Header(None)):
    verify_api_key(app_settings, x_api_key)
    manager.stop_server()
    import time
    time.sleep(1)                     # give previous process time to clean up
    logger.info("New restart arguments received: %s", new_args)
    success = manager.start_server(new_args)
    if success:
        return {"status": "restarting", "message": "Process restarting with new parameters."}
    else:
        raise HTTPException(status_code=500, detail="Failed to start server.")
