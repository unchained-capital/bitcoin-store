from flask import url_for
from lib.test import ViewTestMixin


class TestApiV1(ViewTestMixin):
    def test_up_api(self):
        """Up api should respond with a success 200."""
        response = self.client.get(url_for("api.up"))

        assert response.status_code == 200
