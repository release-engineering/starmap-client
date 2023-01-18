import json
from typing import Any

import pytest
from attrs.exceptions import FrozenInstanceError

from starmap_client.models import Destination, Mapping, Policy, QueryResponse


def load_json(json_file: str) -> Any:
    with open(json_file, "r") as fd:
        data = json.load(fd)
    return data


class TestDestination:
    @pytest.mark.parametrize(
        "json_file",
        [
            "tests/data/destination/valid_dest1.json",
            "tests/data/destination/valid_dest2.json",
            "tests/data/destination/valid_dest3.json",
            "tests/data/destination/valid_dest4.json",
            "tests/data/destination/valid_dest5.json",
        ],
    )
    def test_valid_destination_json(self, json_file: str) -> None:
        data = load_json(json_file)

        # From JSON should always work
        res = Destination.from_json(data)
        assert res

        # While constructor is expected to fail when not all parameters are present
        with pytest.raises(TypeError):
            Destination(**data)

    @pytest.mark.parametrize(
        "json_file",
        [
            "tests/data/destination/invalid_dest1.json",
            "tests/data/destination/invalid_dest2.json",
            "tests/data/destination/invalid_dest3.json",
        ],
    )
    def test_invalid_destination_json(self, json_file: str) -> None:
        data = load_json(json_file)
        err = data.pop("error")

        with pytest.raises(TypeError, match=err):
            Destination.from_json(data)

    def test_parse_json_not_dict(self):
        fake_json = ["I", "am", "a", "list"]
        err = "Got an unsupported JSON type: \"<class 'list'>\". Expected: \"<class 'dict'>\'"

        with pytest.raises(ValueError, match=err):
            Destination.from_json(fake_json)

    def test_invalid_meta(self):
        data = load_json("tests/data/destination/valid_dest1.json")

        # Test invalid `meta` type
        data["meta"] = "I'm invalid"
        err = "The value for \"meta\" should be a dictionary."

        with pytest.raises(TypeError, match=err):
            Destination.from_json(data)

        # Test invalid `meta` value
        data["meta"] = {1: "This is also invalid."}
        err = "Invalid key \"1\" for \"meta\". Expected: \"str\""
        with pytest.raises(ValueError, match=err):
            Destination.from_json(data)

    def test_frozen_destination(self):
        data = load_json("tests/data/destination/valid_dest1.json")

        d = Destination.from_json(data)

        with pytest.raises(FrozenInstanceError):
            d.architecture = "test"


class TestMapping:
    @pytest.mark.parametrize(
        "json_file",
        [
            "tests/data/mapping/valid_map1.json",
            "tests/data/mapping/valid_map2.json",
            "tests/data/mapping/valid_map3.json",
            "tests/data/mapping/valid_map4.json",
            "tests/data/mapping/valid_map5.json",
        ],
    )
    def test_valid_mapping_json(self, json_file: str) -> None:
        data = load_json(json_file)

        # From JSON should always work
        res = Mapping.from_json(data)
        assert res
        assert res.destinations
        for d in res.destinations:
            assert isinstance(d, Destination), "Elements of destinations should be \"Destination\""

        # While constructor is expected to fail when not all parameters are present
        with pytest.raises(TypeError):
            Mapping(**data)

    @pytest.mark.parametrize(
        "json_file",
        [
            "tests/data/mapping/invalid_map1.json",
            "tests/data/mapping/invalid_map2.json",
            "tests/data/mapping/invalid_map3.json",
        ],
    )
    def test_invalid_mapping_json(self, json_file: str) -> None:
        data = load_json(json_file)
        err = data.pop("error")

        with pytest.raises((TypeError, ValueError), match=err):
            Mapping.from_json(data)

    def test_frozen_mapping(self):
        data = load_json("tests/data/mapping/valid_map1.json")

        m = Mapping.from_json(data)

        with pytest.raises(FrozenInstanceError):
            m.marketplace_account = "test"


class TestPolicy:
    @pytest.mark.parametrize(
        "json_file",
        [
            "tests/data/policy/valid_pol1.json",
            "tests/data/policy/valid_pol2.json",
            "tests/data/policy/valid_pol3.json",
            "tests/data/policy/valid_pol4.json",
            "tests/data/policy/valid_pol5.json",
        ],
    )
    def test_valid_policy_json(self, json_file: str) -> None:
        data = load_json(json_file)

        # From JSON should always work
        res = Policy.from_json(data)
        assert res
        assert res.mappings
        for m in res.mappings:
            assert isinstance(m, Mapping), "Elements of mappings should be \"Mapping\""

        # While constructor is expected to fail when not all parameters are present
        with pytest.raises(TypeError):
            Policy(**data)

    @pytest.mark.parametrize(
        "json_file",
        [
            "tests/data/policy/invalid_pol1.json",
            "tests/data/policy/invalid_pol2.json",
            "tests/data/policy/invalid_pol3.json",
        ],
    )
    def test_invalid_policy_json(self, json_file: str) -> None:
        data = load_json(json_file)
        err = data.pop("error")

        with pytest.raises((TypeError, ValueError), match=err):
            Policy.from_json(data)

    def test_frozen_policy(self):
        data = load_json("tests/data/policy/valid_pol1.json")

        p = Policy.from_json(data)

        with pytest.raises(FrozenInstanceError):
            p.name = "test"


class TestQueryResponse:
    @pytest.mark.parametrize(
        "json_file",
        [
            "tests/data/query/valid_quer1.json",
            "tests/data/query/valid_quer2.json",
            "tests/data/query/valid_quer3.json",
            "tests/data/query/valid_quer4.json",
            "tests/data/query/valid_quer5.json",
        ],
    )
    def test_valid_query_resp_json(self, json_file: str) -> None:
        data = load_json(json_file)

        # From JSON should always work
        res = QueryResponse.from_json(data)
        assert res
        assert res.clouds
        for k, v in res.clouds.items():
            assert isinstance(k, str), "Cloud names should be string"
            assert isinstance(v, list), "Value of clouds should be \"List[Destination]\"."
            for d in v:
                assert isinstance(d, Destination), "Elements of clouds should be \"Destination\""

        # While constructor is expected to fail when not all parameters are present
        with pytest.raises(TypeError):
            QueryResponse(**data)

    def test_frozen_query(self):
        data = load_json("tests/data/query/valid_quer1.json")

        q = QueryResponse.from_json(data)

        with pytest.raises(FrozenInstanceError):
            q.name = "test"
