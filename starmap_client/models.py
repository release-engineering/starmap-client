# SPDX-License-Identifier: GPL-3.0-or-later
import sys
from copy import deepcopy
from enum import Enum
from typing import Any, Dict, List, Optional, Type

if sys.version_info >= (3, 8):
    from typing import TypedDict  # pragma: no cover
else:
    from typing_extensions import TypedDict  # pragma: no cover

from attrs import Attribute, Factory, asdict, evolve, field, frozen
from attrs.validators import deep_iterable, deep_mapping, instance_of, min_len, optional

from starmap_client.utils import assert_is_dict, dict_merge

__all__ = [
    'BillingCodeRule',
    'BillingImageType',
    'Destination',
    'Mapping',
    'Policy',
    'QueryResponse',
    'QueryResponseEntity',
    'QueryResponseContainer',
    'PaginatedRawData',
    'PaginationMetadata',
    'Workflow',
]


# ============================================ Common ==============================================


class PaginationMetadata(TypedDict):
    """Datastructure of the metadata about the paginated query."""

    first: str
    last: str
    next: Optional[str]
    page: int
    per_page: int
    previous: Optional[str]
    total: int
    total_pages: int


class PaginatedRawData(TypedDict):
    """Represent a paginated StArMap data in its raw format (Dict)."""

    items: List[Any]
    nav: PaginationMetadata


class Workflow(str, Enum):
    """Define the valid workflows for StArMap."""

    community = "community"
    """Workflow ``community``."""

    stratosphere = "stratosphere"
    """Workflow ``stratosphere`` for marketplaces."""


@frozen
class StarmapJSONDecodeMixin:
    """Implement the default JSON deserialization for StArMap models."""

    @classmethod
    def _assert_json_dict(cls, json: Any) -> None:
        """
        Ensure the given JSON is an instance of `dict`.

        Args:
            json (Any)
                A JSON containing a StArMap response.
        """
        if not isinstance(json, dict):
            raise ValueError(
                f"Got an unsupported JSON type: \"{type(json)}\". Expected: \"<class 'dict'>\'"
            )

    @classmethod
    def _preprocess_json(cls, json: Dict[str, Any]) -> Dict[str, Any]:
        """
        Preprocess the JSON before converting it to class object.

        It's intended to be overriden by base classes which needs to do it.

        Args:
            json (dict)
                A JSON containing a StArMap response.
        Returns:
            dict: The modified JSON.
        """
        return json

    @classmethod
    def from_json(cls, json: Any):
        """
        Convert a JSON dictionary into class object.

        Args:
            json (dict)
                A JSON containing a StArMap response.
        Returns:
            The converted object from JSON.
        """
        cls._assert_json_dict(json)

        json = cls._preprocess_json(json)

        args = {}
        cls_attr = [a.name for a in cls.__attrs_attrs__ if isinstance(a, Attribute)]  # type: ignore
        for a in cls_attr:
            args[a] = json.pop(a, None)
        return cls(**args)


@frozen
class MetaMixin:
    """Mixin for defining the meta attribute and its validator."""

    meta: Optional[Dict[str, Any]] = field()
    """Dictionary with additional information related to a VM image."""

    @meta.validator
    def _is_meta_dict_of_str_any(self, attribute: Attribute, value: Any):
        if not value:
            return None
        if not isinstance(value, dict):
            raise TypeError(f"The value for \"{attribute.name}\" should be a dictionary.")
        for k in value.keys():
            if not isinstance(k, str):
                raise ValueError(f"Invalid key \"{k}\" for \"{attribute.name}\". Expected: \"str\"")


@frozen
class StarmapBaseData(MetaMixin, StarmapJSONDecodeMixin):
    """Represent the common data present in StArMap entities."""

    id: Optional[str] = field(validator=optional(instance_of(str)))
    """
    The unique ID for a StArMap model.
    This field is never set on :class:`~starmap_client.models.QueryResponse`.
    """


