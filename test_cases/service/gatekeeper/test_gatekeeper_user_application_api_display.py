"""
@summary: Contains a set of test cases for the user application API of the
gatekeeper(single sign on) project
Note: only 1 factor authentication test cases
These test have a number of dependencies
1. the database update script updates the gatekeepr schema - the script can be
found at the root of the gatekeeper app
2. the build script starts the gatekeeper app with ssl enbaled by default
3. the build script starts the dummy app with ssl enabled
and application_name is adfuser
4. The dummy app is pre-configure with two permissions
'ADFUSER_USER' and 'ADFUSER_ADMIN'
@since: Created on 3rd January 2014
@author: Conor Fitzgerald
"""

import requests
from nose.plugins.attrib import attr
from . import ApiTestCase
from testconfig import config
from framework.service.gatekeeper.gatekeeper_service import SERVICE_NAME, \
    GateKeeperService


class TestGateKeeperUserApplicationAPI(ApiTestCase):
    @attr(env=['test'], priority=1)
    def test_user_app_and_auth_app_perms(self):
        """
        GATEKEEPER_USER_SESSION_API_001 test_user_app_and_auth_app_perms
        test user api and permissions for user with only app access
        Part a - Ensures user info can be return from the user api when
         a valid session,user id and application is provided for a user
        Part b  - Using the dummy application verify the end points the user
        can access when the user only has access to the dummy app
        """

        # admin - login and create session
        a_session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        #username
        username = self.util.random_str(8)
        password = self.util.random_str(8)
        app_name = self.gk_service.ANOTHER_TEST_APP

        # credentials
        credentials_payload = {
            'username': username,
            'password': password
        }
        user_data = self.gk_service.create_user_data(
            user_dict=credentials_payload)

        # create a new user
        create_response = self.gk_service.gk_crud(
            a_session, method='POST', resource="user", data=user_data
        )

        # ensure a 201 is returned
        self.assertEquals(create_response.status_code, requests.codes.created)

        # get user_id
        user_id = self.gk_dao.get_user_by_username(
            self.db,
            username
        )['user_id']

        # get app id
        app_id = self.gk_dao.get_app_by_app_name(
            self.db,
            app_name
        )['application_id']

        # get user data directly from database
        user_info = self.gk_dao.get_user_by_username(self.db, username)

        # associate user with app
        self.assertTrue(self.gk_dao.set_user_app_id(self.db, app_id, user_id))

        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False,
            credentials=credentials_payload
        )

        # Verify the user API
        response = self.gk_service.user_app(session, user_id, app_name)
        self.assertEquals(response.status_code, requests.codes.ok)

        self.assertUserAppDisplay(response.json(), user_info)

        # Using the dummy application verify the permissions
        # the user is authorized for

        # verify the dummy application can be accessed
        response = self.gk_service.validate_end_point(session)
        self.assertEquals(response.status_code, requests.codes.ok)

        # verify the user end point cannot be accessed
        response = self.gk_service.validate_end_point(
            session,
            end_point=config[SERVICE_NAME]['dummy']['user_endpoint']
        )

        self.assertEquals(response.status_code, requests.codes.forbidden)

        # verify the admin end point cannot be accessed
        response = self.gk_service.validate_end_point(
            session,
            end_point=config[SERVICE_NAME]['dummy']['admin_endpoint']
        )
        self.assertEquals(response.status_code, requests.codes.forbidden)

        # delete user - cascade delete by default
        self.assertTrue(self.gk_dao.del_gk_user(self.db, user_id))

    @attr(env=['test'], priority=1)
    def test_user_app_and_auth_user_perms(self):
        """
        GATEKEEPER_USER_SESSION_API_002 test_user_app_and_auth_user_perms
        test user api and permissions for user with user_permission access
        Part a - Using the dummy application verify the end points the user
        can access when the user has permissions configured for the with
        user permissions in the user_permissions table
        Part b  - Ensures user info can be return from the user api when a
        valid session,user id and application is provided for a user
        """

        # create a user and associate user with relevant
        # pre confiured application for dummy app

        # create a user and associate user with relevant
        # pre confiured application for dummy app

        #username
        username = self.util.random_str(8)
        password = self.util.random_str(8)
        appname = self.gk_service.ANOTHER_TEST_APP

        # credentials
        credentials_payload = {
            'username': username,
            'password': password
        }
        user_data = self.gk_service.create_user_data(
            user_dict=credentials_payload
        )
        # admin - login and create session
        a_session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        # create basic user - no permisssions
        response = self.gk_service.gk_crud(
            a_session, method='POST', resource="user", data=user_data
        )

        # ensure a 201 is returned
        self.assertEquals(response.status_code, requests.codes.created)

        # get user_id
        user_id = self.gk_dao.get_user_by_username(
            self.db,
            username
        )['user_id']

        # get app id
        app_id = self.gk_dao.get_app_by_app_name(
            self.db,
            appname
        )['application_id']

        # get user data directly from database
        user_info = self.gk_dao.get_user_by_username(self.db, username)

        # get permissions
        user_permission = self.gk_dao.get_permission_by_name(
            self.db,
            self.gk_service.DEFAULT_ADFUSER_USER,
            app_id
        )['permission_id']

        admin_permission = self.gk_dao.get_permission_by_name(
            self.db,
            self.gk_service.DEFAULT_ADFUSER_ADMIN,
            app_id
        )['permission_id']

        perm_info = [
            self.gk_service.DEFAULT_ADFUSER_ADMIN,
            self.gk_service.DEFAULT_ADFUSER_USER
        ]

        # associate user with app
        self.assertTrue(self.gk_dao.set_user_app_id(self.db, app_id, user_id))

        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False,
            credentials=credentials_payload
        )

        # set the user permissions for the app
        # i.e user can only access the dummy application and user end point

        self.assertTrue(
            self.gk_dao.set_user_permissions_id(
                self.db,
                user_id,
                user_permission
            )
        )

        # Using the dummy application verify the permissions for the user

        # verify the dummy applcation can be accessed
        response = self.gk_service.validate_end_point(session)
        self.assertEquals(response.status_code, requests.codes.ok)

        # verify the user end point can be accessed
        response = self.gk_service.validate_end_point(
            session,
            end_point=config[SERVICE_NAME]['dummy']['user_endpoint']
        )
        self.assertEquals(response.status_code, requests.codes.ok)

        # verify the admin end point cannot be accessed
        response = self.gk_service.validate_end_point(
            session,
            end_point=config[SERVICE_NAME]['dummy']['admin_endpoint']
        )
        self.assertEquals(response.status_code, requests.codes.forbidden)

        # set the admin permissions for the app
        # i.e user can access admin end point

        self.assertTrue(
            self.gk_dao.set_user_permissions_id(
                self.db, user_id,
                admin_permission
            )
        )

        # must disable caching in dummyapp for this check
        parameters = {'sso_cache_enabled': False}
        # Using the dummy application verify the permissions for the user
        # verify the dummy applcation can be accessed
        response = self.gk_service.validate_end_point(session,
                                                      parameters=parameters)
        self.assertEquals(response.status_code, requests.codes.ok)

        # verify the user end point can be accessed
        response = self.gk_service.validate_end_point(
            session,
            end_point=config[SERVICE_NAME]['dummy']['user_endpoint'],
            parameters=parameters
        )
        self.assertEquals(response.status_code, requests.codes.ok)

        # verify the admin end point can be accessed
        response = self.gk_service.validate_end_point(
            session,
            end_point=config[SERVICE_NAME]['dummy']['admin_endpoint'],
            parameters=parameters
        )

        self.assertEquals(response.status_code, requests.codes.ok)

        # Verify the user API
        response = self.gk_service.user_app(
            session,
            user_id,
            appname
        )
        self.assertEquals(response.status_code, requests.codes.ok)

        # Verify the user API
        self.assertUserAppDisplay(
            response.json(), user_info, expected_perm_data=perm_info,
        )

        # delete user - cascade delete by default
        self.assertTrue(self.gk_dao.del_gk_user(self.db, user_id))

    @attr(env=['test'], priority=1)
    def test_user_app_and_auth_group_perms(self):
        """
        GATEKEEPER_USER_SESSION_API_003 test_user_app_and_auth_group_perms
        test user api and permissions for user with group_permission access
        Part a - Using the dummy application verify the end points the user
        can access when the user has permissions configured for the
        with user permissions in the group_permissions table
        Part b  - Ensures user info can be return from the user api when a
        valid session,user id and application is provided for a user

        """

        # create a user and associate user with relevant
        # pre confiured application for dummy app

        #username
        username = self.util.random_str(8)
        password = self.util.random_str(8)
        appname = self.gk_service.ANOTHER_TEST_APP

        # credentials
        credentials_payload = {
            'username': username,
            'password': password
        }
        user_data = self.gk_service.create_user_data(
            user_dict=credentials_payload
        )
        # admin - login and create session
        a_session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        # create basic user - no permisssions
        response = self.gk_service.gk_crud(
            a_session, method='POST', resource="user", data=user_data
        )
        # ensure a 201 is returned
        self.assertEquals(response.status_code, requests.codes.created)

        # get user_id
        user_id = self.gk_dao.get_user_by_username(
            self.db,
            username
        )['user_id']

        # get app id
        app_id = self.gk_dao.get_app_by_app_name(
            self.db,
            appname
        )['application_id']

        # get user data directly from database
        user_info = self.gk_dao.get_user_by_username(self.db, username)

        # get permissions
        user_permission = self.gk_dao.get_permission_by_name(
            self.db,
            self.gk_service.DEFAULT_ADFUSER_USER,
            app_id
        )['permission_id']

        admin_permission = self.gk_dao.get_permission_by_name(
            self.db,
            self.gk_service.DEFAULT_ADFUSER_ADMIN,
            app_id
        )['permission_id']

        perm_info = [
            self.gk_service.DEFAULT_ADFUSER_ADMIN,
            self.gk_service.DEFAULT_ADFUSER_USER
        ]
        # create a new group
        create_grp_response = self.gk_service.gk_crud(
            a_session, method='POST', resource="group"
        )

        grp_name = create_grp_response.json()['name']
        # get group id
        group_id = self.gk_dao.get_group_by_name(
            self.db,
            grp_name
        )['group_id']
        grp_info = [grp_name]

        # associate user with app
        self.assertTrue(self.gk_dao.set_user_app_id(self.db, app_id, user_id))

        # associate user with group
        self.assertTrue(self.gk_dao.set_user_group(self.db, user_id, group_id))

        # associate group with application
        self.assertTrue(
            self.gk_dao.set_group_app_id(self.db, app_id, group_id)
        )

        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False,
            credentials=credentials_payload
        )

        # set the group permissions for the app
        # i.e user can only access the dummy application and user end point

        # set group permission for user access
        self.assertTrue(
            self.gk_dao.set_group_permission(
                self.db,
                group_id,
                user_permission)
        )

        # Using the dummy application
        # verify the permissions the user is authorized

        # verify the dummy applcation can be accessed
        response = self.gk_service.validate_end_point(session)
        self.assertEquals(response.status_code, requests.codes.ok)

        # verify the user end point can be accessed
        response = self.gk_service.validate_end_point(
            session,
            end_point=config[SERVICE_NAME]['dummy']['user_endpoint']
        )
        self.assertEquals(response.status_code, requests.codes.ok)

        # verify the admin end point cannot be accessed
        response = self.gk_service.validate_end_point(
            session,
            end_point=config[SERVICE_NAME]['dummy']['admin_endpoint']
        )
        self.assertEquals(response.status_code, requests.codes.forbidden)

        # set the group permissions for the app
        # i.e user can access the admin endpoint

        # set group permission for admin access
        self.assertTrue(
            self.gk_dao.set_group_permission(
                self.db,
                group_id,
                admin_permission
            )
        )

        # Using the dummy application
        # verify the permissions the user is authorized
        # must disable caching in dummyapp for this check
        parameters = {'sso_cache_enabled': False}
        # verify the dummy application can be accessed
        response = self.gk_service.validate_end_point(session,
                                                      parameters=parameters)
        self.assertEquals(response.status_code, requests.codes.ok)

        # verify the user end point can be accessed
        response = self.gk_service.validate_end_point(
            session,
            end_point=config[SERVICE_NAME]['dummy']['user_endpoint'],
            parameters=parameters
        )
        self.assertEquals(response.status_code, requests.codes.ok)

        # verify the admin end point cannot be accessed
        response = self.gk_service.validate_end_point(
            session,
            end_point=config[SERVICE_NAME]['dummy']['admin_endpoint'],
            parameters=parameters
        )
        self.assertEquals(response.status_code, requests.codes.ok)

        # Verify the user API
        response = self.gk_service.user_app(
            session,
            user_id,
            appname
        )
        self.assertEquals(response.status_code, requests.codes.ok)

        self.assertUserAppDisplay(
            response.json(), user_info, grp_info, perm_info,
        )

        # create another group, associate with the user but not the application
        # this group should NOT be retured by the API

        # create a new group
        create_grp2_response = self.gk_service.gk_crud(
            a_session, method='POST', resource="group"
        )

        grp_name_2 = create_grp2_response.json()['name']
        # get group id
        group_id_2 = self.gk_dao.get_group_by_name(
            self.db,
            grp_name_2
        )['group_id']

        # associate user with group
        self.assertTrue(
            self.gk_dao.set_user_group(self.db, user_id, group_id_2)
        )

        # user API response
        response = self.gk_service.user_app(session, user_id, appname)
        self.assertEquals(response.status_code, requests.codes.ok)
        # ensure that only 1 group is associate with the application/user
        self.assertEquals(1, len(response.json()['groups']))

        # delete the group and user
        # delete the groups
        self.assertTrue(self.gk_dao.del_gk_group(self.db, group_id))
        self.assertTrue(self.gk_dao.del_gk_group(self.db, group_id_2))
        # delete user - cascade delete by default
        self.assertTrue(self.gk_dao.del_gk_user(self.db, user_id))

    @attr(env=['test'], priority=1)
    def test_user_app_invalid_cookie_session(self):
        """
        GATEKEEPER_USER_SESSION_API_004 test_user_app_invalid_cookie_session
        Ensures user info CANNOT be return from the user api when a invalid
        session is provided
        """

        cookie_value = "fakecookie"

        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False,
            redirect_url=config[SERVICE_NAME]['redirect'],
            cookie_value=cookie_value
        )

        response = self.gk_service.user_app(
            session,
            self.default_test_user,
            self.gk_service.DEFAULT_TEST_APP
        )
        # ensure that the request is forbidden(403)
        # without a valid session cookie
        self.assertEquals(response.status_code, requests.codes.forbidden)
        self.assertTrue(self.gk_service.USER_ERROR in response.json()['error'])

    @attr(env=['test'], priority=1)
    def test_user_app_invalid_application(self):
        """
        GATEKEEPER_USER_SESSION_API_005 test_user_app_invalid_application
        Ensures user info CANNOT be return from the user api when a invalid
        application is provided
        """

        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False,
            redirect_url=config[SERVICE_NAME]['redirect']
        )

        fake_application = "fake"
        response = self.gk_service.user_app(
            session,
            self.default_test_user,
            fake_application
        )

        # ensure it returns a 404 not found
        self.assertEquals(response.status_code, requests.codes.not_found)

        self.assertTrue("No user with id" in response.json()['error'])
        self.assertTrue("found for application" in response.json()['error'])

    @attr(env=['test'], priority=1)
    def test_user_app_invalid_user_id(self):
        """
        GATEKEEPER_USER_SESSION_API_006 test_user_app_invalid_user_id
        Ensures user info CANNOT be return from the user api when a invalid
        user id is provided
        """

        # login and create admin session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        # create first random user
        password = 'testtest'
        user1_data = self.gk_service.create_user_data({'password': password})
        response = self.gk_service.gk_crud(session, 'POST', 'user',
                                           data=user1_data)
        self.assertEquals(response.status_code, requests.codes.created)

        # create second random user, storing user ID
        user2_data = self.gk_service.create_user_data()
        response = self.gk_service.gk_crud(session, 'POST', 'user',
                                           data=user2_data)
        self.assertEquals(response.status_code, requests.codes.created)
        json_data = response.json()
        self.assertTrue('user_id' in json_data)
        user2_data['user_id'] = json_data['user_id']

        # login with first random user
        credentials = {'username': user1_data['username'],
                       'password': password}
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False,
            credentials=credentials
        )

        # attempt access to user application for second random user
        response = self.gk_service.user_app(
            session,
            user2_data['user_id'],
            self.gk_service.DEFAULT_TEST_APP
        )

        # ensure that the request is forbidden(403)
        # without a valid session cookie
        self.assertEquals(response.status_code, requests.codes.forbidden)
        self.assertTrue(self.gk_service.USER_ERROR in response.json()['error'])

    @attr(env=['test'], priority=1)
    def test_user_app_with_no_args(self):
        """
        GATEKEEPER_USER_SESSION_API_007 test_user_app_with_no_args
        Ensures user info CANNOT be return from the user api when no
        user id or application name is provided
        """
        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False,
            redirect_url=config[SERVICE_NAME]['redirect']
        )

        response = self.gk_service.user_app(session, '', '')

        self.assertEquals(response.status_code, requests.codes.bad_request)
        json_data = response.json()
        self.assertTrue('error' in json_data)
        self.assertTrue(
            self.gk_service.MISSING_PARAMETERS in json_data['error']
        )

    @attr(env=['test'], priority=1)
    def test_user_app_with_no_application_name(self):
        """
        GATEKEEPER_USER_SESSION_API_008 test_user_app_with_no_application_name
        Ensures user info CANNOT be return from the user api when no
        application name is provided
        """
        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False,
            redirect_url=config[SERVICE_NAME]['redirect']
        )

        user_id = self.gk_dao.get_user_by_username(
            self.db,
            self.gk_service.ADMIN_USER
        )['user_id']

        response = self.gk_service.user_app(session, user_id, '')

        self.assertEquals(response.status_code, requests.codes.bad_request)
        json_data = response.json()
        self.assertTrue('error' in json_data)
        self.assertEqual(json_data['error'],
                         self.gk_service.MISSING_APP_NAME)

    @attr(env=['test'], priority=1)
    def test_user_app_with_no_user_id(self):
        """
        GATEKEEPER_USER_SESSION_API_009 test_user_app_with_no_user_id
        Ensures user info CANNOT be return from the user api when no
        application id is provided
        """
        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False,
            redirect_url=config[SERVICE_NAME]['redirect']
        )

        response = self.gk_service.user_app(
            session, '', self.gk_service.DEFAULT_TEST_APP
        )
        self.assertEquals(response.status_code, requests.codes.bad_request)
        json_data = response.json()
        self.assertTrue('error' in json_data)
        self.assertEqual(json_data['error'],
                         self.gk_service.MISSING_APP_ID)
