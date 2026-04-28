from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .models import Decision


def decision_to_dict(decision: Decision) -> dict[str, Any]:
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "coin": decision.coin.name,
        "tag": decision.coin.tag,
        "profitability": None if decision.profitability is None else decision.profitability.profitability,
        "profitability24": None if decision.profitability is None else decision.profitability.profitability24,
        "pool_server": None if decision.pool is None else decision.pool.server,
        "pool_port": None if decision.pool is None else decision.pool.port,
        "pool_source_url": None if decision.pool is None else decision.pool.source_url,
        "command": decision.command,
        "command_text": decision.command_text,
    }


def write_json(path: Path, decision: Decision) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(decision_to_dict(decision), handle, indent=2)


def append_csv(path: Path, decision: Decision) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    row = decision_to_dict(decision)
    exists = path.exists()
    with path.open("a", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(row.keys()))
        if not exists:
            writer.writeheader()
        writer.writerow(row)


def write_markdown(path: Path, decision: Decision) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = decision_to_dict(decision)
    lines = [
        "# rigManager Report",
        "",
        f"- Timestamp: `{data['timestamp']}`",
        f"- Selected coin: **{data['coin']}**",
        f"- 24h profitability: `{data['profitability24']}`",
        f"- Pool server: `{data['pool_server'] or 'unknown'}`",
        f"- Pool port: `{data['pool_port'] or 'unknown'}`",
        "",
        "## Command",
        "",
        "```powershell",
        data["command_text"],
        "```",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")
