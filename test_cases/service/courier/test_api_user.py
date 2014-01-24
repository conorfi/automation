"""
Integration tests for user API
"""
import requests
from nose.plugins.attrib import attr

from . import ApiTestCase
from framework.db.model.courier import User


class UserApiTestCase(ApiTestCase):

    @attr(env=['test'], priority=1)
    def test_list_success(self):
        """
        COURIER_USER_API_001 test_list_success

        Return list of users successfully
        """
        login_user, session = self.login_random_user()
        users = {}
        for index in range(2):
            user = self.service.users.create_random()
            users[user.user_id] = user

        response = self.service.resource_request('user', session=session)

        self.assertResponseSuccess(response)
        json_data = response.json()
        self.assertIsInstance(json_data.get('data'), list)
        for user_data in json_data['data']:
            user = users.get(user_data['id'])
            if user is not None:
                self.assertUserData(user.to_response_data(), user_data)

        self.service.users.remove(login_user)
        for user in users.itervalues():
            self.service.users.remove(user)

    @attr(env=['test'], priority=1)
    def test_read_success(self):
        """
        COURIER_USER_API_002 test_read_success

        Return data for one user successfully.
        """
        login_user, session = self.login_random_user()
        user = self.service.users.create_random()

        response = self.service.resource_request(
            'user', parameters={'user_id': user.user_id}, session=session)

        self.assertResponseSuccess(response)
        json_data = response.json()
        user_data = json_data.get('data')
        self.assertUserData(user.to_response_data(), user_data)

        self.service.users.remove(login_user)
        self.service.users.remove(user)

    @attr(env=['test'], priority=1)
    def test_read_fail(self):
        """
        COURIER_USER_API_003 test_read_fail

        Negative test for missing user ID
        """
        login_user, session = self.login_random_user()

        response = self.service.resource_request(
            'user', parameters={'user_id': 45}, session=session)

        self.assertResponseFail(response)

        self.service.users.remove(login_user)

    @attr(env=['test'], priority=1)
    def test_read_fail_invalid(self):
        """
        COURIER_USER_API_004 test_read_fail_invalid

        Negative test for invalid user ID
        """
        login_user, session = self.login_random_user()

        response = self.service.resource_request(
            'user', parameters={'user_id': 'invalid'}, session=session)

        self.assertResponseFail(response)

        self.service.users.remove(login_user)

    @attr(env=['test'], priority=1)
    def test_create_success(self):
        """
        COURIER_USER_API_005 test_create_success

        Test user creation successfully
        """
        login_user, session = self.login_random_user()
        group = self.service.groups.create_random()
        # BUG: group_id is required for the POST, though it is not used if
        # user being created is admin
        user = self.service.users.generate(group_id=group.group_id)

        response = self.service.resource_request(
            'user', method='post', data=user.to_request_data(),
            session=session)

        self.assertResponseSuccess(response)
        json_data = response.json()
        user_data = json_data.get('data')
        self.assertEqual({}, user_data)
        # BUG: verify change occurred via DB check since response body doesn't
        # give updated data
        db_user = self.dao.users.read(user)
        # admin user never has group ID, even if passed
        self.assertTrue(db_user.group_id is None)

        self.service.users.remove(login_user)
        self.service.groups.remove(group)
        self.service.users.remove(user)

    @attr(env=['test'], priority=1)
    def test_create_success_standard(self):
        """
        COURIER_USER_API_006 test_create_success_standard

        Test standard user creation successfully
        """
        login_user, session = self.login_random_user()
        group = self.service.groups.create_random()
        user = self.service.users.generate(level=User.LEVEL_STANDARD,
                                           group_id=group.group_id)

        response = self.service.resource_request(
            'user', method='post', data=user.to_request_data(),
            session=session)

        self.assertResponseSuccess(response)
        json_data = response.json()
        user_data = json_data.get('data')
        self.assertEqual({}, user_data)
        # verify change occurred via DB check since response body doesn't give
        # updated data
        db_user = self.dao.users.read(user)
        # standard user has group ID
        self.assertEqual(db_user.group_id, user.group_id)

        self.service.users.remove(login_user)
        self.service.groups.remove(group)
        self.service.users.remove(user)

    @attr(env=['test'], priority=1)
    def test_create_fail_missingdata(self):
        """
        COURIER_USER_API_007 test_create_fail_missingdata

        Negative test to show user creation not possible with missing data
        """
        login_user, session = self.login_random_user()
        group = self.service.groups.create_random()
        user = self.service.users.generate(group_id=group.group_id)
        user.username = None

        response = self.service.resource_request(
            'user', method='post', data=user.to_request_data(),
            session=session)

        self.assertEqual(response.status_code, requests.codes.not_found)

        self.service.users.remove(login_user)
        self.service.groups.remove(group)

    @attr(env=['test'], priority=1)
    def test_create_fail_extradata(self):
        """
        COURIER_USER_API_008 test_create_fail_extradata

        Negative test to show user creation not possible with extra post data
        """
        login_user, session = self.login_random_user()
        group = self.service.groups.create_random()
        user = self.service.users.generate(group_id=group.group_id)
        user_data = user.to_request_data()
        user_data['extra'] = self.util.random_str()

        response = self.service.resource_request(
            'user', method='post', data=user_data, session=session)

        self.assertEqual(response.status_code, requests.codes.bad_request)

        self.service.users.remove(login_user)
        self.service.groups.remove(group)

    @attr(env=['test'], priority=1)
    def test_create_fail_invaliddata(self):
        """
        COURIER_USER_API_009 test_create_fail_invaliddata

        Negative test to show user creation not possible with invalid data
        """
        login_user, session = self.login_random_user()
        group = self.service.groups.create_random()
        user = self.service.users.generate(group_id=group.group_id)
        user.username = self.util.random_str(101)

        response = self.service.resource_request(
            'user', method='post', data=user.to_request_data(),
            session=session)

        self.assertResponseFail(response)

        self.service.users.remove(login_user)
        self.service.groups.remove(group)

    @attr(env=['test'], priority=1)
    def test_create_fail_permissions(self):
        """
        COURIER_USER_API_010 test_create_fail_permissions

        Negative test to show user creation not possible with standard user
        """
        login_user, session = self.login_random_user(level=User.LEVEL_STANDARD)
        group = self.service.groups.create_random()
        user = self.service.users.generate(group_id=group.group_id)

        response = self.service.resource_request(
            'user', method='post', data=user.to_request_data(),
            session=session)

        self.assertEqual(response.status_code, requests.codes.forbidden)

        self.service.users.remove(login_user)
        self.service.groups.remove(group)

    @attr(env=['test'], priority=1)
    def test_update_success(self):
        """
        COURIER_USER_API_011 test_update_success

        Test user update is successful.
        """
        login_user, session = self.login_random_user()
        group = self.service.groups.create_random()
        user = self.service.users.create_random(
            username='oldname', group_id=group.group_id)
        user.username = 'newname'

        response = self.service.resource_request(
            'user', method='post', data=user.to_request_data(),
            session=session)

        self.assertResponseSuccess(response)
        json_data = response.json()
        user_data = json_data.get('data')
        self.assertEqual({}, user_data)
        # verify change occurred via DB check since response body doesn't give
        # updated data
        db_user = self.dao.users.read(user)
        self.assertEqual(user.username, db_user.username)

        self.service.users.remove(login_user)
        self.service.groups.remove(group)
        self.service.users.remove(user)

    @attr(env=['test'], priority=1)
    def test_update_fail_missingdata(self):
        """
        COURIER_USER_API_012 test_update_fail_missingdata

        Negative test to show user update not possible with missing data
        """
        login_user, session = self.login_random_user()
        user = self.service.users.create_random()

        response = self.service.resource_request(
            'user', method='post', data=user.to_request_data(),
            session=session)

        self.assertEqual(response.status_code, requests.codes.not_found)

        self.service.users.remove(login_user)
        self.service.users.remove(user)

    @attr(env=['test'], priority=1)
    def test_update_fail_invaliddata(self):
        """
        COURIER_USER_API_013 test_update_fail_invaliddata

        Negative test to show user update not possible with invalid data
        """
        login_user, session = self.login_random_user()
        group = self.service.groups.create_random()
        user = self.service.users.create_random(group_id=group.group_id)
        user.username = self.util.random_str(101)

        response = self.service.resource_request(
            'user', method='post', data=user.to_request_data(),
            session=session)

        self.assertResponseFail(response)

        self.service.users.remove(login_user)
        self.service.groups.remove(group)
        self.service.users.remove(user)

    @attr(env=['test'], priority=1)
    def test_delete_success(self):
        """
        COURIER_USER_API_014 test_delete_success

        Test user deletion successfully
        """
        login_user, session = self.login_random_user()
        group = self.service.groups.create_random()
        user = self.service.users.create_random(group_id=group.group_id)

        response = self.service.resource_request(
            'user', method='delete', parameters={'user_id': user.user_id},
            session=session)

        self.assertResponseSuccess(response)
        db_user = self.dao.users.read(user)
        self.assertEqual(None, db_user)

        self.service.users.remove(login_user)
        self.service.groups.remove(group)

    @attr(env=['test'], priority=1)
    def test_delete_fail_missingdata(self):
        """
        COURIER_USER_API_015 test_delete_fail_missingdata

        Test user deletion successfully
        """
        login_user, session = self.login_random_user()
        group = self.service.groups.create_random()
        user = self.service.users.create_random(group_id=group.group_id)

        response = self.service.resource_request(
            'user', method='delete', session=session)

        self.assertEqual(response.status_code, requests.codes.not_found)

        self.service.users.remove(login_user)
        self.service.groups.remove(group)
        self.service.users.remove(user)
