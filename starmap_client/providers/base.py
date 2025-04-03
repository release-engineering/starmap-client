from abc import ABC, abstractmethod
from typing import Any, Dict, Generic, List, Optional, TypeVar

TQRC = TypeVar("TQRC")  # QueryResponseContainer
TQRE = TypeVar("TQRE")  # QueryResponseEntity


class StarmapProvider(ABC, Generic[TQRC, TQRE]):
    """Define the interface for a local mappings provider."""

    api = "default"
    """The provider's API level implementation."""

    @abstractmethod
    def query(self, params: Dict[str, Any]) -> Optional[TQRC]:
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
    def list_content(self) -> List[TQRE]:
        """Return a list with all stored responses."""

    @abstractmethod
    def store(self, response: TQRE) -> None:
        """Store a single response into the local provider.

        Args:
            response (response):
                The object to store.
        """
