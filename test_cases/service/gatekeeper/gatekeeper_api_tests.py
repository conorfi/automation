"""
@summary: Contains a set of API tests for the gate keeper(single sign on)
project - 1 factor authentication test cases
These test have a number of dependencies
1. the database update script updates the gatekeepr schema - the script can be
found at the root of the gatekeeper app
2. the build script starts the gatekeeper app with ssl enbaled by default
3. the build script starts the dummy app with ssl enabled
and application_name is adfuser
4. The dummy app is pre-configure with two permissions
'ADFUSER_USER' and 'ADFUSER_ADMIN'

@since: Created on October 31st 2013

@author: Conor Fitzgerald

"""
import requests
from testconfig import config
from nose.plugins.attrib import attr
from framework.service.gatekeeper.gatekeeper_service import GateKeeperService
from framework.db.base_dao import BaseDAO
from framework.db.gate_keeper_dao import GateKeeperDAO
from framework.utility.utility import Utility
import Cookie
from multiprocessing import Process
import time

# adfuser is the defaut test application
DEFAULT_TEST_APP = "adfuser"
ANOTHER_TEST_APP = "anotherapp"
GK_APP = "gatekeeper"

# admin user is 'admin' and is used as the default user
ADMIN_USER = 'admin'

# default user permission configured for adfuser in the dummy app
DEFAULT_ADFUSER_USER = 'ADFUSER_USER'
# default admin permission configured for adfuser in the dummy app
DEFAULT_ADFUSER_ADMIN = 'ADFUSER_ADMIN'
# special permission that allows acess to the gk admin end point
GK_ALL_PERMISSION = "gatekeeper_all"

USER_TOTAL = 5

"""
hash of the password test - using this rather than implementing the
gatekeeper hashing function if the hashing function ever change sit will
break a number of these functions
"""
HASH_PASSWORD_TEST = (
    "pbkdf2_sha256$12000$m5uwpzIW9qaO$88p"
    "IM25AqnXu4Fgt/Xgtpp3AInYgk5sxaxJmxxpcR8A="
)
GATEKEEPER_TITLE = "<title>Gatekeeper / Arts Alliance Media</title>"
USER_ERROR = (
    "User is either not logged in or not the same"
    " user as the user described in the resource URI"
)
SESSION_FORBIDDEN = 'Forbidden session with cookie %s for application fake'
SESSION_NOT_ALLOWED = 'User not allowed access this session!'
MISSING_PARAMETERS = "Missing parameters: application_name,user_id"
CONFIRM_LOGOUT = "Please confirm logout"
NO_DATA_ERROR = "No data for ID"
DUPLICATE_KEY = "duplicate key value violates unique constraint"
MISSING_PARAM = "Missing parameter(s)"
NOT_LOGGED_IN = "Not logged in"


