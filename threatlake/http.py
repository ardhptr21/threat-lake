from __future__ import annotations

import json
from typing import Any

import requests


def get_json(url: str, timeout: int = 30, headers: dict[str, str] | None = None, params: dict[str, Any] | None = None) -> Any:
    response = requests.get(url, timeout=timeout, headers=headers, params=params)
    response.raise_for_status()
    return response.json()


def get_text(url: str, timeout: int = 30, headers: dict[str, str] | None = None, params: dict[str, Any] | None = None) -> str:
    response = requests.get(url, timeout=timeout, headers=headers, params=params)
    response.raise_for_status()
    return response.text


def parse_json_lines(text: str) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        records.append(json.loads(line))
    return records

