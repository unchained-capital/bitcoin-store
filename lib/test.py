import pytest


class ApiTestMixin(object):
    """
    Automatically load in a session and client..
    """

    @pytest.fixture(autouse=True)
    def set_common_fixtures(self, session, client, db):
        self.session = session
        self.client = client
        self.db = db


class ViewTestMixin(object):
    """
    Automatically load in a session and client, this is common for a lot of
    tests that work with views.
    """

    @pytest.fixture(autouse=True)
    def set_common_fixtures(self, session, client):
        self.session = session
        self.client = client
