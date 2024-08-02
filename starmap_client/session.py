# SPDX-License-Identifier: GPL-3.0-or-later
import logging
import re
from abc import ABC, abstractmethod
from typing import Any, Dict

import requests
import requests_mock
from requests.adapters import HTTPAdapter, Retry

log = logging.getLogger(__name__)


class StarmapBaseSession(ABC):
    """Define the interface for the Starmap's session objects."""

    @abstractmethod
    def get(self, path: str, **kwargs) -> requests.Response:
        """Perform a GET request on StArMap."""

    @abstractmethod
    def post(self, path: str, json: Dict[str, Any], **kwargs) -> requests.Response:
        """Perform a POST request on StArMap."""

    @abstractmethod
    def put(self, path: str, json: Dict[str, Any], **kwargs) -> requests.Response:
        """Perform a PUT request on StArMap."""


class StarmapSession(StarmapBaseSession):
    """Implement a HTTP(S) session with StArMap."""

    def __init__(
        self,
        url: str,
        api_version: str,
        retries: int = 3,
        backoff_factor: float = 2.0,
    ):
        """
        Create the StarmapSession object.

        Args:
            url (str)
                The StArMap server endpoint base URL
            api_version
                The StArMap server API version to call
            retries (int, optional)
                The number of request retries on failure
            backoff_factor (float, optional)
                The backoff factor to apply between attempts after the second try
        """
        super(StarmapSession, self).__init__()
        self.url = url
        self.api_version = api_version
        self.session = requests.Session()
        retry = Retry(
            total=retries,
            read=retries,
            connect=retries,
            backoff_factor=backoff_factor,
            status_forcelist=set(range(500, 512)),
        )
        adapter = HTTPAdapter(max_retries=retry)
        self.session.mount("https://", adapter)
        self.verify = True

    def _request(self, method: str, path: str, **kwargs) -> requests.Response:
        """Perform a generic request on StArMap."""
        headers = {
            "Accept": "application/json",
        }

        log.info(f"Sending a {method} request to {path}")
        url_elements = [self.url, f"/api/{self.api_version}", path]
        url = "/".join(arg.strip("/") for arg in url_elements)

        return self.session.request(method, url=url, headers=headers, verify=self.verify, **kwargs)

    def get(self, path: str, **kwargs) -> requests.Response:
        """Perform a GET request on StArMap."""
        return self._request("get", path, **kwargs)

    def post(self, path: str, json: Dict[str, Any], **kwargs) -> requests.Response:
        """Perform a POST request on StArMap."""
        return self._request("post", path, json=json, **kwargs)

    def put(self, path: str, json: Dict[str, Any], **kwargs) -> requests.Response:
        """Perform a PUT request on StArMap."""
        return self._request("put", path, json=json, **kwargs)


class StarmapMockSession(StarmapSession):
    """Implement a mock session with predefined responses."""

    def __init__(self, url: str, api_version: str, status_code: int = 404, json_data: Any = None):
        """Create the StarmapMockSession object.

        Args:
            url (str)
                The mock server endpoint base URL
            api_version
                The mock server API version to call
            status_code (optional, int)
                The status code to return on each request

            json_data (optional, any)
                The JSON data to return on each request
        """
        super(StarmapMockSession, self).__init__(url, api_version)
        self.url = f"mock://{url}"
        self.api_version = api_version
        self.status_code = status_code
        self.json_data = json_data or {}
        self.session = requests.Session()
        self.adapter = requests_mock.Adapter()
        self.session.mount("mock://", self.adapter)
        self._register_starmap_endpoints()

    def _register_starmap_endpoints(self) -> None:
        base_url_elements = [self.url, f"/api/{self.api_version}"]
        base_url = "/".join(arg.strip("/") for arg in base_url_elements)
        methods = ["GET", "POST", "PUT"]
        for m in methods:
            self.register_uri(m, re.compile(f"{base_url}/.*"))  # type: ignore [arg-type]

    def register_uri(self, method: str, uri: str):
        """Register an URI into the ``requests_mock`` adapter.

        Args:
            method (str):
                The HTTP method to register
            uri:
                The URI to register
        """
        self.adapter.register_uri(
            method, url=uri, status_code=self.status_code, json=self.json_data
        )
