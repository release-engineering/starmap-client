import json
from copy import deepcopy
from typing import Any, Optional

import pytest
from attrs import asdict
from attrs.exceptions import FrozenInstanceError

from starmap_client.models import (
    Destination,
    Mapping,
    MappingResponseObject,
    Policy,
    QueryResponseContainer,
    QueryResponseEntity,
    Workflow,
)


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
            "tests/data/destination/valid_dest6.json",
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
            "tests/data/destination/invalid_dest4.json",
            "tests/data/destination/invalid_dest5.json",
        ],
    )
    def test_invalid_destination_json(self, json_file: str) -> None:
        data = load_json(json_file)
        err = data.pop("error")

        with pytest.raises(TypeError, match=err):
            Destination.from_json(data)

    def test_parse_json_not_dict(self) -> None:
        fake_json = ["I", "am", "a", "list"]
        err = "Got an unsupported JSON type: \"<class 'list'>\". Expected: \"<class 'dict'>\'"

        with pytest.raises(ValueError, match=err):
            Destination.from_json(fake_json)

    def test_invalid_meta(self) -> None:
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

    def test_frozen_destination(self) -> None:
        data = load_json("tests/data/destination/valid_dest1.json")

        d = Destination.from_json(data)

        with pytest.raises(FrozenInstanceError):
            d.architecture = "test"  # type: ignore[misc]


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

        with pytest.raises((TypeError, ValueError)):
            Mapping.from_json(data)

    def test_frozen_mapping(self) -> None:
        data = load_json("tests/data/mapping/valid_map1.json")

        m = Mapping.from_json(data)

        with pytest.raises(FrozenInstanceError):
            m.marketplace_account = "test"  # type: ignore[misc]


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

        with pytest.raises((TypeError, ValueError)):
            Policy.from_json(data)

    def test_frozen_policy(self) -> None:
        data = load_json("tests/data/policy/valid_pol1.json")

        p = Policy.from_json(data)

        with pytest.raises(FrozenInstanceError):
            p.name = "test"  # type: ignore[misc]


class TestV2MappingResponseObject:
    @pytest.mark.parametrize(
        "json_file,meta,provider",
        [
            (
                "tests/data/query_v2/mapping_response_obj/valid_mro1.json",
                "tests/data/query_v2/mapping_response_obj/valid_mro1_meta.json",
                "AWS",
            ),
            (
                "tests/data/query_v2/mapping_response_obj/valid_mro2.json",
                "tests/data/query_v2/mapping_response_obj/valid_mro2_meta.json",
                "AZURE",
            ),
            (
                "tests/data/query_v2/mapping_response_obj/valid_mro3.json",
                "tests/data/query_v2/mapping_response_obj/valid_mro3_meta.json",
                None,
            ),
            (
                "tests/data/query_v2/mapping_response_obj/valid_mro4.json",
                "tests/data/query_v2/mapping_response_obj/valid_mro4_meta.json",
                None,
            ),
        ],
    )
    def test_valid_mapping_response_obj(
        self, json_file: str, meta: str, provider: Optional[str]
    ) -> None:
        data = load_json(json_file)
        expected_meta = load_json(meta)

        m = MappingResponseObject.from_json(data)
        assert m.provider == provider
        for d in m.destinations:
            assert d.meta == expected_meta
            assert d.provider == provider

    @pytest.mark.parametrize(
        "json_file",
        [
            "tests/data/query_v2/mapping_response_obj/invalid_mro1.json",
            "tests/data/query_v2/mapping_response_obj/invalid_mro2.json",
            "tests/data/query_v2/mapping_response_obj/invalid_mro3.json",
        ],
    )
    def test_invalid_clouds(self, json_file: str) -> None:
        data = load_json(json_file)
        err = data.pop("error")

        with pytest.raises((TypeError, ValueError), match=err):
            MappingResponseObject.from_json(data)


