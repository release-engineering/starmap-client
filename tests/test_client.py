import json
import logging
from copy import deepcopy
from typing import Any
from unittest import TestCase, mock

import pytest
from _pytest.logging import LogCaptureFixture
from requests.exceptions import HTTPError

from starmap_client import StarmapClient
from starmap_client.models import Destination, Mapping, Policy, QueryResponseContainer
from starmap_client.providers import InMemoryMapProviderV2
from starmap_client.session import StarmapMockSession


def load_json(json_file: str) -> Any:
    with open(json_file, "r") as fd:
        data = json.load(fd)
    return data


class TestStarmapClient(TestCase):
    @pytest.fixture(autouse=True)
    def inject_fixtures(self, caplog: LogCaptureFixture) -> None:
        self._caplog = caplog

    def setUp(self) -> None:
        self.svc_v2 = StarmapClient("https://test.starmap.com", api_version="v2")

        self.mock_requests = mock.patch('starmap_client.session.requests').start()
        self.mock_session_v2 = mock.patch.object(self.svc_v2, 'session').start()

        self.image_name = "foo-bar"
        self.image_version = "1.0-1"
        self.image = f"{self.image_name}-{self.image_version}.raw.xz"

        # Mock requests responses
        self.mock_resp_success = mock.MagicMock()
        self.mock_resp_success.status_code = 200
        self.mock_resp_not_found = mock.MagicMock()
        self.mock_resp_not_found.status_code = 404
        self.mock_resp_not_found.raise_for_status.side_effect = HTTPError("Not found")  # noqa: E501

    def tearDown(self) -> None:
        mock.patch.stopall()

    def test_query_image_success_APIv2(self) -> None:
        fpath = "tests/data/query_v2/query_response_container/valid_qrc1.json"
        self.mock_resp_success.json.return_value = load_json(fpath)
        self.mock_session_v2.get.return_value = self.mock_resp_success

        res = self.svc_v2.query_image(self.image)

        expected_params = {"image": self.image}
        self.mock_session_v2.get.assert_called_once_with("/query", params=expected_params)
        self.mock_resp_success.raise_for_status.assert_called_once()
        # Note: JSON need to be loaded twice as `from_json` pops its original data
        assert res == QueryResponseContainer.from_json(load_json(fpath))

    def test_in_memory_query_image_APIv2(self) -> None:
        fpath = "tests/data/query_v2/query_response_container/valid_qrc1.json"
        data = QueryResponseContainer.from_json(load_json(fpath))
        provider = InMemoryMapProviderV2(data)

        self.svc_v2 = StarmapClient("https://test.starmap.com", api_version="v2", provider=provider)

        res = self.svc_v2.query_image("product-test-1.0-1.raw.xz", workflow="stratosphere")
        assert res.responses == [data.responses[0]]

    def test_in_memory_api_mismatch(self) -> None:
        fpath = "tests/data/query_v2/query_response_container/valid_qrc1.json"
        data = QueryResponseContainer.from_json(load_json(fpath))
        provider_v2 = InMemoryMapProviderV2(data)

        err = "API mismatch: Provider has API v2 but the client expects: v1"
        with pytest.raises(ValueError, match=err):
            StarmapClient("foo", api_version="v1", provider=provider_v2)

    def test_query_image_not_found(self) -> None:
        self.mock_session_v2.get.return_value = self.mock_resp_not_found
        self.mock_session_v2.get.return_value = self.mock_resp_not_found

        for svc in [self.svc_v2, self.svc_v2]:
            with self._caplog.at_level(logging.ERROR):
                res = svc.query_image(self.image)
                expected_msg = "Marketplace mappings not defined for {'image': '%s'}" % self.image
                assert expected_msg in self._caplog.text
                assert res is None

    def test_query_image_by_name_APIv2(self) -> None:
        fpath = "tests/data/query_v2/query_response_container/valid_qrc1.json"
        self.mock_resp_success.json.return_value = load_json(fpath)
        self.mock_session_v2.get.return_value = self.mock_resp_success

        res = self.svc_v2.query_image_by_name(name=self.image_name)

        expected_params = {"name": self.image_name}
        self.mock_session_v2.get.assert_called_once_with("/query", params=expected_params)
        self.mock_resp_success.raise_for_status.assert_called_once()
        # Note: JSON need to be loaded twice as `from_json` pops its original data
        assert res == QueryResponseContainer.from_json(load_json(fpath))

    def test_in_memory_query_image_by_name_APIv2(self) -> None:
        fpath = "tests/data/query_v2/query_response_container/valid_qrc1.json"
        data = QueryResponseContainer.from_json(load_json(fpath))
        provider = InMemoryMapProviderV2(data)

        self.svc_v2 = StarmapClient("https://test.starmap.com", api_version="v2", provider=provider)

        res = self.svc_v2.query_image_by_name(name="product-test", workflow="stratosphere")
        self.mock_session_v2.get.assert_not_called()
        assert res.responses == [data.responses[0]]

    def test_query_image_by_name_version_APIv2(self) -> None:
        fpath = "tests/data/query_v2/query_response_container/valid_qrc1.json"
        self.mock_resp_success.json.return_value = load_json(fpath)
        self.mock_session_v2.get.return_value = self.mock_resp_success

        res = self.svc_v2.query_image_by_name(name=self.image_name, version=self.image_version)

        expected_params = {
            "name": self.image_name,
            "version": self.image_version,
        }
        self.mock_session_v2.get.assert_called_once_with("/query", params=expected_params)
        self.mock_resp_success.raise_for_status.assert_called_once()
        # Note: JSON need to be loaded twice as `from_json` pops its original data
        assert res == QueryResponseContainer.from_json(load_json(fpath))

    def test_policies_single_page(self) -> None:
        fpath = "tests/data/policy/valid_pol1.json"
        single_page = {
            "items": [load_json(fpath)],
            "nav": {
                "first": "https://test.starmap.com/api/v2/policy?page=1&per_page=1",
                "last": "https://test.starmap.com/api/v2/policy?page=1&per_page=1",
                "next": None,
                "page": 1,
                "per_page": 1,
                "previous": None,
                "total": 1,
                "total_pages": 1,
            },
        }
        self.svc_v2.POLICIES_PER_PAGE = 1
        self.mock_resp_success.json.return_value = single_page
        self.mock_session_v2.get.return_value = self.mock_resp_success

        # Iterate over all policies from StarmapClient property and
        # ensure each of them has a valid format.
        for p in self.svc_v2.policies:
            assert p == Policy.from_json(load_json(fpath))

        expected_params = {"page": 1, "per_page": 1}
        self.mock_session_v2.get.assert_called_once_with("policy", params=expected_params)
        self.mock_session_v2.get.call_count == 1
        self.mock_resp_success.raise_for_status.assert_called_once()

    def test_policies_multi_page(self) -> None:
        fpath = "tests/data/policy/valid_pol1.json"
        page1 = {
            "items": [load_json(fpath)],
            "nav": {
                "first": "https://test.starmap.com/api/v2/policy?page=1&per_page=1",
                "last": "https://test.starmap.com/api/v2/policy?page=1&per_page=1",
                "next": "https://test.starmap.com/api/v2/policy?page=2&per_page=1",
                "page": 1,
                "per_page": 1,
                "previous": None,
                "total": 2,
                "total_pages": 2,
            },
        }
        page2 = deepcopy(page1)
        page2["nav"]["next"] = None
        page2["nav"]["page"] = 2
        self.svc_v2.POLICIES_PER_PAGE = 1
        self.mock_resp_success.json.side_effect = [page1, page2]
        self.mock_session_v2.get.return_value = self.mock_resp_success

        # Iterate over all policies from StarmapClient property and
        # ensure each of them has a valid format.
        for p in self.svc_v2.policies:
            assert p == Policy.from_json(load_json(fpath))

        get_calls = [
            mock.call("policy", params={"page": 1, "per_page": 1}),
            mock.call().raise_for_status,
            mock.call().json(),
            mock.call("policy", params={"page": 2, "per_page": 1}),
            mock.call().raise_for_status,
            mock.call().json(),
        ]
        self.mock_session_v2.get.assert_has_calls(get_calls)
        self.mock_session_v2.get.call_count == 2
        self.mock_resp_success.raise_for_status.call_count == 2

    def test_policies_not_found(self) -> None:
        self.svc_v2.POLICIES_PER_PAGE = 1
        self.mock_session_v2.get.return_value = self.mock_resp_not_found

        with self._caplog.at_level(logging.ERROR):
            with pytest.raises(StopIteration):
                next(self.svc_v2.policies)
        assert "No policies registered in StArMap." in self._caplog.text

    @mock.patch('starmap_client.StarmapClient.policies')
    def test_list_policies(self, mock_policies: mock.MagicMock) -> None:
        fpath = "tests/data/policy/valid_pol1.json"
        pol = Policy.from_json(load_json(fpath))
        pol_list = [pol]
        mock_policies.__iter__.return_value = pol_list

        # Test cached policies list
        self.svc_v2._policies = pol_list
        res = self.svc_v2.list_policies()
        mock_policies.__iter__.assert_not_called()
        assert res == self.svc_v2._policies

        # Test uncached policies list
        self.svc_v2._policies = []
        res = self.svc_v2.list_policies()
        mock_policies.__iter__.assert_called_once()
        assert res == pol_list

    def test_get_policy(self) -> None:
        fpath = "tests/data/policy/valid_pol1.json"
        self.mock_resp_success.json.return_value = load_json(fpath)
        self.mock_session_v2.get.return_value = self.mock_resp_success

        res = self.svc_v2.get_policy(policy_id="policy-id")

        self.mock_session_v2.get.assert_called_once_with("/policy/policy-id")
        self.mock_resp_success.raise_for_status.assert_called_once()
        # Note: JSON need to be loaded twice as `from_json` pops its original data
        assert res == Policy.from_json(load_json(fpath))

    def test_get_policy_not_found(self) -> None:
        self.mock_session_v2.get.return_value = self.mock_resp_not_found

        with self._caplog.at_level(logging.ERROR):
            res = self.svc_v2.get_policy(policy_id="policy-id")

        expected_msg = "Policy not found with ID = \"policy-id\""
        assert expected_msg in self._caplog.text

        assert res is None

    @mock.patch("starmap_client.StarmapClient.get_policy")
    def test_list_mappings(self, mock_get_policy: mock.MagicMock) -> None:
        fpath = "tests/data/policy/valid_pol1.json"
        p = Policy.from_json(load_json(fpath))
        mock_get_policy.return_value = p

        res = self.svc_v2.list_mappings(policy_id="policy-id")

        mock_get_policy.assert_called_once_with("policy-id")
        assert res == p.mappings

    @mock.patch("starmap_client.StarmapClient.get_policy")
    def test_list_mappings_not_found(self, mock_get_policy: mock.MagicMock) -> None:
        mock_get_policy.return_value = None
        res = self.svc_v2.list_mappings(policy_id="policy-id")

        mock_get_policy.assert_called_once_with("policy-id")

        assert res == []

    def test_get_mapping(self) -> None:
        fpath = "tests/data/mapping/valid_map1.json"
        self.mock_resp_success.json.return_value = load_json(fpath)
        self.mock_session_v2.get.return_value = self.mock_resp_success

        res = self.svc_v2.get_mapping(mapping_id="mapping-id")

        self.mock_session_v2.get.assert_called_once_with("/mapping/mapping-id")
        self.mock_resp_success.raise_for_status.assert_called_once()
        # Note: JSON need to be loaded twice as `from_json` pops its original data
        assert res == Mapping.from_json(load_json(fpath))

    def test_get_mapping_not_found(self) -> None:
        self.mock_session_v2.get.return_value = self.mock_resp_not_found

        with self._caplog.at_level(logging.ERROR):
            res = self.svc_v2.get_mapping(mapping_id="mapping-id")

        expected_msg = "Marketplace Mapping not found with ID = \"mapping-id\""
        assert expected_msg in self._caplog.text

        assert res is None

    @mock.patch("starmap_client.StarmapClient.get_mapping")
    def test_list_destinations(self, mock_get_mapping: mock.MagicMock) -> None:
        fpath = "tests/data/mapping/valid_map1.json"
        m = Mapping.from_json(load_json(fpath))
        mock_get_mapping.return_value = m

        res = self.svc_v2.list_destinations(mapping_id="mapping-id")

        mock_get_mapping.assert_called_once_with("mapping-id")
        assert res == m.destinations

    @mock.patch("starmap_client.StarmapClient.get_mapping")
    def test_list_destinations_not_found(self, mock_get_mapping: mock.MagicMock) -> None:
        mock_get_mapping.return_value = None
        res = self.svc_v2.list_destinations(mapping_id="mapping-id")

        mock_get_mapping.assert_called_once_with("mapping-id")

        assert res == []

    def test_get_destination(self) -> None:
        fpath = "tests/data/destination/valid_dest1.json"
        self.mock_resp_success.json.return_value = load_json(fpath)
        self.mock_session_v2.get.return_value = self.mock_resp_success

        res = self.svc_v2.get_destination(destination_id="destination-id")

        self.mock_session_v2.get.assert_called_once_with("/destination/destination-id")
        self.mock_resp_success.raise_for_status.assert_called_once()
        # Note: JSON need to be loaded twice as `from_json` pops its original data
        assert res == Destination.from_json(load_json(fpath))

    def test_get_destination_not_found(self) -> None:
        self.mock_session_v2.get.return_value = self.mock_resp_not_found

        with self._caplog.at_level(logging.ERROR):
            res = self.svc_v2.get_destination(destination_id="destination-id")

        expected_msg = "Destination not found with ID = \"destination-id\""
        assert expected_msg in self._caplog.text

        assert res is None

    def test_client_requires_url_or_session(self) -> None:
        error = "Cannot initialize the client without defining either an \"url\" or \"session\"."
        with pytest.raises(ValueError, match=error):
            StarmapClient()


def test_offline_client() -> None:
    """Ensure the cient can be used offline with a local provider."""
    fpath = "tests/data/query_v2/query_response_container/valid_qrc2.json"
    qrc = QueryResponseContainer.from_json(load_json(fpath))

    # The provider will have the QueryResponseContainer from fpath
    provider = InMemoryMapProviderV2(qrc)

    # The session will prevent StarmapClient to request a real server
    session = StarmapMockSession("fake.starmap.url", "v2")

    # Offline client
    svc = StarmapClient(session=session, api_version="v2", provider=provider)

    assert session.json_data == {}
    assert session.status_code == 404

    assert svc.query_image("product-test-123.132-0.123") == qrc
    assert svc.query_image_by_name("product-test", "8.0") == qrc
    assert svc.get_destination("test") is None
    assert svc.get_mapping("test") is None
    assert svc.get_policy("test") is None
    assert svc.list_policies() == []
    assert svc.list_mappings("test") == []
    assert svc.list_destinations("test") == []
