"""
@summary: Contains a set of API tests for the gate keeper(single sign on)
project - 2 factor authentication test cases
@since: Created on November 28th 2013
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

# admin user is 'admin' and is used as the default user
ADMIN_USER = 'admin'

# default user permission configured for adfuser in the dummy app
DEFAULT_ADFUSER_USER = 'ADFUSER_USER'
# default admin permission configured for adfuser in the dummy app
DEFAULT_ADFUSER_ADMIN = 'ADFUSER_ADMIN'
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
INVALID_VERIFCATION_CODE = "Verification+code+not+valid"


class TestGateKeeper2FaAPI:
    @classmethod
    def setUpClass(cls):
        '''Things that need to be done once.'''
        cls.db = BaseDAO(config['gatekeeper']['db']['connection'])

    @classmethod
    def tearDownClass(cls):
        '''Things that need to be done once.'''
        cls.db.close()

    def setup(self):

        # Things to run before each test
        self.gk_service = GateKeeperService()
        self.gk_dao = GateKeeperDAO()
        self.default_test_user = self.gk_dao.get_user_by_username(
            self.db,
            ADMIN_USER
        )['user_id']
        self.util = Utility()

    @attr(env=['test'], priority=1)
    def test_can_login_two_factor(self):
        '''
        GATEKEEPER-2FA-API001 test_can_login_two_factor
        - verify basic 2FA functionality from gatekeeper application
        '''
        # create a session - do not allow redirects
        response = self.gk_service.create_session_urlencoded(
            allow_redirects=False
        )
        # 303 response
        assert response.status_code == requests.codes.other

        # convert Set_Cookie response header to simple cookie object
        cookie_id = self.gk_service.extract_cred_cookie_value(
            response.headers
        )
        my_cookie = dict(name='sso_credentials', value=cookie_id)
        session = self.gk_service.create_requests_session_with_cookie(
            my_cookie
        )

        # assert against database
        db_response = self.gk_dao.get_session_by_cookie_id(
            self.db,
            cookie_id
        )
        assert db_response['cookie_id'] == cookie_id
        assert db_response['user_id'] == self.default_test_user

        verification_code = self.gk_dao.get_verification_code_by_user_id(
            self.db,
            self.default_test_user
        )['verification_code']
        # print    verification_code
        payload = {'verification_code': verification_code}
        # print payload
        response = self.gk_service.submit_verification_code(
            session,
            payload,
            allow_redirects=False
        )
        assert response.status_code == requests.codes.other

        cookie = Cookie.SimpleCookie()
        cookie.load(response.headers['Set-Cookie'])
        # print cookie
        cookie_id_verf = cookie['sso_verification_code'].value
        cookie_id_sso = cookie['sso_cookie'].value

        db_response = self.gk_dao.get_session_by_cookie_id(
            self.db,
            cookie_id_verf
        )
        assert db_response['cookie_id'] == cookie_id_verf

        db_response = self.gk_dao.get_session_by_cookie_id(
            self.db,
            cookie_id_sso
        )
        assert db_response['cookie_id'] == cookie_id_sso

    @attr(env=['test'], priority=1)
    def test_can_login_two_factor_from_dummy_app(self):
        """
        GATEKEEPER-2FA-API002 test_can_login_two_factor_from_dummy_app
        - verify basic 2FA functionality from the dummy app
        """

        # create a user and associate user with relevant
        # pre-configured application for dummy app

        username = 'automation_' + self.util.random_str(5)
        appname = ANOTHER_TEST_APP
        fullname = 'automation ' + self.util.random_str(5)
        email = self.util.random_email(5)

        # create basic user - no permissions
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
        # create a session - do not allow redirects - urlencoded post

        # create a session - do not allow redirects
        response = self.gk_service.create_session_urlencoded(
            credentials=credentials_payload,
            allow_redirects=False
        )
        # 303 response
        assert response.status_code == requests.codes.other

        # convert Set_Cookie response header to simple cookie object
        cookie_id = self.gk_service.extract_cred_cookie_value(
            response.headers
        )
        my_cookie = dict(name='sso_credentials', value=cookie_id)
        session = self.gk_service.create_requests_session_with_cookie(
            my_cookie
        )
        # assert against database
        db_response = self.gk_dao.get_session_by_cookie_id(
            self.db,
            cookie_id
        )
        assert db_response['cookie_id'] == cookie_id
        assert db_response['user_id'] == user_id

        verification_code = self.gk_dao.get_verification_code_by_user_id(
            self.db,
            user_id
        )['verification_code']
        # print    verification_code
        payload = {'verification_code': verification_code}

        response = self.gk_service.submit_verification_code(
            session,
            payload,
            allow_redirects=False
        )
        assert response.status_code == requests.codes.other

        cookie = Cookie.SimpleCookie()
        cookie.load(response.headers['Set-Cookie'])
        # print cookie
        cookie_id_verf = cookie['sso_verification_code'].value
        cookie_id_sso = cookie['sso_cookie'].value

        db_response = self.gk_dao.get_session_by_cookie_id(
            self.db,
            cookie_id_verf
        )
        assert db_response['cookie_id'] == cookie_id_verf

        db_response = self.gk_dao.get_session_by_cookie_id(
            self.db,
            cookie_id_sso
        )
        assert db_response['cookie_id'] == cookie_id_sso

        my_cookie = dict(name='sso_cookie', value=cookie_id_sso)
        session = self.gk_service.create_requests_session_with_cookie(
            my_cookie
        )

        # verify the dummy application can be accessed
        response = self.gk_service.validate_end_point(session)
        assert response.status_code == requests.codes.ok

        # print response.text
        # delete user - cascade delete by default
        assert (self.gk_dao.del_gk_user(self.db, user_id))

    @attr(env=['test'], priority=1)
    def test_attempt_bypass_verifcation_code(self):
        """
        GATEKEEPER-2FA-API003 - test_attempt_bypass_verifcation_code
        - attempt to access gatekeeper or dummy app without
        entering verification code
        """
        # create a session - do not allow redirects
        response = self.gk_service.create_session_urlencoded(
            allow_redirects=False
        )
        # 303 response
        assert response.status_code == requests.codes.other

        # convert Set_Cookie response header to simple cookie object
        cookie_id = self.gk_service.extract_cred_cookie_value(
            response.headers
        )
        my_cookie = dict(name='sso_credentials', value=cookie_id)
        session = self.gk_service.create_requests_session_with_cookie(
            my_cookie
        )

        # assert against database
        db_response = self.gk_dao.get_session_by_cookie_id(
            self.db,
            cookie_id
        )
        assert db_response['cookie_id'] == cookie_id
        assert db_response['user_id'] == self.default_test_user

        # redirected to login page if it tries to access other pages

        # attempt to access gatekeeper app
        gk_url = '{0}://{1}:{2}/'.format(
            config['gatekeeper']['scheme'],
            config['gatekeeper']['host'],
            config['gatekeeper']['port']
        )
        response = self.gk_service.validate_url_with_cookie(
            session,
            url=gk_url
        )
        assert response.status_code == requests.codes.ok
        assert GATEKEEPER_TITLE in response.text

        # attempt to access dummy app
        gk_url = '{0}://{1}:{2}/'.format(
            config['gatekeeper']['scheme'],
            config['gatekeeper']['dummy']['host'],
            config['gatekeeper']['dummy']['port']
        )
        response = self.gk_service.validate_url_with_cookie(
            session,
            url=gk_url
        )
        assert response.status_code == requests.codes.ok
        assert GATEKEEPER_TITLE in response.text

    @attr(env=['test'], priority=1)
    def test_invalid_verification_code(self):
        """
        GATEKEEPER-2FA-API004 - test_invalid_verifcation_code -
        ensure that an invalid verification is not accepted,
        but a valid verification code can still be entered after
        an invalid code is entered
        """
        # create a session - do not allow redirects
        response = self.gk_service.create_session_urlencoded(
            allow_redirects=False
        )
        # 303 response
        assert response.status_code == requests.codes.other

        # convert Set_Cookie response header to simple cookie object
        cookie_id = self.gk_service.extract_cred_cookie_value(
            response.headers
        )
        my_cookie = dict(name='sso_credentials', value=cookie_id)
        session = self.gk_service.create_requests_session_with_cookie(
            my_cookie
        )
        # assert against database
        db_response = self.gk_dao.get_session_by_cookie_id(
            self.db,
            cookie_id
        )
        assert db_response['cookie_id'] == cookie_id
        assert db_response['user_id'] == self.default_test_user

        # fake verificaton code
        verification_code = 123456
        payload = {'verification_code': verification_code}

        # try the invalid verification code
        response = self.gk_service.submit_verification_code(
            session,
            payload, allow_redirects=False
        )
        # 303 response(as allow_redirects=False)
        # ensure the url encoded error message is correct
        assert response.status_code == requests.codes.other
        assert INVALID_VERIFCATION_CODE in response.text

        # ensure we can still use the correct verification code
        verification_code = self.gk_dao.get_verification_code_by_user_id(
            self.db,
            self.default_test_user
        )['verification_code']
        # print    verification_code
        payload = {'verification_code': verification_code}
        # print payload
        response = self.gk_service.submit_verification_code(
            session,
            payload,
            allow_redirects=False
        )
        assert response.status_code == requests.codes.other

        cookie = Cookie.SimpleCookie()
        cookie.load(response.headers['Set-Cookie'])
        # print cookie
        cookie_id_verf = cookie['sso_verification_code'].value
        cookie_id_sso = cookie['sso_cookie'].value

        db_response = self.gk_dao.get_session_by_cookie_id(
            self.db,
            cookie_id_verf
        )
        assert db_response['cookie_id'] == cookie_id_verf

        db_response = self.gk_dao.get_session_by_cookie_id(
            self.db,
            cookie_id_sso)
        assert db_response['cookie_id'] == cookie_id_sso

    @attr(env=['test'], priority=1)
    def test_expired_verification_code(self):
        """
        GATEKEEPER-2FA-API005 test_expired_verification_code,
        ensure than an expired verification code is not accepted
        """
        # create a session - do not allow redirects
        response = self.gk_service.create_session_urlencoded(
            allow_redirects=False
        )
        # 303 response
        assert response.status_code == requests.codes.other

        # convert Set_Cookie response header to simple cookie object
        cookie_id = self.gk_service.extract_cred_cookie_value(
            response.headers
        )
        my_cookie = dict(name='sso_credentials', value=cookie_id)
        session = self.gk_service.create_requests_session_with_cookie(
            my_cookie
        )
        # assert against database
        db_response = self.gk_dao.get_session_by_cookie_id(
            self.db,
            cookie_id
        )
        assert db_response['cookie_id'] == cookie_id
        assert db_response['user_id'] == self.default_test_user

        verification_code = self.gk_dao.get_verification_code_by_user_id(
            self.db,
            self.default_test_user
        )['verification_code']

        # expire the verification code
        assert(
            self.gk_dao.set_verification_code_to_expire_by_verification_code(
                self.db,
                verification_code
            )
        )

        payload = {'verification_code': verification_code}
        # try the invalid verification code
        response = self.gk_service.submit_verification_code(
            session,
            payload, allow_redirects=False
        )
        # 303 response(as allow_redirects=False)
        # ensure the url encoded error message is correct
        assert response.status_code == requests.codes.other
        assert INVALID_VERIFCATION_CODE in response.text

    @attr(env=['test'], priority=1)
    def test_only_latest_verification_code_is_valid(self):
        """
        GATEKEEPER-2FA-API006 - test_only_latest_verification_code_is_valid
        Test to ensure that if multiple verifications are created,
        that only the most recent verification code is accepted
        """
        # user_login - do not allow redirects
        response = self.gk_service.create_session_urlencoded(
            allow_redirects=False
        )
        # 303 response
        assert response.status_code == requests.codes.other

        verification_code_one = self.gk_dao.get_verification_code_by_user_id(
            self.db,
            self.default_test_user
        )['verification_code']

        # user_login - do not allow redirects
        response = self.gk_service.create_session_urlencoded(
            allow_redirects=False
        )
        # 303 response
        assert response.status_code == requests.codes.other

        # convert Set_Cookie response header to simple cookie object
        cookie_id = self.gk_service.extract_cred_cookie_value(
            response.headers
        )
        my_cookie = dict(name='sso_credentials', value=cookie_id)
        session = self.gk_service.create_requests_session_with_cookie(
            my_cookie
        )

        verification_code_two = self.gk_dao.get_verification_code_by_user_id(
            self.db,
            self.default_test_user
        )['verification_code']

        payload = {'verification_code': verification_code_one}

        response = self.gk_service.submit_verification_code(
            session,
            payload, allow_redirects=False
        )
        # 303 response(as allow_redirects=False)
        # ensure the url encoded error message is correct
        assert response.status_code == requests.codes.other
        assert INVALID_VERIFCATION_CODE in response.text

        payload = {'verification_code': verification_code_two}
        response = self.gk_service.submit_verification_code(
            session,
            payload,
            allow_redirects=False
        )
        assert response.status_code == requests.codes.other

        cookie = Cookie.SimpleCookie()
        cookie.load(response.headers['Set-Cookie'])
        # print cookie
        cookie_id_verf = cookie['sso_verification_code'].value
        cookie_id_sso = cookie['sso_cookie'].value

        db_response = self.gk_dao.get_session_by_cookie_id(
            self.db,
            cookie_id_verf
        )
        assert db_response['cookie_id'] == cookie_id_verf

        db_response = self.gk_dao.get_session_by_cookie_id(
            self.db,
            cookie_id_sso
        )
        assert db_response['cookie_id'] == cookie_id_sso

    @attr(env=['test'], priority=1)
    def test_invalid_credientials_cookie_value_in_session(self):
        """
        GATEKEEPER-2FA-API007  test_invalid_credientials_cook_value_in_session,
        verify that a verification code cannot be posted when the session
        contains an incorrect cookie value
        """
        # create a session - do not allow redirects
        response = self.gk_service.create_session_urlencoded(
            allow_redirects=False
        )
        # 303 response
        assert response.status_code == requests.codes.other

        # convert Set_Cookie response header to simple cookie object
        cookie_id = self.gk_service.extract_cred_cookie_value(
            response.headers
        )
        # assert against database
        db_response = self.gk_dao.get_session_by_cookie_id(
            self.db,
            cookie_id
        )
        assert db_response['cookie_id'] == cookie_id
        assert db_response['user_id'] == self.default_test_user

        fake_cookie_value = "fakecredCookie"
        my_cookie = dict(name='sso_credentials', value=fake_cookie_value)
        session = self.gk_service.create_requests_session_with_cookie(
            my_cookie
        )

        verification_code = self.gk_dao.get_verification_code_by_user_id(
            self.db,
            self.default_test_user
        )['verification_code']
        payload = {'verification_code': verification_code}

        response = self.gk_service.submit_verification_code(
            session,
            payload,
            allow_redirects=False
        )

        # 303 response(as allow_redirects=False)
        # ensure the url encoded error message is correct
        assert response.status_code == requests.codes.other
        no_cookie_found = \
            "No+session+with+cookie+%s+found" % (fake_cookie_value)
        assert no_cookie_found in response.text

    @attr(env=['test'], priority=1)
    def test_no_verifcation_code(self):
        '''
        GATEKEEPER-2FA-API008 - test_no_verifcation_code Verify the behaviour
        when no verification code is provided
        '''
        # create a session - do not allow redirects
        response = self.gk_service.create_session_urlencoded(
            allow_redirects=False
        )
        # 303 response
        assert response.status_code == requests.codes.other

        # convert Set_Cookie response header to simple cookie object
        cookie_id = self.gk_service.extract_cred_cookie_value(
            response.headers
        )

        my_cookie = dict(name='sso_credentials', value=cookie_id)
        session = self.gk_service.create_requests_session_with_cookie(
            my_cookie
        )

        # assert against database
        db_response = self.gk_dao.get_session_by_cookie_id(
            self.db,
            cookie_id
        )

        assert db_response['cookie_id'] == cookie_id
        assert db_response['user_id'] == self.default_test_user

        verification_code_blank = ''
        # print    verification_code
        payload = {'verification_code': verification_code_blank}

        response = self.gk_service.submit_verification_code(
            session,
            payload, allow_redirects=False
        )
        # 303 response(as allow_redirects=False)
        # ensure the url encoded error message is correct
        assert response.status_code == requests.codes.other
        assert INVALID_VERIFCATION_CODE in response.text
