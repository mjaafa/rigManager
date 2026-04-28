from __future__ import annotations

import logging
import re
import time
import urllib.request
from dataclasses import dataclass
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

from .models import PoolResult

LOG = logging.getLogger(__name__)

_STRATUM_RE = re.compile(r"stratum\+tcp://([A-Za-z0-9.-]+):([0-9]{2,5})")
_HASHRATE_RE = re.compile(r"([\d]+\.?\d*)\s*(P|T|G|M|K)?H/s", re.IGNORECASE)
_FEE_RE = re.compile(r"([\d]+\.?\d*)\s*%")
_HR_MULT = {"p": 1e15, "t": 1e12, "g": 1e9, "m": 1e6, "k": 1e3, "": 1.0}

# Chrome error-page marker — present in every Chrome net-error/offline page
_CHROME_ERROR_MARKER = "#main-frame-error"


@dataclass
class _PoolEntry:
    server: str
    port: str
    hashrate: float = 0.0
    fee_pct: float = 0.0
    name: str = ""


def _parse_hashrate(value: str, unit: str) -> float:
    return float(value) * _HR_MULT.get(unit.lower() if unit else "", 1.0)


def _score(entry: _PoolEntry) -> float:
    return entry.hashrate / (1.0 + entry.fee_pct / 100.0)


class PoolClient:
    def __init__(self, url_template: str, timeout: int = 30) -> None:
        self.url_template = url_template
        self.timeout = timeout

    def lookup(self, tag: str) -> PoolResult:
        url = self.url_template.format(tag=tag.lower())
        if "miningpoolstats.stream" in url:
            html = _fetch_miningpoolstats(url, self.timeout)
        else:
            response = requests.get(url, timeout=self.timeout, headers={"User-Agent": "rigManager/2.0"})
            response.raise_for_status()
            html = response.text
        return _parse_pool_page(html, url)


# ---------------------------------------------------------------------------
# Fetching
# ---------------------------------------------------------------------------

_BROWSER_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/148.0.0.0 Safari/537.36"
)


def _fetch_miningpoolstats(url: str, timeout: int) -> str:
    """Try Selenium first; fall back to plain requests if Chrome can't reach the site."""
    try:
        html = _fetch_with_selenium(url, timeout)
        LOG.debug("Selenium fetch succeeded (%d chars)", len(html))
        return html
    except Exception as exc:
        LOG.warning("Selenium fetch failed (%s) — retrying with requests", exc)

    response = requests.get(url, timeout=timeout, headers={"User-Agent": _BROWSER_UA})
    response.raise_for_status()
    if "can't be found" in response.text[:500].lower():
        raise RuntimeError(f"Page not found (soft 404): {url}")
    LOG.debug("requests fetch succeeded (%d chars)", len(response.text))
    return response.text


def _fetch_with_selenium(url: str, timeout: int) -> str:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.support.ui import WebDriverWait

    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument(f"--user-agent={_BROWSER_UA}")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    # Forward the system proxy so headless Chrome uses the same network path
    # as the regular requests library.
    sys_proxies = urllib.request.getproxies()
    proxy = sys_proxies.get("https") or sys_proxies.get("http")
    if proxy:
        options.add_argument(f"--proxy-server={proxy}")

    driver = webdriver.Chrome(options=options)
    try:
        # Hide the navigator.webdriver flag (bot-detection bypass)
        driver.execute_cdp_cmd(
            "Page.addScriptToEvaluateOnNewDocument",
            {"source": "Object.defineProperty(navigator,'webdriver',{get:()=>undefined})"},
        )
        driver.get(url)

        WebDriverWait(driver, timeout).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )

        # Detect Chrome error page (DNS failure, connection refused, etc.)
        if _CHROME_ERROR_MARKER in driver.page_source[:4000]:
            raise RuntimeError(
                f"Chrome could not reach {url} — got an error page. "
                "The site may be unreachable from headless Chrome."
            )

        # Detect site-level 404 pages (soft 404 served with HTTP 200)
        if "can't be found" in driver.title.lower() or driver.title.strip() in ("404", "Not Found"):
            raise RuntimeError(f"Page not found (404): {url}")

        # Scroll to trigger lazy-loaded content
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight / 2);")
        time.sleep(2)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)

        return driver.page_source
    finally:
        driver.quit()


# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------

def _extract_pool_entries(text: str) -> list[_PoolEntry]:
    entries: list[_PoolEntry] = []
    seen: set[tuple[str, str]] = set()

    for m in _STRATUM_RE.finditer(text):
        server, port = m.group(1), m.group(2)
        if (server, port) in seen:
            continue
        seen.add((server, port))

        # Search a window around the stratum address for hashrate and fee
        start = max(0, m.start() - 600)
        end = min(len(text), m.end() + 200)
        window = text[start:end]

        hashrate = 0.0
        hr_m = _HASHRATE_RE.search(window)
        if hr_m:
            hashrate = _parse_hashrate(hr_m.group(1), hr_m.group(2) or "")

        fee_pct = 0.0
        fee_m = _FEE_RE.search(window)
        if fee_m:
            val = float(fee_m.group(1))
            if val <= 10.0:  # pool fees are typically 0–10 %
                fee_pct = val

        entries.append(_PoolEntry(server=server, port=port, hashrate=hashrate, fee_pct=fee_pct))

    return entries


def _parse_pool_page(html: str, url: str) -> PoolResult:
    soup = BeautifulSoup(html, "html.parser")

    # --- strategy 1: structured data attributes (legacy sites) ---
    row = soup.find("tr", attrs={"class": "table-pool"})
    if row is not None:
        server = row.get("data-child-server")
        port = row.get("data-child-port")
        if server or port:
            return PoolResult(
                server=_clean_server(server),
                port=_clean_port(port),
                source_url=url,
                raw={"source": "data-child"},
            )

    # --- strategy 2: collect all pools, pick the best ---
    text = soup.get_text(" ", strip=True)
    entries = _extract_pool_entries(text)

    if entries:
        any_hashrate = any(e.hashrate > 0 for e in entries)
        if any_hashrate:
            best = max(entries, key=_score)
            LOG.info(
                "Best pool: %s:%s  hashrate=%.2e H/s  fee=%.1f%%  (from %d candidates)",
                best.server, best.port, best.hashrate, best.fee_pct, len(entries),
            )
        else:
            # Page already sorted by hashrate — first entry is the largest pool
            best = entries[0]
            LOG.info(
                "Best pool (first on page): %s:%s  (from %d candidates, no hashrate data parsed)",
                best.server, best.port, len(entries),
            )
        return PoolResult(
            server=best.server,
            port=best.port,
            source_url=url,
            name=best.name or None,
            hashrate=best.hashrate,
            fee_pct=best.fee_pct,
            raw={"source": "miningpoolstats", "candidates": len(entries)},
        )

    # --- strategy 3: generic host:port fallback ---
    server, port = _find_host_port(text)
    if not server:
        LOG.warning("No pool address found in page. Run with --log-level DEBUG to inspect page content.")
        LOG.debug("Page text sample (first 2000 chars): %s", text[:2000])
    return PoolResult(server=server, port=port, source_url=url, raw={"source": "fallback"})


def _clean_server(value: str | None) -> str | None:
    if not value:
        return None
    candidate = value.split(",", 1)[0].strip().strip("'\"")
    if candidate.startswith("stratum+tcp://"):
        candidate = candidate.removeprefix("stratum+tcp://")
    if ":" in candidate:
        parsed = urlparse("//" + candidate)
        return parsed.hostname or candidate.split(":", 1)[0]
    return candidate or None


def _clean_port(value: str | None) -> str | None:
    if not value:
        return None
    candidate = value.split(",", 1)[0].strip().strip("'\"")
    if candidate.isdigit():
        return candidate
    digits = "".join(ch for ch in candidate if ch.isdigit())
    return digits or None


def _find_host_port(text: str) -> tuple[str | None, str | None]:
    pattern = re.compile(r"(?P<host>[A-Za-z0-9.-]+\.[A-Za-z]{2,})(?::|\s+)(?P<port>[0-9]{2,5})")
    match = pattern.search(text)
    if not match:
        return None, None
    return match.group("host"), match.group("port")
