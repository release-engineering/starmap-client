from typing import Any, Dict, List, Optional

from starmap_client.models import QueryResponse
from starmap_client.providers.base import StarmapProvider
from starmap_client.providers.utils import get_image_name


class InMemoryMapProvider(StarmapProvider):
    """Provide in memory (RAM) QueryResponse mapping objects."""

    def __init__(
        self, map_responses: Optional[List[QueryResponse]] = None, *args, **kwargs
    ) -> None:
        """Crete a new InMemoryMapProvider object.

        Args:
            map_responses (list, optional)
                List of QueryResponse objects to load into memory. They will be
                used by query to fetch the correct response based on name
                and workflow.
        """
        self._separator = str(kwargs.pop("separator", "+"))
        self._content: Dict[str, QueryResponse] = {}
        super(StarmapProvider, self).__init__()
        self._boostrap(map_responses)

    def _boostrap(self, map_responses: Optional[List[QueryResponse]]) -> None:
        """Initialize the internal content dictionary.

        Args:
            map_responses (list, optional)
                List of QueryResponse objects to load into memory.
        """
        if not map_responses:
            return None

        # The in memory content is made of a combination of name and workflow
        for map in map_responses:
            key = f"{map.name}{self._separator}{map.workflow.value}"
            self._content[key] = map

    def list_content(self) -> List[QueryResponse]:
        """Return a list of stored content."""
        return list(self._content.values())

    def store(self, query_response: QueryResponse) -> None:
        """Store/replace a single QueryResponse object.

        Args:
            query_response (query_response):
                The object to store.
        """
        key = f"{query_response.name}{self._separator}{query_response.workflow.value}"
        self._content[key] = query_response

    def query(self, params: Dict[str, Any]) -> Optional[QueryResponse]:
        """Return the mapping from memory according to the received params.

        Args:
            params (dict):
                The request params to retrieve the mapping.
        Returns:
            The requested mapping when found.
        """
        name = params.get("name") or get_image_name(params.get("image"))
        workflow = str(params.get("workflow", ""))
        search_key = f"{name}{self._separator}{workflow}"
        return self._content.get(search_key)
