"""
Integration tests for user API
"""
import requests
from nose.plugins.attrib import attr

from . import ApiTestCase
from framework.db.model.courier import User

_TEST_COUNT = 0


class UserApiTestCase(ApiTestCase):

    def shortDescription(self):
        global _TEST_COUNT
        _TEST_COUNT += 1
        return ('COURIER_USER_API_%03d %s' %
                (_TEST_COUNT, self.id().split('.')[-1]))

    @attr(env=['test'], priority=1)
    def test_list_success(self):
        """
        Return list of users successfully
        """
        login_user, session = self.login_random_user()
        users = {}
        for index in range(2):
            user = self.service.create_random_user()
            users[user.user_id] = user

        response = self.service.resource_request('user', session=session)

        self.assertResponseSuccess(response)
        json_data = response.json()
        self.assertIsInstance(json_data.get('data'), list)
        for user_data in json_data['data']:
            user = users.get(user_data['id'])
            if user is not None:
                self.assertUserData(user.to_data(), user_data)

        self.service.remove_user(login_user)
        for user in users.itervalues():
            self.service.remove_user(user)

    @attr(env=['test'], priority=1)
    def test_read_success(self):
        """
        Return data for one user successfully.
        """
        login_user, session = self.login_random_user()
        user = self.service.create_random_user()

        response = self.service.resource_request(
            'user', parameters={'user_id': user.user_id}, session=session)

        self.assertResponseSuccess(response)
        json_data = response.json()
        user_data = json_data.get('data')
        self.assertUserData(user.to_data(), user_data)

        self.service.remove_user(login_user)
        self.service.remove_user(user)

    @attr(env=['test'], priority=1)
    def test_read_fail(self):
        """
        Negative test for missing user ID
        """
        login_user, session = self.login_random_user()

        response = self.service.resource_request(
            'user', parameters={'user_id': 45}, session=session)

        self.assertResponseFail(response)

        self.service.remove_user(login_user)

    @attr(env=['test'], priority=1)
    def test_read_fail_invalid(self):
        """
        Negative test for invalid user ID
        """
        login_user, session = self.login_random_user()

        response = self.service.resource_request(
            'user', parameters={'user_id': 'invalid'}, session=session)

        self.assertResponseFail(response)

        self.service.remove_user(login_user)

    @attr(env=['test'], priority=1)
    def test_create_success(self):
        """
        Test user creation successfully
        """
        login_user, session = self.login_random_user()
        group = self.service.create_random_group()
        # BUG: group_id is required for the POST, though it is not used if
        # user being created is admin
        user = self.service.generate_user(group_id=group.group_id)

        response = self.service.resource_request(
            'user', method='post', data=user.to_request_data(),
            session=session)

        self.assertResponseSuccess(response)
        json_data = response.json()
        user_data = json_data.get('data')
        self.assertEqual({}, user_data)
        # BUG: verify change occurred via DB check since response body doesn't
        # give updated data
        db_user = self.dao.read_user(user)
        # admin user never has group ID, even if passed
        self.assertTrue(db_user.group_id is None)

        self.service.remove_user(login_user)
        self.service.remove_group(group)
        self.service.remove_user(user)

    @attr(env=['test'], priority=1)
    def test_create_success_standard(self):
        """
        Test standard user creation successfully
        """
        login_user, session = self.login_random_user()
        group = self.service.create_random_group()
        user = self.service.generate_user(level=User.LEVEL_STANDARD,
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
        db_user = self.dao.read_user(user)
        # standard user has group ID
        self.assertEqual(db_user.group_id, user.group_id)

        self.service.remove_user(login_user)
        self.service.remove_group(group)
        self.service.remove_user(user)

    @attr(env=['test'], priority=1)
    def test_create_fail_missingdata(self):
        """
        Negative test to show user creation not possible with missing data
        """
        login_user, session = self.login_random_user()
        group = self.service.create_random_group()
        user = self.service.generate_user(group_id=group.group_id)
        user.username = None

        response = self.service.resource_request(
            'user', method='post', data=user.to_request_data(),
            session=session)

        self.assertEqual(response.status_code, requests.codes.not_found)

        self.service.remove_user(login_user)
        self.service.remove_group(group)

    @attr(env=['test'], priority=1)
    def test_create_fail_invaliddata(self):
        """
        Negative test to show user creation not possible with invalid data
        """
        login_user, session = self.login_random_user()
        group = self.service.create_random_group()
        user = self.service.generate_user(group_id=group.group_id)
        user.username = self.util.random_str(101)

        response = self.service.resource_request(
            'user', method='post', data=user.to_request_data(),
            session=session)

        self.assertResponseFail(response)

        self.service.remove_user(login_user)
        self.service.remove_group(group)

    @attr(env=['test'], priority=1)
    def test_create_fail_permissions(self):
        """
        Negative test to show user creation not possible with standard user
        """
        login_user, session = self.login_random_user(level=User.LEVEL_STANDARD)
        group = self.service.create_random_group()
        user = self.service.generate_user(group_id=group.group_id)

        response = self.service.resource_request(
            'user', method='post', data=user.to_request_data(),
            session=session)

        self.assertEqual(response.status_code, requests.codes.forbidden)

        self.service.remove_user(login_user)
        self.service.remove_group(group)

    @attr(env=['test'], priority=1)
    def test_update_success(self):
        """
        Test user update is successful.
        """
        login_user, session = self.login_random_user()
        group = self.service.create_random_group()
        user = self.service.create_random_user(
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
        db_user = self.dao.read_user(user)
        self.assertEqual(user.username, db_user.username)

        self.service.remove_user(login_user)
        self.service.remove_group(group)
        self.service.remove_user(user)

    @attr(env=['test'], priority=1)
    def test_update_fail_missingdata(self):
        """
        Negative test to show user update not possible with missing data
        """
        login_user, session = self.login_random_user()
        user = self.service.create_random_user()

        response = self.service.resource_request(
            'user', method='post', data=user.to_request_data(),
            session=session)

        self.assertEqual(response.status_code, requests.codes.not_found)

        self.service.remove_user(login_user)
        self.service.remove_user(user)

    @attr(env=['test'], priority=1)
    def test_update_fail_invaliddata(self):
        """
        Negative test to show user update not possible with invalid data
        """
        login_user, session = self.login_random_user()
        group = self.service.create_random_group()
        user = self.service.create_random_user(group_id=group.group_id)
        user.username = self.util.random_str(101)

        response = self.service.resource_request(
            'user', method='post', data=user.to_request_data(),
            session=session)

        self.assertResponseFail(response)

        self.service.remove_user(login_user)
        self.service.remove_group(group)
        self.service.remove_user(user)

    @attr(env=['test'], priority=1)
    def test_delete_success(self):
        """
        Test user deletion successfully
        """
        login_user, session = self.login_random_user()
        group = self.service.create_random_group()
        user = self.service.create_random_user(group_id=group.group_id)

        response = self.service.resource_request(
            'user', method='delete', parameters={'user_id': user.user_id},
            session=session)

        self.assertResponseSuccess(response)
        db_user = self.dao.read_user(user)
        self.assertEqual(None, db_user)

        self.service.remove_user(login_user)
        self.service.remove_group(group)

    @attr(env=['test'], priority=1)
    def test_delete_fail_missingdata(self):
        """
        Test user deletion successfully
        """
        login_user, session = self.login_random_user()
        group = self.service.create_random_group()
        user = self.service.create_random_user(group_id=group.group_id)

        response = self.service.resource_request(
            'user', method='delete', session=session)

        self.assertEqual(response.status_code, requests.codes.not_found)

        self.service.remove_user(login_user)
        self.service.remove_group(group)
        self.service.remove_user(user)
