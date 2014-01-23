"""
Integration tests for group API
"""
import requests
from nose.plugins.attrib import attr

from . import ApiTestCase
from framework.db.model.courier import User


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
                self.assertGroupData(group.to_data(), group_data)

        self.service.remove_user(user)
        for group in groups.itervalues():
            self.service.remove_group(group)

    @attr(env=['test'], priority=1)
    def test_list_success_empty(self):
        """
        COURIER_GROUP_API_002 test_list_success_empty

        Return empty list of groups successfully
        """
        user, session = self.login_random_user()

        response = self.service.resource_request('group', session=session)

        self.assertResponseSuccess(response)
        json_data = response.json()
        data = json_data.get('data')
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 0)

        self.service.remove_user(user)

    @attr(env=['test'], priority=1)
    def test_read_success(self):
        """
        COURIER_GROUP_API_003 test_read_success

        Return data for one group successfully.
        """
        user, session = self.login_random_user()
        group = self.service.create_random_group()

        response = self.service.resource_request(
            'group', parameters={'group_id': group.group_id}, session=session)

        self.assertResponseSuccess(response)
        json_data = response.json()
        group_data = json_data.get('data')
        self.assertGroupData(group.to_data(), group_data)

        self.service.remove_user(user)
        self.service.remove_group(group)

    @attr(env=['test'], priority=1)
    def test_read_fail(self):
        """
        COURIER_GROUP_API_004 test_read_fail

        Negative test when group ID doesn't exist
        """
        user, session = self.login_random_user()

        response = self.service.resource_request(
            'group', parameters={'group_id': 33}, session=session)

        self.assertResponseFail(response)

        self.service.remove_user(user)

    @attr(env=['test'], priority=1)
    def test_read_fail_invalid(self):
        """
        COURIER_GROUP_API_005 test_read_fail_invalid

        Negative test when group ID is invalid
        """
        user, session = self.login_random_user()

        response = self.service.resource_request(
            'group', parameters={'group_id': 'notaninteger'}, session=session)

        self.assertResponseFail(response)

        self.service.remove_user(user)

    @attr(env=['test'], priority=1)
    def test_create_success(self):
        """
        COURIER_GROUP_API_006 test_create_success

        Successful test when creating group via API
        """
        user, session = self.login_random_user()
        group = self.service.generate_group()

        response = self.service.resource_request(
            'group', method='post', data=group.to_post_data(), session=session)

        self.assertResponseSuccess(response)
        json_data = response.json()
        group_data = json_data.get('data')
        self.assertGroupData(group.to_post_data(), group_data)

        self.service.remove_user(user)
        self.service.remove_group(group)

    @attr(env=['test'], priority=1)
    def test_create_fail_empty(self):
        """
        COURIER_GROUP_API_007 test_create_fail_empty

        Negative test when giving no group data
        """
        user, session = self.login_random_user()
        group = self.service.generate_group()
        group.name = None

        response = self.service.resource_request(
            'group', method='post', data=group.to_post_data(), session=session)

        self.assertResponseFail(response)

        self.service.remove_user(user)

    @attr(env=['test'], priority=1)
    def test_create_fail_invalidname(self):
        """
        COURIER_GROUP_API_008 test_create_fail_invalidname

        Negative test when sending invalid group name
        """
        user, session = self.login_random_user()
        group = self.service.generate_group(name=self.util.random_str(51))

        response = self.service.resource_request(
            'group', method='post', data=group.to_post_data(), session=session)

        self.assertResponseFail(response)

        self.service.remove_user(user)

    @attr(env=['test'], priority=1)
    def test_create_fail_permissions(self):
        """
        COURIER_GROUP_API_009 test_create_fail_permissions

        Negative test when attempting create with non-admin user
        """
        user, session = self.login_random_user(level=User.LEVEL_STANDARD)
        group = self.service.generate_group(name=self.util.random_str(51))

        response = self.service.resource_request(
            'group', method='post', data=group.to_post_data(), session=session)

        self.assertEqual(response.status_code, requests.codes.forbidden)

        self.service.remove_user(user)

    @attr(env=['test'], priority=1)
    def test_update_success(self):
        """
        COURIER_GROUP_API_010 test_update_success

        Successful test when updating group via API
        """
        user, session = self.login_random_user()
        group = self.service.create_random_group(name='oldname')
        group.name = 'newname'

        response = self.service.resource_request(
            'group', method='post', data=group.to_post_data(), session=session)

        self.assertResponseSuccess(response)
        json_data = response.json()
        group_data = json_data.get('data')
        self.assertGroupData(group.to_post_data(), group_data)

        self.service.remove_user(user)
        self.service.remove_group(group)

    @attr(env=['test'], priority=1)
    def test_update_success_awscredentials(self):
        """
        COURIER_GROUP_API_011 test_update_success_awscredentials

        Successful test when updating group with credentials via API
        """
        user, session = self.login_random_user()
        credentials = self.service.generate_group_credentials()
        group = self.service.create_random_group(name='oldname',
                                                 credentials=credentials)
        group.name = 'newname'
        group.upload_credentials = \
            self.service.generate_group_credentials(public_key='totallyrandom')

        response = self.service.resource_request(
            'group', method='post', data=group.to_post_data(), session=session)

        self.assertResponseSuccess(response)
        json_data = response.json()
        group_data = json_data.get('data')
        self.assertGroupData(group.to_post_data(), group_data)

        self.service.remove_user(user)
        self.service.remove_group(group)

    @attr(env=['test'], priority=1)
    def test_update_fail_empty(self):
        """
        COURIER_GROUP_API_012 test_update_fail_empty

        Negative test when updating group via API with no data
        """
        user, session = self.login_random_user()
        group = self.service.create_random_group()
        old_name = group.name
        group.name = None

        response = self.service.resource_request(
            'group', method='post', data=group.to_post_data(), session=session)

        self.assertResponseFail(response)

        group.name = old_name
        self.service.remove_user(user)
        self.service.remove_group(group)

    @attr(env=['test'], priority=1)
    def test_update_fail_invalidname(self):
        """
        COURIER_GROUP_API_013 test_update_fail_invalidname

        Negative test when updating group via API with no data
        """
        user, session = self.login_random_user()
        group = self.service.create_random_group()
        old_name = group.name
        group.name = None

        response = self.service.resource_request(
            'group', method='post', data=group.to_post_data(), session=session)

        self.assertResponseFail(response)

        group.name = old_name
        self.service.remove_user(user)
        self.service.remove_group(group)

    @attr(env=['test'], priority=1)
    def test_update_fail_permissions(self):
        """
        COURIER_GROUP_API_014 test_update_fail_permissions

        Negative test when updating group via API with missing permissions
        """
        user, session = self.login_random_user(level=User.LEVEL_STANDARD)
        group = self.service.create_random_group()
        old_name = group.name
        group.name = None

        response = self.service.resource_request(
            'group', method='post', data=group.to_post_data(), session=session)

        self.assertEqual(response.status_code, requests.codes.forbidden)

        group.name = old_name
        self.service.remove_user(user)
        self.service.remove_group(group)

    @attr(env=['test'], priority=1)
    def test_delete_success(self):
        """
        COURIER_GROUP_API_015 test_delete_success

        Successful test when deleting group via API
        """
        user, session = self.login_random_user()
        group = self.service.create_random_group()

        self.assertTrue(self.service.group_exists(group))
        response = self.service.resource_request(
            'group', method='delete', parameters={'group_id': group.group_id},
            session=session)

        self.assertResponseSuccess(response)
        self.assertFalse(self.service.group_exists(group))

        self.service.remove_user(user)

    @attr(env=['test'], priority=1)
    def test_delete_fail(self):
        """
        COURIER_GROUP_API_016 test_delete_fail

        Negative test when deleting non-existent group via API
        """
        user, session = self.login_random_user()

        response = self.service.resource_request(
            'group', method='delete', parameters={'group_id': 44},
            session=session)

        self.assertResponseSuccess(response)

        self.service.remove_user(user)

    @attr(env=['test'], priority=1)
    def test_delete_fail_invalid(self):
        """
        COURIER_GROUP_API_017 test_delete_fail_invalid

        Negative test when deleting invalid group via API
        """
        user, session = self.login_random_user()

        response = self.service.resource_request(
            'group', method='delete', parameters={'group_id': 'wrong'},
            session=session)

        self.assertResponseFail(response)

        self.service.remove_user(user)

    @attr(env=['test'], priority=1)
    def test_delete_fail_permissions(self):
        """
        COURIER_GROUP_API_018 test_delete_fail_permissions

        Negative test when deleting invalid group via API
        """
        user, session = self.login_random_user(level=User.LEVEL_STANDARD)

        response = self.service.resource_request(
            'group', method='delete', parameters={'group_id': 22},
            session=session)

        self.assertEqual(response.status_code, requests.codes.forbidden)

        self.service.remove_user(user)
