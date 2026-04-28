from __future__ import annotations

import shlex
from typing import Any

from .models import CoinConfig, PoolResult

RESERVED = "reserved"


def _reserved_value(option_name: str, pool: PoolResult | None) -> str:
    server = pool.server if pool else None
    port = pool.port if pool else None
    if option_name in {"-epool", "-l", "-o"}:
        if server and port:
            return f"stratum+tcp://{server}:{port}"
    if option_name in {"--server"}:
        return server or ""
    if option_name in {"-mport", "--port"}:
        return port or ""
    return ""


def build_command(coin: CoinConfig, pool: PoolResult | None = None) -> list[str]:
    command = [str(coin.miner_tool.executable_path)]
    for key, value in coin.options.items():
        if isinstance(value, str) and value.lower() == RESERVED:
            resolved = _reserved_value(str(key), pool)
            if resolved:
                command.append(str(key))
                command.append(resolved)
            continue
        command.append(str(key))
        if value is None or value is False:
            continue
        command.append(str(value))
    return command


def command_to_text(command: list[str]) -> str:
    return " ".join(shlex.quote(part) for part in command)
