from unittest import TestCase, mock

from starmap_client.session import StarmapSession


class TestStarmapSession(TestCase):
    def setUp(self):
        self.starmap_url = "test.starmap.com"
        self.starmap_api_version = "v1"
        self.session = StarmapSession(url=self.starmap_url, api_version=self.starmap_api_version)

        # Mock requests.Session()
        self.mock_requests = mock.patch.object(self.session, 'session').start()

    def _assert_requested_with(self, method, path, **kwargs):
        headers = {
            "Accept": "application/json",
        }

        self.mock_requests.request.assert_called_once_with(
            method,
            url=f"{self.starmap_url}/api/{self.starmap_api_version}/{path}",
            headers=headers,
            verify=True,
            **kwargs,
        )

    def test_get_request(self):
        self.session.get("/foo")
        self._assert_requested_with(method="get", path="foo")

    def test_post_request(self):
        data = {"foo": "bar"}
        self.session.post("/foo", json=data)
        self._assert_requested_with(method="post", path="foo", json=data)

    def test_put_request(self):
        data = {"foo": "bar"}
        self.session.put("/foo", json=data)
        self._assert_requested_with(method="put", path="foo", json=data)
