from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any

from .models import AppConfig, AppSettings, CoinConfig, MinerTool

_ENV_PATTERN = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}")


class ConfigError(ValueError):
    """Raised when the rigManager configuration is invalid."""


def _expand_env(value: Any) -> Any:
    if isinstance(value, str):
        def replace(match: re.Match[str]) -> str:
            return os.getenv(match.group(1), "")

        return _ENV_PATTERN.sub(replace, value)
    if isinstance(value, list):
        return [_expand_env(item) for item in value]
    if isinstance(value, dict):
        return {key: _expand_env(item) for key, item in value.items()}
    return value


def _as_path(base_dir: Path, raw_path: str | Path) -> Path:
    path = Path(raw_path)
    if path.is_absolute():
        return path
    return (base_dir / path).resolve()


def _load_new_schema(data: dict[str, Any], base_dir: Path) -> AppConfig:
    settings_raw = data.get("settings", {})
    settings = AppSettings(
        poll_interval_seconds=int(settings_raw.get("poll_interval_seconds", 300)),
        report_dir=_as_path(base_dir, settings_raw.get("report_dir", "reports")),
        what_to_mine_url=str(settings_raw.get("what_to_mine_url", "https://whattomine.com/coins.json")),
        pool_url_template=str(settings_raw.get("pool_url_template", "https://investoon.com/mining_pools/{tag}")),
        allow_launch=bool(settings_raw.get("allow_launch", False)),
        min_profit_delta_percent=float(settings_raw.get("min_profit_delta_percent", 5.0)),
    )

    coins: dict[str, CoinConfig] = {}
    coins_raw = data.get("coins")
    if not isinstance(coins_raw, dict) or not coins_raw:
        raise ConfigError("Configuration must contain a non-empty 'coins' object.")

    for name, item in coins_raw.items():
        if not isinstance(item, dict):
            raise ConfigError(f"Coin '{name}' must be an object.")
        tool_raw = item.get("miner_tool", {})
        options = item.get("options", {})
        if not isinstance(options, dict):
            raise ConfigError(f"Coin '{name}' options must be an object.")
        directory = tool_raw.get("directory")
        executable = tool_raw.get("executable")
        tag = item.get("tag")
        if not directory or not executable or not tag:
            raise ConfigError(f"Coin '{name}' must define tag, miner_tool.directory, and miner_tool.executable.")
        coins[name] = CoinConfig(
            name=name,
            tag=str(tag).lower(),
            miner_tool=MinerTool(directory=_as_path(base_dir, str(directory)), executable=str(executable)),
            options=options,
        )

    return AppConfig(version=str(data.get("version", "2.0")), settings=settings, coins=coins)


def _load_legacy_schema(data: dict[str, Any], base_dir: Path) -> AppConfig:
    coins: dict[str, CoinConfig] = {}
    ignored = {"ConfigFileVersion"}
    for name, items in data.items():
        if name in ignored:
            continue
        if not isinstance(items, list) or not items:
            continue
        item = items[0]
        tool_raw = item.get("MinerTool", [{}])[0]
        options_raw = item.get("options", [{}])[0]
        tag = item.get("Tag", name)
        directory = tool_raw.get("directory")
        executable = tool_raw.get("executable")
        if not directory or not executable:
            continue
        coins[name] = CoinConfig(
            name=name,
            tag=str(tag).lower(),
            miner_tool=MinerTool(directory=_as_path(base_dir, str(directory)), executable=str(executable)),
            options=dict(options_raw),
        )

    if not coins:
        raise ConfigError("No usable coins found in legacy configuration.")
    return AppConfig(version="legacy", settings=AppSettings(report_dir=_as_path(base_dir, "reports")), coins=coins)


def load_config(path: str | Path) -> AppConfig:
    config_path = Path(path).expanduser().resolve()
    if not config_path.exists():
        raise ConfigError(f"Configuration file does not exist: {config_path}")

    with config_path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)

    data = _expand_env(data)
    base_dir = config_path.parent
    if "coins" in data:
        return _load_new_schema(data, base_dir)
    return _load_legacy_schema(data, base_dir)


def validate_config(config: AppConfig) -> list[str]:
    warnings: list[str] = []
    if config.settings.poll_interval_seconds < 10:
        warnings.append("poll_interval_seconds is very low; consider 60 seconds or more to avoid API rate limiting.")
    for name, coin in config.coins.items():
        if not coin.options:
            warnings.append(f"{name}: no miner options configured.")
        for key, value in coin.options.items():
            if isinstance(value, str) and value == "":
                warnings.append(f"{name}: option {key!r} is empty, probably because an environment variable is missing.")
        if not coin.miner_tool.executable_path.exists():
            warnings.append(f"{name}: miner executable not found: {coin.miner_tool.executable_path}")
    return warnings
