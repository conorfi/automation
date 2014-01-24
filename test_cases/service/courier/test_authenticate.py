"""
Authentication integration tests
"""
import requests
from nose.plugins.attrib import attr

from . import ApiTestCase


class AuthenticateTestCase(ApiTestCase):

    @attr(env=['test'], priority=1)
    def test_authenticate_success(self):
        """
        COURIER_AUTHENTICATE_API_001 test_authenticate_success

        Authenticate a user created directly in the DB.
        """
        user, session = self.login_random_user()
        self.service.users.remove(user)

    @attr(env=['test'], priority=1)
    def test_authenticate_fail(self):
        """
        COURIER_AUTHENTICATE_API_002 test_authenticate_fail

        Attempt authentication of a user not in the DB.
        """
        response, session = self.service.authenticate('nonexistent',
                                                      'nonexistent')

        self.assertTrue(session is None)
        self.assertEqual(response.status_code, requests.codes.ok)
