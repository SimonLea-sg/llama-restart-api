from typing import List
from pydantic import BaseModel, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

# --- API Configuration ---
class AppSettings(BaseSettings):
    """Main application settings loaded from .env"""
    # Default values for llama-server
    default_host: str = "0.0.0.0"
    default_port: int = 8080
    default_model: str = "/models/mistralai_Mistral-Small-3.2-24B-Instruct-2506-Q4_K_M.gguf"
    default_cache_type_k: str = "f16"
    default_cache_type_v: str = "f16"
    default_n_cpu_moe: int = 0
    default_ngl: int = 99
    default_n_gpu_layers: int = 99
    default_no_mmap: bool = False
    default_mlock: bool = False
    default_jinja: bool = False
    default_ctx_size: int = 4096
    default_np: int = -1  # -1 = auto

    # API Configuration
    api_keys: List[str] = []  # List of valid keys

    model_config = SettingsConfigDict(env_file="/app/api/.env", env_nested_delimiter="_")

    @field_validator("default_model")
    def model_must_exist(cls, v: str):
        model_path = Path(v)
        if not model_path.is_file():
            raise ValueError(f"Model file does not exist: {v}")
        return v

# --- Llama Server Configuration ---
class LlamaArgs(BaseModel):
    # Grab default settings.
    app_default = AppSettings()
    port = app_default.default_port
    host = app_default.default_host
    m = app_default.default_model
    cache_type_k = app_default.default_cache_type_k
    cache_type_v = app_default.default_cache_type_v
    n_cpu_moe = app_default.default_n_cpu_moe
    ngl = app_default.default_ngl
    n_gpu_layers = app_default.default_n_gpu_layers
    no_mmap = app_default.default_no_mmap
    mlock = app_default.default_mlock
    jinja = app_default.default_jinja
    ctx_size = app_default.default_ctx_size
    np = app_default.default_np

    def to_command_list(self) -> List[str]:
        """Converts the Pydantic model into a list of command line arguments."""
        cmd = []
        # Boolean flags: add flag if True
        if self.no_mmap:
            cmd.append("--no-mmap")
        else:
            cmd.append("--mmap")
        if self.mlock:
            cmd.append("--mlock")
        if self.jinja:
            cmd.append("--jinja")
        else:
            cmd.append("--no-jinja")
        # String/Int flags
        if self.host:
            cmd.extend(["--host", self.host])
        if self.port > 0:
            cmd.extend(["--port", str(self.port)])

        if self.cache_type_k:
            cmd.extend(["--cache-type-k", self.cache_type_k])
        if self.cache_type_v:
            cmd.extend(["--cache-type-v", self.cache_type_v])

        if self.n_cpu_moe > 0:
            cmd.extend(["--n-cpu-moe", str(self.n_cpu_moe)])
        if self.ngl > 0:
            cmd.extend(["-ngl", str(self.ngl)])

        if self.n_gpu_layers > 0:
            cmd.extend(["--n-gpu-layers", str(self.n_gpu_layers)])

        if self.ctx_size > 0:
            cmd.extend(["--ctx-size", str(self.ctx_size)])

        # Model path (-m)
        if self.m:
            cmd.extend(["-m", self.m])

        # number of reserved server slots (-np)
        if self.np:
            cmd.extend(["-np", str(self.np)])

        return cmd
