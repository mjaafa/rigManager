from __future__ import annotations

import argparse
import json
from pathlib import Path


def migrate(input_path: Path, output_path: Path) -> None:
    data = json.loads(input_path.read_text(encoding="utf-8"))
    migrated = {
        "version": "2.0",
        "settings": {
            "poll_interval_seconds": 300,
            "report_dir": "reports",
            "what_to_mine_url": "https://whattomine.com/coins.json",
            "pool_url_template": "https://investoon.com/mining_pools/{tag}",
            "allow_launch": False,
        },
        "coins": {},
    }
    for name, items in data.items():
        if name == "ConfigFileVersion" or not isinstance(items, list) or not items:
            continue
        item = items[0]
        tool = item.get("MinerTool", [{}])[0]
        options = item.get("options", [{}])[0]
        if not tool.get("directory") or not tool.get("executable"):
            continue
        migrated["coins"][name] = {
            "tag": str(item.get("Tag", name)).lower(),
            "miner_tool": {
                "directory": f"miners/{tool['directory']}",
                "executable": tool["executable"],
            },
            "options": options,
        }
    output_path.write_text(json.dumps(migrated, indent=2), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Convert legacy rigManager JSON config to the v2 schema.")
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    migrate(args.input, args.output)
    print(f"Wrote migrated config to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
