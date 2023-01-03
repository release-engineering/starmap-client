# SPDX-License-Identifier: GPL-3.0-or-later
import logging
from typing import Any, Dict

import requests

log = logging.getLogger(__name__)


class StarmapSession(object):
    """Implement a HTTP(S) session with StArMap."""

    def __init__(self, url: str, api_version: str):
        """
        Create the StarmapSession object.

        Args:
            url (str): The StArMap server endpoint base URL
            api_version: The StArMap server API version to call
        """
        self.url = url
        self.api_version = api_version

    def _request(self, method: str, path: str, **kwargs) -> requests.Response:
        """Perform a generic request on StArMap."""
        headers = {
            "Accept": "application/json",
        }

        log.info(f"Sending a {method} request to {path}")
        url_elements = [self.url, f"/api/{self.api_version}", path]
        url = "/".join(arg.strip("/") for arg in url_elements)

        return requests.request(method, url=url, headers=headers, **kwargs)

    def get(self, path: str, **kwargs) -> requests.Response:
        """Perform a GET request on StArMap."""
        return self._request("get", path, **kwargs)

    def post(self, path: str, json: Dict[str, Any], **kwargs) -> requests.Response:
        """Perform a POST request on StArMap."""
        return self._request("post", path, json=json, **kwargs)

    def put(self, path: str, json: Dict[str, Any], **kwargs) -> requests.Response:
        """Perform a PUT request on StArMap."""
        return self._request("put", path, json=json, **kwargs)
