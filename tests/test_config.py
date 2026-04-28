import json
from pathlib import Path

from rig_manager.config import load_config


def test_load_new_schema(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("ETH_WALLET", "0xabc")
    config_path = tmp_path / "config.json"
    config_path.write_text(
        json.dumps(
            {
                "version": "2.0",
                "coins": {
                    "Ethereum": {
                        "tag": "eth",
                        "miner_tool": {"directory": "miners/Claymore", "executable": "miner.exe"},
                        "options": {"-ewal": "${ETH_WALLET}"},
                    }
                },
            }
        ),
        encoding="utf-8",
    )

    config = load_config(config_path)

    assert config.coins["Ethereum"].options["-ewal"] == "0xabc"
    assert config.coins["Ethereum"].miner_tool.executable_path.name == "miner.exe"


def test_load_legacy_schema(tmp_path: Path) -> None:
    config_path = tmp_path / "legacy.json"
    config_path.write_text(
        json.dumps(
            {
                "ConfigFileVersion": {"Major": 1},
                "Zcash": [
                    {
                        "Tag": "ZEC",
                        "MinerTool": [{"directory": "nheqminer", "executable": "nheqminer.exe"}],
                        "options": [{"-l": "reserved"}],
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    config = load_config(config_path)

    assert "Zcash" in config.coins
    assert config.coins["Zcash"].tag == "zec"
