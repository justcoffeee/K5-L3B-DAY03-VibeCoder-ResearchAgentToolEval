from run_eval import compare_subset


def test_compare_subset_matches_nested_item_objects_order_independently() -> None:
    expected = {"items": [{"title": "B", "published": "2024-01-01"}, {"title": "A", "stars": 3}]}
    actual = {"items": [{"title": "A", "stars": 3}, {"title": "B", "published": "2024-01-01"}]}

    assert compare_subset(expected, actual) == (True, [], 1, 1)


def test_compare_subset_rejects_missing_or_wrong_rank_items() -> None:
    expected = {"items": [{"title": "A", "url": "https://example.com/a"}]}

    assert not compare_subset(expected, {})[0]
    assert not compare_subset(expected, {"items": []})[0]
    assert not compare_subset(expected, {"items": [{"title": "A", "url": "https://wrong.example/"}]})[0]
