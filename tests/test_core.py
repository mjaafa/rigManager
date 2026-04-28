from __future__ import annotations

import json
from pathlib import Path

import pytest

from rig_manager.core import make_decision


@pytest.fixture()
def config_path(tmp_path: Path) -> Path:
    cfg = tmp_path / "config.json"
    cfg.write_text(
        json.dumps(
            {
                "version": "2.0",
                "settings": {"poll_interval_seconds": 300, "allow_launch": False},
                "coins": {
                    "Ethereum": {
                        "tag": "eth",
                        "miner_tool": {"directory": str(tmp_path / "miners"), "executable": "miner.exe"},
                        "options": {"-ewal": "0xabc"},
                    },
                    "Zcash": {
                        "tag": "zec",
                        "miner_tool": {"directory": str(tmp_path / "miners"), "executable": "miner2.exe"},
                        "options": {"-u": "t1abc"},
                    },
                },
            }
        ),
        encoding="utf-8",
    )
    return cfg


def test_make_decision_offline_returns_first_coin(config_path: Path) -> None:
    decision, warnings = make_decision(config_path, offline=True)
    assert decision.coin.name in ("Ethereum", "Zcash")
    assert decision.command_text != ""


def test_make_decision_forced_coin(config_path: Path) -> None:
    decision, _ = make_decision(config_path, coin_name="Zcash")
    assert decision.coin.name == "Zcash"
    assert decision.profitability is None
    assert decision.pool is None


def test_make_decision_unknown_coin_raises(config_path: Path) -> None:
    with pytest.raises(ValueError, match="Unknown coin"):
        make_decision(config_path, coin_name="Dogecoin")


def test_make_decision_offline_command_includes_executable(config_path: Path) -> None:
    decision, _ = make_decision(config_path, offline=True)
    assert len(decision.command) >= 1
    assert decision.command[0].endswith(".exe")
