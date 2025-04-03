from typing import Any, Dict, List, Optional

from starmap_client.models import QueryResponseContainer, QueryResponseEntity
from starmap_client.providers.base import StarmapProvider
from starmap_client.providers.utils import get_image_name


class InMemoryMapProviderV2(StarmapProvider[QueryResponseContainer, QueryResponseEntity]):
    """Provide in memory (RAM) QueryResponseContainer objects for APIv2."""

    api = "v2"

    def __init__(self, container: QueryResponseContainer, *args: None, **kwargs: None) -> None:
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
