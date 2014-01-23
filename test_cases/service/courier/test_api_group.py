"""
Integration tests for group API
"""
import requests
from nose.plugins.attrib import attr

from . import ApiTestCase


class GroupApiTestCase(ApiTestCase):

    @attr(env=['test'], priority=1)
    def test_list_success(self):
        """
        COURIER_GROUP_API_001 test_list_success

        Return list of groups successfully
        """
        user, session = self.login_random_user()
        groups = {}
        for index in range(2):
            group = self.service.create_random_group()
            groups[group.group_id] = group

        response = self.service.resource_request('group', session=session)

        self.assertResponseSuccess(response)
        json_data = response.json()
        self.assertIsInstance(json_data.get('data'), list)
        for group_data in json_data['data']:
            group = groups.get(group_data['id'])
            if group is not None:
                self.assertDictContains(group_data, 'name')
                self.assertEqual(group_data['name'], group.name)
                self.assertDictContains(group_data, 'upload_credentials')
                self.assertEqual(group_data['upload_credentials'],
                                 group.upload_credentials)

        self.service.remove_user(user)
        for group in groups.itervalues():
            self.service.remove_group(group)
