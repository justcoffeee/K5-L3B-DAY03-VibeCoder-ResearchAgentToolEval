from __future__ import annotations

import math
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from typing import Any
from urllib.parse import parse_qsl, urlencode, urlparse

from tools._shared import err, fold_text, terms

VALID_CRITERIA = {"balanced", "relevance", "recency", "popularity"}
WEIGHTS = {
    "balanced": {"relevance": 0.5, "recency": 0.25, "popularity": 0.25},
    "balanced_no_query": {"relevance": 0.0, "recency": 0.5, "popularity": 0.5},
    "relevance": {"relevance": 1.0, "recency": 0.0, "popularity": 0.0},
    "recency": {"relevance": 0.0, "recency": 1.0, "popularity": 0.0},
    "popularity": {"relevance": 0.0, "recency": 0.0, "popularity": 1.0},
}
DATE_FIELDS = ("date", "published", "updated_at", "updated", "published_date")
DEFAULT_TOP_K = 5
MAX_TOP_K = 20


# ---------------- helpers ----------------

def _clamp_top_k(value: Any) -> int:
    try:
        n = int(value)
    except (TypeError, ValueError):
        return DEFAULT_TOP_K
    return max(1, min(n, MAX_TOP_K))


def _num(value: Any) -> float:
    """Engagement counts may arrive as int, float, '1,234' or None."""
    if isinstance(value, bool):
        return 0.0
    if isinstance(value, (int, float)):
        return float(value) if value > 0 else 0.0
    if isinstance(value, str):
        try:
            return max(0.0, float(value.replace(",", "").strip()))
        except ValueError:
            return 0.0
    return 0.0


def _parse_date(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        return None
    text = value.strip()
    try:  # ISO 8601: arXiv "2026-11-09T10:00:00Z", GitHub, plain "2026-11-09"
        dt = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        try:  # RFC 2822: "Mon, 10 Nov 2026 10:00:00 +0000"
            dt = parsedate_to_datetime(text)
        except (TypeError, ValueError):
            try:  # Twitter: "Mon Nov 10 10:00:00 +0000 2026"
                dt = datetime.strptime(text, "%a %b %d %H:%M:%S %z %Y")
            except ValueError:
                return None
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


def _item_date(item: dict[str, Any]) -> datetime | None:
    for field in DATE_FIELDS:
        dt = _parse_date(item.get(field))
        if dt:
            return dt
    return None


def _engagement(item: dict[str, Any]) -> float:
    metrics = item.get("metrics") if isinstance(item.get("metrics"), dict) else {}
    raw = (
        _num(metrics.get("favorites")) + _num(metrics.get("likes"))
        + 2 * _num(metrics.get("retweets"))
        + _num(metrics.get("views")) / 100
        + _num(item.get("stars")) + _num(item.get("points"))
    )
    return math.log1p(raw)


def _relevance(item: dict[str, Any], query_terms: set[str]) -> float:
    if not query_terms:
        return 0.0
    title_terms = terms(str(item.get("title") or ""))
    body_terms = terms(str(item.get("summary") or ""))
    title_hit = len(query_terms & title_terms) / len(query_terms)
    any_hit = len(query_terms & (title_terms | body_terms)) / len(query_terms)
    overlap = 0.6 * any_hit + 0.4 * title_hit
    engine_score = item.get("score")  # e.g. Tavily relevance in [0, 1]
    if isinstance(engine_score, (int, float)) and not isinstance(engine_score, bool) and 0 <= engine_score <= 1:
        return 0.7 * overlap + 0.3 * float(engine_score)
    return overlap


def _dedupe_key(item: dict[str, Any]) -> str:
    url = str(item.get("url") or "").strip()
    if url:
        parsed = urlparse(url if "://" in url else f"https://{url}")
        query = urlencode([(k, v) for k, v in parse_qsl(parsed.query) if not k.lower().startswith("utm_")])
        host = parsed.netloc.lower().removeprefix("www.")
        path = parsed.path.rstrip("/")
        return f"url:{host}{path}?{query}" if query else f"url:{host}{path}"
    title = " ".join(fold_text(str(item.get("title") or "")).split())
    return f"title:{title}" if title else ""


def _normalise(values: list[float]) -> list[float]:
    """Min-max to [0, 1]; all-equal values become 0 so they don't affect the order."""
    if not values:
        return []
    lo, hi = min(values), max(values)
    if hi == lo:
        return [0.0] * len(values)
    return [(v - lo) / (hi - lo) for v in values]


def _recency_scores(dates: list[datetime | None]) -> list[float]:
    """Undated -> 0. Dated -> 0.1 (oldest) .. 1.0 (newest), so any date beats no date."""
    stamps = [d.timestamp() for d in dates if d]
    if not stamps:
        return [0.0] * len(dates)
    lo, hi = min(stamps), max(stamps)
    return [0.0 if d is None else 1.0 if hi == lo else 0.1 + 0.9 * (d.timestamp() - lo) / (hi - lo) for d in dates]


# ---------------- tool ----------------

def rank_items(
    items: list[dict[str, Any]] | None = None,
    query: str = "",
    criteria: str = "balanced",
    top_k: int = DEFAULT_TOP_K,
) -> dict[str, Any]:
    """Deduplicate and rank items the agent already collected. Local, no network. Never raises."""
    try:
        if items is None:
            items = []
        if not isinstance(items, list):
            raise ValueError("items must be a list of objects returned by other tools (lookup, social_search, papers...)")

        warnings: list[str] = []
        query = query.strip() if isinstance(query, str) else ""
        if criteria not in VALID_CRITERIA:
            warnings.append(f"unknown criteria {criteria!r}, used 'balanced'")
            criteria = "balanced"
        if criteria == "relevance" and not query:
            warnings.append("criteria 'relevance' needs a query, used 'balanced'")
            criteria = "balanced"
        k = _clamp_top_k(top_k)

        valid = [item for item in items if isinstance(item, dict)]
        dropped_invalid = len(items) - len(valid)

        unique: list[dict[str, Any]] = []
        seen: set[str] = set()
        for item in valid:
            key = _dedupe_key(item)
            if key and key in seen:
                continue
            if key:
                seen.add(key)
            unique.append(item)
        dropped_duplicates = len(valid) - len(unique)

        query_terms = terms(query)
        recency = _recency_scores([_item_date(item) for item in unique])
        popularity = _normalise([_engagement(item) for item in unique])
        relevance = [_relevance(item, query_terms) for item in unique]

        weights = WEIGHTS["balanced_no_query" if criteria == "balanced" and not query_terms else criteria]
        scored = []
        for index, item in enumerate(unique):
            signals = {"relevance": round(relevance[index], 3), "recency": round(recency[index], 3),
                       "popularity": round(popularity[index], 3)}
            score = sum(weights[name] * value for name, value in signals.items())
            scored.append((score, index, item, signals))
        scored.sort(key=lambda row: (-row[0], row[1]))  # stable: ties keep the original order

        ranked = [
            {**item, "rank": position, "rank_score": round(score, 3), "rank_signals": signals}
            for position, (score, _, item, signals) in enumerate(scored[:k], start=1)
        ]
        return {
            "tool": "rank",
            "query": query,
            "criteria": criteria,
            "input_count": len(items),
            "dropped_invalid": dropped_invalid,
            "dropped_duplicates": dropped_duplicates,
            "warnings": warnings,
            "items": ranked,
        }
    except Exception as exc:
        return err("rank", exc)
