# SPDX-License-Identifier: GPL-3.0-or-later
import sys
from typing import Any, Dict, List, Optional

if sys.version_info >= (3, 8):
    from typing import TypedDict  # pragma: no cover
else:
    from typing_extensions import TypedDict  # pragma: no cover

from attrs import Attribute, Factory, field, frozen
from attrs.validators import deep_iterable, deep_mapping, instance_of, min_len, optional

__all__ = [
    'Destination',
    'Mapping',
    'Policy',
    'QueryResponse',
    'PaginatedRawData',
    'PaginationMetadata',
]


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
class StarmapBaseData:
    """Represent the common data present in StArMap entities."""

    id: Optional[str] = field(validator=optional(instance_of(str)))
    """
    The unique ID for a StArMap model.
    This field is never set on :class:`~starmap_client.models.QueryResponse`.
    """

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
class Destination(StarmapBaseData, StarmapJSONDecodeMixin):
    """Represent a destination entry from Mapping."""

    architecture: Optional[str] = field(validator=optional(instance_of(str)))
    """Architecture of the VM image."""

    destination: str = field(validator=instance_of(str))
    """The product listing destination in the cloud marketplace."""

    overwrite: bool = field(validator=instance_of(bool))
    """Whether to replace the existing VM image in the destination or append."""


@frozen
class Mapping(StarmapBaseData, StarmapJSONDecodeMixin):
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
    """A ``fnmatch`` string to apply the destinations only to the matched NVR versions."""


@frozen
class Policy(StarmapBaseData, StarmapJSONDecodeMixin):
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


@frozen
class QueryResponse(StarmapJSONDecodeMixin):
    """Represent a query response from StArMap."""

    name: str = field(validator=instance_of(str))
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
