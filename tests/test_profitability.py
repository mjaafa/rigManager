from pathlib import Path

from rig_manager.models import AppConfig, AppSettings, CoinConfig, MinerTool
from rig_manager.profitability import choose_best_coin


def test_choose_best_coin_uses_configured_coins_only() -> None:
    config = AppConfig(
        version="2.0",
        settings=AppSettings(),
        coins={
            "Ethereum": CoinConfig("Ethereum", "eth", MinerTool(Path("miners"), "miner.exe")),
            "Zcash": CoinConfig("Zcash", "zec", MinerTool(Path("miners"), "miner.exe")),
        },
    )
    data = {
        "coins": {
            "Ethereum": {"tag": "ETH", "profitability": 1.0, "profitability24": 2.0},
            "Zcash": {"tag": "ZEC", "profitability": 5.0, "profitability24": 4.0},
            "OtherCoin": {"tag": "OTHER", "profitability": 100.0, "profitability24": 100.0},
        }
    }

    best = choose_best_coin(config, data)

    assert best.coin_name == "Zcash"
    assert best.tag == "zec"


def _make_config() -> AppConfig:
    return AppConfig(
        version="2.0",
        settings=AppSettings(),
        coins={
            "Ethereum": CoinConfig("Ethereum", "eth", MinerTool(Path("miners"), "miner.exe")),
            "Zcash": CoinConfig("Zcash", "zec", MinerTool(Path("miners"), "miner.exe")),
        },
    )


def test_hysteresis_keeps_current_coin_below_threshold() -> None:
    config = _make_config()
    data = {
        "coins": {
            "Ethereum": {"tag": "ETH", "profitability": 1.0, "profitability24": 100.0},
            "Zcash": {"tag": "ZEC", "profitability": 1.0, "profitability24": 103.0},  # only 3% better
        }
    }
    best = choose_best_coin(config, data, current_coin_name="Ethereum", min_delta_pct=5.0)
    assert best.coin_name == "Ethereum"


def test_hysteresis_switches_when_above_threshold() -> None:
    config = _make_config()
    data = {
        "coins": {
            "Ethereum": {"tag": "ETH", "profitability": 1.0, "profitability24": 100.0},
            "Zcash": {"tag": "ZEC", "profitability": 1.0, "profitability24": 110.0},  # 10% better
        }
    }
    best = choose_best_coin(config, data, current_coin_name="Ethereum", min_delta_pct=5.0)
    assert best.coin_name == "Zcash"


def test_hysteresis_ignored_when_no_current_coin() -> None:
    config = _make_config()
    data = {
        "coins": {
            "Ethereum": {"tag": "ETH", "profitability": 1.0, "profitability24": 100.0},
            "Zcash": {"tag": "ZEC", "profitability": 1.0, "profitability24": 101.0},
        }
    }
    best = choose_best_coin(config, data, current_coin_name=None, min_delta_pct=5.0)
    assert best.coin_name == "Zcash"
