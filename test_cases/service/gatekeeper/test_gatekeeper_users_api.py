"""
@summary: Contains a set of test cases for the users API of the
gatekeeper(single sign on) project
Note: only 1 factor authentication test cases

These test have a number of dependencies
1. the database update script updates the gatekeepr schema - the script can be
found at the root of the gatekeeper app
2. the build script starts the gatekeeper app with ssl enbaled by default
3. the build script starts the dummy app with ssl enabled
and application_name is adfuser
@since: Created on 4th January 2014
@author: Conor Fitzgerald
"""

import requests
from nose.plugins.attrib import attr
from . import ApiTestCase


class TestGateUsersAPI(ApiTestCase):

    @attr(env=['test'], priority=1)
    def test_users_api(self):
        """
        GATEKEEPER_USERS_API_001 test_users_api
        Ensure all the user information stored is returned
        """
        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        # return list of all users
        response = self.gk_service.gk_listing(
            session, resource="user"
        )

        # 200
        self.assertEquals(response.status_code, requests.codes.ok)

        # ensure that the count of the users returned
        # is matched by the count in the database
        api_count = response.json().__len__()
        db_count = self.gk_dao.get_user_count(self.db)['count']
        self.assertEquals(api_count, db_count, "count mismatch")

    @attr(env=['test'], priority=1)
    def test_users_api_filters(self):
        """
        GATEKEEPER_USERS_API_002 test_users_api_filters
        Ensure the filters works correctly
        A) verify single and multiple valid filters
        B) basic check of some valid and invalid filters
        """

        #create user and app assocation
        user_app_dict = self.gk_service.create_user_app_api_display_data(
            user_permission=True
        )
        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        user_filters = [
            {'name': user_app_dict['name']},
            {'username': user_app_dict['credentials_payload']['username']},
            {'application': user_app_dict['application_name']},
            {
                'name': user_app_dict['name'],
                'username': user_app_dict['credentials_payload']['username']
            },
            {
                'name': user_app_dict['name'],
                'application': user_app_dict['application_name']
            },
            {
                'username': user_app_dict['credentials_payload']['username'],
                'application': user_app_dict['application_name']
            },
            {
                'name': user_app_dict['name'],
                'username': user_app_dict['credentials_payload']['username'],
                'application': user_app_dict['application_name']
            }
        ]

        # get user data directly from database
        user_info = self.gk_dao.get_user_by_username(
            self.db,
            user_app_dict['credentials_payload']['username']
        )

        # A) verify single and multiple valid filters
        for filters in user_filters:
            # return just the newly created user fron the list of users
            response = self.gk_service.gk_listing(
                session,
                resource="user",
                **filters
            )
            # 200
            self.assertEquals(response.status_code, requests.codes.ok)

            # field count check form read
            # 7 fields should be returned
            self.assertEquals(len(response.json()[0]), 7)

            # verify the contents of the users API
            self.assertUserData(response.json()[0], user_info)

        #  B) basic check of some valid and invalid filters
        user_filters = [
            {
                'name': user_app_dict['name'],
                'username': None
            },
            {
                'name': "sofake",
                'username': user_app_dict['credentials_payload']['username']
            },
        ]
        for filters in user_filters:
            # return just the newly created user from the list of users
            response = self.gk_service.gk_listing(
                session,
                resource="user",
                **filters
            )

            # 200
            self.assertEquals(response.status_code, requests.codes.ok)
            # length 2 i.e empty array
            self.assertEquals(len(response.content), 2)

        #clean up the data
        self.data_clean_up(**user_app_dict)

    @attr(env=['test'], priority=1)
    def test_users_api_filter_common_name(self):
        """
        GATEKEEPER_USERS_API_003 test_users_api_filters
        Ensure the filters works correctly when two users have the same name
        """

        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        #create 2 users with applications and required permissions
        user_app_dict = self.gk_service.create_user_app_api_display_data(
            user_permission=True
        )
        user_app_dict2 = self.gk_service.create_user_app_api_display_data(
            user_permission=True
        )
        #set the same name for user2
        update_response = self.gk_service.gk_crud(
            session,
            method='PUT',
            resource="user",
            data={'name': user_app_dict['name']},
            id=user_app_dict2['user_id']
        )

        # ensure correct status code is returned
        self.assertEquals(
            update_response.status_code, requests.codes.accepted
        )

        name_dict = {'name': user_app_dict['name']}

        # return just the newly created user from the list of users
        response = self.gk_service.gk_listing(
            session,
            resource="user",
            **name_dict
        )

        # 200
        self.assertEquals(response.status_code, requests.codes.ok)
        #list contains 2 users
        self.assertEquals(len(response.json()), 2, "should contain 2 users")

        self.data_clean_up(**user_app_dict)
        self.data_clean_up(**user_app_dict2)

    @attr(env=['test'], priority=1)
    def test_users_api_filter_common_app(self):
        """
        GATEKEEPER_USERS_API_004 test_users_api_filter_common_app
        Ensure the filters works correctly when an app has two users
        """

        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        #create 2 users with applications and required permissions
        user_app_dict = self.gk_service.create_user_app_api_display_data(
            user_permission=True
        )

        #set second user to use the same app as user 1
        user_app_dict2 = self.gk_service.create_user_app_api_display_data(
            app_id=user_app_dict['application_id'],
            user_permission=True
        )

        app_dict = {'application': user_app_dict['application_name']}

        # return just the newly created user from the list of users
        response = self.gk_service.gk_listing(
            session,
            resource="user",
            **app_dict
        )
        # 200
        self.assertEquals(response.status_code, requests.codes.ok)
        #list contains 2 users
        self.assertEquals(len(response.json()), 2, "should contain 2 users")

        self.data_clean_up(**user_app_dict)
        # only delete the required data
        user_data = {
            'user_id': user_app_dict2['user_id'],
            'group_id': user_app_dict2['group_id'],

        }
        self.data_clean_up(**user_data)

    @attr(env=['test'], priority=1)
    def test_users_api_name_invalid_filter_data(self):
        """
        GATEKEEPER_USERS_API_005 test_users_api_name_filter_invalid_name
        Ensure the name filter works correctly when no data or data that
        does not exist is provided
        """
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        user_filters = [
            {'name': "sofake"},
            {'username': "sofake"},
            {'application': "sofake"},
            {'name': None},
            {'username': None},
            {'application': None},
            {
                'username': None,
                'application': "Sofake",
            },
            {
                'name': "Sofake",
                'username': None,
                'application': "Sofake",
            }
        ]

        for filters in user_filters:
            # return just the newly created user from the list of users
            response = self.gk_service.gk_listing(
                session,
                resource="user",
                **filters
            )
            # 200
            self.assertEquals(response.status_code, requests.codes.ok)
            # length 2 i.e empty array
            self.assertEquals(len(response.content), 2)

    @attr(env=['test'], priority=1)
    def test_users_api_name_invalid_filter(self):
        """
        GATEKEEPER_USERS_API_006 test_users_api_name_invalid_filter
        Ensure the an error is returned if invalid filter is provided
        """
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        # create a fake filter
        invalid_filter = {'so_fake': "sofake"}

        response = self.gk_service.gk_listing(
            session,
            resource="user",
            **invalid_filter
        )
        # 400
        self.assertEquals(response.status_code, requests.codes.bad_request)
        #param not allowed
        self.assertTrue(
            self.gk_service.PARAM_NOT_ALLOWED
            in response.json()['error']
        )
