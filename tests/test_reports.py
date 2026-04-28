from __future__ import annotations

import csv
import json
from pathlib import Path

import pytest

from rig_manager.models import CoinConfig, Decision, MinerTool
from rig_manager.reports import append_csv, write_json, write_markdown


@pytest.fixture()
def decision() -> Decision:
    coin = CoinConfig("Ethereum", "eth", MinerTool(Path("miners/Claymore"), "EthDcrMiner64.exe"))
    return Decision(
        coin=coin,
        profitability=None,
        pool=None,
        command=["miners/Claymore/EthDcrMiner64.exe", "-ewal", "0xabc"],
        command_text="'miners/Claymore/EthDcrMiner64.exe' -ewal 0xabc",
    )


def test_write_json_creates_file(tmp_path: Path, decision: Decision) -> None:
    out = tmp_path / "latest.json"
    write_json(out, decision)
    assert out.exists()
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["coin"] == "Ethereum"
    assert data["tag"] == "eth"
    assert "timestamp" in data


def test_write_json_creates_missing_parent(tmp_path: Path, decision: Decision) -> None:
    out = tmp_path / "sub" / "dir" / "report.json"
    write_json(out, decision)
    assert out.exists()


def test_write_markdown_creates_file(tmp_path: Path, decision: Decision) -> None:
    out = tmp_path / "latest.md"
    write_markdown(out, decision)
    content = out.read_text(encoding="utf-8")
    assert "Ethereum" in content
    assert "# rigManager Report" in content


def test_append_csv_creates_file_with_header(tmp_path: Path, decision: Decision) -> None:
    out = tmp_path / "history.csv"
    append_csv(out, decision)
    assert out.exists()
    rows = list(csv.DictReader(out.open(encoding="utf-8")))
    assert len(rows) == 1
    assert rows[0]["coin"] == "Ethereum"


def test_append_csv_accumulates_rows(tmp_path: Path, decision: Decision) -> None:
    out = tmp_path / "history.csv"
    append_csv(out, decision)
    append_csv(out, decision)
    rows = list(csv.DictReader(out.open(encoding="utf-8")))
    assert len(rows) == 2
