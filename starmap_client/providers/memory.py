from typing import Any, Dict, List, Optional

from starmap_client.models import QueryResponse, QueryResponseContainer, QueryResponseEntity
from starmap_client.providers.base import StarmapProvider
from starmap_client.providers.utils import get_image_name


class InMemoryMapProviderV1(StarmapProvider):
    """Provide in memory (RAM) QueryResponse mapping objects for APIv1."""

    api = "v1"

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

    def store(self, response: QueryResponse) -> None:
        """Store/replace a single QueryResponse object.

        Args:
            response (QueryResponse):
                The object to store.
        """
        key = f"{response.name}{self._separator}{response.workflow.value}"
        self._content[key] = response

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


class InMemoryMapProviderV2(StarmapProvider):
    """Provide in memory (RAM) QueryResponseContainer objects for APIv2."""

    api = "v2"

    def __init__(self, container: QueryResponseContainer, *args, **kwargs) -> None:
        """Crete a new InMemoryMapProvider object.

        Args:
            container (QueryResponseContainer)
                QueryResponseContainer object to load into memory. It will be
                used by query to return the correct response based on name
                and workflow.
        """
        self._container = container
        super(StarmapProvider, self).__init__()

    def query(self, params: Dict[str, Any]) -> Optional[QueryResponseContainer]:
        """Retrieve the mapping without using the server.

        It relies in the local provider to retrieve the correct mappings
        according to the parameters.

        Args:
            params (dict):
                The request params to retrieve the mapping.
        Returns:
            The requested container with mappings when found.
        """
        filter_params = {"name": params.get("name") or get_image_name(params.get("image"))}
        for k in ["cloud", "workflow"]:
            v = params.get(k)
            if v:
                filter_params.update({k: v})
        res = self._container.filter_by(**filter_params)
        if res:
            return QueryResponseContainer(res)
        return None

    def list_content(self) -> List[QueryResponseEntity]:
        """Return a the responses stored in the container."""
        return self._container.responses

    def store(self, response: QueryResponseEntity) -> None:
        """Store a single response into the local provider's container.

        Args:
            container (container):
                The container to store.
        """
        self._container.responses.append(response)
