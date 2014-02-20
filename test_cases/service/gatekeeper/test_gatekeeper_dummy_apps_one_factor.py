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


class TestDummyApps(ApiTestCase):

    @attr(env=['test'], priority=1)
    def test_user_app_and_auth_app_perms(self):
        """
        TestDummyApps_001 test_user_app_and_auth_app_perms
        test user api and permissions for user with only app access
        Part a - Ensures user info can be return from the user api when
         a valid session,user id and application is provided for a user
        Part b  - Using the dummy application verify the end points the user
        can access when the user only has access to the dummy app
        """

        app_name = self.gk_service.ANOTHER_TEST_APP

        # get app id
        app_id = self.gk_dao.get_app_by_app_name(
            self.db,
            app_name
        )['application_id']

        #create user and associate with application
        user_app_dict = self.gk_service.create_user_app_api_display_data(
            app_id=app_id
        )

        # get user data directly from database
        user_info = self.gk_dao.get_user_by_username(
            self.db,
            user_app_dict['credentials_payload']['username']
        )

        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False,
            credentials=user_app_dict['credentials_payload']
        )

        # Verify the user API
        response = self.gk_service.user_app(
            session,
            user_app_dict['user_id'],
            app_name
        )
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

        # delete all created data
        self.data_clean_up(application_protected=True, **user_app_dict)


    @attr(env=['test'], priority=1)
    def test_user_app_and_auth_user_perms(self):
        """
        TestDummyApps_002 test_user_app_and_auth_user_perms
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

        app_name = self.gk_service.ANOTHER_TEST_APP

        # get app id
        app_id = self.gk_dao.get_app_by_app_name(
            self.db,
            app_name
        )['application_id']

        #cretate user and associate with application
        user_app_dict = self.gk_service.create_user_app_api_display_data(
            app_id=app_id
        )

        # get user data directly from database
        user_info = self.gk_dao.get_user_by_username(
            self.db,
            user_app_dict['credentials_payload']['username']
        )

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

        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False,
            credentials=user_app_dict['credentials_payload']
        )

        # set the user permissions for the app
        # i.e user can only access the dummy application and user end point

        self.assertTrue(
            self.gk_dao.set_user_permissions_id(
                self.db,
                user_app_dict['user_id'],
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
                self.db,
                user_app_dict['user_id'],
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
            user_app_dict['user_id'],
            app_name
        )
        self.assertEquals(response.status_code, requests.codes.ok)

        # Verify the user API
        self.assertUserAppDisplay(
            response.json(), user_info, expected_perm_data=perm_info,
        )

        # delete all created data
        self.data_clean_up(application_protected=True, **user_app_dict)

    @attr(env=['test'], priority=1)
    def test_user_app_and_auth_group_perms(self):
        """
        TestDummyApps_003 test_user_app_and_auth_group_perms
        test user api and permissions for user with group_permission access
        Part a - Using the dummy application verify the end points the user
        can access when the user has permissions configured for the
        with user permissions in the group_permissions table
        Part b  - Ensures user info can be return from the user api when a
        valid session,user id and application is provided for a user

        """
        app_name = self.gk_service.ANOTHER_TEST_APP

        # get app id
        app_id = self.gk_dao.get_app_by_app_name(
            self.db,
            app_name
        )['application_id']

        #cretate user and associate with application
        user_app_dict = self.gk_service.create_user_app_api_display_data(
            app_id=app_id,
            user_group=True
        )

        # get user data directly from database
        user_info = self.gk_dao.get_user_by_username(
            self.db,
            user_app_dict['credentials_payload']['username']
        )

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
        grp_info = [user_app_dict['group_name']]

        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False,
            credentials=user_app_dict['credentials_payload']
        )

        # set the group permissions for the app
        # i.e user can only access the dummy application and user end point

        # set group permission for user access
        self.assertTrue(
            self.gk_dao.set_group_permission(
                self.db,
                user_app_dict['group_id'],
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
                user_app_dict['group_id'],
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
            user_app_dict['user_id'],
            app_name
        )
        self.assertEquals(response.status_code, requests.codes.ok)

        self.assertUserAppDisplay(
            response.json(), user_info, grp_info, perm_info,
        )

        # delete all created data
        self.data_clean_up(application_protected=True, **user_app_dict)

    @attr(env=['test'], priority=1)
    def test_validate_user_with_no_access_for_app(self):
        """
        TestDummyApps_004 test_validate_user_with_no_access_for_app
        Ensure that user returns 403 when it tries to access an application
        that it has association with
        """

        # create a user and associate user with relevant
        # pre confiured application for dummy app
        username = 'automation_' + self.util.random_str(5)
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

        # create a session for the user
        credentials_payload = {'username': username, 'password': 'test'}

        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False,
            credentials=credentials_payload
        )

        # verify the end point cannot be accessed
        response = self.gk_service.validate_end_point(
            session,
            end_point=config[SERVICE_NAME]['dummy']['user_endpoint']
        )
        self.assertEquals(response.status_code, requests.codes.forbidden)
        response = self.gk_service.validate_end_point(
            session,
            end_point=config[SERVICE_NAME]['dummy']['admin_endpoint']
        )
        self.assertEquals(response.status_code, requests.codes.forbidden)

    @attr(env=['test'], priority=1)
    def test_validate_caching(self):
        """
        TestDummyApps_005 test_validate_caching
        Caching is enabled by default in the dummy app
        To ensure that caching is enabled this tests work in 3 parts
        Part A) Ensure user cannnot access user end point
        part B) Add user endpoint permission but as caching is enabled
                the new permission will not have been cached
        Part C) Disable caching, the new permission will now be retrieved
                and the user can access the user end point
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

        # associate user with app
        self.assertTrue(self.gk_dao.set_user_app_id(self.db, app_id, user_id))

        # create a session for the user
        credentials_payload = {'username': username, 'password': 'test'}
        # create a session - do not allow redirects - urlencoded post

        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False,
            credentials=credentials_payload
        )

        # Part A)
        # verify the user end point dummy application cannot be accessed
        response = self.gk_service.validate_end_point(session)
        self.assertEquals(response.status_code, requests.codes.ok)

        # verify the user end point cannot be accessed
        response = self.gk_service.validate_end_point(
            session,
            end_point=config[SERVICE_NAME]['dummy']['user_endpoint']
        )
        # 403
        self.assertEquals(response.status_code, requests.codes.forbidden)

        # Part B)
        # set the user permissions for the app
        # i.e user can only access the dummy application and user end point
        self.assertTrue(
            self.gk_dao.set_user_permissions_id(
                self.db,
                user_id,
                user_permission
            )
        )

        # verify the user end point cannot be accessed due to caching,
        # the updated permissions will not apply
        response = self.gk_service.validate_end_point(
            session,
            end_point=config[SERVICE_NAME]['dummy']['user_endpoint']
        )
        # 403
        self.assertEquals(response.status_code, requests.codes.forbidden)

        # Part C)
        # must disable caching in dummyapp for this check
        parameters = {'sso_cache_enabled': False}
        # verify the dummy application can be accessed
        # when caching is disabled as the new permission can now
        # be retreived

        response = self.gk_service.validate_end_point(
            session,
            end_point=config[SERVICE_NAME]['dummy']['user_endpoint'],
            parameters=parameters
        )
        # 200
        self.assertEquals(response.status_code, requests.codes.ok)

        # delete user - cascade delete by default
        self.assertTrue(self.gk_dao.del_gk_user(self.db, user_id))

    @attr(env=['test'], priority=1)
    def test_ajax_no_redirect_dummy_app(self):
        """
        TestDummyApps_006 test_ajax_no_redirect
        If the user tries to reach a uri in a browser and that uri is
        protected by the SSO tool, user will be redirected to the login page
        If the user makes an AJAX request, user will get a 401 and the
        redirection URL in the JSON response and won't be redirected
        There's no configuration or query string option to modify
        this behaviour. We reply with redirection to browsers and JSON
        package to AJAX calls
        """
        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        response = self.gk_service.validate_end_point(
            session, allow_redirects=False
        )

        self.assertEquals(response.status_code, requests.codes.ok)
        self.assertTrue(
            self.gk_service.GATEKEEPER_TITLE not in response.text
        )

        # logout
        response = self.gk_service.logout_user_session(session)
        self.assertEquals(response.status_code, requests.codes.ok)

        # must disable caching in dummyapp for this check
        parameters = {'sso_cache_enabled': False}

        # firstly browser call test - 303 redirect
        response = self.gk_service.validate_end_point(
            session, allow_redirects=False, parameters=parameters
        )
        self.assertTrue(response.status_code in [requests.codes.found,
                                                 requests.codes.see_other])
        response = self.gk_service.validate_end_point(
            session, parameters=parameters
        )
        self.assertTrue(self.gk_service.GATEKEEPER_TITLE in response.text)

        # set header to emulate an ajax call
        session.headers.update({'X-Requested-With': 'XMLHttpRequest'})
        response = self.gk_service.validate_end_point(
            session, allow_redirects=False, parameters=parameters
        )
        # ajax call 401
        self.assertEquals(response.status_code, requests.codes.unauthorized)
        self.assertTrue(
            self.gk_service.NOT_LOGGED_IN in response.json()['error']
        )

    @attr(env=['test'], priority=1)
    def test_invalid_dummy_app_endpoint(self):
        """
        TestDummyApps_007 test_invalid_dummy_app_endpoint
        - test an invalid endpoint on gatekeeper
        - test an invlaid endpoint on the dummy app
        """

        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        # validate a fake dummy app endpoint
        response = self.gk_service.validate_end_point(
            session,
            end_point="fake"
        )
        # 404
        self.assertEquals(response.status_code, requests.codes.not_found)

    @attr(env=['test'], priority=1)
    def test_can_login_with_redirect(self):
        """
        TestDummyApps_008 test_can_login_with_redirect
        Creates a session through a POST to the login API
        using urlencoded body. Specified redirect
        """
        # login and create session - allow_redirects=False
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False,
            redirect_url=config[SERVICE_NAME]['redirect']
        )
        #set redirect_url from the response
        redirect_url = response.url

        # assert against database
        db_response = self.gk_dao.get_session_by_cookie_id(self.db, cookie_id)
        self.assertEquals(db_response['cookie_id'], cookie_id)
        self.assertEquals(db_response['user_id'], self.default_test_user)

        # create a session - allow_redirects=True
        response = self.gk_service.create_session_urlencoded(
            allow_redirects=True,
            redirect_url=redirect_url
        )
        # 200 response
        self.assertEquals(response.status_code, requests.codes.ok)
        self.assertTrue('Example Domain' in response.text)

    @attr(env=['test'], priority=1)
    def test_login_with_redirect_validate_url(self):
        """
        TestDummyApps_009 test_login_with_redirect_validate_url
        Creates a session through a POST to the login API and then verifies
        that a user can access an url using a session with a valid cookie.
        Specified redirect
        """

        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False,
            redirect_url=config[SERVICE_NAME]['redirect']
        )

        #set redirect_url from the response
        redirect_url = response.url

        response = self.gk_service.validate_url_with_cookie(
            session=session,
            redirect_url=redirect_url
        )
        self.assertEquals(response.status_code, requests.codes.ok)
        self.assertTrue('Example Domain' in response.text)

    @attr(env=['test'], priority=1)
    def test_can_logout_with_redirect(self):
        """
        TestDummyApps_010 test_can_logout_with_redirect
        Ensures a user session can be deleted using single logout
        using POST
        Specified redirect on logout
        """

         # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False,
            redirect_url=config[SERVICE_NAME]['redirect']
        )

        #set redirect_url from the response
        redirect_url = response.url

        response = self.gk_service.validate_url_with_cookie(
            session,
            redirect_url=redirect_url
        )
        self.assertEquals(response.status_code, requests.codes.ok)
        self.assertTrue('Example Domain' in response.text)

        # logout with POST
        response = self.gk_service.logout_user_session(session)
        self.assertEquals(response.status_code, requests.codes.ok)

        response = self.gk_service.validate_url_with_cookie(session)
        self.assertEquals(response.status_code, requests.codes.ok)
        self.assertTrue(self.gk_service.GATEKEEPER_TITLE in response.text)

        # assert againist the database - ensure it no longer exists
        db_response = self.gk_dao.get_session_by_cookie_id(
            self.db,
            cookie_id
        )
        self.assertEquals(db_response, None)
