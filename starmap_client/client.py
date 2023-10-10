# SPDX-License-Identifier: GPL-3.0-or-later
import logging
from typing import Any, Dict, Iterator, List, Optional

from starmap_client.models import (
    Destination,
    Mapping,
    PaginatedRawData,
    Policy,
    QueryResponse,
    Workflow,
)
from starmap_client.session import StarmapSession

log = logging.getLogger(__name__)


class StarmapClient(object):
    """Implement the StArMap client."""

    POLICIES_PER_PAGE = 100
    """Number of policies to retrieve per call."""

    def __init__(
        self, url: str, api_version: str = "v1", session_params: Optional[Dict[str, Any]] = None
    ):
        """
        Create a new StArMapClient.

        Args:
            url (str)
                URL of the StArMap endpoint.

            api_version (str, optional)
                The StArMap API version. Defaults to `v1`.
            session_params (dict, optional)
                Additional keyword arguments for StarmapSession
        """
        session_params = session_params or {}
        self.session = StarmapSession(url, api_version, **session_params)
        self._policies: List[Policy] = []

    def _query(self, params: Dict[str, Any]) -> Optional[QueryResponse]:
        rsp = self.session.get("/query", params=params)
        if rsp.status_code == 404:
            log.error(f"Marketplace mappings not defined for {params}")
            return None
        rsp.raise_for_status()
        return QueryResponse.from_json(json=rsp.json())

    def query_image(
        self, nvr: str, workflow: Workflow = Workflow.stratosphere
    ) -> Optional[QueryResponse]:
        """
        Query StArMap using an image NVR.

        Args:
            nvr (str): The image archive name or NVR.
            workflow(Workflow, optional): The desired workflow to retrieve the mappings from.

        Returns:
            QueryResponse: The query result when found or None.
        """
        return self._query(params={"image": nvr, "workflow": workflow.value})

    def query_image_by_name(
        self,
        name: str,
        version: Optional[str] = None,
        workflow: Workflow = Workflow.stratosphere,
    ) -> Optional[QueryResponse]:
        """
        Query StArMap using an image NVR.

        Args:
            name (str): The image name from NVR.
            version (str, optional): The version from NVR.
            workflow (Workflow, optional): The desired workflow to retrieve the mappings from.

        Returns:
            QueryResponse: The query result when found or None.
        """
        params = {"name": name, "workflow": workflow.value}
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
