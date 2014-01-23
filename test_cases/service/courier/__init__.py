"""
Common test case functionality for the Courier service.
"""
import requests
import testy as unittest
from testconfig import config

from framework.utility.utility import Utility
from framework.db.base_dao import BaseDAO
from framework.service.courier import CourierService, SERVICE_NAME
from framework.db.courier import CourierDao
from framework.db.model.courier import User
from framework.db.model import Tablify


class ApiTestCase(unittest.TestCase):

    SERVICE_NAME = SERVICE_NAME

    @classmethod
    def setUpClass(cls):
        cls.db = BaseDAO(config[SERVICE_NAME]['db']['connection'])

    @classmethod
    def tearDownClass(cls):
        cls.db.close()

    def setUp(self):
        super(ApiTestCase, self).setUp()
        self.tablify = Tablify()
        self.dao = CourierDao(self.db, self.tablify)
        self.service = CourierService(self.dao)
        self.util = Utility()

    def login_random_user(self, level=User.LEVEL_ADMIN):
        """
        Creates a random user and authenticates them on the service.
        Returns the newly created user object and the associated session.
        """
        user = self.service.create_random_user(level=level)
        response, session = self.service.authenticate(user.username,
                                                      user.password)
        self.assertTrue(session is not None)
        self.assertEqual(response.status_code, requests.codes.ok)
        return user, session

    def assertDictContains(self, data, key, message=None):
        """
        Asserts that the given data is a dict and contains the given key.

        :param data:
        :param key:
        """
        self.assertIsInstance(data, dict, message)
        if message is None:
            message = 'Data does not contain "%s"' % key
        self.assertTrue(key in data, message)

    def assertResponseSuccess(self, response):
        """
        Asserts that the given response is OK and has JSON payload in the
        most common formats:
        {
            "data": <some_data>
            "messages": [
                {
                    <some_more_data>
                    "type": "success"
                }
            ]
        }

        OR

        {
            "data": <some_data>
            "messages": []
        }
        """
        self.assertEqual(response.status_code, requests.codes.ok,
                         'Invalid status code "%d"' % response.status_code)
        try:
            json_data = response.json()
        except ValueError:
            json_data = None
        self.assertTrue(json_data is not None, 'Response not in JSON format')
        messages = json_data.get('messages')
        self.assertIsInstance(messages, list,
                              'Messages non-existent or not list')
        if len(messages) > 0:
            self.assertEqual(len(messages), 1,
                             'Messages must be list of length 1')
            message = messages[0]
            self.assertIsInstance(message, dict, 'Message must be dict')
            # default to success if it doesn't exist
            type_message = message.get('type', 'success')
            self.assertEqual(type_message, 'success', 'Message type is error')

    def assertResponseFail(self, response):
        """
        Asserts that the given response is OK and has JSON payload in the
        most common format:
        {
            "data": <some_data>
            "messages": [
                {
                    <some_more_data>
                    "type": "error"
                }
            ]
        }
        """
        self.assertEqual(response.status_code, requests.codes.ok,
                         'Invalid status code "%d"' % response.status_code)
        try:
            json_data = response.json()
        except ValueError:
            json_data = None
        self.assertTrue(json_data is not None, 'Response not in JSON format')
        messages = json_data.get('messages')
        self.assertIsInstance(messages, list,
                              'Messages non-existent or not list')
        self.assertEqual(len(messages), 1,
                         'Messages must be list of length 1')
        message = messages[0]
        self.assertIsInstance(message, dict, 'Message must be dict')
        # default to success if it doesn't exist
        type_message = message.get('type', 'success')
        self.assertEqual(type_message, 'error', 'Message type is success')

    def assertGroupData(self, expected_data, actual_data):
        """
        Asserts that the given expected group data matches the actual group
        data.
        """
        self.assertDictContains(actual_data, 'name')
        self.assertEqual(expected_data['name'], actual_data['name'])
        self.assertDictContains(actual_data, 'upload_credentials')
        self.assertEqual(expected_data['upload_credentials'],
                         actual_data['upload_credentials'])

    def assertClientData(self, expected_data, actual_data):
        """
        Asserts that the given expected client data matches the actual group
        data.
        """
        self.assertDictContains(actual_data, 'name')
        self.assertEqual(expected_data['name'], actual_data['name'])
