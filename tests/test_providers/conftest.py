from typing import Any, Dict

import pytest

from starmap_client.models import QueryResponse


@pytest.fixture
def qr1() -> Dict[str, Any]:
    return {
        "mappings": {
            "aws-na": [
                {
                    "architecture": "x86_64",
                    "destination": "ffffffff-ffff-ffff-ffff-ffffffffffff",
                    "overwrite": True,
                    "restrict_version": False,
                    "meta": {"tag1": "aws-na-value1", "tag2": "aws-na-value2"},
                    "tags": {"key1": "value1", "key2": "value2"},
                }
            ],
            "aws-emea": [
                {
                    "architecture": "x86_64",
                    "destination": "00000000-0000-0000-0000-000000000000",
                    "overwrite": True,
                    "restrict_version": False,
                    "meta": {"tag1": "aws-emea-value1", "tag2": "aws-emea-value2"},
                    "tags": {"key3": "value3", "key4": "value4"},
                }
            ],
        },
        "name": "sample-product",
        "workflow": "stratosphere",
    }


@pytest.fixture
def qr2() -> Dict[str, Any]:
    return {
        "mappings": {
            "aws-na": [
                {
                    "architecture": "x86_64",
                    "destination": "test-dest-1",
                    "overwrite": True,
                    "restrict_version": False,
                    "meta": {"tag1": "aws-na-value1", "tag2": "aws-na-value2"},
                    "tags": {"key1": "value1", "key2": "value2"},
                }
            ],
            "aws-emea": [
                {
                    "architecture": "x86_64",
                    "destination": "test-dest-2",
                    "overwrite": True,
                    "restrict_version": False,
                    "meta": {"tag1": "aws-emea-value1", "tag2": "aws-emea-value2"},
                    "tags": {"key3": "value3", "key4": "value4"},
                }
            ],
        },
        "name": "sample-product",
        "workflow": "community",
    }


@pytest.fixture
def qr1_object(qr1) -> QueryResponse:
    return QueryResponse.from_json(qr1)


@pytest.fixture
def qr2_object(qr2) -> QueryResponse:
    return QueryResponse.from_json(qr2)