class TestGateKeeperAPI:

    @classmethod
    def setUpClass(cls):
        # Things that need to be done once
        cls.db = BaseDAO(config['gatekeeper']['db']['connection'])

    @classmethod
    def tearDownClass(cls):
        # Things that need to be done once.
        cls.db.close()

    def setup(self):
        # Things to run before each test.

        self.gk_service = GateKeeperService()
        self.gk_dao = GateKeeperDAO()
        self.default_test_user = self.gk_dao.get_user_by_username(
            self.db,
            ADMIN_USER
        )['user_id']
        self.util = Utility()

    @attr(env=['test'], priority=1)
    def test_can_login_with_redirect(self):
        """
        GATEKEEPER-API001 test_can_login_with_redirect - creates a session
        through a POST to the login API using urlencoded body.
        Specified redirect
        """
        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False,
            redirect_url=config['gatekeeper']['redirect']
        )

        # assert against database
        db_response = self.gk_dao.get_session_by_cookie_id(self.db, cookie_id)
        assert db_response['cookie_id'] == cookie_id
        assert db_response['user_id'] == self.default_test_user

        # create a session - allow redirects
        response = self.gk_service.create_session_urlencoded(
            allow_redirects=True,
            redirect_url=config['gatekeeper']['redirect']
        )
        # 200 response
        assert response.status_code == requests.codes.ok
        assert 'Example Domain' in response.text

    @attr(env=['test'], priority=1)
    def test_can_login_default_redirect(self):
        """
        GATEKEEPER-API002 test_can_login_default_redirect -
        creates a session through a POST to the login API using urlencoded
        body. Default redirect
        """

        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        # assert against database
        db_response = self.gk_dao.get_session_by_cookie_id(self.db, cookie_id)
        assert db_response['cookie_id'] == cookie_id
        assert db_response['user_id'] == self.default_test_user

        # create a session - allow redirects
        response = self.gk_service.create_session_urlencoded(
            allow_redirects=True
        )

        # 200 response
        assert response.status_code == requests.codes.ok

    @attr(env=['test'], priority=1)
    def test_validate_session_with_cookie_default_redirect(self):
        """
        GATEKEEPER-API003 test_validate_session_with_cookie_default_redirect
        - creates a session through a POST to the login API and then
        validates the user_id and session_id(cookie value)
        """

        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        response = self.gk_service.validate_session(
            cookie_id=cookie_id,
            session=session
        )

        assert response.status_code == requests.codes.ok
        # obtain session id and user id from database
        db_response = self.gk_dao.get_session_by_cookie_id(self.db, cookie_id)

        # assert against database
        assert response.json()['user_id'] == db_response['user_id']
        assert response.json()['session_id'] == db_response['session_id']

    @attr(env=['test'], priority=1)
    def test_validate_session_with_valid_cookie_with_redirect(self):
        """
        GATEKEEPER-API004 test_validate_session_with_valid_cookie_with_redirect
        creates a session through a POST to the login API and then verifies
        that a user can access an url using a session with a valid cookie.
        Specified redirect
        """

        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False,
            redirect_url=config['gatekeeper']['redirect']
        )

        response = self.gk_service.validate_url_with_cookie(
            session=session,
            redirect_url=config['gatekeeper']['redirect']
        )
        assert response.status_code == requests.codes.ok
        assert 'Example Domain' in response.text

    @attr(env=['test'], priority=1)
    def test_validate_session_with_application_filter(self):
        """
        GATEKEEPER-API005 test_validate_session_with_application_filter -
        creates a session through a POST to the login API and then validates
        the  user_id and session_id(cookie value)  and applciation filter
        """

        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False,
        )

        response = self.gk_service.validate_session(
            cookie_id=cookie_id,
            session=session,
            application=DEFAULT_TEST_APP
        )

        assert response.status_code == requests.codes.ok
        # obtain session id and user id from database
        db_response = self.gk_dao.get_session_by_cookie_id(self.db, cookie_id)

        # assert against database
        assert response.json()['user_id'] == db_response['user_id']
        assert response.json()['session_id'] == db_response['session_id']

    @attr(env=['test'], priority=1)
    def test_validate_session_with_invalid_cookie_id(self):
        """
        GATEKEEPER-API006 test_validate_session_with_invalid_cookie_id -
        creates a session through a POST to the login API and then verifies
        that a user cannot access an url using a session with
        invalid cookie id/session id.
        """

        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        # set cookie to invalid value
        cookie_value = "fake"

        my_cookie = dict(name='sso_cookie', value=cookie_id)
        response = self.gk_service.validate_session(
            cookie_id=cookie_value,
            session=session
        )

        assert response.status_code == requests.codes.not_found
        assert "Cookie does not exist" in response.json()['error']

    @attr(env=['test'], priority=1)
    def test_validate_session_with_no_cookie_id(self):
        """
        GATEKEEPER-API007 test_validate_session_with_no_cookie_id - creates a
        session through a POST to the login API and then verifies that a user
        cannot access an url using a session with no cookieid/session id.
        """

        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        # set cookie to empty value
        cookie_value = ''

        response = self.gk_service.validate_session(
            cookie_id=cookie_value,
            session=session
        )

        assert response.status_code == requests.codes.not_found
        assert "Missing parameters: cookie" in response.json()['error']

    @attr(env=['test'], priority=1)
    def test_validate_session_with_invalid_session(self):
        """
        GATEKEEPER-API008 test_validate_session_with_no_cookie_id - creates a
        session through a POST to the login API and then verifies that a user
        cannot access an url using an invalid session
        """

        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        # set the cookie dict being passed to the session as invalid value
        fake_value = 'fake'
        my_cookie = dict(name='sso_cookie', value=fake_value)

        response = self.gk_service.validate_session(
            cookie_id=cookie_id,
            session=self.gk_service.create_requests_session_with_cookie(
                my_cookie
            )
        )
        assert response.status_code == requests.codes.forbidden
        assert SESSION_NOT_ALLOWED in response.json()['error']

    @attr(env=['test'], priority=1)
    def test_validate_session_with_app_filter_with_no_app(self):
        """
        GATEKEEPER-API009  test_validate_session_with_app_filter_with_no_app
        creates a session through a POST to the login API and then validates
        the session by providing no application name to the application filter
        As the application filter is optional - if no application name is
        provided it as treated as if the application filter is not applied
        """

        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False,
        )

        # set application to none
        application = ''

        response = self.gk_service.validate_session(
            cookie_id=cookie_id,
            session=session,
            application=application
        )

        #
        assert response.status_code == requests.codes.ok
        # obtain session id and user id from database
        db_response = self.gk_dao.get_session_by_cookie_id(self.db, cookie_id)

        # assert against database
        assert response.json()['user_id'] == db_response['user_id']
        assert response.json()['session_id'] == db_response['session_id']

    @attr(env=['test'], priority=1)
    def test_validate_session_app_filter_with_invalid_app(self):
        """
        GATEKEEPER-API010 test_validate_session_app_filter_with_invalid_app
        - creates a session through a POST to the login API and then validates
        the session by providing an invalid application name to the
        application filter
        """
        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False,
        )

        # set application to none
        application = 'fake'

        my_cookie = dict(name='sso_cookie', value=cookie_id)
        response = self.gk_service.validate_session(
            cookie_id=cookie_id,
            session=session,
            application=application
        )

        # ensure that the request is forbidden (403)
        assert response.status_code == requests.codes.forbidden
        # ensure the correct message is returned
        error_message = SESSION_FORBIDDEN % (cookie_id)
        assert error_message in response.json()['error']

    @attr(env=['test'], priority=1)
    def test_can_access_url_with_cookie_default_redirect(self):
        """
        GATEKEEPER-API011 test_can_access_url_with_cookie_default_redirect
        - creates a session through a POST to the login API and then verifies
        that a user can access an url using a session with a valid cookie.
        Default redirect
        """
        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        response = self.gk_service.validate_url_with_cookie(session)

        assert response.status_code == requests.codes.ok
        assert "/logout/" in response.text

    @attr(env=['test'], priority=1)
    def test_access_url_with_invalid_cookie(self):
        """
        GATEKEEPER-API012 test_access_url_with_Invalid_cookie - creates a
        session through a POST to the login API and then verify that a user
        CANNOT access an url using a session with a invalid cookie.
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

        assert response.status_code == requests.codes.ok
        assert GATEKEEPER_TITLE in response.text

    @attr(env=['test'], priority=1)
    def test_expired_client_cookie(self):
        """
        GATEKEEPER-API013 test_expired_client_cookie - creates a session
        through a POST to the login API and then verifies that a user
        cannot access an url using an expired cookie on the client side
        """
        # urlencoded post
        # create a session - do not allow redirects
        response = self.gk_service.create_session_urlencoded(
            allow_redirects=False
        )
        # 303 response
        assert response.status_code == requests.codes.other
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

        assert response.status_code == requests.codes.ok
        assert GATEKEEPER_TITLE in response.text

    @attr(env=['test'], priority=1)
    def test_expired_server_cookie(self):
        """
        GATEKEEPER-API014 test_expired_server_cookie - creates a session
        through a POST to the login API and then verifies that a user
        cannot access an url using an expired cookie on the server side
        """
         # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        # update cookie in the database so thats its expired
        assert(
            self.gk_dao.set_session_to_expire_by_session_id(
                self.db,
                cookie_id
            )
        )

        response = self.gk_service.validate_url_with_cookie(session)

        assert response.status_code == requests.codes.ok
        assert GATEKEEPER_TITLE in response.text

        # User login causes expired cookie to be deleted
        response = self.gk_service.create_session_urlencoded(
            allow_redirects=False
        )

        # assert against the database - ensure it no longer exists
        db_response = self.gk_dao.get_session_by_cookie_id(
            self.db,
            cookie_id
        )
        assert db_response is None

    @attr(env=['test'], priority=1)
    def test_header_verification_urlencoded_session(self):
        """
        GATEKEEPER-API015 test_header_verification_urlencoded_session -
        creates a session through a POST to the login API and then validates
        the  user_id and session_id(cookie value).
        Ensure httponly header is present
        """
        # urlencoded post
        # create a session - do not allow redirects
        response = self.gk_service.create_session_urlencoded(
            allow_redirects=False
        )
        # 303 response
        assert response.status_code == requests.codes.other

        headers = response.headers['Set-Cookie']
        # assert that the header httponly is present
        if config['gatekeeper']['scheme'] == 'https':
            assert 'httponly' in headers
        else:
            assert 'httponly' not in headers

    @attr(env=['test'], priority=1)
    def test_can_logout_with_redirect(self):
        """
        GATEKEEPER-API016 test_can_logout_with_redirect
        Ensures a user session can be deleted using single logout
        using POST
        Specified redirect on logout
        """

         # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False,
            redirect_url=config['gatekeeper']['redirect']
        )

        response = self.gk_service.validate_url_with_cookie(
            session,
            redirect_url=config['gatekeeper']['redirect']
        )
        assert response.status_code == requests.codes.ok
        assert 'Example Domain' in response.text

        # logout with POST
        response = self.gk_service.logout_user_session(session)
        assert response.status_code == requests.codes.ok

        response = self.gk_service.validate_url_with_cookie(session)
        assert response.status_code == requests.codes.ok
        assert GATEKEEPER_TITLE in response.text

        # assert againist the database - ensure it no longer exists
        db_response = self.gk_dao.get_session_by_cookie_id(
            self.db,
            cookie_id
        )
        assert db_response is None

    @attr(env=['test'], priority=1)
    def test_can_logout_default_redirect(self):
        """
        GATEKEEPER-API017 test_can_logout_default_redirect
        Ensures a user session can be deleted using single logout
        using a POST
        Default redirect on logout
        """

        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        response = self.gk_service.validate_url_with_cookie(session)
        assert response.status_code == requests.codes.ok

        # logout with a post
        response = self.gk_service.logout_user_session(session)
        assert response.status_code == requests.codes.ok

        response = self.gk_service.validate_url_with_cookie(session)
        assert response.status_code == requests.codes.ok
        assert GATEKEEPER_TITLE in response.text

        # assert againist the database - ensure it no longer exists
        db_response = self.gk_dao.get_session_by_cookie_id(
            self.db,
            cookie_id
        )
        assert db_response is None

    @attr(env=['test'], priority=1)
    def test_can_logout_get(self):
        """
        GATEKEEPER-API017A test_can_logout_default_redirect
        Ensures the logout confirmation button is returned
        when the logout is called with a get
        Note: the python-request library can not be sued for web based tests
        so cannot click the confirmation button
        """

        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        response = self.gk_service.validate_url_with_cookie(session)
        assert response.status_code == requests.codes.ok

        # logout using GET call
        response = self.gk_service.logout_user_session_get(session)
        assert response.status_code == requests.codes.ok
        assert CONFIRM_LOGOUT in response.text

    @attr(env=['test'], priority=1)
    def test_validate_user_app_api_and_auth_app_permissions(self):
        """
        GATEKEEPER-API018 - test_validate_user_app_api_and_auth_app_permissions
        test user api and permissions for user with only app access
        Part a - Ensures user info can be return from the user api when
         a valid session,user id and application is provided for a user
        Part b  - Using the dummy application verify the end points the user
        can access when the user only has access to the dummy app
        """

        # create a user and associate user with relevant
        # pre confiured application for dummy app
        username = 'automation_' + self.util.random_str(5)
        appname = ANOTHER_TEST_APP
        fullname = 'automation ' + self.util.random_str(5)
        email = self.util.random_email(5)

        # create basic user - no permisssions
        assert (
            self.gk_dao.set_gk_user(
                self.db,
                username,
                HASH_PASSWORD_TEST,
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
        assert(self.gk_dao.set_user_app_id(self.db, app_id, user_id))

        # create a session for the user
        credentials_payload = {'username': username, 'password': 'test'}

        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False,
            credentials=credentials_payload
        )

        # Verify the user API
        response = self.gk_service.user_info(session, user_id, appname)
        assert response.status_code == requests.codes.ok

        assert username in response.json()['username']
        assert [] == response.json()['organizations']
        assert str(user_id) in response.json()['user_id']
        assert [] == response.json()['groups']
        assert fullname in response.json()['fullname']
        assert email in response.json()['email']
        assert [] == response.json()['permissions']

        # Using the dummy application verify the permissions
        # the user is authorized for

        # verify the dummy applcation can be accessed
        response = self.gk_service.validate_end_point(session)
        assert response.status_code == requests.codes.ok

        # verify the user end point cannot be accessed
        response = self.gk_service.validate_end_point(
            session,
            end_point=config['gatekeeper']['dummy']['user_endpoint']
        )

        assert response.status_code == requests.codes.forbidden

        # verify the admin end point cannot be accessed
        response = self.gk_service.validate_end_point(
            session,
            end_point=config['gatekeeper']['dummy']['admin_endpoint']
        )
        assert response.status_code == requests.codes.forbidden

        # delete user - cascade delete by default
        assert (self.gk_dao.del_gk_user(self.db, user_id))

    @attr(env=['test'], priority=1)
    def test_validate_user_with_no_access_for_application(self):
        """
        GATEKEEPER-API018A
        Ensure that user returns 403 when it tries to access an application
        that it has assosation with
        """

        # create a user and associate user with relevant
        # pre confiured application for dummy app
        username = 'automation_' + self.util.random_str(5)
        fullname = 'automation ' + self.util.random_str(5)
        email = self.util.random_email(5)

        # create basic user - no permisssions
        assert (
            self.gk_dao.set_gk_user(
                self.db,
                username,
                HASH_PASSWORD_TEST,
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
            end_point=config['gatekeeper']['dummy']['user_endpoint']
        )
        assert response.status_code == requests.codes.forbidden
        response = self.gk_service.validate_end_point(
            session,
            end_point=config['gatekeeper']['dummy']['admin_endpoint']
        )
        assert response.status_code == requests.codes.forbidden

    @attr(env=['test'], priority=1)
    def test_validate_user_app_api_and_auth_user_permissions(self):
        """
        GATEKEEPER-API019 test_validate_user_app_api_and_auth_user_permissions
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
        appname = ANOTHER_TEST_APP
        fullname = 'automation ' + self.util.random_str(5)
        email = self.util.random_email(5)

        # create basic user - no permisssions
        assert (
            self.gk_dao.set_gk_user(
                self.db, username,
                HASH_PASSWORD_TEST,
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
        user_permission = self.gk_dao.get_permission_id_by_name(
            self.db,
            DEFAULT_ADFUSER_USER, app_id
        )['permission_id']
        admin_permission = self.gk_dao.get_permission_id_by_name(
            self.db,
            DEFAULT_ADFUSER_ADMIN, app_id
        )['permission_id']

        # associate user with app
        assert(self.gk_dao.set_user_app_id(self.db, app_id, user_id))

        # create a session for the user
        credentials_payload = {'username': username, 'password': 'test'}

        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False,
            credentials=credentials_payload
        )

        # set the user permissions for the app
        # i.e user can only access the dummy application and user end point

        assert (
            self.gk_dao.set_user_permissions_id(
                self.db,
                user_id,
                user_permission
            )
        )

        # Using the dummy application verify the permissions for the user

        # verify the dummy applcation can be accessed
        response = self.gk_service.validate_end_point(session)
        assert response.status_code == requests.codes.ok

        # verify the user end point can be accessed
        response = self.gk_service.validate_end_point(
            session,
            end_point=config['gatekeeper']['dummy']['user_endpoint']
        )
        assert response.status_code == requests.codes.ok

        # verify the admin end point cannot be accessed
        response = self.gk_service.validate_end_point(
            session,
            end_point=config['gatekeeper']['dummy']['admin_endpoint']
        )
        assert response.status_code == requests.codes.forbidden

        # set the admin permissions for the app
        # i.e user can access admin end point

        assert (
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
        assert response.status_code == requests.codes.ok

        # verify the user end point can be accessed
        response = self.gk_service.validate_end_point(
            session,
            end_point=config['gatekeeper']['dummy']['user_endpoint'],
            parameters=parameters
        )
        assert response.status_code == requests.codes.ok

        # verify the admin end point can be accessed
        response = self.gk_service.validate_end_point(
            session,
            end_point=config['gatekeeper']['dummy']['admin_endpoint'],
            parameters=parameters
        )
        assert response.status_code == requests.codes.ok

        # Verify the user API
        response = self.gk_service.user_info(session, user_id, appname)
        assert response.status_code == requests.codes.ok
        assert username in response.json()['username']
        assert [] == response.json()['organizations']
        assert str(user_id) in response.json()['user_id']
        assert [] == response.json()['groups']
        assert fullname in response.json()['fullname']
        assert email in response.json()['email']
        assert DEFAULT_ADFUSER_ADMIN == response.json()['permissions'][0]
        assert DEFAULT_ADFUSER_USER == response.json()['permissions'][1]

        # delete user - cascade delete by default
        assert (self.gk_dao.del_gk_user(self.db, user_id))

    @attr(env=['test'], priority=1)
    def test_validate_user_app_api_and_auth_group_permissions(self):
        """
        GATEKEEPER-API020 test_validate_user_app_api_and_auth_group_permissions
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
        appname = ANOTHER_TEST_APP
        fullname = 'automation ' + self.util.random_str(5)
        email = self.util.random_email(5)
        grp_name = 'automation_' + self.util.random_str(5)
        grp_name_2 = 'automation_' + self.util.random_str(5)

        # create basic user - no permisssions
        assert (
            self.gk_dao.set_gk_user(
                self.db,
                username,
                HASH_PASSWORD_TEST,
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
        user_permission = self.gk_dao.get_permission_id_by_name(
            self.db,
            DEFAULT_ADFUSER_USER,
            app_id
        )['permission_id']

        admin_permission = self.gk_dao.get_permission_id_by_name(
            self.db,
            DEFAULT_ADFUSER_ADMIN,
            app_id
        )['permission_id']

        # associate user with app
        assert(self.gk_dao.set_user_app_id(self.db, app_id, user_id))

        # creat gatekeeper group
        assert (self.gk_dao.set_gk_group(self.db, grp_name))
        # get group id
        group_id = self.gk_dao.get_gk_group_id_by_name(
            self.db,
            grp_name
        )['group_id']

        # associate user with group
        assert(self.gk_dao.set_user_group(self.db, user_id, group_id))

        # associate group with application
        assert(self.gk_dao.set_group_app_id(self.db, app_id, group_id))

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
        assert(
            self.gk_dao.set_group_permission(
                self.db,
                group_id,
                user_permission)
        )

        # Using the dummy application
        # verify the permissions the user is authorized

        # verify the dummy applcation can be accessed
        response = self.gk_service.validate_end_point(session)
        assert response.status_code == requests.codes.ok

        # verify the user end point can be accessed
        response = self.gk_service.validate_end_point(
            session,
            end_point=config['gatekeeper']['dummy']['user_endpoint']
        )
        assert response.status_code == requests.codes.ok

        # verify the admin end point cannot be accessed
        response = self.gk_service.validate_end_point(
            session,
            end_point=config['gatekeeper']['dummy']['admin_endpoint']
        )
        assert response.status_code == requests.codes.forbidden

        # set the group permissions for the app
        # i.e user can access the admin endpoint

        # set group permission for admin access
        assert(
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
        assert response.status_code == requests.codes.ok

        # verify the user end point can be accessed
        response = self.gk_service.validate_end_point(
            session,
            end_point=config['gatekeeper']['dummy']['user_endpoint'],
            parameters=parameters
        )
        assert response.status_code == requests.codes.ok

        # verify the admin end point cannot be accessed
        response = self.gk_service.validate_end_point(
            session,
            end_point=config['gatekeeper']['dummy']['admin_endpoint'],
            parameters=parameters
        )
        assert response.status_code == requests.codes.ok

        # Verify the user API
        response = self.gk_service.user_info(
            session,
            user_id,
            appname
        )
        assert response.status_code == requests.codes.ok

        assert username in response.json()['username']
        assert [] == response.json()['organizations']
        assert str(user_id) in response.json()['user_id']
        assert grp_name in response.json()['groups'][0]
        assert fullname in response.json()['fullname']
        assert email in response.json()['email']
        assert DEFAULT_ADFUSER_ADMIN == response.json()['permissions'][0]
        assert DEFAULT_ADFUSER_USER == response.json()['permissions'][1]

        # create another group, associate with the user but not the application
        # this group should NOT be retured by the API

        # create gatekeeper group
        assert(
            self.gk_dao.set_gk_group(
                self.db,
                grp_name_2
            )
        )
        # get group id
        group_id_2 = self.gk_dao.get_gk_group_id_by_name(
            self.db,
            grp_name_2
        )['group_id']

        # associate user with group
        assert(self.gk_dao.set_user_group(self.db, user_id, group_id_2))

        # user API response
        response = self.gk_service.user_info(session, user_id, appname)
        assert response.status_code == requests.codes.ok
        # ensure that only 1 group is associate with the application/user
        assert 1 == len(response.json()['groups'])

        # delete the group and user
        # delete the group
        assert (self.gk_dao.del_gk_group(self.db, group_id))

        # delete user - cascade delete by default
        assert (self.gk_dao.del_gk_user(self.db, user_id))

    @attr(env=['test'], priority=1)
    def test_user_info_with_invalid_cookie_session(self):
        """
        GATEKEEPER-API021 test_user_info_with_invalid_cookie_session
        Ensures user info CANNOT be return from the user api when a invalid
        session is provided
        """

        cookie_value = "fakecookie"

        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False,
            redirect_url=config['gatekeeper']['redirect'],
            cookie_value=cookie_value
        )

        response = self.gk_service.user_info(
            session,
            self.default_test_user,
            DEFAULT_TEST_APP
        )
        # ensure that the request is forbidden(403)
        # without a valid session cookie
        assert response.status_code == requests.codes.forbidden
        assert USER_ERROR in response.json()['error']

    @attr(env=['test'], priority=1)
    def test_return_user_info_with_invalid_application(self):
        """
        GATEKEEPER-API022 test_return_user_info_with_invalid_application
        Ensures user info CANNOT be return from the user api when a invalid
        application is provided
        """

        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False,
            redirect_url=config['gatekeeper']['redirect']
        )

        fake_application = "fake"
        response = self.gk_service.user_info(
            session,
            self.default_test_user,
            fake_application
        )

        # ensure it returns a 404 not found
        assert response.status_code == requests.codes.not_found

        assert "No user with id" in response.json()['error']
        assert "found for application" in response.json()['error']

    @attr(env=['test'], priority=1)
    def test_return_user_info_with_invalid_user_id(self):
        """
        GATEKEEPER-API023 test_return_user_info_with_invalid_user_id
        Ensures user info CANNOT be return from the user api when a invalid
        user id is provided
        """
        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False,
            redirect_url=config['gatekeeper']['redirect']
        )

        # add one to the user id to create a random element to userid
        random_user_id = self.gk_dao.get_user_by_username(
            self.db,
            ADMIN_USER
        )['user_id'] + 1

        response = self.gk_service.user_info(
            session,
            random_user_id,
            DEFAULT_TEST_APP
        )
        # ensure that the request is forbidden(403)
        # without a valid session cookie
        assert response.status_code == requests.codes.forbidden
        assert USER_ERROR in response.json()['error']

    @attr(env=['test'], priority=1)
    def test_return_user_info_with_no_args(self):
        '''
        GATEKEEPER-API024 test_return_user_info_with_no_user_id -
        Ensures user info CANNOT be return from the user api when no
        user id or application name is provided
        '''
        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False,
            redirect_url=config['gatekeeper']['redirect']
        )

        response = self.gk_service.user_info(session, '', '')

        # a 404 will alwasy be returend
        assert response.status_code == requests.codes.not_found
        assert MISSING_PARAMETERS in response.json()['error']

    @attr(env=['test'], priority=1)
    def test_validate_user_access_gk_route(self):
        """
        GATEKEEPER-API025 test_validate_user_access_gk_route
        Ensure a user with the permission gatekeeper_all
        can access the admin endpoint on gatekeeper application
        The test ensure that the endpoint cannot be acccessed
        without the permission and can be acccesed with the permission
        """

        # create a user and associate user with relevant
        # pre confiured application for dummy app

        username = 'automation_' + self.util.random_str(5)
        appname = GK_APP
        fullname = 'automation_' + self.util.random_str(5)
        email = self.util.random_email(5)

        # create basic user - no permisssions
        assert (
            self.gk_dao.set_gk_user(
                self.db, username,
                HASH_PASSWORD_TEST,
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
        gk_all_permission = self.gk_dao.get_permission_id_by_name(
            self.db,
            GK_ALL_PERMISSION, app_id
        )['permission_id']

        # associate user with app
        assert(self.gk_dao.set_user_app_id(self.db, app_id, user_id))

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
            end_point=config['gatekeeper']['admin_endpoint'],
            url=gk_url
        )

        # ensure that the request is forbidden (403)
        assert response.status_code == requests.codes.forbidden

        # set the user permission for the gatekeeper admin endpoint
        assert (
            self.gk_dao.set_user_permissions_id(
                self.db,
                user_id,
                gk_all_permission
            )
        )

        # verify the admin endpoint can be accessed
        response = self.gk_service.validate_end_point(
            session,
            end_point=config['gatekeeper']['admin_endpoint'],
            url=gk_url
        )

        # ensure that the request is ok(200)
        assert response.status_code == requests.codes.ok

        # Verify the user API
        response = self.gk_service.user_info(session, user_id, appname)
        assert response.status_code == requests.codes.ok
        assert username in response.json()['username']
        assert [] == response.json()['organizations']
        assert str(user_id) in response.json()['user_id']
        assert [] == response.json()['groups']
        assert fullname in response.json()['fullname']
        assert email in response.json()['email']
        assert GK_ALL_PERMISSION == response.json()['permissions'][0]

        # delete user - cascade delete by default
        assert (self.gk_dao.del_gk_user(self.db, user_id))

    @attr(env=['test'], priority=1)
    def test_validate_group_access_gk_route(self):
        """
        GATEKEEPER-API026 test_validate_group_access_gk_route
        Ensure a group with the permission gatekeeper_all
        can access the admin endpoint on gatekeeper application
        The test ensure that the endpoint cannot be acccessed
        without the permission and can be acccesed with the permission
        """

        # create a user and associate user with relevant
        # pre confiured application for dummy app

        username = 'automation_' + self.util.random_str(5)
        appname = GK_APP
        fullname = 'automation ' + self.util.random_str(5)
        email = self.util.random_email(5)
        grp_name = 'automation_' + self.util.random_str(5)

        # create basic user - no permisssions
        assert (
            self.gk_dao.set_gk_user(
                self.db,
                username,
                HASH_PASSWORD_TEST,
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
        gk_all_permission = self.gk_dao.get_permission_id_by_name(
            self.db,
            GK_ALL_PERMISSION,
            app_id
        )['permission_id']

        # associate user with app
        assert(self.gk_dao.set_user_app_id(self.db, app_id, user_id))

        # creat gatekeeper group
        assert (self.gk_dao.set_gk_group(self.db, grp_name))
        # get group id
        group_id = self.gk_dao.get_gk_group_id_by_name(
            self.db,
            grp_name
        )['group_id']

        # associate user with group
        assert(self.gk_dao.set_user_group(self.db, user_id, group_id))

        # associate group with application
        assert(self.gk_dao.set_group_app_id(self.db, app_id, group_id))

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
            end_point=config['gatekeeper']['admin_endpoint'],
            url=gk_url
        )

        # ensure that the request is forbidden (403)
        assert response.status_code == requests.codes.forbidden

        # set the group permission for the gatekeeper admin endpoint
        assert(
            self.gk_dao.set_group_permission(
                self.db,
                group_id,
                gk_all_permission)
        )

        # verify the admin endpoint can be accessed
        response = self.gk_service.validate_end_point(
            session,
            end_point=config['gatekeeper']['admin_endpoint'],
            url=gk_url
        )

        # ensure that the request is ok(200)
        assert response.status_code == requests.codes.ok

        # Verify the user API
        response = self.gk_service.user_info(session, user_id, appname)

        assert response.status_code == requests.codes.ok
        assert username in response.json()['username']
        assert [] == response.json()['organizations']
        assert str(user_id) in response.json()['user_id']
        assert grp_name in response.json()['groups'][0]
        assert fullname in response.json()['fullname']
        assert email in response.json()['email']
        assert GK_ALL_PERMISSION == response.json()['permissions'][0]

        # delete the group and user

        # delete the group
        assert (self.gk_dao.del_gk_group(self.db, group_id))
        # delete user - cascade delete by default
        assert (self.gk_dao.del_gk_user(self.db, user_id))

    @attr(env=['test'], priority=1)
    def test_application_api_create(self):
        """
        GATEKEEPER-API027 test_application_api_create
        create a new application using the application api,
        clean up the data (implictly tests DELETE and GET)
        """
        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        # create a new application
        create_response = self.gk_service.application(
            session, method='POST'
        )
        # ensure correct status code is returned
        assert create_response.status_code == requests.codes.created

        app_id = create_response.json()['application_id']
        appname = create_response.json()['name']
        # get app data
        app_data = self.gk_dao.get_app_by_app_name(
            self.db,
            appname
        )
        # verify the post data againist the db data
        assert (
            create_response.json()['application_id']
            == app_data['application_id']
        )
        assert (
            create_response.json()['name']
            == app_data['name']
        )
        assert (
            create_response.json()['default_url']
            == app_data['default_url']
        )

        # clean up - delete the application
        del_response = self.gk_service.application(
            session, method='DELETE', app_id=app_id
        )
        # ensure correct status code is returned
        assert del_response.status_code == requests.codes.no_content

        # read the data
        read_response = self.gk_service.application(
            session, method='GET', app_id=app_id
        )
        assert NO_DATA_ERROR in read_response.json()['error']

    @attr(env=['test'], priority=1)
    def test_application_api_create_duplicate_name(self):
        """
        GATEKEEPER-API028 test_application_api_create_duplicate_name
        create a new application using the application api,
        then attempt to create an application with the same name
        clean up the data (implictly tests DELETE and GET)
        """

         # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        new_app = self.util.random_str(5)
        name_dict = {'name': new_app}
        app_data = self.gk_service.create_app_data(name_dict)

        # create the new application
        response = self.gk_service.application(
            session, method='POST', app_data=app_data
        )
        # capture the application id
        app_id = response.json()['application_id']
        # ensure correct status code is returned
        assert response.status_code == requests.codes.created

        # attempt to use the same data with the same app name again
        response = self.gk_service.application(
            session, method='POST', app_data=app_data
        )
        # ensure correct status code is returned
        assert response.status_code == requests.codes.conflict
        assert DUPLICATE_KEY in response.json()['error']

        # clean up - delete the application
        del_response = self.gk_service.application(
            session, method='DELETE', app_id=app_id
        )
        # ensure correct status code is returned
        assert del_response.status_code == requests.codes.no_content

        # read the new application data
        read_response = self.gk_service.application(
            session, method='GET', app_id=app_id
        )
        assert NO_DATA_ERROR in read_response.json()['error']

    @attr(env=['test'], priority=1)
    def test_application_api_create_missing_params(self):
        """
        GATEKEEPER-API029 test_application_api_create_no_data
        attempt to create a new application missing paramters
        """
        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        # list of dicts with missing data
        no_data = [
            {'name': None},
            {'default_url': None},
        ]

        for app_dict in no_data:

            app_data = self.gk_service.create_app_data(app_dict)
            create_response = self.gk_service.application(
                session, method='POST', app_data=app_data
            )
            assert (
                create_response.status_code ==
                requests.codes.bad_request
            )
            assert MISSING_PARAM in create_response.json()['error']

    @attr(env=['test'], priority=1)
    def test_application_api_update(self):
        """
        GATEKEEPER-API030 test_application_api_update
        update an application using the application api,
        verify the repposne with the read function
        clean up the data (implictly tests DELETE and GET)
        """

        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        # create a new application
        create_response = self.gk_service.application(
            session, method='POST'
        )
        # ensure a 200 is returned
        assert create_response.status_code == requests.codes.created
        app_id = create_response.json()['application_id']

        # update the application

        update_response = self.gk_service.application(
            session, method='PUT', app_id=app_id
        )

        # ensure a 202 is returned
        assert update_response.status_code == requests.codes.accepted

        app_id = update_response.json()['application_id']
        appname = update_response.json()['name']
        # get app data
        app_data = self.gk_dao.get_app_by_app_name(
            self.db,
            appname
        )

        # verify the post data againist the db data
        assert (
            update_response.json()['application_id']
            == app_data['application_id']
        )
        assert (
            update_response.json()['name']
            == app_data['name']
        )
        assert (
            update_response.json()['default_url']
            == app_data['default_url']
        )

        # clean up - delete the application
        del_response = self.gk_service.application(
            session, method='DELETE', app_id=app_id
        )
        # ensure a 204 is returned
        assert del_response.status_code == requests.codes.no_content

        # read the new application data
        read_response = self.gk_service.application(
            session, method='GET', app_id=app_id
        )
        assert NO_DATA_ERROR in read_response.json()['error']

    @attr(env=['test'], priority=1)
    def test_application_api_update_individually(self):
        """
        GATEKEEPER-API030A test_application_api_update_individually
        update application fields individually using the application api,
        verify the repposne with the read function
        clean up the data (implictly tests DELETE and GET)
        """
        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        # create a new application
        create_response = self.gk_service.application(
            session, method='POST'
        )
        # ensure a 201 is returned
        assert create_response.status_code == requests.codes.created
        app_id = create_response.json()['application_id']

        # update the application
        rand_str = self.util.random_str(5)
        update_data = [
            {'name': rand_str},
            {'default_url': rand_str},
        ]

        for app_dict in update_data:
            app_data = self.gk_service.create_app_data(app_dict)
            update_response = self.gk_service.application(
                session, method='PUT', app_data=app_data, app_id=app_id
            )
            # ensure a 202 is returned
            assert update_response.status_code == requests.codes.accepted

        appname = update_response.json()['name']
        # get app data from db
        app_data = self.gk_dao.get_app_by_app_name(
            self.db,
            appname
        )

        # verify the update data againist the db data
        assert (
            update_response.json()['application_id']
            == app_data['application_id']
        )
        assert (
            update_response.json()['name']
            == app_data['name']
        )
        assert (
            update_response.json()['default_url']
            == app_data['default_url']
        )

        # clean up - delete the application
        del_response = self.gk_service.application(
            session, method='DELETE', app_id=app_id
        )
        # ensure correct status code is returned
        assert del_response.status_code == requests.codes.no_content

        # read the new application data
        read_response = self.gk_service.application(
            session, method='GET', app_id=app_id
        )
        assert NO_DATA_ERROR in read_response.json()['error']

    @attr(env=['test'], priority=1)
    def test_application_api_update_duplicate_name(self):
        """
        GATEKEEPER-API032 test_application_api_update_duplicate_name
        attempt to update an application using the application api but
        the app name should not be unique
        clean up the data (implictly tests DELETE and GET)
        """

        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        app_one = self.util.random_str(5)
        app_two = self.util.random_str(5)
        url_one = self.util.random_url(5)
        url_two = self.util.random_url(5)
        app_one_data = {'name': app_one, 'default_url': url_one}
        app_two_data = {'name': app_two, 'default_url': url_two}

        # create  application one
        app_one_response = self.gk_service.application(
            session, method='POST', app_data=app_one_data
        )
        # ensure correct status code is returned
        assert app_one_response.status_code == requests.codes.created
        app_id_one = app_one_response.json()['application_id']

        # create  application two
        app_two_response = self.gk_service.application(
            session, method='POST', app_data=app_two_data
        )
        # ensure correct status code is returned
        assert app_two_response.status_code == requests.codes.created

        # update the application one with application two data
        update_response = self.gk_service.application(
            session, method='PUT', app_data=app_two_data, app_id=app_id_one
        )

        # ensure correct status code is returned
        assert update_response.status_code == requests.codes.conflict
        assert DUPLICATE_KEY in update_response.json()['error']
        # clean up - delete the application
        del_response = self.gk_service.application(
            session, method='DELETE', app_id=app_id_one
        )
        # ensure correct status code is returned
        assert del_response.status_code == requests.codes.no_content

        # read the new application data
        read_response = self.gk_service.application(
            session, method='GET', app_id=app_id_one
        )
        assert NO_DATA_ERROR in read_response.json()['error']

    @attr(env=['test'], priority=1)
    def test_application_api_read(self):
        """
        GATEKEEPER-API033 test_application_api_read
        read an application data using the application api
        clean up the data (implictly tests DELETE and GET)
        """
        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        # create a new application
        create_response = self.gk_service.application(
            session, method='POST'
        )
        # ensure a 201 is returned
        assert create_response.status_code == requests.codes.created
        app_id = create_response.json()['application_id']

        # update the application

        read_response = self.gk_service.application(
            session, method='GET', app_id=app_id
        )

        # ensure a 200 is returned
        assert read_response.status_code == requests.codes.ok

        app_id = read_response.json()['application_id']
        appname = read_response.json()['name']
        # get app data from db
        app_data = self.gk_dao.get_app_by_app_name(
            self.db,
            appname
        )

        # verify the post data againist the db data
        assert (
            read_response.json()['application_id']
            == app_data['application_id']
        )
        assert (
            read_response.json()['name']
            == app_data['name']
        )
        assert (
            read_response.json()['default_url']
            == app_data['default_url']
        )

        # clean up - delete the application
        del_response = self.gk_service.application(
            session, method='DELETE', app_id=app_id
        )
        # ensure a 204 is returned
        assert del_response.status_code == requests.codes.no_content

        # read the new application data
        read_response = self.gk_service.application(
            session, method='GET', app_id=app_id
        )
        assert NO_DATA_ERROR in read_response.json()['error']

    @attr(env=['test'], priority=1)
    def test_application_api_update_not_existant_app_id(self):
        """
        GATEKEEPER-API033A test_application_api_invalid_app_id
        attempt to update an application with an app_id that dosen't exist
        """
        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        update_app = self.util.random_str(5)
        update_url = self.util.random_url(5)
        app_data = {'name': update_app, 'default_url': update_url}

        # create random integer for the application id
        app_id = self.util.random_int()

        # update the application
        update_response = self.gk_service.application(
            session, method='PUT', app_data=app_data, app_id=app_id
        )

        # 404 response
        assert update_response.status_code == requests.codes.not_found
        # verify that the error message is correct
        assert NO_DATA_ERROR in update_response.json()['error']

    @attr(env=['test'], priority=1)
    def test_application_api_read_not_existant_app_id(self):
        """
        GATEKEEPER-API034 test_application_api_invalid_app_id
        attempt to read an application with an app_id that dosen't exist
        """
        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        # create random integer for the application id
        app_id = self.util.random_int()

        # read the new application data
        read_response = self.gk_service.application(
            session, method='GET', app_id=app_id
        )

        # 404 response
        assert read_response.status_code == requests.codes.not_found
        # verify that the error message is correct
        assert NO_DATA_ERROR in read_response.json()['error']

    @attr(env=['test'], priority=1)
    def test_application_api_delete(self):
        """
        GATEKEEPER-API034 test_application_api_delete
        delete an application using the application api
        This test case is to have a test case that explictly
        tests the delete functioanlity
        """
        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        new_app = self.util.random_str(5)
        new_url = self.util.random_url(5)
        app_data = {'name': new_app, 'default_url': new_url}

        # create a new application
        create_response = self.gk_service.application(
            session, method='POST', app_data=app_data
        )
        # ensure correct status code is returned
        assert create_response.status_code == requests.codes.created

        app_id = create_response.json()['application_id']

        # read the new application data
        read_response = self.gk_service.application(
            session, method='GET', app_id=app_id
        )
        # ensure correct status code is returned
        assert read_response.status_code == requests.codes.ok

        # clean up - delete the application
        del_response = self.gk_service.application(
            session, method='DELETE', app_id=app_id
        )
        # ensure correct status code is returned
        assert del_response.status_code == requests.codes.no_content
        # ensure no response is returned
        assert len(del_response.content) == 0

        # read the new application data
        read_response = self.gk_service.application(
            session, method='GET', app_id=app_id
        )
        assert NO_DATA_ERROR in read_response.json()['error']

    @attr(env=['test'], priority=1)
    def test_application_api_delete_not_existant_app_id(self):
        """
        GATEKEEPER-API036 test_application_api_invalid_app_id
        attempt to delete an application with an app_id that dosen't exist
        """
        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        # create random integer for the application id
        app_id = self.util.random_int()

        # read the new application data
        read_response = self.gk_service.application(
            session, method='DELETE', app_id=app_id
        )

        # 404 response
        assert read_response.status_code == requests.codes.not_found
        # verify that the error message is correct
        assert NO_DATA_ERROR in read_response.json()['error']

    @attr(env=['test'], priority=1)
    def test_user_api_create(self):
        """
        GATEKEEPER-API037 test_user_api_create
        create a new user using the user api,
        clean up the data (implictly tests DELETE and GET)
        """
        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        # create a new application
        create_response = self.gk_service.user(
            session, method='POST'
        )

        # ensure a 201 is returned
        assert create_response.status_code == requests.codes.created

        # set username
        username = create_response.json()['username']
        # get user data directly from database
        user_info = self.gk_dao.get_user_by_username(self.db, username)

        # verify the creation of the user POST action
        assert create_response.json()['username'] == user_info['username']
        assert create_response.json()['user_id'] == user_info['user_id']
        assert create_response.json()['name'] == user_info['name']
        assert create_response.json()['phone'] == user_info['phone']
        assert create_response.json()['email'] == user_info['email']
        assert (
            create_response.json()['last_logged_in']
            == user_info['last_logged_in']
        )

        # set user_id
        user_id = create_response.json()['user_id']
        # clean up - delete the application
        del_response = self.gk_service.user(
            session, method='DELETE', user_id=user_id
        )
        # ensure a 204 is returned
        assert del_response.status_code == requests.codes.no_content

        # read the new application data
        read_response = self.gk_service.user(
            session, method='GET', user_id=user_id
        )
        assert NO_DATA_ERROR in read_response.json()['error']

    @attr(env=['test'], priority=1)
    def test_user_api_create_missing_params(self):
        """
        GATEKEEPER-API038 test_user_api_create_missing_params
        attempt to create a new user using the user api with missing params
        """
        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        # list of dicts with missing data
        no_data = [
            {'username': None},
            {'name': None},
            {'phone': None},
            {'email': None},
            {'password': None}
        ]

        for user_dict in no_data:

            user_data = self.gk_service.create_user_data(user_dict)
            create_response = self.gk_service.user(
                session, method='POST', user_data=user_data
            )
            assert create_response.status_code == requests.codes.bad_request
            assert MISSING_PARAM in create_response.json()['error']

    @attr(env=['test'], priority=1)
    def test_user_api_create_duplicate_username(self):
        """
        GATEKEEPER-API039 test_user_api_create_duplicate_username
        attempt to create a new user using the user api with same params
        """

        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        user_data = self.gk_service.create_user_data()
        # create a new application
        create_response = self.gk_service.user(
            session, method='POST', user_data=user_data
        )

        # ensure a 201 is returned
        assert create_response.status_code == requests.codes.created

        create_response = self.gk_service.user(
            session, method='POST', user_data=user_data
        )

        assert create_response.status_code == requests.codes.conflict
        assert DUPLICATE_KEY in create_response.json()['error']

    @attr(env=['test'], priority=1)
    def test_user_api_update(self):
        """
        GATEKEEPER-API040 test_user_api_update
        update all the user data using the user api
        """

        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        # create a new application
        create_response = self.gk_service.user(
            session, method='POST'
        )

        # ensure a 201 is returned
        assert create_response.status_code == requests.codes.created
        # set user_id
        user_id = create_response.json()['user_id']

        # update application
        update_response = self.gk_service.user(
            session, method='PUT', user_id=user_id
        )

        # set username
        username = update_response.json()['username']

        # get user_info directly from database
        user_info = self.gk_dao.get_user_by_username(self.db, username)

        # verify the creation of the user POST action
        assert update_response.json()['username'] == user_info['username']
        assert update_response.json()['user_id'] == user_info['user_id']
        assert update_response.json()['name'] == user_info['name']
        assert update_response.json()['phone'] == user_info['phone']
        assert update_response.json()['email'] == user_info['email']
        assert (
            update_response.json()['last_logged_in']
            == user_info['last_logged_in']
        )

        # clean up - delete the application
        del_response = self.gk_service.user(
            session, method='DELETE', user_id=user_id
        )
        # ensure a 204 is returned
        assert del_response.status_code == requests.codes.no_content

        # read the new application data
        read_response = self.gk_service.user(
            session, method='GET', user_id=user_id
        )
        assert NO_DATA_ERROR in read_response.json()['error']

    @attr(env=['test'], priority=1)
    def test_user_api_update_duplicate_name(self):
        """
        GATEKEEPER-API040A test_user_api_update_duplicate_name
        attempt to update an user using the user api but
        the username should not be unique
        clean up the data (implictly tests DELETE and GET)
        """

        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        rand_username = self.util.random_str(5)
        user_one_data = self.gk_service.create_user_data()
        user_two_data = self.gk_service.create_user_data()
        # create user one
        user_one_response = self.gk_service.user(
            session, method='POST', user_data=user_one_data
        )
        # ensure correct status code is returned
        assert user_one_response.status_code == requests.codes.created
        user_id_one = user_one_response.json()['user_id']

        # create user two
        user_two_response = self.gk_service.user(
            session, method='POST', user_data=user_two_data
        )
        # ensure correct status code is returned
        assert user_two_response.status_code == requests.codes.created

        # update the application one with application two data
        update_response = self.gk_service.user(
            session, method='PUT', user_data=user_two_data, user_id=user_id_one
        )

        # ensure correct status code is returned
        assert update_response.status_code == requests.codes.conflict
        assert DUPLICATE_KEY in update_response.json()['error']
        # clean up - delete the application
        del_response = self.gk_service.user(
            session, method='DELETE', user_id=user_id_one
        )
        # ensure correct status code is returned
        assert del_response.status_code == requests.codes.no_content

        # read the new application data
        read_response = self.gk_service.user(
            session, method='GET', user_id=user_id_one
        )
        assert NO_DATA_ERROR in read_response.json()['error']

    @attr(env=['test'], priority=1)
    def test_user_api_update_individually(self):
        """
        GATEKEEPER-API041  test_user_api_update_individually
        update fields individually
        """
        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        # create a new application
        create_response = self.gk_service.user(
            session, method='POST'
        )

        # ensure a 201 is returned
        assert create_response.status_code == requests.codes.created
        # set user_id
        user_id = create_response.json()['user_id']

        # create individual dicts for updating each paramater
        rand_str = self.util.random_str(5)
        phone = self.util.phone_number()
        email = self.util.random_email()
        user_dict = [
            {'username': rand_str},
            {'name': rand_str},
            {'phone': phone},
            {'email': email},
            {'password': rand_str}
        ]

        for data in user_dict:
            user_data = self.gk_service.create_user_data(data)
            update_response = self.gk_service.user(
                session, method='PUT', user_data=user_data, user_id=user_id
            )

        # set username
        username = update_response.json()['username']

        # get user_info directly from database
        user_info = self.gk_dao.get_user_by_username(self.db, username)

        # verify the creation of the user POST action
        assert update_response.json()['username'] == user_info['username']
        assert update_response.json()['user_id'] == user_info['user_id']
        assert update_response.json()['name'] == user_info['name']
        assert update_response.json()['phone'] == user_info['phone']
        assert update_response.json()['email'] == user_info['email']
        assert (
            update_response.json()['last_logged_in']
            == user_info['last_logged_in']
        )

        # clean up - delete the application
        del_response = self.gk_service.user(
            session, method='DELETE', user_id=user_id
        )
        # ensure a 204 is returned
        assert del_response.status_code == requests.codes.no_content

        # read the new application data
        read_response = self.gk_service.user(
            session, method='GET', user_id=user_id
        )
        assert NO_DATA_ERROR in read_response.json()['error']

    @attr(env=['test'], priority=1)
    def test_user_api_update_non_existant_user_id(self):
        """
        GATEKEEPER-API042  test_user_api_update_non_existant_user_id
        attempt to update a non existant user id
        """
        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        user_id = self.util.random_int()
        update_response = self.gk_service.user(
            session, method='PUT', user_id=user_id
        )

        # 404 response
        assert update_response.status_code == requests.codes.not_found
        # verify that the error message is correct
        assert NO_DATA_ERROR in update_response.json()['error']

    @attr(env=['test'], priority=1)
    def test_user_api_read(self):
        """
        GATEKEEPER-API043 test_user_api_read
        verify the read(GET) response
        """

        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        # create a new application
        create_response = self.gk_service.user(
            session, method='POST'
        )

        # ensure a 201 is returned
        assert create_response.status_code == requests.codes.created

        # set user_id
        user_id = create_response.json()['user_id']
        # set username
        username = create_response.json()['username']
        # get user_info directly from database
        user_info = self.gk_dao.get_user_by_username(self.db, username)

        # read(GET) application data
        read_response = self.gk_service.user(
            session, method='GET', user_id=user_id
        )

        # verify the creation of the user POST action
        assert read_response.json()['username'] == user_info['username']
        assert read_response.json()['user_id'] == user_info['user_id']
        assert read_response.json()['name'] == user_info['name']
        assert read_response.json()['phone'] == user_info['phone']
        assert read_response.json()['email'] == user_info['email']
        assert (
            create_response.json()['last_logged_in']
            == user_info['last_logged_in']
        )

        # clean up - delete the application
        del_response = self.gk_service.user(
            session, method='DELETE', user_id=user_id
        )
        # ensure a 204 is returned
        assert del_response.status_code == requests.codes.no_content

        # read the new application data
        read_response = self.gk_service.user(
            session, method='GET', user_id=user_id
        )
        assert NO_DATA_ERROR in read_response.json()['error']

    @attr(env=['test'], priority=1)
    def test_user_api_read_non_existant_user_id(self):
        """
        GATEKEEPER-API044  test_user_api_get_non_existant_user_id
        attempt to get a non existant user id
        """
        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        user_id = self.util.random_int()
        update_response = self.gk_service.user(
            session, method='GET', user_id=user_id
        )

        # 404 response
        assert update_response.status_code == requests.codes.not_found
        # verify that the error message is correct
        assert NO_DATA_ERROR in update_response.json()['error']

    @attr(env=['test'], priority=1)
    def test_user_api_delete(self):
        """
        GATEKEEPER-API045 test_user_api_delete
        explicit test case for delete functionality
        """

        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        # create a new application
        create_response = self.gk_service.user(
            session, method='POST'
        )

        # ensure a 201 is returned
        assert create_response.status_code == requests.codes.created

        # set user_id
        user_id = create_response.json()['user_id']
        # clean up - delete the application
        del_response = self.gk_service.user(
            session, method='DELETE', user_id=user_id
        )
        # ensure a 204 is returned
        assert del_response.status_code == requests.codes.no_content
        # ensure no response is returned
        assert len(del_response.content) == 0

        # read the new application data
        read_response = self.gk_service.user(
            session, method='GET', user_id=user_id
        )
        assert NO_DATA_ERROR in read_response.json()['error']

    @attr(env=['test'], priority=1)
    def test_user_api_read_non_existant_user_id(self):
        """
        GATEKEEPER-API046  test_user_api_get_non_existant_user_id
        attempt to get a non existant user id
        """
        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        user_id = self.util.random_int()
        update_response = self.gk_service.user(
            session, method='DELETE', user_id=user_id
        )

        # 404 response
        assert update_response.status_code == requests.codes.not_found
        # verify that the error message is correct
        assert NO_DATA_ERROR in update_response.json()['error']

    @attr(env=['test'], priority=1)
    def test_user_api_user_login(self):
        """
        GATEKEEPER-API046A test_user_api_user_login
        login as newly created,updated and deleted user
        """

        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        # create username and apssword
        rand_str = self.util.random_str()
        credentials = {
            'username': rand_str,
            'password': rand_str
        }
        user_data = self.gk_service.create_user_data(user_dict=credentials)

        # create a new user
        create_response = self.gk_service.user(
            session, method='POST', user_data=user_data
        )
        # ensure a 201 is returned
        assert create_response.status_code == requests.codes.created

        # login in as new user
        response = self.gk_service.create_session_urlencoded(
            allow_redirects=False, credentials=credentials
        )
        # 303 response
        assert response.status_code == requests.codes.other

        # set user_id
        user_id = create_response.json()['user_id']

        # update username and password
        rand_str = self.util.random_str()
        credentials = {
            'username': rand_str,
            'password': rand_str
        }
        user_data = self.gk_service.create_user_data(user_dict=credentials)

        # update application
        update_response = self.gk_service.user(
            session, method='PUT', user_id=user_id, user_data=user_data
        )

        # login in as updated user
        response = self.gk_service.create_session_urlencoded(
            allow_redirects=False, credentials=credentials
        )
        # 303 response
        assert response.status_code == requests.codes.other

        # clean up - delete the application
        del_response = self.gk_service.user(
            session, method='DELETE', user_id=user_id
        )
        # ensure a 204 is returned
        assert del_response.status_code == requests.codes.no_content

        # TODO: readd verifcation when 500 status issue is resolved
        # defect https://www.pivotaltracker.com/story/show/62791020
        # login in as new user
        """
        response = self.gk_service.create_session_urlencoded(
            allow_redirects=False, credentials=credentials
        )
        # 40X
        assert response.status_code == requests.codes
        """

    @attr(env=['test'], priority=1)
    def test_session_concurrency(self):

        """
        GATEKEEPER-API047  test_session_concurrency
        Random 403s occur when accessing the user session API via the
        SSO tool with a large number of multiple users.
        defect: https://www.pivotaltracker.com/story/show/62219660
        """

        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        # initial setup - create arbitrary number of users via REST API
        # TODO: replace this code with the user API when the user API on
        # the develop branch is merged to master
        user_data = []
        created_user_data = []
        for index in range(USER_TOTAL):
            user_data = {
                'username': 'automation_' + self.util.random_str(5),
                'name': 'automation ' + self.util.random_str(5),
                'phone': self.util.random_email(5),
                'email': self.util.random_email(5),
                'password': HASH_PASSWORD_TEST
            }
            # create basic user - no permissions
            assert (
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

            # get app id
            app_id = self.gk_dao.get_app_by_app_name(
                self.db,
                ANOTHER_TEST_APP
            )['application_id']

            # associate user with app
            assert(self.gk_dao.set_user_app_id(self.db, app_id, user_id))

            created_user_data.append(user_data)

        # login each user and retain cookie info for use later
        for user in created_user_data:
            payload = {'username': user['username'], 'password': 'test'}
            response = self.gk_service.create_session_urlencoded(
                allow_redirects=False, credentials=payload
            )
            assert response.status_code == requests.codes.see_other
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
    def test_ajax_no_redirect(self):
        """
        GATEKEEPER-API048 test_ajax_no_redirect
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
        assert response.status_code == requests.codes.ok
        assert GATEKEEPER_TITLE not in response.text

        # logout
        response = self.gk_service.logout_user_session(session)
        assert response.status_code == requests.codes.ok

        # must disable caching in dummyapp for this check
        parameters = {'sso_cache_enabled': False}

        # firstly browser call test - 303 redirect
        response = self.gk_service.validate_end_point(
            session, allow_redirects=False, parameters=parameters
        )
        assert response.status_code == requests.codes.other
        response = self.gk_service.validate_end_point(
            session, parameters=parameters
        )
        assert GATEKEEPER_TITLE in response.text

        # set header to emualte ajax call
        session.headers.update({'X-Requested-With': 'XMLHttpRequest'})
        response = response = self.gk_service.validate_end_point(
            session, allow_redirects=False, parameters=parameters
        )
        # ajax call 401
        assert response.status_code == requests.codes.unauthorized
        assert NOT_LOGGED_IN in response.json()['error']

    @attr(env=['test'], priority=1)
    def test_validate_caching(self):
        """
        GATEKEEPER-API049 - test_validate_caching
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
        appname = ANOTHER_TEST_APP
        fullname = 'automation ' + self.util.random_str(5)
        email = self.util.random_email(5)

        # create basic user - no permisssions
        assert (
            self.gk_dao.set_gk_user(
                self.db, username,
                HASH_PASSWORD_TEST,
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
        user_permission = self.gk_dao.get_permission_id_by_name(
            self.db,
            DEFAULT_ADFUSER_USER, app_id
        )['permission_id']
        admin_permission = self.gk_dao.get_permission_id_by_name(
            self.db,
            DEFAULT_ADFUSER_ADMIN, app_id
        )['permission_id']

        # associate user with app
        assert(self.gk_dao.set_user_app_id(self.db, app_id, user_id))

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
        assert response.status_code == requests.codes.ok

        # verify the user end point cannot be accessed
        response = self.gk_service.validate_end_point(
            session,
            end_point=config['gatekeeper']['dummy']['user_endpoint']
        )
        # 403
        assert response.status_code == requests.codes.forbidden

        # Part B)
        # set the user permissions for the app
        # i.e user can only access the dummy application and user end point
        assert (
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
            end_point=config['gatekeeper']['dummy']['user_endpoint']
        )
        # 403
        assert response.status_code == requests.codes.forbidden

        # Part C)
        # must disable caching in dummyapp for this check
        parameters = {'sso_cache_enabled': False}
        # verify the dummy application can be accessed
        # when caching is disabled as the new permission can now
        # be retreived

        response = self.gk_service.validate_end_point(
            session,
            end_point=config['gatekeeper']['dummy']['user_endpoint'],
            parameters=parameters
        )
        # 200
        assert response.status_code == requests.codes.ok

        # delete user - cascade delete by default
        assert (self.gk_dao.del_gk_user(self.db, user_id))

    @attr(env=['test'], priority=1)
    def test_invalid_endpoint(self):
        """
        GATEKEEPER-API050- test_invalid_endpoint
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
        assert response.status_code == requests.codes.not_found

        # validate a fake dummy app endpoint
        response = self.gk_service.validate_end_point(
            session,
            end_point="fake"
        )
        # 404
        assert response.status_code == requests.codes.not_found
