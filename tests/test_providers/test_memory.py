from typing import Any, Dict, Optional

import pytest

from starmap_client.models import QueryResponse, QueryResponseContainer, QueryResponseEntity
from starmap_client.providers import InMemoryMapProviderV1, InMemoryMapProviderV2


class TestInMemoryMapProviderV1:

    def test_list_content(self, qr1_object: QueryResponse, qr2_object: QueryResponse) -> None:
        data = [qr1_object, qr2_object]

        provider = InMemoryMapProviderV1(map_responses=data)

        assert provider.list_content() == data

    def test_store(self, qr1_object: QueryResponse, qr2_object: QueryResponse) -> None:
        provider = InMemoryMapProviderV1()

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
        provider = InMemoryMapProviderV1(data)

        if expected is not None:
            expected = request.getfixturevalue(expected)

        qr = provider.query(params)
        assert qr == expected


class TestInMemoryMapProviderV2:

    def test_list_content(self, qrc_object: QueryResponseContainer) -> None:
        provider = InMemoryMapProviderV2(container=qrc_object)

        assert provider.list_content() == qrc_object.responses

    def test_store(
        self,
        qre1: Dict[str, Any],
        qre1_object: QueryResponseEntity,
        qre2_object: QueryResponseEntity,
    ) -> None:
        container = QueryResponseContainer.from_json([qre1])
        provider = InMemoryMapProviderV2(container=container)

        assert provider.list_content() == [qre1_object]

        provider.store(qre2_object)
        assert provider.list_content() == [qre1_object, qre2_object]

    @pytest.mark.parametrize(
        "params, expected",
        [
            (
                {"name": "sample-product", "version": "8.0", "workflow": "stratosphere"},
                'qre1',
            ),
            ({"name": "sample-product", "version": "8.1", "workflow": "community"}, 'qre2'),
            ({"name": "another-product", "version": "8.2", "workflow": "stratosphere"}, None),
            ({"name": "another-product", "version": "8.2", "workflow": "community"}, None),
        ],
    )
    def test_query(
        self,
        params: Dict[str, Any],
        expected: Optional[str],
        qrc_object: QueryResponseContainer,
        request: pytest.FixtureRequest,
    ) -> None:
        provider = InMemoryMapProviderV2(container=qrc_object)
        expected_container = None

        if expected is not None:
            qre = request.getfixturevalue(expected)
            expected_container = QueryResponseContainer.from_json([qre])

        qr = provider.query(params)
        assert qr == expected_container
