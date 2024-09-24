# SPDX-License-Identifier: GPL-3.0-or-later
import logging
from typing import Any, Dict, Iterator, List, Optional, Type, Union

from starmap_client.models import (
    Destination,
    Mapping,
    PaginatedRawData,
    Policy,
    QueryResponse,
    QueryResponseContainer,
)
from starmap_client.providers import StarmapProvider
from starmap_client.session import StarmapBaseSession, StarmapSession

log = logging.getLogger(__name__)


Q = Union[QueryResponse, QueryResponseContainer]

API_QUERY_RESPONSE: Dict[str, Type[Q]] = {
    "v1": QueryResponse,
    "v2": QueryResponseContainer,
    "default": QueryResponseContainer,
}


class StarmapClient(object):
    """Implement the StArMap client."""

    POLICIES_PER_PAGE = 100
    """Number of policies to retrieve per call."""

    def __init__(
        self,
        url: Optional[str] = None,
        api_version: str = "v2",
        session: Optional[StarmapBaseSession] = None,
        session_params: Optional[Dict[str, Any]] = None,
        provider: Optional[StarmapProvider] = None,
    ):
        """
        Create a new StArMapClient.

        Args:
            url (str, optional)
                URL of the StArMap endpoint. Required when session is not set.

            api_version (str, optional)
                The StArMap API version. Defaults to `v2`.
            session (StarmapBaseSession, optional)
                Defines the session object to use. Defaults to `StarmapSession` when not set
            session_params (dict, optional)
                Additional keyword arguments for StarmapSession
            provider (StarmapProvider, optional):
                Object responsible to provide mappings locally. When set the client will be query it
                first and if no mapping is found the subsequent request will be made to the server.
        """
        if url is None and session is None:
            raise ValueError(
                "Cannot initialize the client without defining either an \"url\" or \"session\"."
            )
        if provider and provider.api != api_version:
            raise ValueError(
                f"API mismatch: Provider has API {provider.api} but the client expects: {api_version}"  # noqa: E501
            )
        session_params = session_params or {}
        url = url or ""  # just to make mypy happy. The URL is mandatory if session is not defined
        self.session = session or StarmapSession(url, api_version, **session_params)
        self.api_version = api_version
        self._provider = provider
        self._policies: List[Policy] = []

    def _query(self, params: Dict[str, Any]) -> Optional[Q]:
        qr = None
        if self._provider:
            qr = self._provider.query(params)
        rsp = qr or self.session.get("/query", params=params)
        if isinstance(rsp, QueryResponse) or isinstance(rsp, QueryResponseContainer):
            log.debug(
                "Returning response from the local provider %s", self._provider.__class__.__name__
            )
            return rsp
        if rsp.status_code == 404:
            log.error(f"Marketplace mappings not defined for {params}")
            return None
        rsp.raise_for_status()
        converter = API_QUERY_RESPONSE.get(self.api_version, API_QUERY_RESPONSE["default"])
        return converter.from_json(json=rsp.json())

    def query_image(self, nvr: str, **kwargs) -> Optional[Q]:
        """
        Query StArMap using an image NVR.

        Args:
            nvr (str): The image archive name or NVR.
            workflow(Workflow, optional): The desired workflow to retrieve the mappings (APIv1 Only)

        Returns:
            Q: The query result when found or None.
        """
        return self._query(params={"image": nvr, **kwargs})

    def query_image_by_name(
        self,
        name: str,
        version: Optional[str] = None,
        **kwargs,
    ) -> Optional[Q]:
        """
        Query StArMap using an image NVR.

        Args:
            name (str): The image name from NVR.
            version (str, optional): The version from NVR.
            workflow(Workflow, optional): The desired workflow to retrieve the mappings (APIv1 Only)

        Returns:
            Q: The query result when found or None.
        """
        params = {"name": name, **kwargs}
        if version:
            params.update({"version": version})
        return self._query(params=params)

    @property
    def policies(self) -> Iterator[Policy]:
        """Iterate over all Policies registered in StArMap."""
        has_next_page = True
        page = 1

        # Iterate over pagination until there is no longer a "next" URL
        while has_next_page:
            params = {"page": page, "per_page": self.POLICIES_PER_PAGE}
            res = self.session.get("policy", params=params)
            if res.status_code == 404:
                log.error("No policies registered in StArMap.")
                return
            res.raise_for_status()

            data: PaginatedRawData = res.json()
            nav = data["nav"]

            # Yield all Policy elements from the current page list
            for item in data.get("items", []):
                yield Policy.from_json(item)

            # next iteration
            has_next_page = nav.get("next") is not None
            page += 1

    def list_policies(self) -> List[Policy]:
        """
        List all Policies present in StArMap.

        Returns:
            list(Policy): List with all policies present in StArMap.
        """
        if not self._policies:
            self._policies = [p for p in self.policies]
        return self._policies

    def get_policy(self, policy_id: str) -> Optional[Policy]:
        """
        Retrieve a single policy by its ID.

        Args:
            policy_id (str): The Policy ID to retrieve from StArMap.

        Returns:
            Policy: The requested Policy when found.
        """
        rsp = self.session.get(f"/policy/{policy_id}")
        if rsp.status_code == 404:
            log.error(f"Policy not found with ID = \"{policy_id}\"")
            return None
        rsp.raise_for_status()
        return Policy.from_json(json=rsp.json())

    def list_mappings(self, policy_id: str) -> List[Mapping]:
        """
        List all mappings for a given Policy ID.

        Args:
            policy_id (str)
                Policy ID to list the mappings.

        Returns:
            List with the Mappings for the requested Policy.
        """
        res = self.get_policy(policy_id)
        if res:
            return res.mappings
        return []

    def get_mapping(self, mapping_id: str) -> Optional[Mapping]:
        """
        Retrieve a single Marketplace Mapping by its ID.

        Args:
            mapping_id (str)
                The Markeplace Mapping ID to retrieve from StArmAp.

        Returns:
            The requested Marketplace Mapping when found.
        """
        rsp = self.session.get(f"/mapping/{mapping_id}")
        if rsp.status_code == 404:
            log.error(f"Marketplace Mapping not found with ID = \"{mapping_id}\"")
            return None
        rsp.raise_for_status()
        return Mapping.from_json(json=rsp.json())

    def list_destinations(self, mapping_id: str) -> List[Destination]:
        """
        List all destinations for a given Marketplace Mapping ID.

        Args:
            mapping_id (str)
                Marketplace Mapping ID to list the mappings.

        Returns:
            List with the Destinations for the requested Mapping.
        """
        res = self.get_mapping(mapping_id)
        if res:
            return res.destinations
        return []

    def get_destination(self, destination_id: str) -> Optional[Destination]:
        """
        Retrieve a single Destination by its ID.

        Args:
            destination_id (str)
                The Destination ID to retrieve from StArmAp.

        Returns:
            The requested Destination when found.
        """
        rsp = self.session.get(f"/destination/{destination_id}")
        if rsp.status_code == 404:
            log.error(f"Destination not found with ID = \"{destination_id}\"")
            return None
        rsp.raise_for_status()
        return Destination.from_json(json=rsp.json())
