from copy import deepcopy
from typing import Any, Dict, List

import pytest

from starmap_client.models import QueryResponseContainer, QueryResponseEntity

# ============================================ APIv2 ===============================================


@pytest.fixture
def qre1() -> Dict[str, Any]:
    return {
        "name": "sample-product",
        "workflow": "stratosphere",
        "cloud": "aws",
        "mappings": {
            "aws-na": {
                "destinations": [
                    {
                        "architecture": "x86_64",
                        "destination": "ffffffff-ffff-ffff-ffff-ffffffffffff",
                        "overwrite": True,
                        "restrict_version": False,
                        "meta": {"tag1": "aws-na-value1", "tag2": "aws-na-value2"},
                        "tags": {"key1": "value1", "key2": "value2"},
                    }
                ],
                "provider": None,
            },
            "aws-emea": {
                "destinations": [
                    {
                        "architecture": "x86_64",
                        "destination": "00000000-0000-0000-0000-000000000000",
                        "overwrite": True,
                        "restrict_version": False,
                        "meta": {"tag1": "aws-emea-value1", "tag2": "aws-emea-value2"},
                        "tags": {"key3": "value3", "key4": "value4"},
                    }
                ],
                "provider": None,
            },
        },
    }


@pytest.fixture
def qre2() -> Dict[str, Any]:
    return {
        "name": "sample-product",
        "workflow": "community",
        "cloud": "aws",
        "mappings": {
            "aws-na": {
                "destinations": [
                    {
                        "architecture": "x86_64",
                        "destination": "test-dest-1",
                        "overwrite": True,
                        "restrict_version": False,
                        "meta": {"tag1": "aws-na-value1", "tag2": "aws-na-value2"},
                        "tags": {"key1": "value1", "key2": "value2"},
                    }
                ],
                "provider": "AWS",
            },
            "aws-emea": {
                "destinations": [
                    {
                        "architecture": "x86_64",
                        "destination": "test-dest-2",
                        "overwrite": True,
                        "restrict_version": False,
                        "meta": {"tag1": "aws-emea-value1", "tag2": "aws-emea-value2"},
                        "tags": {"key3": "value3", "key4": "value4"},
                    }
                ],
                "provider": "AWS",
            },
        },
    }


@pytest.fixture
def qrc(qre1: Dict[str, Any], qre2: Dict[str, Any]) -> List[Dict[str, Any]]:
    return [deepcopy(qre1), deepcopy(qre2)]


@pytest.fixture
def qre1_object(qre1: Any) -> QueryResponseEntity:
    return QueryResponseEntity.from_json(deepcopy(qre1))


@pytest.fixture
def qre2_object(qre2: Any) -> QueryResponseEntity:
    return QueryResponseEntity.from_json(deepcopy(qre2))


@pytest.fixture
def qrc_object(qrc: Any) -> QueryResponseContainer:
    return QueryResponseContainer.from_json(qrc)
