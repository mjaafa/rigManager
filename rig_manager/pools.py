from __future__ import annotations

import logging
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

from .models import PoolResult

LOG = logging.getLogger(__name__)


class PoolClient:
    def __init__(self, url_template: str, timeout: int = 20) -> None:
        self.url_template = url_template
        self.timeout = timeout

    def lookup(self, tag: str) -> PoolResult:
        url = self.url_template.format(tag=tag.lower())
        response = requests.get(url, timeout=self.timeout, headers={"User-Agent": "rigManager/2.0"})
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        row = soup.find("tr", attrs={"class": "table-pool"})
        if row is not None:
            server = row.get("data-child-server")
            port = row.get("data-child-port")
            if server or port:
                return PoolResult(server=_clean_server(server), port=_clean_port(port), source_url=url, raw={"source": "data-child"})

        # Fallback: search table text for likely host:port values.
        text = soup.get_text(" ", strip=True)
        server, port = _find_host_port(text)
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
    import re

    pattern = re.compile(r"(?P<host>[A-Za-z0-9.-]+\.[A-Za-z]{2,})(?::|\s+)(?P<port>[0-9]{2,5})")
    match = pattern.search(text)
    if not match:
        return None, None
    return match.group("host"), match.group("port")
