from typing import Any, Dict

import pytest

from starmap_client.utils import assert_is_dict, dict_merge


def test_assert_is_dict() -> None:
    assert_is_dict({})

    for x in [[], (), "a", 1, 1.0, True]:
        err = f"Expected dictionary, got {type(x)}: {x}"
        err = err.replace("[", "\\[").replace("]", "\\]")  # Avoid bad regex match
        with pytest.raises(ValueError, match=err):
            assert_is_dict(x)


@pytest.mark.parametrize(
    "a,b,expected",
    [
        ({}, {}, {}),
        ({"foo": "bar"}, {}, {"foo": "bar"}),
        ({}, {"foo": "bar"}, {"foo": "bar"}),
        ({"1": 1, "3": 3}, {"2": 2}, {"1": 1, "2": 2, "3": 3}),
        ({"1": 1, "3": 3}, {"2": 2, "3": 4}, {"1": 1, "2": 2, "3": 4}),
        ({"A": True, "B": True, "C": True}, {"B": False}, {"A": True, "B": False, "C": True}),
    ],
)
def test_dict_merge(a: Dict[str, Any], b: Dict[str, Any], expected: Dict[str, Any]) -> None:
    assert dict_merge(a, b) == expected