@frozen
class Destination(StarmapBaseData):
    """Represent a destination entry from Mapping."""

    architecture: Optional[str] = field(validator=optional(instance_of(str)))
    """Architecture of the VM image."""

    destination: str = field(validator=instance_of(str))
    """The product listing destination in the cloud marketplace."""

    overwrite: bool = field(validator=instance_of(bool))
    """Whether to replace the existing VM image in the destination or append."""

    restrict_version: bool = field(validator=instance_of(bool))
    """Whether to restrict and image and delete it's AMI and snapshot"""

    restrict_major: Optional[int] = field(validator=optional(instance_of(int)))
    """How many major versions are allowed in product"""

    restrict_minor: Optional[int] = field(validator=optional(instance_of(int)))
    """How many minor versions are allowed in product"""

    ami_version_template: Optional[str] = field(validator=optional(instance_of(str)))
    """Ami versioning template. Available options are major,minor,patch, or version.
    Such as {major}.{minor}. If version is used it'll use the already available version."""

    provider: Optional[str] = field(validator=optional(instance_of(str)))
    """Represent the RHSM provider name for the community workflow."""

    tags: Optional[Dict[str, str]] = field(
        validator=optional(
            deep_mapping(
                key_validator=instance_of(str),
                value_validator=instance_of(str),
                mapping_validator=instance_of(dict),
            )
        )
    )
    """Dictionary with custom tags to be set on cloud marketplaces resources."""


@frozen
class Mapping(StarmapBaseData):
    """Represent a marketplace Mapping from Policy."""

    destinations: List[Destination] = field(
        validator=[
            min_len(1),
            deep_iterable(
                member_validator=instance_of(Destination), iterable_validator=instance_of(list)
            ),
        ],
        converter=lambda x: [Destination.from_json(d) for d in x] if x else [],
    )
    """List of destinations for the marketplace account."""

    marketplace_account: str = field(validator=instance_of(str))
    """A string representing the destination marketplace account."""

    version_fnmatch: Optional[str] = field(validator=optional(instance_of(str)))
    """A ``fnmatch`` string to apply the destinations only to the matched NVR versions.

    It can't be set together with ``version_regexmatch``.
    """

    version_regexmatch: Optional[str] = field(validator=optional(instance_of(str)))
    """A ``regex`` string to apply the destinations only to the matched NVR versions.

    It can't be set together with ``version_fnmatch``."""


@frozen
class Policy(StarmapBaseData):
    """Represent a StArMap policy."""

    mappings: List[Mapping] = field(
        validator=[
            min_len(1),
            deep_iterable(
                member_validator=instance_of(Mapping), iterable_validator=instance_of(list)
            ),
        ],
        converter=lambda x: [Mapping.from_json(m) for m in x] if x else [],
    )
    """List of marketplace mappings which the Policy applies to."""

    name: str = field(validator=instance_of(str))
    """The Koji Package name representing also the Policy name."""

    workflow: Workflow = field(converter=lambda x: Workflow(x))
    """The policy workflow name."""


# ============================================ APIv1 ===============================================


@frozen
class QueryResponse(StarmapJSONDecodeMixin):
    """Represent a query response from StArMap."""

    name: str = field(validator=instance_of(str))
    """The :class:`~Policy` name."""

    workflow: Workflow = field(converter=lambda x: Workflow(x))
    """The :class:`~Policy` workflow."""

    clouds: Dict[str, List[Destination]] = field(
        default=Factory(dict),
        validator=deep_mapping(
            key_validator=instance_of(str),
            value_validator=deep_iterable(
                member_validator=instance_of(Destination), iterable_validator=instance_of(list)
            ),
            mapping_validator=instance_of(dict),
        ),
    )
    """Dictionary with the cloud marketplaces aliases and their respective Destinations."""

    @classmethod
    def _preprocess_json(cls, json: Any) -> Dict[str, Any]:
        """
        Convert the JSON format to the expected by QueryResponse.

        Params:
            json (dict): A JSON containing a StArMap Query response.
        Returns:
            dict: The modified JSON.
        """
        mappings = json.pop("mappings", {})
        for c in mappings.keys():
            if not isinstance(mappings[c], list):
                raise ValueError(f"Expected mappings to be a list, got \"{type(mappings[c])}\".")
            dst = [Destination.from_json(d) for d in mappings[c]]
            mappings[c] = dst
        json["clouds"] = mappings
        return json


# ============================================ APIv2 ===============================================


class BillingImageType(str, Enum):
    """Define the image type for :class:`~BillingCodeRule` for APIv2."""

    access = "access"
    """Billing type ``access``."""

    hourly = "hourly"
    """Billing type ``hourly``."""

    marketplace = "marketplace"
    """Billing type ``marketplace``."""


