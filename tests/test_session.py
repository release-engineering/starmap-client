from unittest import TestCase, mock

from starmap_client.session import StarmapSession


class TestStarmapSession(TestCase):
    def setUp(self):
        self.starmap_url = "test.starmap.com"
        self.starmap_api_version = "v1"
        self.session = StarmapSession(url=self.starmap_url, api_version=self.starmap_api_version)

    def _assert_requested_with(self, mock_requests, method, path, **kwargs):
        headers = {
            "Accept": "application/json",
        }

        mock_requests.request.assert_called_once_with(
            method,
            url=f"{self.starmap_url}/api/{self.starmap_api_version}/{path}",
            headers=headers,
            **kwargs,
        )

    @mock.patch("starmap_client.session.requests")
    def test_get_request(self, mock_requests: mock.MagicMock):
        self.session.get("/foo")
        self._assert_requested_with(mock_requests, method="get", path="foo")

    @mock.patch("starmap_client.session.requests")
    def test_post_request(self, mock_requests: mock.MagicMock):
        data = {"foo": "bar"}
        self.session.post("/foo", json=data)
        self._assert_requested_with(mock_requests, method="post", path="foo", json=data)

    @mock.patch("starmap_client.session.requests")
    def test_put_request(self, mock_requests: mock.MagicMock):
        data = {"foo": "bar"}
        self.session.put("/foo", json=data)
        self._assert_requested_with(mock_requests, method="put", path="foo", json=data)
