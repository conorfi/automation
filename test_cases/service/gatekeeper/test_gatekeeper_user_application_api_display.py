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
from testconfig import config
from nose.plugins.attrib import attr
from framework.service.gatekeeper.gatekeeper_service import SERVICE_NAME, \
    GateKeeperService
from framework.db.base_dao import BaseDAO
from framework.db.gate_keeper_dao import GateKeeperDAO
from framework.utility.utility import Utility
import Cookie
from multiprocessing import Process
import time
import unittest


class TestGateKeeperUserApplicationAPI(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Things that need to be done once
        cls.db = BaseDAO(config[SERVICE_NAME]['db']['connection'])

    @classmethod
    def tearDownClass(cls):
        # Things that need to be done once.
        cls.db.close()

    def setUp(self):
        # Things to run before each test.
        self.gk_service = GateKeeperService()
        self.gk_dao = GateKeeperDAO()
        self.default_test_user = self.gk_dao.get_user_by_username(
            self.db,
            self.gk_service.ADMIN_USER
        )['user_id']
        self.util = Utility()

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

        # create a user and associate user with relevant
        # pre confiured application for dummy app
        username = 'automation_' + self.util.random_str(5)
        appname = self.gk_service.ANOTHER_TEST_APP
        fullname = 'automation ' + self.util.random_str(5)
        email = self.util.random_email(5)

        # create basic user - no permisssions
        self.assertTrue(
            self.gk_dao.set_gk_user(
                self.db,
                username,
                self.gk_service.HASH_PASSWORD_TEST,
                email,
                fullname,
                '123-456-789123456'
            )
        )

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

        # associate user with app
        self.assertTrue(self.gk_dao.set_user_app_id(self.db, app_id, user_id))

        # create a session for the user
        credentials_payload = {'username': username, 'password': 'test'}

        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False,
            credentials=credentials_payload
        )

        # Verify the user API
        response = self.gk_service.user_app(session, user_id, appname)
        self.assertEquals(response.status_code, requests.codes.ok)

        self.assertTrue(username in response.json()['username'])
        self.assertEquals([], response.json()['organizations'])
        self.assertTrue(str(user_id) in response.json()['user_id'])
        self.assertEquals([], response.json()['groups'])
        self.assertTrue(fullname in response.json()['fullname'])
        self.assertTrue(email in response.json()['email'])
        self.assertEquals([], response.json()['permissions'])

        # Using the dummy application verify the permissions
        # the user is authorized for

        # verify the dummy applcation can be accessed
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

        username = 'automation_' + self.util.random_str(5)
        appname = self.gk_service.ANOTHER_TEST_APP
        fullname = 'automation ' + self.util.random_str(5)
        email = self.util.random_email(5)

        # create basic user - no permisssions
        self.assertTrue(
            self.gk_dao.set_gk_user(
                self.db, username,
                self.gk_service.HASH_PASSWORD_TEST,
                email,
                fullname,
                '123-456-789123456')
        )

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

        # get permissions
        user_permission = self.gk_dao.get_permission_by_name(
            self.db,
            self.gk_service.DEFAULT_ADFUSER_USER, app_id
        )['permission_id']
        admin_permission = self.gk_dao.get_permission_by_name(
            self.db,
            self.gk_service.DEFAULT_ADFUSER_ADMIN, app_id
        )['permission_id']

        # associate user with app
        self.assertTrue(self.gk_dao.set_user_app_id(self.db, app_id, user_id))

        # create a session for the user
        credentials_payload = {'username': username, 'password': 'test'}

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
        response = self.gk_service.user_app(session, user_id, appname)
        self.assertEquals(response.status_code, requests.codes.ok)
        self.assertTrue(username in response.json()['username'])
        self.assertEquals([], response.json()['organizations'])
        self.assertTrue(str(user_id) in response.json()['user_id'])
        self.assertEquals([], response.json()['groups'])
        self.assertTrue(fullname in response.json()['fullname'])
        self.assertTrue(email in response.json()['email'])
        self.assertEquals(
            self.gk_service.DEFAULT_ADFUSER_ADMIN,
            response.json()['permissions'][0]
        )
        self.assertEquals(
            self.gk_service.DEFAULT_ADFUSER_USER,
            response.json()['permissions'][1]
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

        username = 'automation_' + self.util.random_str(5)
        appname = self.gk_service.ANOTHER_TEST_APP
        fullname = 'automation ' + self.util.random_str(5)
        email = self.util.random_email(5)
        grp_name = 'automation_' + self.util.random_str(5)
        grp_name_2 = 'automation_' + self.util.random_str(5)

        # create basic user - no permisssions
        self.assertTrue(
            self.gk_dao.set_gk_user(
                self.db,
                username,
                self.gk_service.HASH_PASSWORD_TEST,
                email,
                fullname,
                '123-456-789123456'
            )
        )

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

        # associate user with app
        self.assertTrue(self.gk_dao.set_user_app_id(self.db, app_id, user_id))

        # creat gatekeeper group
        self.assertTrue(self.gk_dao.set_gk_group(self.db, grp_name))
        # get group id
        group_id = self.gk_dao.get_group_by_name(
            self.db,
            grp_name
        )['group_id']

        # associate user with group
        self.assertTrue(self.gk_dao.set_user_group(self.db, user_id, group_id))

        # associate group with application
        self.assertTrue(
            self.gk_dao.set_group_app_id(self.db, app_id, group_id)
        )

        # create a session for the user

        credentials_payload = {'username': username, 'password': 'test'}

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

        self.assertTrue(username in response.json()['username'])
        self.assertEquals([], response.json()['organizations'])
        self.assertTrue(str(user_id) in response.json()['user_id'])
        self.assertTrue(grp_name in response.json()['groups'][0])
        self.assertTrue(fullname in response.json()['fullname'])
        self.assertTrue(email in response.json()['email'])
        self.assertEquals(
            self.gk_service.DEFAULT_ADFUSER_ADMIN,
            response.json()['permissions'][0]
        )
        self.assertEquals(
            self.gk_service.DEFAULT_ADFUSER_USER,
            response.json()['permissions'][1]
        )

        # create another group, associate with the user but not the application
        # this group should NOT be retured by the API

        # create gatekeeper group
        self.assertTrue(
            self.gk_dao.set_gk_group(
                self.db,
                grp_name_2
            )
        )
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
        # delete the group
        self.assertTrue(self.gk_dao.del_gk_group(self.db, group_id))

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
        '''
        GATEKEEPER_USER_SESSION_API_007 test_user_app_with_no_args
        Ensures user info CANNOT be return from the user api when no
        user id or application name is provided
        '''
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
        '''
        GATEKEEPER_USER_SESSION_API_008 test_user_app_with_no_application_name
        Ensures user info CANNOT be return from the user api when no
        application name is provided
        '''
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
        '''
        GATEKEEPER_USER_SESSION_API_009 test_user_app_with_no_user_id
        Ensures user info CANNOT be return from the user api when no
        application id is provided
        '''
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
