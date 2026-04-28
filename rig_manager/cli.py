from __future__ import annotations

import argparse
import logging
import sys
import time
from pathlib import Path

from . import __version__
from .config import ConfigError, load_config
from .core import make_decision, write_reports
from .process_manager import ProcessManager

LOG = logging.getLogger(__name__)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Cryptocurrency mining rig manager and profitability launcher.")
    parser.add_argument("--config", default="configRigManager.json", help="Path to rigManager JSON configuration.")
    parser.add_argument("--coin", help="Force a configured coin instead of selecting by profitability.")
    parser.add_argument("--once", action="store_true", help="Run one decision cycle and exit.")
    parser.add_argument("--dry-run", action="store_true", help="Show the selected command without launching a miner.")
    parser.add_argument("--offline", action="store_true", help="Do not call external APIs; use the first configured coin or --coin.")
    parser.add_argument("--launch", action="store_true", help="Actually launch the selected miner command. Disabled by default.")
    parser.add_argument("--report", action="store_true", help="Write JSON, Markdown, and CSV reports.")
    parser.add_argument("--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"], help="Logging level.")
    parser.add_argument("--version", action="version", version=f"rigManager {__version__}")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    logging.basicConfig(level=getattr(logging, args.log_level), format="%(asctime)s %(levelname)s %(message)s")

    try:
        config = load_config(args.config)
    except (ConfigError, OSError, ValueError) as exc:
        LOG.error("Configuration error: %s", exc)
        return 2

    manager = ProcessManager()
    current_coin: str | None = None

    while True:
        # Warn if a previously launched miner died between cycles
        if manager.current is not None and not manager.is_alive():
            LOG.warning("Miner process (PID %s) died unexpectedly; it will restart this cycle", manager.current.process.pid)

        try:
            decision, warnings = make_decision(
                args.config,
                offline=args.offline,
                coin_name=args.coin,
                current_coin_name=current_coin,
            )
        except Exception as exc:
            LOG.exception("Decision cycle failed: %s", exc)
            if args.once or args.dry_run:
                return 1
            time.sleep(config.settings.poll_interval_seconds)
            continue

        for warning in warnings:
            LOG.warning("%s", warning)

        LOG.info("Selected coin: %s", decision.coin.name)
        if decision.profitability is not None:
            LOG.info("Profitability 24h: %s", decision.profitability.profitability24)
        if decision.pool is not None:
            LOG.info("Pool: %s:%s", decision.pool.server or "unknown", decision.pool.port or "unknown")
        LOG.info("Command: %s", decision.command_text)

        current_coin = decision.coin.name

        if args.report:
            write_reports(config.settings.report_dir, decision)
            LOG.info("Reports written to: %s", Path(config.settings.report_dir))

        can_launch = args.launch and config.settings.allow_launch and not args.dry_run
        if can_launch:
            manager.start(decision.command)
        elif args.launch and not config.settings.allow_launch:
            LOG.warning("Launch requested, but settings.allow_launch is false in the config. Not launching.")

        if args.once or args.dry_run:
            return 0
        time.sleep(config.settings.poll_interval_seconds)


if __name__ == "__main__":
    raise SystemExit(main())
