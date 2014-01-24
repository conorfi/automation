"""
Integration tests for client API
"""
import requests
from nose.plugins.attrib import attr

from . import ApiTestCase
from framework.db.model.courier import Client


class ClientApiTestCase(ApiTestCase):

    @attr(env=['test'], priority=1)
    def test_read_success(self):
        """
        COURIER_CLIENT_API_001 test_read_success

        Return data for one client successfully.
        """
        user, session = self.login_random_user()
        client = self.service.create_random_client()

        response = self.service.resource_request(
            'client', parameters={'client_uuid': client.client_uuid},
            session=session)

        self.assertResponseSuccess(response)
        json_data = response.json()
        client_data = json_data.get('data')
        self.assertClientData(client.to_response_data(), client_data)
