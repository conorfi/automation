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
        user_data = self.service.create_random_user()

        response, session = self.service.authenticate(user_data['username'],
                                                      user_data['password'])

        self.assertTrue(session is not None)
        self.assertEqual(response.status_code, requests.codes.ok)

        self.service.remove_user(user_data)

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
