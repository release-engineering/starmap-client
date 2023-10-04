import json
import logging
from copy import deepcopy
from typing import Any
from unittest import TestCase, mock

import pytest
from _pytest.logging import LogCaptureFixture
from requests.exceptions import HTTPError

from starmap_client import StarmapClient
from starmap_client.models import Destination, Mapping, Policy, QueryResponse


def load_json(json_file: str) -> Any:
    with open(json_file, "r") as fd:
        data = json.load(fd)
    return data


class TestStarmapClient(TestCase):
    @pytest.fixture(autouse=True)
    def inject_fixtures(self, caplog: LogCaptureFixture):
        self._caplog = caplog

    def setUp(self) -> None:
        self.svc = StarmapClient("https://test.starmap.com", api_version="v1")

        self.mock_requests = mock.patch('starmap_client.session.requests').start()
        self.mock_session = mock.patch.object(self.svc, 'session').start()

        self.image_name = "foo-bar"
        self.image_version = "1.0-1"
        self.image = f"{self.image_name}-{self.image_version}.raw.xz"

        # Mock requests responses
        self.mock_resp_success = mock.MagicMock()
        self.mock_resp_success.status_code = 200
        self.mock_resp_not_found = mock.MagicMock()
        self.mock_resp_not_found.status_code = 404
        self.mock_resp_not_found.raise_for_status.side_effect = HTTPError("Not found")  # type: ignore  # noqa: E501

    def tearDown(self):
        mock.patch.stopall()

    def test_query_image_success(self):
        fpath = "tests/data/query/valid_quer1.json"
        self.mock_resp_success.json.return_value = load_json(fpath)
        self.mock_session.get.return_value = self.mock_resp_success

        res = self.svc.query_image(self.image)

        expected_params = {"image": self.image}
        self.mock_session.get.assert_called_once_with("/query", params=expected_params)
        self.mock_resp_success.raise_for_status.assert_called_once()
        # Note: JSON need to be loaded twice as `from_json` pops its original data
        self.assertEqual(res, QueryResponse.from_json(load_json(fpath)))

    def test_query_image_not_found(self):
        self.mock_session.get.return_value = self.mock_resp_not_found

        with self._caplog.at_level(logging.ERROR):
            res = self.svc.query_image(self.image)

        expected_msg = "Marketplace mappings not defined for {'image': '%s'}" % self.image
        assert expected_msg in self._caplog.text

        self.assertIsNone(res)

    def test_query_image_by_name(self):
        fpath = "tests/data/query/valid_quer1.json"
        self.mock_resp_success.json.return_value = load_json(fpath)
        self.mock_session.get.return_value = self.mock_resp_success

        res = self.svc.query_image_by_name(name=self.image_name)

        expected_params = {"name": self.image_name}
        self.mock_session.get.assert_called_once_with("/query", params=expected_params)
        self.mock_resp_success.raise_for_status.assert_called_once()
        # Note: JSON need to be loaded twice as `from_json` pops its original data
        self.assertEqual(res, QueryResponse.from_json(load_json(fpath)))

    def test_query_image_by_name_version(self):
        fpath = "tests/data/query/valid_quer1.json"
        self.mock_resp_success.json.return_value = load_json(fpath)
        self.mock_session.get.return_value = self.mock_resp_success

        res = self.svc.query_image_by_name(name=self.image_name, version=self.image_version)

        expected_params = {"name": self.image_name, "version": self.image_version}
        self.mock_session.get.assert_called_once_with("/query", params=expected_params)
        self.mock_resp_success.raise_for_status.assert_called_once()
        # Note: JSON need to be loaded twice as `from_json` pops its original data
        self.assertEqual(res, QueryResponse.from_json(load_json(fpath)))

    def test_policies_single_page(self):
        fpath = "tests/data/policy/valid_pol1.json"
        single_page = {
            "items": [load_json(fpath)],
            "nav": {
                "first": "https://test.starmap.com/api/v1/policy?page=1&per_page=1",
                "last": "https://test.starmap.com/api/v1/policy?page=1&per_page=1",
                "next": None,
                "page": 1,
                "per_page": 1,
                "previous": None,
                "total": 1,
                "total_pages": 1,
            },
        }
        self.svc.POLICIES_PER_PAGE = 1
        self.mock_resp_success.json.return_value = single_page
        self.mock_session.get.return_value = self.mock_resp_success

        # Iterate over all policies from StarmapClient property and
        # ensure each of them has a valid format.
        for p in self.svc.policies:
            self.assertEqual(p, Policy.from_json(load_json(fpath)))

        expected_params = {"page": 1, "per_page": 1}
        self.mock_session.get.assert_called_once_with("policy", params=expected_params)
        self.mock_session.get.call_count == 1
        self.mock_resp_success.raise_for_status.assert_called_once()

    def test_policies_multi_page(self):
        fpath = "tests/data/policy/valid_pol1.json"
        page1 = {
            "items": [load_json(fpath)],
            "nav": {
                "first": "https://test.starmap.com/api/v1/policy?page=1&per_page=1",
                "last": "https://test.starmap.com/api/v1/policy?page=1&per_page=1",
                "next": "https://test.starmap.com/api/v1/policy?page=2&per_page=1",
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
        self.svc.POLICIES_PER_PAGE = 1
        self.mock_resp_success.json.side_effect = [page1, page2]
        self.mock_session.get.return_value = self.mock_resp_success

        # Iterate over all policies from StarmapClient property and
        # ensure each of them has a valid format.
        for p in self.svc.policies:
            self.assertEqual(p, Policy.from_json(load_json(fpath)))

        get_calls = [
            mock.call("policy", params={"page": 1, "per_page": 1}),
            mock.call().raise_for_status,
            mock.call().json(),
            mock.call("policy", params={"page": 2, "per_page": 1}),
            mock.call().raise_for_status,
            mock.call().json(),
        ]
        self.mock_session.get.assert_has_calls(get_calls)
        self.mock_session.get.call_count == 2
        self.mock_resp_success.raise_for_status.call_count == 2

    def test_policies_not_found(self):
        self.svc.POLICIES_PER_PAGE = 1
        self.mock_session.get.return_value = self.mock_resp_not_found

        with self._caplog.at_level(logging.ERROR):
            with pytest.raises(HTTPError):
                for _ in self.svc.policies:
                    pass

        assert "No policies registered in StArMap." in self._caplog.text

    @mock.patch('starmap_client.StarmapClient.policies')
    def test_list_policies(self, mock_policies: mock.MagicMock):
        fpath = "tests/data/policy/valid_pol1.json"
        pol = Policy.from_json(load_json(fpath))
        pol_list = [pol]
        mock_policies.__iter__.return_value = pol_list

        # Test cached policies list
        self.svc._policies = pol_list
        res = self.svc.list_policies()
        mock_policies.__iter__.assert_not_called()
        self.assertEqual(res, self.svc._policies)

        # Test uncached policies list
        self.svc._policies = []
        res = self.svc.list_policies()
        mock_policies.__iter__.assert_called_once()
        self.assertEqual(res, pol_list)

    def test_get_policy(self):
        fpath = "tests/data/policy/valid_pol1.json"
        self.mock_resp_success.json.return_value = load_json(fpath)
        self.mock_session.get.return_value = self.mock_resp_success

        res = self.svc.get_policy(policy_id="policy-id")

        self.mock_session.get.assert_called_once_with("/policy/policy-id")
        self.mock_resp_success.raise_for_status.assert_called_once()
        # Note: JSON need to be loaded twice as `from_json` pops its original data
        self.assertEqual(res, Policy.from_json(load_json(fpath)))

    def test_get_policy_not_found(self):
        self.mock_session.get.return_value = self.mock_resp_not_found

        with self._caplog.at_level(logging.ERROR):
            res = self.svc.get_policy(policy_id="policy-id")

        expected_msg = "Policy not found with ID = \"policy-id\""
        assert expected_msg in self._caplog.text

        self.assertIsNone(res)

    @mock.patch("starmap_client.StarmapClient.get_policy")
    def test_list_mappings(self, mock_get_policy: mock.MagicMock) -> None:
        fpath = "tests/data/policy/valid_pol1.json"
        p = Policy.from_json(load_json(fpath))
        mock_get_policy.return_value = p

        res = self.svc.list_mappings(policy_id="policy-id")

        mock_get_policy.assert_called_once_with("policy-id")
        self.assertEqual(res, p.mappings)

    @mock.patch("starmap_client.StarmapClient.get_policy")
    def test_list_mappings_not_found(self, mock_get_policy: mock.MagicMock) -> None:
        mock_get_policy.return_value = None
        res = self.svc.list_mappings(policy_id="policy-id")

        mock_get_policy.assert_called_once_with("policy-id")

        self.assertEqual(res, [])

    def test_get_mapping(self):
        fpath = "tests/data/mapping/valid_map1.json"
        self.mock_resp_success.json.return_value = load_json(fpath)
        self.mock_session.get.return_value = self.mock_resp_success

        res = self.svc.get_mapping(mapping_id="mapping-id")

        self.mock_session.get.assert_called_once_with("/mapping/mapping-id")
        self.mock_resp_success.raise_for_status.assert_called_once()
        # Note: JSON need to be loaded twice as `from_json` pops its original data
        self.assertEqual(res, Mapping.from_json(load_json(fpath)))

    def test_get_mapping_not_found(self):
        self.mock_session.get.return_value = self.mock_resp_not_found

        with self._caplog.at_level(logging.ERROR):
            res = self.svc.get_mapping(mapping_id="mapping-id")

        expected_msg = "Marketplace Mapping not found with ID = \"mapping-id\""
        assert expected_msg in self._caplog.text

        self.assertIsNone(res)

    @mock.patch("starmap_client.StarmapClient.get_mapping")
    def test_list_destinations(self, mock_get_mapping: mock.MagicMock) -> None:
        fpath = "tests/data/mapping/valid_map1.json"
        m = Mapping.from_json(load_json(fpath))
        mock_get_mapping.return_value = m

        res = self.svc.list_destinations(mapping_id="mapping-id")

        mock_get_mapping.assert_called_once_with("mapping-id")
        self.assertEqual(res, m.destinations)

    @mock.patch("starmap_client.StarmapClient.get_mapping")
    def test_list_destinations_not_found(self, mock_get_mapping: mock.MagicMock) -> None:
        mock_get_mapping.return_value = None
        res = self.svc.list_destinations(mapping_id="mapping-id")

        mock_get_mapping.assert_called_once_with("mapping-id")

        self.assertEqual(res, [])

    def test_get_destination(self):
        fpath = "tests/data/destination/valid_dest1.json"
        self.mock_resp_success.json.return_value = load_json(fpath)
        self.mock_session.get.return_value = self.mock_resp_success

        res = self.svc.get_destination(destination_id="destination-id")

        self.mock_session.get.assert_called_once_with("/destination/destination-id")
        self.mock_resp_success.raise_for_status.assert_called_once()
        # Note: JSON need to be loaded twice as `from_json` pops its original data
        self.assertEqual(res, Destination.from_json(load_json(fpath)))

    def test_get_destination_not_found(self):
        self.mock_session.get.return_value = self.mock_resp_not_found

        with self._caplog.at_level(logging.ERROR):
            res = self.svc.get_destination(destination_id="destination-id")

        expected_msg = "Destination not found with ID = \"destination-id\""
        assert expected_msg in self._caplog.text

        self.assertIsNone(res)
