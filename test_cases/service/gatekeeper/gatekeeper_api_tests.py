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


class TestGateKeeperAPI:

    @classmethod
    def setUpClass(cls):
        # Things that need to be done once
        cls.db = BaseDAO(config['gatekeeper']['db']['connection'])

    @classmethod
    def tearDownClass(cls):
        # Things that need to be done once.
        cls.db.connection.close()

    def setup(self):
        # Things to run before each test.

        self.gk_service = GateKeeperService()
        self.gk_dao = GateKeeperDAO()
        self.DEFAULT_TEST_USER = self.gk_dao.get_user_id_by_username(
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
        # create a session - do not allow redirects
        response = self.gk_service.create_session_urlencoded(
            allow_redirects=False,
            redirect_url=config['gatekeeper']['redirect']
        )
        # 303 response
        assert response.status_code == requests.codes.other

        # covert Set_Cookie response header to simple cookie object
        cookie = Cookie.SimpleCookie()
        cookie.load(response.headers['Set-Cookie'])
        cookie_id = cookie['sso_cookie'].value
        # assert against database
        db_response = self.gk_dao.get_session_by_cookie_id(self.db, cookie_id)
        assert db_response['cookie_id'] == cookie_id
        assert db_response['user_id'] == self.DEFAULT_TEST_USER

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
        # create a session - do not allow redirects
        response = self.gk_service.create_session_urlencoded(
            allow_redirects=False
        )
        # 303 response
        assert response.status_code == requests.codes.other
        # covert Set_Cookie response header to simple cookie object
        cookie = Cookie.SimpleCookie()
        cookie.load(response.headers['Set-Cookie'])
        cookie_id = cookie['sso_cookie'].value
        # assert against database
        db_response = self.gk_dao.get_session_by_cookie_id(self.db, cookie_id)
        assert db_response['cookie_id'] == cookie_id
        assert db_response['user_id'] == self.DEFAULT_TEST_USER

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

        # urlencoded post
        # create a session - do not allow redirects
        response = self.gk_service.create_session_urlencoded(
            allow_redirects=False
        )
        # 303 response
        assert response.status_code == requests.codes.other
        # covert Set_Cookie response header to simple cookie object
        cookie = Cookie.SimpleCookie()
        cookie.load(response.headers['Set-Cookie'])
        cookie_id = cookie['sso_cookie'].value

        my_cookie = dict(name='sso_cookie', value=cookie_id)
        response = self.gk_service.validate_session(
            cookie_id=cookie_id,
            session=self.gk_service.create_requests_session_with_cookie(
                my_cookie)
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
        # urlencoded post
        # create a session - do not allow redirects
        response = self.gk_service.create_session_urlencoded(
            allow_redirects=False,
            redirect_url=config['gatekeeper']['redirect']
        )
        # 303 response
        assert response.status_code == requests.codes.other
        # covert Set_Cookie response header to simple cookie object
        cookie = Cookie.SimpleCookie()
        cookie.load(response.headers['Set-Cookie'])
        cookie_value_sso = cookie['sso_cookie'].value

        my_cookie = dict(name='sso_cookie', value=cookie_value_sso)

        response = self.gk_service.validate_url_with_cookie(
            self.gk_service.create_requests_session_with_cookie(
                my_cookie
                ),
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

        # urlencoded post
        # create a session - do not allow redirects
        response = self.gk_service.create_session_urlencoded(
            allow_redirects=False
        )
        # 303 response
        assert response.status_code == requests.codes.other
        # covert Set_Cookie response header to simple cookie object
        cookie = Cookie.SimpleCookie()
        cookie.load(response.headers['Set-Cookie'])
        cookie_id = cookie['sso_cookie'].value

        my_cookie = dict(name='sso_cookie', value=cookie_id)
        response = self.gk_service.validate_session(
            cookie_id=cookie_id,
            session=self.gk_service.create_requests_session_with_cookie(
                my_cookie
                ),
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
        # urlencoded post
        # create a session - do not allow redirects
        response = self.gk_service.create_session_urlencoded(
            allow_redirects=False
        )
        # 303 response
        assert response.status_code == requests.codes.other
        # covert Set_Cookie response header to simple cookie object
        cookie = Cookie.SimpleCookie()
        cookie.load(response.headers['Set-Cookie'])

        # set cookie to invalid value
        cookie_value = "fake"

        my_cookie = dict(name='sso_cookie', value=cookie_value)
        response = self.gk_service.validate_session(
            cookie_id=cookie_value,
            session=self.gk_service.create_requests_session_with_cookie(
                my_cookie
                )
        )

        # ensure that the request is forbidden(403)
        # without a valid session cookie
        # TODO: verify on 403 if this defect is resolved
        # - https://www.pivotaltracker.com/story/show/61545596
        # assert response.status_code == requests.codes.forbidden

        assert "Cookie does not exist" in response.json()['error']

    @attr(env=['test'], priority=1)
    def test_validate_session_with_no_cookie_id(self):
        """
        GATEKEEPER-API007 test_validate_session_with_no_cookie_id - creates a
        session through a POST to the login API and then verifies that a user
        cannot access an url using a session with no cookieid/session id.
        """
        # urlencoded post
        # create a session - do not allow redirects
        response = self.gk_service.create_session_urlencoded(
            allow_redirects=False
        )
        # 303 response
        assert response.status_code == requests.codes.other
        # covert Set_Cookie response header to simple cookie object
        cookie = Cookie.SimpleCookie()
        cookie.load(response.headers['Set-Cookie'])
        # set cookie to empty value
        cookie_value = ''

        my_cookie = dict(name='sso_cookie', value=cookie_value)
        response = self.gk_service.validate_session(
            cookie_id=cookie_value,
            session=self.gk_service.create_requests_session_with_cookie(
                my_cookie
                )
        )

        # ensure that the request is forbidden(403)
        # without a valid session cookie
        # TODO: verify on 403 if this defect is resolved
        # - https://www.pivotaltracker.com/story/show/61545596
        # assert response.status_code == requests.codes.forbidden
        assert "Missing parameters: cookie" in response.json()['error']

    @attr(env=['test'], priority=1)
    def test_validate_session_with_invalid_session(self):
        """
        GATEKEEPER-API008 test_validate_session_with_no_cookie_id - creates a
        session through a POST to the login API and then verifies that a user
        cannot access an url using an invalid session
        """
        # urlencoded post
        # create a session - do not allow redirects
        response = self.gk_service.create_session_urlencoded(
            allow_redirects=False
        )
        # 303 response
        assert response.status_code == requests.codes.other
        # covert Set_Cookie response header to simple cookie object
        cookie = Cookie.SimpleCookie()
        cookie.load(response.headers['Set-Cookie'])
        cookie_value = cookie['sso_cookie'].value

        # set the cookie dict being passed to the session as invalid value
        fake_value = 'fake'
        my_cookie = dict(name='sso_cookie', value=fake_value)

        response = self.gk_service.validate_session(
            cookie_id=cookie_value,
            session=self.gk_service.create_requests_session_with_cookie(
                my_cookie
                )
        )

        # ensure that the request is forbidden(403) without a
        # valid session cookie
        # TODO: verify on 403 if this defect is resolved
        # - https://www.pivotaltracker.com/story/show/61545596
        # assert response.status_code == requests.codes.forbidden
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

        # urlencoded post
        # create a session - do not allow redirects
        response = self.gk_service.create_session_urlencoded(
            allow_redirects=False
        )
        # 303 response
        assert response.status_code == requests.codes.other
        # covert Set_Cookie response header to simple cookie object
        cookie = Cookie.SimpleCookie()
        cookie.load(response.headers['Set-Cookie'])
        cookie_id = cookie['sso_cookie'].value

        # set application to none
        application = ''

        my_cookie = dict(name='sso_cookie', value=cookie_id)
        response = self.gk_service.validate_session(
            cookie_id=cookie_id,
            session=self.gk_service.create_requests_session_with_cookie(
                my_cookie
                ),
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

        # urlencoded post
        # create a session - do not allow redirects
        response = self.gk_service.create_session_urlencoded(
            allow_redirects=False
        )
        # 303 response
        assert response.status_code == requests.codes.other
        # covert Set_Cookie response header to simple cookie object
        cookie = Cookie.SimpleCookie()
        cookie.load(response.headers['Set-Cookie'])
        cookie_id = cookie['sso_cookie'].value

        # set application to none
        application = 'fake'

        my_cookie = dict(name='sso_cookie', value=cookie_id)
        response = self.gk_service.validate_session(
            cookie_id=cookie_id,
            session=self.gk_service.create_requests_session_with_cookie(
                my_cookie
                ),
            application=application
        )

        # ensure that the request is forbidden (403)
        assert response.status_code == requests.codes.forbidden
        # ensure the correct message si returned
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
        # urlencoded post
        # create a session - do not allow redirects
        response = self.gk_service.create_session_urlencoded(
            allow_redirects=False
        )
        # 303 response
        assert response.status_code == requests.codes.other
        # covert Set_Cookie response header to simple cookie object
        cookie = Cookie.SimpleCookie()
        cookie.load(response.headers['Set-Cookie'])
        cookie_value_sso = cookie['sso_cookie'].value

        my_cookie = dict(name='sso_cookie', value=cookie_value_sso)

        response = self.gk_service.validate_url_with_cookie(
            self.gk_service.create_requests_session_with_cookie(
                my_cookie
                )
        )
        assert response.status_code == requests.codes.ok
        assert "/logout/" in response.text

    @attr(env=['test'], priority=1)
    def test_access_url_with_Invalid_cookie(self):
        """
        GATEKEEPER-API012 test_access_url_with_Invalid_cookie - creates a
        session through a POST to the login API and then verify that a user
        CANNOT access an url using a session with a invalid cookie.
        As the session cookie is invalid the user will be prompted
        for a username and password
        """
        # urlencoded post
        # create a session - do not allow redirects
        response = self.gk_service.create_session_urlencoded(
            allow_redirects=False
        )
        # 303 response
        assert response.status_code == requests.codes.other
        # covert Set_Cookie response header to simple cookie object
        cookie = Cookie.SimpleCookie()
        cookie.load(response.headers['Set-Cookie'])
        cookie_value = "fakecookie"

        my_cookie = dict(name='sso_cookie', value=cookie_value)
        response = self.gk_service.validate_url_with_cookie(
            self.gk_service.create_requests_session_with_cookie(
                my_cookie
                )
        )
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
        # covert Set_Cookie response header to simple cookie object
        cookie = Cookie.SimpleCookie()
        cookie.load(response.headers['Set-Cookie'])
        cookie_value = cookie['sso_cookie'].value

        my_cookie = dict(name='sso_cookie', value=cookie_value, expires=-1)
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
        # urlencoded post
        # create a session - do not allow redirects
        response = self.gk_service.create_session_urlencoded(
            allow_redirects=False
        )
        # 303 response
        assert response.status_code == requests.codes.other
        # covert Set_Cookie response header to simple cookie object
        cookie = Cookie.SimpleCookie()
        cookie.load(response.headers['Set-Cookie'])
        cookie_value = cookie['sso_cookie'].value

        # update cookie in the database so thats its expired
        assert(
            self.gk_dao.set_session_to_expire_by_session_id(
                self.db,
                cookie_value
                )
        )

        my_cookie = dict(name='sso_cookie', value=cookie_value)
        response = self.gk_service.validate_url_with_cookie(
            self.gk_service.create_requests_session_with_cookie(
                my_cookie
                )
        )
        assert response.status_code == requests.codes.ok
        assert GATEKEEPER_TITLE in response.text

        # User login causes expired coookie to be deleted
        response = self.gk_service.create_session_urlencoded(
            allow_redirects=False
        )

        # assert againist the database - ensure it no longer exists
        db_response = self.gk_dao.get_session_by_cookie_id(
            self.db,
            cookie_value
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
        # urlencoded post
        # create a session - do not allow redirects
        response = self.gk_service.create_session_urlencoded(
            allow_redirects=False,
            redirect_url=config['gatekeeper']['redirect']
        )
        # 303 response
        assert response.status_code == requests.codes.other
        # covert Set_Cookie response header to simple cookie object
        cookie = Cookie.SimpleCookie()
        cookie.load(response.headers['Set-Cookie'])
        cookie_value_sso = cookie['sso_credentials'].value

        my_cookie = dict(name='sso_cookie', value=cookie_value_sso)

        session = self.gk_service.create_requests_session_with_cookie(
            my_cookie
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
            cookie_value_sso
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
        # urlencoded post
        # create a session - do not allow redirects
        response = self.gk_service.create_session_urlencoded(
            allow_redirects=False
        )
        # 303 response
        assert response.status_code == requests.codes.other
        # covert Set_Cookie response header to simple cookie object
        cookie = Cookie.SimpleCookie()
        cookie.load(response.headers['Set-Cookie'])
        cookie_value = cookie['sso_cookie'].value

        my_cookie = dict(name='sso_cookie', value=cookie_value)
        session = self.gk_service.create_requests_session_with_cookie(
            my_cookie
        )

        response = self.gk_service.validate_url_with_cookie(session)
        assert response.status_code == requests.codes.ok

        # logout with a post
        response = self.gk_service.logout_user_session(session)
        assert response.status_code == requests.codes.ok

        response = self.gk_service.validate_url_with_cookie(session)
        assert response.status_code == requests.codes.ok
        assert "Please confirm logout" in response.text

        # assert againist the database - ensure it no longer exists
        db_response = self.gk_dao.get_session_by_cookie_id(
            self.db,
            cookie_value
        )
        assert db_response is None

    @attr(env=['test'], priority=2)
    def test_can_logout_get(self):
        """
        GATEKEEPER-API017A test_can_logout_default_redirect
        Ensures the logout confirmation button is returned
        when the logout is called with a get
        Note: the python-request library can not be sued for web based tests
        so cannot click the confirmation button
        """
        # urlencoded post
        # create a session - do not allow redirects
        response = self.gk_service.create_session_urlencoded(
            allow_redirects=False
        )
        # 303 response
        assert response.status_code == requests.codes.other
        # covert Set_Cookie response header to simple cookie object
        cookie = Cookie.SimpleCookie()
        cookie.load(response.headers['Set-Cookie'])
        cookie_value = cookie['sso_cookie'].value

        my_cookie = dict(name='sso_cookie', value=cookie_value)
        session = self.gk_service.create_requests_session_with_cookie(
            my_cookie
        )

        response = self.gk_service.validate_url_with_cookie(session)
        assert response.status_code == requests.codes.ok

        # logout using GET call
        response = self.gk_service.logout_user_session_get(session)
        assert response.status_code == requests.codes.ok
        assert CONFIRM_LOGOUT in response.text

    @attr(env=['test'], priority=1)
    def test_validate_user_api_and_auth_app_permissions(self):
        """
        GATEKEEPER-API018 - test_validate_user_api_and_auth_app_permissions
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
        user_id = self.gk_dao.get_user_id_by_username(
            self.db,
            username
        )['user_id']

        # get app id
        app_id = self.gk_dao.get_app_id_by_app_name(
            self.db,
            appname
        )['application_id']

        # associate user with app
        assert(self.gk_dao.set_user_app_id(self.db, app_id, user_id))

        # create a session for the user
        credentials_payload = {'username': username, 'password': 'test'}
        # create a session - do not allow redirects - urlencoded post
        response = self.gk_service.create_session_urlencoded(
            allow_redirects=False,
            payload=credentials_payload
        )
        # 303 response
        assert response.status_code == requests.codes.other
        # covert Set_Cookie response header to simple cookie object
        cookie = Cookie.SimpleCookie()
        cookie.load(response.headers['Set-Cookie'])
        cookie_value_sso = cookie['sso_cookie'].value

        my_cookie = dict(name='sso_cookie', value=cookie_value_sso)

        session = self.gk_service.create_requests_session_with_cookie(
            my_cookie
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
    def test_validate_user_api_and_auth_user_permissions(self):
        """
        GATEKEEPER-API019 test_validate_user_api_and_auth_user_permissions
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
        user_id = self.gk_dao.get_user_id_by_username(
            self.db,
            username
        )['user_id']

        # get app id
        app_id = self.gk_dao.get_app_id_by_app_name(
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
        response = self.gk_service.create_session_urlencoded(
            allow_redirects=False,
            payload=credentials_payload
        )
        # 303 response
        assert response.status_code == requests.codes.other
        # covert Set_Cookie response header to simple cookie object
        cookie = Cookie.SimpleCookie()
        cookie.load(response.headers['Set-Cookie'])
        cookie_value_sso = cookie['sso_cookie'].value

        my_cookie = dict(name='sso_cookie', value=cookie_value_sso)

        session = self.gk_service.create_requests_session_with_cookie(
            my_cookie
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

        # verify the admin end point can be accessed
        response = self.gk_service.validate_end_point(
            session,
            end_point=config['gatekeeper']['dummy']['admin_endpoint']
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
    def test_validate_user_api_and_auth_group_permissions(self):
        """
        GATEKEEPER-API020 - test_validate_user_api_and_auth_group_permissions
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
        user_id = self.gk_dao.get_user_id_by_username(
            self.db,
            username
        )['user_id']

        # get app id
        app_id = self.gk_dao.get_app_id_by_app_name(
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
        # create a session - do not allow redirects - urlencoded post
        response = self.gk_service.create_session_urlencoded(
            allow_redirects=False,
            payload=credentials_payload
        )
        # 303 response
        assert response.status_code == requests.codes.other
        # covert Set_Cookie response header to simple cookie object
        cookie = Cookie.SimpleCookie()
        cookie.load(response.headers['Set-Cookie'])
        cookie_value_sso = cookie['sso_cookie'].value

        my_cookie = dict(name='sso_cookie', value=cookie_value_sso)

        session = self.gk_service.create_requests_session_with_cookie(
            my_cookie
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
        # urlencoded post
        # create a session - do not allow redirects
        response = self.gk_service.create_session_urlencoded(
            allow_redirects=False,
            redirect_url=config['gatekeeper']['redirect']
        )
        # 303 response
        assert response.status_code == requests.codes.other
        # covert Set_Cookie response header to simple cookie object
        cookie = Cookie.SimpleCookie()
        cookie.load(response.headers['Set-Cookie'])
        cookie_value = "fakecookie"

        my_cookie = dict(name='sso_cookie', value=cookie_value)
        session = self.gk_service.create_requests_session_with_cookie(
            my_cookie
        )
        response = self.gk_service.user_info(
            session,
            self.DEFAULT_TEST_USER,
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
        # urlencoded post
        # create a session - do not allow redirects
        response = self.gk_service.create_session_urlencoded(
            allow_redirects=False,
            redirect_url=config['gatekeeper']['redirect']
        )
        # 303 response
        assert response.status_code == requests.codes.other
        # covert Set_Cookie response header to simple cookie object
        cookie = Cookie.SimpleCookie()
        cookie.load(response.headers['Set-Cookie'])
        cookie_value = cookie['sso_cookie'].value
        my_cookie = dict(name='sso_cookie', value=cookie_value)
        session = self.gk_service.create_requests_session_with_cookie(
            my_cookie
        )
        fake_application = "fake"
        response = self.gk_service.user_info(
            session,
            self.DEFAULT_TEST_USER,
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
        # urlencoded post
        # create a session - do not allow redirects
        response = self.gk_service.create_session_urlencoded(
            allow_redirects=False,
            redirect_url=config['gatekeeper']['redirect']
        )
        # 303 response
        assert response.status_code == requests.codes.other
        # covert Set_Cookie response header to simple cookie object
        cookie = Cookie.SimpleCookie()
        cookie.load(response.headers['Set-Cookie'])
        cookie_value = cookie['sso_cookie'].value
        my_cookie = dict(name='sso_cookie', value=cookie_value)
        session = self.gk_service.create_requests_session_with_cookie(
            my_cookie
        )

        # add one to the user id to create a random element to userid
        random_user_id = self.gk_dao.get_user_id_by_username(
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
        # urlencoded post
        # create a session - do not allow redirects
        response = self.gk_service.create_session_urlencoded(
            allow_redirects=False,
            redirect_url=config['gatekeeper']['redirect']
        )
        # 303 response

        assert response.status_code == requests.codes.other
        # covert Set_Cookie response header to simple cookie object

        cookie = Cookie.SimpleCookie()
        cookie.load(response.headers['Set-Cookie'])
        cookie_value = cookie['sso_cookie'].value

        my_cookie = dict(name='sso_cookie', value=cookie_value)
        session = self.gk_service.create_requests_session_with_cookie(
            my_cookie
        )
        response = self.gk_service.user_info(session, '', '')

        # ensure that the request is forbidden(403)
        # without a valid session cookie
        # TODO: verify on 403 if this defect is resolved
        # https://www.pivotaltracker.com/story/show/61545596
        # assert response.status_code == requests.codes.forbidden
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
        user_id = self.gk_dao.get_user_id_by_username(
            self.db,
            username
        )['user_id']

        # get app id
        app_id = self.gk_dao.get_app_id_by_app_name(
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
        # create a session - do not allow redirects - urlencoded post
        response = self.gk_service.create_session_urlencoded(
            allow_redirects=False,
            payload=credentials_payload
        )
        # 303 response
        assert response.status_code == requests.codes.other
        # covert Set_Cookie response header to simple cookie object
        cookie = Cookie.SimpleCookie()
        cookie.load(response.headers['Set-Cookie'])
        cookie_value_sso = cookie['sso_cookie'].value

        my_cookie = dict(name='sso_cookie', value=cookie_value_sso)

        session = self.gk_service.create_requests_session_with_cookie(
            my_cookie
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
        user_id = self.gk_dao.get_user_id_by_username(
            self.db,
            username
        )['user_id']

        # get app id
        app_id = self.gk_dao.get_app_id_by_app_name(
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
        # create a session - do not allow redirects - urlencoded post
        response = self.gk_service.create_session_urlencoded(
            allow_redirects=False,
            payload=credentials_payload
        )
        # 303 response
        assert response.status_code == requests.codes.other
        # covert Set_Cookie response header to simple cookie object
        cookie = Cookie.SimpleCookie()
        cookie.load(response.headers['Set-Cookie'])
        cookie_value_sso = cookie['sso_cookie'].value

        my_cookie = dict(name='sso_cookie', value=cookie_value_sso)

        session = self.gk_service.create_requests_session_with_cookie(
            my_cookie
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
