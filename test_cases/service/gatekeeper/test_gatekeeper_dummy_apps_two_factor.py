"""
@summary: Contains a set of API tests for the gate keeper(single sign on)
project - 2 factor authentication test cases
@since: Created on November 28th 2013
@author: Conor Fitzgerald
"""
import requests
from nose.plugins.attrib import attr
from . import ApiTestCase
from testconfig import config
from framework.service.gatekeeper.gatekeeper_service import SERVICE_NAME, \
        GateKeeperService
import Cookie


class TestGateKeeperDummy2FaAPI(ApiTestCase):

    @attr(env=['test'], priority=1)
    def test_can_login_two_factor_from_dummy_app(self):
        """
        GATEKEEPER-2FA-API002 test_can_login_two_factor_from_dummy_app
        - verify basic 2FA functionality from the dummy app
        """

        # create a user and associate user with relevant
        # pre-configured application for dummy app

        username = 'automation_' + self.util.random_str(5)
        appname = self.gk_service.ANOTHER_TEST_APP
        fullname = 'automation ' + self.util.random_str(5)
        email = self.util.random_email(5)

        # create basic user - no permissions
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
        # create a session - do not allow redirects - urlencoded post

         # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False,
            cookie_type="CRED",
            credentials=credentials_payload
        )

        # assert against database
        db_response = self.gk_dao.get_session_by_cookie_id(
            self.db,
            cookie_id
        )
        self.assertEquals(db_response['cookie_id'], cookie_id)
        self.assertEquals(db_response['user_id'], user_id)

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
        self.assertEquals(response.status_code, requests.codes.found)

        cookie = Cookie.SimpleCookie()
        cookie.load(response.headers['Set-Cookie'])
        # print cookie
        cookie_id_verf = cookie['sso_verification_code'].value
        cookie_id_sso = cookie['sso_cookie'].value

        db_response = self.gk_dao.get_session_by_cookie_id(
            self.db,
            cookie_id_verf
        )
        self.assertEquals(db_response['cookie_id'], cookie_id_verf)

        db_response = self.gk_dao.get_session_by_cookie_id(
            self.db,
            cookie_id_sso
        )
        self.assertEquals(db_response['cookie_id'], cookie_id_sso)

        my_cookie = dict(name='sso_cookie', value=cookie_id_sso)
        session = self.gk_service.create_requests_session_with_cookie(
            my_cookie
        )

        # verify the dummy application can be accessed
        response = self.gk_service.validate_end_point(session)
        self.assertEquals(response.status_code, requests.codes.ok)

        # print response.text
        # delete user - cascade delete by default
        self.assertTrue(self.gk_dao.del_gk_user(self.db, user_id))

    @attr(env=['test'], priority=1)
    def test_attempt_bypass_verifcation_code(self):
        """
        GATEKEEPER-2FA-API003 test_attempt_bypass_verifcation_code
        Attempt to access gatekeeper or dummy app without
        entering verification code
        """

         # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False,
            cookie_type="CRED"
        )

        # assert against database
        db_response = self.gk_dao.get_session_by_cookie_id(
            self.db,
            cookie_id
        )
        self.assertEquals(db_response['cookie_id'], cookie_id)
        self.assertEquals(db_response['user_id'], self.default_test_user)

        # redirected to login page if it tries to access other pages

        # attempt to access gatekeeper app
        gk_url = '{0}://{1}:{2}/'.format(
            config[SERVICE_NAME]['scheme'],
            config[SERVICE_NAME]['host'],
            config[SERVICE_NAME]['port']
        )
        response = self.gk_service.validate_url_with_cookie(
            session,
            url=gk_url
        )
        self.assertEquals(response.status_code, requests.codes.ok)
        self.assertTrue(self.gk_service.GATEKEEPER_TITLE in response.text)

        # attempt to access dummy app
        gk_url = '{0}://{1}:{2}/'.format(
            config[SERVICE_NAME]['scheme'],
            config[SERVICE_NAME]['dummy']['host'],
            config[SERVICE_NAME]['dummy']['port']
        )
        response = self.gk_service.validate_url_with_cookie(
            session,
            url=gk_url
        )
        self.assertEquals(response.status_code, requests.codes.ok)
        self.assertTrue(self.gk_service.GATEKEEPER_TITLE in response.text)
