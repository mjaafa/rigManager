from __future__ import annotations

import logging
from pathlib import Path

from .command_builder import build_command, command_to_text
from .config import load_config, validate_config
from .models import Decision
from .pools import PoolClient
from .profitability import ProfitabilityClient, choose_best_coin
from .reports import append_csv, write_json, write_markdown

LOG = logging.getLogger(__name__)


def make_decision(
    config_path: str | Path,
    offline: bool = False,
    coin_name: str | None = None,
    current_coin_name: str | None = None,
) -> tuple[Decision, list[str]]:
    config = load_config(config_path)
    warnings = validate_config(config)

    if coin_name:
        if coin_name not in config.coins:
            available = ", ".join(sorted(config.coins))
            raise ValueError(f"Unknown coin '{coin_name}'. Available coins: {available}")
        coin = config.coins[coin_name]
        decision = Decision(coin=coin, profitability=None, pool=None, command=[], command_text="")
        decision.command = build_command(coin, None)
        decision.command_text = command_to_text(decision.command)
        return decision, warnings

    if offline:
        first_coin = next(iter(config.coins.values()))
        decision = Decision(coin=first_coin, profitability=None, pool=None, command=[], command_text="")
        decision.command = build_command(first_coin, None)
        decision.command_text = command_to_text(decision.command)
        return decision, warnings

    profitability_data = ProfitabilityClient(config.settings.what_to_mine_url).fetch()
    best = choose_best_coin(
        config,
        profitability_data,
        current_coin_name=current_coin_name,
        min_delta_pct=config.settings.min_profit_delta_percent,
    )
    coin = config.coins[best.coin_name]

    pool = None
    try:
        pool = PoolClient(config.settings.pool_url_template).lookup(best.tag)
    except Exception as exc:  # network/source errors should not kill dry/reporting workflows
        warnings.append(f"Pool lookup failed for {best.coin_name}: {exc}")
        LOG.warning("Pool lookup failed", exc_info=True)

    command = build_command(coin, pool)
    decision = Decision(coin=coin, profitability=best, pool=pool, command=command, command_text=command_to_text(command))
    return decision, warnings


def write_reports(report_dir: str | Path, decision: Decision) -> None:
    report_path = Path(report_dir)
    write_json(report_path / "latest.json", decision)
    write_markdown(report_path / "latest.md", decision)
    append_csv(report_path / "history.csv", decision)
