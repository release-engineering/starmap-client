from typing import Any, Dict


def assert_is_dict(data: Any) -> None:
    """Ensure the incoming data is a dictionary, raises ``ValueError`` if not."""
    if not isinstance(data, dict):
        raise ValueError(f"Expected dictionary, got {type(data)}: {data}")


def dict_merge(a: Dict[str, Any], b: Dict[str, Any]) -> Dict[str, Any]:
    """Return a new dictionary with the combination of A and B.

    Args:
        a (dict):
            The left dictionary to be combined
        b (dict):
            The right dictionary to be combined. It will override the same keys from A.
    Returns:
        dict: A new dictionary with combination of A and B.
    """
    for x in [a, b]:
        assert_is_dict(x)
    return a | b
