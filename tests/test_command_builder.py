from pathlib import Path

from rig_manager.command_builder import build_command, command_to_text
from rig_manager.models import CoinConfig, MinerTool, PoolResult


def test_build_command_replaces_reserved_pool_values() -> None:
    coin = CoinConfig(
        name="Ethereum",
        tag="eth",
        miner_tool=MinerTool(directory=Path("miners/Claymore"), executable="EthDcrMiner64.exe"),
        options={"-epool": "reserved", "-ewal": "wallet", "-mport": "reserved"},
    )
    pool = PoolResult(server="example.pool", port="4444")

    command = build_command(coin, pool)

    assert "stratum+tcp://example.pool:4444" in command
    assert "4444" in command
    assert "wallet" in command


def test_command_to_text_quotes_paths_with_spaces() -> None:
    text = command_to_text(["C:/Program Files/miner/miner.exe", "--user", "wallet address"])

    assert "'C:/Program Files/miner/miner.exe'" in text
    assert "'wallet address'" in text