@frozen
class BillingCodeRule(StarmapJSONDecodeMixin):
    """Define a single Billing Code Configuration rule for APIv2."""

    codes: List[str] = field(
        validator=deep_iterable(
            member_validator=instance_of(str), iterable_validator=instance_of(list)
        )
    )
    """The billing codes to insert when this rule is matched."""

    image_name: str = field(validator=instance_of(str))
    """The image name to match the rule."""

    image_types: List[BillingImageType] = field(
        converter=lambda x: [BillingImageType[d] for d in x],
        validator=deep_iterable(
            member_validator=instance_of(BillingImageType), iterable_validator=instance_of(list)
        ),
    )
    """Image types list. Supported values are ``access`` and ``hourly``."""

    name: Optional[str]
    """The billing code rule name."""


@frozen
class MappingResponseObject(MetaMixin, StarmapJSONDecodeMixin):
    """Represent a single mapping response from :class:`~QueryResponseObject` for APIv2."""

    destinations: List[Destination] = field(
        validator=deep_iterable(
            iterable_validator=instance_of(list), member_validator=instance_of(Destination)
        )
    )
    """List of destinations for the mapping response object."""

    provider: Optional[str] = field(validator=optional(instance_of(str)))
    """The provider name for the community workflow."""

    @staticmethod
    def _unify_meta_with_destinations(json: Dict[str, Any]) -> None:
        """Merge the ``meta`` data from mappings into the destinations."""
        destinations = json.get("destinations", [])
        if not isinstance(destinations, list):
            raise ValueError(f"Expected destinations to be a list, got \"{type(destinations)}\"")
        meta = json.get("meta", {})
        for d in destinations:
            d["meta"] = dict_merge(meta, d.get("meta", {}))

    @classmethod
    def _preprocess_json(cls, json: Any) -> Dict[str, Any]:
        """
        Properly adjust the Destinations list for building this object.

        Params:
            json (dict): A JSON containing a StArMap Query response.
        Returns:
            dict: The modified JSON.
        """
        cls._unify_meta_with_destinations(json)
        provider = json.get("provider", None)
        destinations = json.get("destinations", [])
        converted_destinations = []
        for d in destinations:
            d["provider"] = provider
            converted_destinations.append(Destination.from_json(d))
        json["destinations"] = converted_destinations
        return json


@frozen
class QueryResponseEntity(MetaMixin, StarmapJSONDecodeMixin):
    """Represent a single query response entity from StArMap APIv2."""

    name: str = field(validator=instance_of(str))
    """The :class:`~Policy` name."""

    billing_code_config: Optional[Dict[str, BillingCodeRule]] = field(
        validator=optional(
            deep_mapping(
                key_validator=instance_of(str),
                value_validator=instance_of(BillingCodeRule),
                mapping_validator=instance_of(dict),
            )
        )
    )
    """The Billing Code Configuration for the community workflow."""

    cloud: str = field(validator=instance_of(str))
    """The cloud name where the destinations are meant to."""

    workflow: Workflow = field(converter=lambda x: Workflow(x))
    """The :class:`~Policy` workflow."""

    mappings: Dict[str, MappingResponseObject] = field(
        validator=deep_mapping(
            key_validator=instance_of(str),
            value_validator=instance_of(MappingResponseObject),
            mapping_validator=instance_of(dict),
        ),
    )
    """Dictionary with the cloud account names and MappingResponseObjects."""

    @property
    def account_names(self) -> List[str]:
        """Return the list of cloud account names declared on ``mappings``."""
        return list(self.mappings.keys())

    @property
    def all_mappings(self) -> List[MappingResponseObject]:
        """Return all ``MappingResponseObject`` stored in ``mappings``."""
        return list(self.mappings.values())

    def get_mapping_for_account(self, account: str) -> MappingResponseObject:
        """Return a single ``MappingResponseObject`` for a given account name.

        Args:
            account (str):
                The account name to retrieve the ``MappingResponseObject``
        Returns:
            MappingResponseObject: The required mapping when found
        Raises: KeyError when not found
        """
        obj = self.mappings.get(account, None)
        if not obj:
            raise KeyError(f"No mappings found for account name {account}")
        return obj

    def to_classic_query_response(self) -> QueryResponse:
        """Return the representation of this object as a :class:`~QueryResponse` from APIv1."""

        def add_bc_to_dst_meta(clouds: Dict[str, List[Destination]]):
            if self.billing_code_config:
                bc_data = {k: asdict(v) for k, v in self.billing_code_config.items()}
                for dst_list in clouds.values():
                    for d in dst_list:
                        meta = d.meta or {}
                        meta["billing-code-config"] = bc_data
                        d = evolve(d, meta=meta)

        clouds: Dict[str, List[Destination]] = {}
        for k, v in self.mappings.items():
            clouds[k] = [deepcopy(d) for d in v.destinations]

        if self.billing_code_config:
            add_bc_to_dst_meta(clouds)

        return QueryResponse(name=self.name, workflow=self.workflow, clouds=clouds)

    @staticmethod
    def _unify_meta_with_mappings(json: Dict[str, Any]) -> None:
        """Merge the ``meta`` data from package into the mappings."""
        mappings = json.get("mappings", {})
        meta = json.get("meta", {})
        for k, v in mappings.items():
            mappings[k]["meta"] = dict_merge(meta, v.get("meta", {}))

    @classmethod
    def _preprocess_json(cls, json: Dict[str, Any]) -> Dict[str, Any]:
        """
        Properly adjust the MappingResponseObject list and BillingCodeConfig dict for building this object.

        Params:
            json (dict): A JSON containing a StArMap Query response.
        Returns:
            dict: The modified JSON.
        """  # noqa: D202 E501

        def parse_entity_build_obj(
            entity_name: str, converter_type: Type[StarmapJSONDecodeMixin]
        ) -> None:
            entity = json.pop(entity_name, {})
            for k in entity.keys():
                assert_is_dict(entity[k])
                obj = converter_type.from_json(entity[k])
                entity[k] = obj
            json[entity_name] = entity

        bcc = json.pop("billing-code-config", {})
        json["billing_code_config"] = bcc
        cls._unify_meta_with_mappings(json)
        parse_entity_build_obj("mappings", MappingResponseObject)
        parse_entity_build_obj("billing_code_config", BillingCodeRule)
        return json


