from typing import List, Optional, Union
from pydantic import BaseModel, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

# --- API Configuration ---
class AppSettings(BaseSettings):
    """Main application settings loaded from .env"""

    # API Configuration
    api_keys: Optional[List[str]] = []# List of valid keys

    # Default values for llama-server
    default_host: str = "0.0.0.0"
    default_port: int = 8080
    default_model: str = "/models/mistralai_Mistral-Small-3.2-24B-Instruct-2506-Q4_K_M.gguf"
    default_cache_type_k: str = "f16"
    default_cache_type_v: str = "f16"
    default_n_cpu_moe: int = 0
    default_ngl: Union[int, str] = "all"
    default_no_mmap: bool = False
    default_mlock: bool = False
    default_jinja: bool = False
    default_ctx_size: int = 4096
    default_np: int = -1  # -1 = auto

    model_config = SettingsConfigDict(env_file="/app/api/.env")

    @field_validator("default_model")
    def model_must_exist(cls, v: str):
        model_path = Path(v)
        if not model_path.is_file():
            raise ValueError(f"Model file does not exist: {v}")
        return v

class LlamaArgs(BaseModel):
    # This field will be supplied when the model is created.
    app_default: Optional[AppSettings] = Field(
        default_factory=lambda: AppSettings()
    )

    # All the other values are stored as normal fields.
    port: Optional[int] = None
    host: Optional[str] = None
    m: Optional[str] = None
    cache_type_k: Optional[str] = None
    cache_type_v: Optional[str] = None
    n_cpu_moe: Optional[int] = None
    ngl: Optional[Union[int, str]] = None
    no_mmap: Optional[bool] = None
    mlock: Optional[bool] = None
    jinja: Optional[bool] = None
    ctx_size: Optional[int] = None
    np: Optional[int] = None

    def __init__(self, **data):
        # Let Pydantic run its normal validation first.
        super().__init__(**data)

        # Set defaults if no value for a parameter sent.
        if self.port is None:
            self.port = self.app_default.default_port
        if self.host is None:
            self.app_default.default_host
        if self.m         is None:
            self.app_default.default_model
        if self.cache_type_k is None:
            self.app_default.default_cache_type_k
        if self.cache_type_k is None:
            self.app_default.default_cache_type_v
        if self.n_cpu_moe is None:
            self.app_default.default_n_cpu_moe
        if self.ngl       is None:
            self.app_default.default_ngl
        if self.no_mmap   is None:
            self.app_default.default_no_mmap
        if self.mlock     is None:
            self.app_default.default_mlock
        if self.jinja     is None:
            self.app_default.default_jinja
        if self.ctx_size  is None:
            self.app_default.default_ctx_size
        if self.np        is None:
            self.app_default.default_np

    def to_command_list(self) -> List[str]:
        """Converts the Pydantic model into a list of command line arguments."""
        cmd: List[str] = []

        defaults = self.app_default or AppSettings()

        # Boolean flags ---------------------------------------------------------
        if getattr(self, "no_mmap", defaults.default_no_mmap):
            cmd.append("--no-mmap")
        else:
            cmd.append("--mmap")

        if getattr(self, "mlock", defaults.default_mlock):
            cmd.append("--mlock")
        if getattr(self, "jinja", defaults.default_jinja):
            cmd.append("--jinja")
        else:
            cmd.append("--no-jinja")

        # String / optional arguments -----------------------------------------
        if self.host:
            cmd.extend(["--host", str(self.host)])

        if self.port is not None and self.port > 0:
            cmd.extend(["--port", str(self.port)])

        if self.cache_type_k:
            cmd.extend(["--cache-type-k", str(self.cache_type_k)])
        if self.cache_type_v:
            cmd.extend(["--cache-type-v", str(self.cache_type_v)])

        # n_cpu_moe (only if > 0)
        if self.n_cpu_moe is not None and self.n_cpu_moe > 0:
            cmd.extend(["--n-cpu-moe", str(self.n_cpu_moe)])

        # ngl (GPU count) ------------------------------------------------------
        if isinstance(self.ngl, str):
            if self.ngl == "all":
                cmd.extend(["-ngl", "all"])
            elif self.ngl == "auto":
                # “auto” means no -ngl flag at all
                pass
            else:
                # unknown string – keep it as‑is (the server will ignore it)
                cmd.extend(["-ngl", str(self.ngl)])
        elif isinstance(self.ngl, int) and self.ngl > 0:
            cmd.extend(["-ngl", str(self.ngl)])

        # ctx_size -------------------------------------------------------------
        if self.ctx_size is not None and self.ctx_size > 0:
            cmd.extend(["--ctx-size", str(self.ctx_size)])

        # model path (-m) -------------------------------------------------------
        if self.m:
            cmd.extend(["-m", self.m])

        # number of reserved server slots (-np) -------------------------------
        if self.np is not None and self.np > 0:
            cmd.extend(["-np", str(self.np)])

        return cmd

