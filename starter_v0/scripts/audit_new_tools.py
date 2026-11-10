"""Offline CP3 metadata and rank numeric audit. Run from starter_v0."""
from __future__ import annotations

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import yaml
from tools import TOOL_FUNCTIONS, load_tool_declarations


def main() -> None:
    declarations = {d["name"]: d for d in load_tool_declarations(ROOT / "artifacts/tools.yaml")}
    for name in ("analyze_text", "rank"):
        metadata = yaml.safe_load((ROOT / "tools" / name / "TOOL.md").read_text(encoding="utf-8").split("---")[1])
        assert metadata["name"] == name and metadata["side_effect"] is False
        assert name in TOOL_FUNCTIONS and name in declarations
        print(f"{name}: metadata, registry and declaration OK")

    counts = [float("inf"), "inf", 10**400, float("nan"), "nan", -1, "-3", True, "oops"]
    fields = ["favorites", "likes", "retweets", "views", "stars", "points"]
    checked = 0
    for count in counts:
        for field in fields:
            for criterion in ("balanced", "relevance", "recency", "popularity"):
                bad = {"title": "bad", "date": "2026-11-09"}
                if field in ("stars", "points"):
                    bad[field] = count
                else:
                    bad["metrics"] = {field: count}
                result = TOOL_FUNCTIONS["rank"](items=[bad, {"title": "valid", "date": "2026-11-10", "stars": 10}], query="valid", criteria=criterion)
                assert "error" not in result, result
                assert len(result["items"]) == 2
                for item in result["items"]:
                    assert math.isfinite(item["rank_score"])
                    assert all(math.isfinite(v) for v in item["rank_signals"].values())
                if criterion == "popularity":
                    assert result["items"][0]["title"] == "valid"
                checked += 1
    print(f"rank: {checked} calls passed (9 invalid counts x 6 fields x 4 criteria)")
    print("No API calls; analyze_text request/error paths are covered by mocked unit tests.")


if __name__ == "__main__":
    main()
