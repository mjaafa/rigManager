from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class MinerTool:
    directory: Path
    executable: str

    @property
    def executable_path(self) -> Path:
        return self.directory / self.executable


@dataclass(slots=True)
class CoinConfig:
    name: str
    tag: str
    miner_tool: MinerTool
    options: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class AppSettings:
    poll_interval_seconds: int = 300
    report_dir: Path = Path("reports")
    what_to_mine_url: str = "https://whattomine.com/coins.json"
    pool_url_template: str = "https://miningpoolstats.stream/{tag}"
    allow_launch: bool = False
    min_profit_delta_percent: float = 5.0


@dataclass(slots=True)
class AppConfig:
    version: str
    settings: AppSettings
    coins: dict[str, CoinConfig]


@dataclass(slots=True)
class ProfitabilityResult:
    coin_name: str
    tag: str
    profitability: float
    profitability24: float
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class PoolResult:
    server: str | None = None
    port: str | None = None
    source_url: str | None = None
    name: str | None = None
    hashrate: float = 0.0
    fee_pct: float = 0.0
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class Decision:
    coin: CoinConfig
    profitability: ProfitabilityResult | None
    pool: PoolResult | None
    command: list[str]
    command_text: str
