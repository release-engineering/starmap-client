from typing import Any, Dict, Optional

import pytest

from starmap_client.models import QueryResponseContainer, QueryResponseEntity
from starmap_client.providers import InMemoryMapProviderV2


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
