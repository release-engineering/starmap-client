from typing import Any, Dict, Optional

import pytest

from starmap_client.models import QueryResponse
from starmap_client.providers import InMemoryMapProvider


class TestInMemoryMapProvider:

    def test_list_content(self, qr1_object: QueryResponse, qr2_object: QueryResponse) -> None:
        data = [qr1_object, qr2_object]

        provider = InMemoryMapProvider(map_responses=data)

        assert provider.list_content() == data

    def test_store(self, qr1_object: QueryResponse, qr2_object: QueryResponse) -> None:
        provider = InMemoryMapProvider()

        assert provider.list_content() == []

        provider.store(qr1_object)

        assert provider.list_content() == [qr1_object]

        provider.store(qr2_object)

        assert provider.list_content() == [qr1_object, qr2_object]

    @pytest.mark.parametrize(
        "params, expected",
        [
            (
                {"name": "sample-product", "version": "8.0", "workflow": "stratosphere"},
                'qr1_object',
            ),
            ({"name": "sample-product", "version": "8.1", "workflow": "community"}, 'qr2_object'),
            ({"name": "another-product", "version": "8.2", "workflow": "stratosphere"}, None),
            ({"name": "another-product", "version": "8.2", "workflow": "community"}, None),
        ],
    )
    def test_query(
        self,
        params: Dict[str, Any],
        expected: Optional[str],
        qr1_object: QueryResponse,
        qr2_object: QueryResponse,
        request: pytest.FixtureRequest,
    ) -> None:
        data = [qr1_object, qr2_object]
        provider = InMemoryMapProvider(data)

        if expected is not None:
            expected = request.getfixturevalue(expected)

        qr = provider.query(params)
        assert qr == expected
