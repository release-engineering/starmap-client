from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from starmap_client.models import QueryResponse


class StarmapProvider(ABC):
    """Define the interface for a local mappings provider."""

    @abstractmethod
    def query(self, params: Dict[str, Any]) -> Optional[QueryResponse]:
        """Retrieve the mapping without using the server.

        It relies in the local provider to retrieve the correct mapping
        according to the parameters.

        Args:
            params (dict):
                The request params to retrieve the mapping.
        Returns:
            The requested mapping when found.
        """

    @abstractmethod
    def list_content(self) -> List[QueryResponse]:
        """Return a list with all stored QueryResponse objects."""

    @abstractmethod
    def store(self, query_response: QueryResponse) -> None:
        """Store a single query_response into the local provider.

        Args:
            query_response (query_response):
                The object to store.
        """
