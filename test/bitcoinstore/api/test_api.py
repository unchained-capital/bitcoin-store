from flask import url_for

from lib.test import ViewTestMixin


class TestApi(ViewTestMixin):
    def test_up_page(self):
        """ Up page should respond with a success 200. """
        response = self.client.get(url_for("api/v1.up"))

        assert response.status_code == 200
