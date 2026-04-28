# rigManager

rigManager is a Python 3 cryptocurrency mining rig manager. It checks configured coins, selects the most profitable option from WhatToMine, optionally discovers a mining pool, builds the miner command, and can write reports or launch the selected miner.

This evolved version modernizes the original Python 2 Windows script into a smaller source-only project with a safer configuration format, dry-run mode, reporting, and testable modules.

## What changed in this version

- Migrated the codebase from Python 2 syntax to Python 3.
- Replaced PhantomJS/Selenium scraping with `requests` and `BeautifulSoup`.
- Replaced Windows-only process-killing logic with `psutil`.
- Added a real CLI with `--dry-run`, `--once`, `--offline`, `--coin`, `--report`, and `--launch`.
- Added a new JSON config format with environment-variable placeholders for wallets.
- Added support for legacy `configRigManager.json` files.
- Added Markdown, JSON, and CSV reports.
- Added tests and GitHub Actions.
- Removed bundled `.exe`, `.gif`, `.mp4`, and `.zip` files from the source package. Put binaries and demos in GitHub Releases instead.

## Installation

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

With conda:

```powershell
conda create -n rigmanager python=3.11
conda activate rigmanager
python -m pip install -r requirements.txt
```

## Configuration

Copy the example config:

```powershell
copy configRigManager.example.json configRigManager.json
copy .env.example .env
```

Edit `configRigManager.json` to point to your miner executables and edit `.env` or your shell environment to define your wallet addresses.

Example PowerShell environment variables:

```powershell
$env:ETH_WALLET="your_eth_wallet"
$env:ZCASH_WALLET="your_zcash_wallet"
$env:ZEN_WALLET="your_zen_wallet"
```

By default, `settings.allow_launch` is `false`. This prevents accidental miner execution. Set it to `true` only when your config is correct and you intentionally want the tool to launch miner commands.

## Usage

Show help:

```powershell
python main.py --help
```

Dry-run using the first configured coin without external API calls:

```powershell
python main.py --dry-run --offline
```

Force a specific coin:

```powershell
python main.py --dry-run --coin Ethereum
```

Run one online profitability decision and write reports:

```powershell
python main.py --once --report
```

Launch the selected miner:

```powershell
python main.py --launch
```

To launch, both conditions must be true:

1. You pass `--launch` on the command line.
2. `settings.allow_launch` is `true` in `configRigManager.json`.

## Reports

When `--report` is used, the tool writes:

```text
reports/latest.json
reports/latest.md
reports/history.csv
```

## Migrating an old config

The loader can still read the original `configRigManager.json` format. You can also convert it to the new schema:

```powershell
python scripts\migrate_legacy_config.py old-configRigManager.json configRigManager.json
```

Review the migrated file before launching anything.

## Development

Install development dependencies:

```powershell
python -m pip install -r requirements-dev.txt
```

Run tests:

```powershell
python -m pytest
```

Run linting:

```powershell
python -m ruff check .
```

## GitHub topics

```text
python mining cryptocurrency rig-manager mining-rig windows automation profitability miner-monitoring gpu-mining
```

## Safety note

This project can launch external miner executables. Use `--dry-run` first, verify the generated command, and only run miners you trust from known sources.
