"""
@summary: Contains a set of functional tests cases for the
gate keeper(single sign on)project
Note: 1 factor authentication test cases
These test have a number of dependencies
1. the database update script updates the gatekeepr schema - the script can be
found at the root of the gatekeeper app
2. the build script starts the gatekeeper app with ssl enbaled by default
3. the build script starts the dummy app with ssl enabled
and application_name is adfuser

@since: Created on October 31st 2013
@author: Conor Fitzgerald
"""
import requests
import Cookie
from nose.plugins.attrib import attr
from testconfig import config
from framework.service.gatekeeper.gatekeeper_service import SERVICE_NAME, \
    GateKeeperService
from multiprocessing import Process

from . import ApiTestCase

USER_TOTAL = 5


class TestGateKeeperFunctional(ApiTestCase):

    @attr(env=['test'], priority=1)
    def test_session_concurrency(self):

        """
        GATEKEEPER_FUNCTIONAL_002 test_session_concurrency
        Random 403s occur when accessing the user session API via the
        SSO tool with a large number of multiple users.
        defect: https://www.pivotaltracker.com/story/show/62219660
        """

        # login and create session
        a_session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        # initial setup - create arbitrary number of users via REST API
        # TO DO: replace this code with the user API when the user API on
        # the develop branch is merged to master

        created_user_data = []
        for index in range(USER_TOTAL):
            user_data = {
                'username': 'automation_' + self.util.random_str(5),
                'name': 'automation ' + self.util.random_str(5),
                'phone': self.util.random_email(5),
                'email': self.util.random_email(5),
                'password': self.gk_service.HASH_PASSWORD_TEST
            }
            # create basic user - no permissions
            self.assertTrue(
                self.gk_dao.set_gk_user(
                    self.db,
                    user_data['username'],
                    user_data['password'],
                    user_data['email'],
                    user_data['name'],
                    user_data['phone']
                )
            )
            # get user_id
            user_id = self.gk_dao.get_user_by_username(
                self.db,
                user_data['username']
            )['user_id']

            #create app
            create_response = self.gk_service.gk_crud(
                a_session, method='POST', resource='application'
            )
            # ensure correct status code is returned
            self.assertEquals(
                create_response.status_code, requests.codes.created
            )
            app_id = create_response.json()['application_id']

            # associate user with app
            self.assertTrue(
                self.gk_dao.set_user_app_id(self.db, app_id, user_id)
            )

            created_user_data.append(user_data)

        # login each user and retain cookie info for use later
        for user in created_user_data:
            payload = {'username': user['username'], 'password': 'test'}
            response = self.gk_service.create_session_urlencoded(
                allow_redirects=False, credentials=payload
            )
            self.assertEquals(response.status_code, requests.codes.found)
            # extract cookie from response headers
            cookie = Cookie.SimpleCookie()
            cookie.load(response.headers['Set-Cookie'])
            user['cookie'] = cookie['sso_cookie'].value

        # create processes for each user
        processes = []
        for user in created_user_data:
            process = Process(
                target=self.gk_service.run_user_test,
                args=[user['cookie']]
            )
            process.daemon = True
            # start running user test
            process.start()
            processes.append(process)
        # wait for the child processes to finish
        for process in processes:
            process.join()

    @attr(env=['test'], priority=1)
    def test_invalid_gk_endpoint(self):
        """
        GATEKEEPER_FUNCTIONAL_003 test_invalid_gk_endpoint
        - test an invalid endpoint on gatekeeper
        - test an invlaid endpoint on the dummy app
        """

        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        # create a fake endpoint for the gk app
        gk_url = self.gk_service._create_url('fake')

        # validate a fake gatekeeper endpoint
        response = self.gk_service.validate_end_point(
            session,
            url=gk_url
        )
        # 404
        self.assertEquals(response.status_code, requests.codes.not_found)

    @attr(env=['test'], priority=1)
    def test_expired_client_cookie(self):
        """
        GATEKEEPER_FUNCTIONAL_004 test_expired_client_cookie
        creates a session through a POST to the login API and then verifies
        that a user cannot access an url using an expired cookie
        on the client side
        """
        # urlencoded post
        # create a session - do not allow redirects
        response = self.gk_service.create_session_urlencoded(
            allow_redirects=False
        )
        # 303 response
        self.assertEquals(response.status_code, requests.codes.found)

        # convert Set_Cookie response header to simple cookie object
        cookie_id = self.gk_service.extract_sso_cookie_value(
            response.headers
        )

        my_cookie = dict(name='sso_cookie', value=cookie_id, expires=-1)
        response = self.gk_service.validate_url_with_cookie(
            self.gk_service.create_requests_session_with_cookie(
                my_cookie
            )
        )

        self.assertEquals(response.status_code, requests.codes.ok)
        self.assertTrue(self.gk_service.GATEKEEPER_TITLE in response.text)

    @attr(env=['test'], priority=1)
    def test_expired_server_cookie(self):
        """
        GATEKEEPER_FUNCTIONAL_005 test_expired_server_cookie
        creates a session through a POST to the login API and then verifies
        that a user cannot access an url using an expired cookie on the
        server side
        """
         # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        # update cookie in the database so thats its expired
        self.assertTrue(
            self.gk_dao.set_session_to_expire_by_session_id(
                self.db,
                cookie_id
            )
        )

        response = self.gk_service.validate_url_with_cookie(session)

        self.assertEquals(response.status_code, requests.codes.ok)
        self.assertTrue(self.gk_service.GATEKEEPER_TITLE in response.text)

        # User login causes expired cookie to be deleted
        self.gk_service.create_session_urlencoded(
            allow_redirects=False
        )

        # assert against the database - ensure it no longer exists
        db_response = self.gk_dao.get_session_by_cookie_id(
            self.db,
            cookie_id
        )
        self.assertEquals(db_response, None)

    @attr(env=['test'], priority=1)
    def test_validate_user_access_gk_route(self):
        """
        GATEKEEPER_FUNCTIONAL_006 test_validate_user_access_gk_route
        Ensure a user with the permission gatekeeper_all
        can access the admin endpoint on gatekeeper application
        The test ensure that the endpoint cannot be acccessed
        without the permission and can be acccesed with the permission
        """

        # create a user and associate user with relevant
        # pre confiured application for dummy app

        username = 'automation_' + self.util.random_str(5)
        appname = self.gk_service.GK_APP
        fullname = 'automation_' + self.util.random_str(5)
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
        permissions = self.gk_dao.get_permission_by_name(
            self.db,
            self.gk_service.GK_ALL_PERMISSION, app_id
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

        # create a defaul url for gatekeeper app
        gk_url = self.gk_service._create_url('')

        # verify the admin endpoint can NOT be accessed
        response = self.gk_service.validate_end_point(
            session,
            end_point=config[SERVICE_NAME]['admin_endpoint'],
            url=gk_url
        )

        # ensure that the request is forbidden (403)
        self.assertEquals(response.status_code, requests.codes.forbidden)

        # set the user permission for the gatekeeper admin endpoint
        self.assertTrue(
            self.gk_dao.set_user_permissions_id(
                self.db,
                user_id,
                permissions
            )
        )

        # verify the admin endpoint can be accessed
        response = self.gk_service.validate_end_point(
            session,
            end_point=config[SERVICE_NAME]['admin_endpoint'],
            url=gk_url
        )

        # ensure that the request is ok(200)
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
            self.gk_service.GK_ALL_PERMISSION,
            response.json()['permissions'][0]
        )

        # delete user - cascade delete by default
        self.assertTrue(self.gk_dao.del_gk_user(self.db, user_id))

    @attr(env=['test'], priority=1)
    def test_validate_group_access_gk_route(self):
        """
        GATEKEEPER_FUNCTIONAL_007 test_validate_group_access_gk_route
        Ensure a group with the permission gatekeeper_all
        can access the admin endpoint on gatekeeper application
        The test ensure that the endpoint cannot be acccessed
        without the permission and can be acccesed with the permission
        """

        # create a user and associate user with relevant
        # pre confiured application for dummy app

        username = 'automation_' + self.util.random_str(5)
        appname = self.gk_service.GK_APP
        fullname = 'automation ' + self.util.random_str(5)
        email = self.util.random_email(5)
        grp_name = 'automation_' + self.util.random_str(5)

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
        permissions = self.gk_dao.get_permission_by_name(
            self.db,
            self.gk_service.GK_ALL_PERMISSION,
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

        # create a defaul url for gatekeeper app
        gk_url = self.gk_service._create_url('')

        # verify the admin endpoint can NOT be accessed
        response = self.gk_service.validate_end_point(
            session,
            end_point=config[SERVICE_NAME]['admin_endpoint'],
            url=gk_url
        )

        # ensure that the request is forbidden (403)
        self.assertEquals(response.status_code, requests.codes.forbidden)

        # set the group permission for the gatekeeper admin endpoint
        self.assertTrue(
            self.gk_dao.set_group_permission(
                self.db,
                group_id,
                permissions)
        )

        # verify the admin endpoint can be accessed
        response = self.gk_service.validate_end_point(
            session,
            end_point=config[SERVICE_NAME]['admin_endpoint'],
            url=gk_url
        )

        # ensure that the request is ok(200)
        self.assertEquals(response.status_code, requests.codes.ok)

        # Verify the user API
        response = self.gk_service.user_app(session, user_id, appname)

        self.assertEquals(response.status_code, requests.codes.ok)
        self.assertTrue(username in response.json()['username'])
        self.assertEquals([], response.json()['organizations'])
        self.assertTrue(str(user_id) in response.json()['user_id'])
        self.assertTrue(grp_name in response.json()['groups'][0])
        self.assertTrue(fullname in response.json()['fullname'])
        self.assertTrue(email in response.json()['email'])
        self.assertEquals(
            self.gk_service.GK_ALL_PERMISSION,
            response.json()['permissions'][0]
        )
        # delete the group and user

        # delete the group
        self.assertTrue(self.gk_dao.del_gk_group(self.db, group_id))
        # delete user - cascade delete by default
        self.assertTrue(self.gk_dao.del_gk_user(self.db, user_id))

    @attr(env=['test'], priority=1)
    def test_validate_user_with_no_access_for_app(self):
        """
        GATEKEEPER_FUNCTIONAL_008 test_validate_user_with_no_access_for_app
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

        # create a fake endpoint for the gk app
        gk_url = self.gk_service._create_url('fake')

        # validate a fake gatekeeper endpoint
        response = self.gk_service.validate_end_point(
            session,
            url=gk_url
        )
        # 404
        self.assertEquals(response.status_code, requests.codes.not_found)

    @attr(env=['test'], priority=1)
    def test_access_url_default_redirect(self):
        """
        GATEKEEPER_FUNCTIONAL_009 test_access_url_default_redirect
        - creates a session through a POST to the login API and then verifies
        that a user can access an url using a session with a valid cookie.
        Default redirect
        """
        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        response = self.gk_service.validate_url_with_cookie(session)

        self.assertEquals(response.status_code, requests.codes.ok)
        self.assertTrue("logout_button" in response.text)

    @attr(env=['test'], priority=1)
    def test_access_url_with_invalid_cookie(self):
        """
        GATEKEEPER_FUNCTIONAL_010 test_access_url_with_invalid_cookie
        Creates a session through a POST to the login API and then verify
        that a user CANNOT access an url using a session with a invalid cookie.
        As the session cookie is invalid the user will be prompted
        for a username and password
        """
        # create fake cookie value
        cookie_value = "fakecookie"

        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False,
            cookie_value=cookie_value
        )

        response = self.gk_service.validate_url_with_cookie(session)

        self.assertEquals(response.status_code, requests.codes.ok)
        self.assertTrue(self.gk_service.GATEKEEPER_TITLE in response.text)

    @attr(env=['test'], priority=1)
    def test_header_verification_urlencoded_session(self):
        """
        GATEKEEPER_FUNCTIONAL_011 test_header_verification_urlencoded_session
        Creates a session through a POST to the login API and then validates
        the  user_id and session_id(cookie value).
        Ensure httponly header is present
        """
        # urlencoded post
        # create a session - do not allow redirects
        response = self.gk_service.create_session_urlencoded(
            allow_redirects=False
        )
        # 303 response
        self.assertEquals(response.status_code, requests.codes.found)

        headers = response.headers['Set-Cookie']
        # assert that the header httponly is present
        if config[SERVICE_NAME]['scheme'] == 'https':
            assert 'httponly' in headers
        else:
            assert 'httponly' not in headers
