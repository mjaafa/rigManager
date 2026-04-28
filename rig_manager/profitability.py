from __future__ import annotations

import logging
from typing import Any

import requests

from .models import AppConfig, ProfitabilityResult

LOG = logging.getLogger(__name__)


class ProfitabilityClient:
    def __init__(self, url: str, timeout: int = 20) -> None:
        self.url = url
        self.timeout = timeout

    def fetch(self) -> dict[str, Any]:
        response = requests.get(self.url, timeout=self.timeout, headers={"User-Agent": "rigManager/2.0"})
        response.raise_for_status()
        data = response.json()
        if "coins" not in data or not isinstance(data["coins"], dict):
            raise ValueError("Unexpected WhatToMine response: missing 'coins' object")
        return data


def _to_float(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def choose_best_coin(
    config: AppConfig,
    data: dict[str, Any],
    current_coin_name: str | None = None,
    min_delta_pct: float = 0.0,
) -> ProfitabilityResult:
    configured = set(config.coins.keys())
    coins = data.get("coins", {})
    best: ProfitabilityResult | None = None
    current: ProfitabilityResult | None = None

    for coin_name in configured:
        raw = coins.get(coin_name)
        if not isinstance(raw, dict):
            LOG.debug("Skipping %s because it was not found in profitability data", coin_name)
            continue
        result = ProfitabilityResult(
            coin_name=coin_name,
            tag=str(raw.get("tag", config.coins[coin_name].tag)).lower(),
            profitability=_to_float(raw.get("profitability")),
            profitability24=_to_float(raw.get("profitability24")),
            raw=raw,
        )
        if coin_name == current_coin_name:
            current = result
        if best is None or result.profitability24 > best.profitability24:
            best = result

    if best is None:
        raise ValueError("None of the configured coins were present in the profitability data.")

    # Hysteresis: only switch if improvement exceeds min_delta_pct
    if current is not None and best.coin_name != current.coin_name and min_delta_pct > 0.0:
        improvement = (best.profitability24 - current.profitability24) / max(abs(current.profitability24), 1e-9) * 100
        if improvement < min_delta_pct:
            LOG.info(
                "Keeping %s — improvement to %s is %.1f%% which is below the %.1f%% threshold",
                current.coin_name,
                best.coin_name,
                improvement,
                min_delta_pct,
            )
            return current

    return best
