"""
Integration tests for client API
"""
import requests
from nose.plugins.attrib import attr

from . import ApiTestCase
from framework.db.model.courier import User


class ClientApiTestCase(ApiTestCase):

    @attr(env=['test'], priority=1)
    def test_list_success(self):
        """
        COURIER_CLIENT_API_001 test_list_success

        Return list of clients successfully
        """
        user, session = self.login_random_user()
        clients = {}
        for index in range(2):
            client = self.service.clients.create_random()
            clients[client.client_uuid] = client

        response = self.service.resource_request('client', session=session)

        self.assertResponseSuccess(response)
        json_data = response.json()
        self.assertIsInstance(json_data.get('data'), list)
        for client_data in json_data['data']:
            client = clients.get(client_data['uuid'])
            if client is not None:
                self.assertClientData(client.to_response_data(), client_data)

    @attr(env=['test'], priority=1)
    def test_list_success_empty(self):
        """
        COURIER_CLIENT_API_002 test_list_success_empty

        Return empty list of clients successfully
        """
        user, session = self.login_random_user()

        response = self.service.resource_request('client', session=session)

        self.assertResponseSuccess(response)
        json_data = response.json()
        data = json_data.get('data')
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 0)

    @attr(env=['test'], priority=1)
    def test_read_success(self):
        """
        COURIER_CLIENT_API_003 test_read_success

        Return data for one client successfully.
        """
        user, session = self.login_random_user()
        client = self.service.clients.create_random()

        response = self.service.resource_request(
            'client', parameters={'client_uuid': client.client_uuid},
            session=session
        )

        self.assertResponseSuccess(response)
        json_data = response.json()
        client_data = json_data.get('data')
        self.assertClientData(client.to_response_data(), client_data)

    @attr(env=['test'], priority=1)
    def test_read_fail(self):
        """
        COURIER_CLIENT_API_004 test_read_fail

        Negative test when client ID doesn't exist
        """
        user, session = self.login_random_user()

        response = self.service.resource_request(
            'client', parameters={'client_uuid': 33}, session=session)

        self.assertResponseFail(response)

    @attr(env=['test'], priority=1)
    def test_read_fail_invalid(self):
        """
        COURIER_CLIENT_API_005 test_read_fail_invalid

        Negative test when client ID is invalid
        """
        user, session = self.login_random_user()

        response = self.service.resource_request(
            'client', parameters={'client_uuid': 'notaninteger'},
            session=session
        )

        self.assertResponseFail(response)

    @attr(env=['test'], priority=1)
    def test_update_success(self):
        """
        COURIER_CLIENT_API_006 test_update_success

        Test client update is successful.
        """
        login_user, session = self.login_random_user()
        group = self.service.groups.create_random()
        client = self.service.clients.create_random(name='oldname',
                                                    group_id=group.group_id)
        client.name = 'newname'

        response = self.service.resource_request(
            'client', method='post', data=client.to_request_data(),
            session=session)

        self.assertResponseSuccess(response)
        json_data = response.json()
        client_data = json_data.get('data')
        self.assertEqual({}, client_data)
        # verify change occurred via DB check since response body doesn't give
        # updated data
        db_client = self.dao.clients.read(client)
        self.assertEqual(client.name, db_client.name)

        client.name = 'oldname'