class TestV2QueryResponseEntity:
    @pytest.mark.parametrize(
        "json_file,meta",
        [
            (
                "tests/data/query_v2/query_response_entity/valid_qre1.json",
                "tests/data/query_v2/query_response_entity/valid_qre1_meta.json",
            ),
            (
                "tests/data/query_v2/query_response_entity/valid_qre2.json",
                "tests/data/query_v2/query_response_entity/valid_qre2_meta.json",
            ),
            (
                "tests/data/query_v2/query_response_entity/valid_qre3.json",
                "tests/data/query_v2/query_response_entity/valid_qre3_meta.json",
            ),
            (
                "tests/data/query_v2/query_response_entity/valid_qre4.json",
                "tests/data/query_v2/query_response_entity/valid_qre4_meta.json",
            ),
            (
                "tests/data/query_v2/query_response_entity/valid_qre5.json",
                "tests/data/query_v2/query_response_entity/valid_qre5_meta.json",
            ),
        ],
    )
    def test_valid_query_response_entity(self, json_file: str, meta: str) -> None:
        data = load_json(json_file)
        d = deepcopy(data)
        expected_meta_dict = load_json(meta)

        q = QueryResponseEntity.from_json(data)

        # Test the merged meta attributes on destinations
        for account_name in q.account_names:
            for dest in q.mappings[account_name].destinations:
                assert dest.meta == expected_meta_dict[account_name]

        # Test the billing_code_config
        if q.billing_code_config:
            bc_asdict = {k: asdict(v) for k, v in q.billing_code_config.items()}
            assert bc_asdict == d["billing-code-config"]

    def test_query_response_properties(self) -> None:
        data = load_json("tests/data/query_v2/query_response_entity/valid_qre1.json")
        q = QueryResponseEntity.from_json(data)

        assert q.account_names == ["test-emea", "test-na"]
        assert q.all_mappings == list(q.mappings.values())

    def test_get_mapping_for_account(self) -> None:
        data = load_json("tests/data/query_v2/query_response_entity/valid_qre1.json")
        q = QueryResponseEntity.from_json(data)

        assert q.get_mapping_for_account("test-na") == q.mappings["test-na"]

        with pytest.raises(KeyError):
            q.get_mapping_for_account("foo-bar")


class TestV2QueryResponseContainer:

    @pytest.mark.parametrize(
        "json_file", ["tests/data/query_v2/query_response_container/invalid_qrc1.json"]
    )
    def test_invalid_query_response_container(self, json_file: str) -> None:
        data = load_json(json_file)
        err = f"Expected root to be a list, got \"{type(data)}\""
        with pytest.raises(ValueError, match=err):
            QueryResponseContainer.from_json(data)

    def test_filter_by_name(self) -> None:
        data = load_json("tests/data/query_v2/query_response_container/valid_qrc1.json")
        qc = QueryResponseContainer.from_json(data)

        stt = QueryResponseEntity.from_json(
            load_json("tests/data/query_v2/query_response_entity/valid_qre1.json")
        )

        assert qc.filter_by_name("product-test")[0] == stt
        assert qc.filter_by_name("product-test", responses=[]) == []
        assert qc.filter_by_name("foo") == []
        assert qc.filter_by(name="product-test")[0] == stt

    def test_filter_by_workflow(self) -> None:
        data = load_json("tests/data/query_v2/query_response_container/valid_qrc1.json")
        qc = QueryResponseContainer.from_json(data)

        stt = QueryResponseEntity.from_json(
            load_json("tests/data/query_v2/query_response_entity/valid_qre1.json")
        )
        cmt = QueryResponseEntity.from_json(
            load_json("tests/data/query_v2/query_response_entity/valid_qre4.json")
        )

        assert qc.filter_by_workflow(Workflow.stratosphere)[0] == stt
        assert qc.filter_by_workflow(Workflow.community)[0] == cmt
        assert qc.filter_by_workflow(Workflow.stratosphere, responses=[]) == []
        assert qc.filter_by_workflow(Workflow.community, responses=[]) == []
        assert qc.filter_by(workflow=Workflow.stratosphere)[0] == stt
        assert qc.filter_by(workflow=Workflow.community)[0] == cmt

    def test_filter_by_cloud(self) -> None:
        data = load_json("tests/data/query_v2/query_response_container/valid_qrc2.json")
        qc = QueryResponseContainer.from_json(data)

        expected = QueryResponseEntity.from_json(
            load_json("tests/data/query_v2/query_response_entity/valid_qre1.json")
        )

        assert qc.filter_by_cloud("test")[0] == expected
        assert qc.filter_by_cloud("foo") == []
        assert qc.filter_by_cloud("test", responses=[]) == []
        assert qc.filter_by(cloud="test")[0] == expected

    def test_multiple_filters(slef) -> None:
        data = load_json("tests/data/query_v2/query_response_container/valid_qrc3.json")
        qc = QueryResponseContainer.from_json(data)
        expected = QueryResponseEntity.from_json(
            load_json("tests/data/query_v2/query_response_entity/valid_qre1.json")
        )

        assert qc.filter_by(cloud="test", workflow=Workflow.stratosphere)[0] == expected