@frozen
class QueryResponseContainer:
    """Represent a full query response from APIv2."""

    responses: List[QueryResponseEntity] = field(
        validator=deep_iterable(
            member_validator=instance_of(QueryResponseEntity), iterable_validator=instance_of(list)
        )
    )
    """List with all responses from a Query V2 mapping."""

    @classmethod
    def from_json(cls, json: Any):
        """
        Convert the APIv2 response JSON into this object.

        Args:
            json (list)
                A JSON containing a StArMap APIv2 response.
        Returns:
            The converted object from JSON.
        """
        if not isinstance(json, list):
            raise ValueError(f"Expected root to be a list, got \"{type(json)}\".")

        responses = [QueryResponseEntity.from_json(qre) for qre in json]
        return cls(responses)

    def filter_by_name(
        self, name: str, responses: Optional[List[QueryResponseEntity]] = None
    ) -> List[QueryResponseEntity]:
        """Return a sublist of the responses with only the selected image name.

        Args:
            name (str):
                The image name to filter the list of responses
            responses (list, optional):
                List of existing responses to filter. Default by the container's own list.
        Returns:
            list: The sublist with only the selected image name.
        """
        if responses == []:
            return responses
        rsp = responses or self.responses
        return [x for x in rsp if x.name == name]

    def filter_by_workflow(
        self, workflow: Workflow, responses: Optional[List[QueryResponseEntity]] = None
    ) -> List[QueryResponseEntity]:
        """Return a sublist of the responses with only the selected workflow.

        Args:
            workflow (Workflow):
                The workflow to filter the list of responses
            responses (list, optional):
                List of existing responses to filter. Default by the container's own list.
        Returns:
            list: The sublist with only the selected workflows
        """
        if responses == []:
            return responses
        rsp = responses or self.responses
        return [x for x in rsp if x.workflow == workflow]

    def filter_by_cloud(
        self, cloud: str, responses: Optional[List[QueryResponseEntity]] = None
    ) -> List[QueryResponseEntity]:
        """Return a sublist of the responses with only the selected cloud name.

        Args:
            cloud (str):
                The cloud name to filter the list of responses
            responses (list, optional):
                List of existing responses to filter. Default by the container's own list.
        Returns:
            list: The sublist with only the selected cloud name.
        """
        if responses == []:
            return responses
        rsp = responses or self.responses
        return [x for x in rsp if x.cloud == cloud]

    def filter_by(self, **kwargs) -> List[QueryResponseEntity]:
        """Return a sublist of the responses with the selected filters."""
        filters = {
            "name": self.filter_by_name,
            "cloud": self.filter_by_cloud,
            "workflow": self.filter_by_workflow,
        }
        res = self.responses
        for k, v in kwargs.items():
            res = filters[k](v, responses=res)
        return res
