"""
@summary: Contains a set of test cases for the user session API of the
gatekeeper(single sign on) project
Note: only 1 factor authentication test cases
These test have a number of dependencies
1. the database update script updates the gatekeepr schema - the script can be
found at the root of the gatekeeper app
2. the build script starts the gatekeeper app with ssl enbaled by default
3. the build script starts the dummy app with ssl enabled
and application_name is adfuser
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
import unittest


class TestGateKeeperUserSessionAPI(unittest.TestCase):

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
    def test_user_session(self):
        """
        GATEKEEPER_USER_SESSION_API_001 test_user_session
        Creates a session through a POST to the login API and then validates
        the session_id(cookie value)
        """

        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False,
        )

        response = self.gk_service.user_session(
            cookie_id=cookie_id,
            session=session
        )

        self.assertEquals(response.status_code, requests.codes.ok)
        # obtain session id and user id from database
        db_response = self.gk_dao.get_session_by_cookie_id(self.db, cookie_id)

        # assert against database
        self.assertEquals(response.json()['user_id'], db_response['user_id'])
        self.assertEquals(
            response.json()['session_id'], db_response['session_id']
        )

    @attr(env=['test'], priority=1)
    def test_user_session_with_app_filter(self):
        """
        GATEKEEPER_USER_SESSION_API_002 test_user_session_with_app_filter
        creates a session through a POST to the login API and then validates
        the session_id(cookie value)  and application filter
        """

        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False,
        )

        response = self.gk_service.user_session(
            cookie_id=cookie_id,
            session=session,
            application=self.gk_service.DEFAULT_TEST_APP
        )

        self.assertEquals(response.status_code, requests.codes.ok)
        # obtain session id and user id from database
        db_response = self.gk_dao.get_session_by_cookie_id(self.db, cookie_id)

        # assert against database
        self.assertEquals(response.json()['user_id'], db_response['user_id'])
        self.assertEquals(
            response.json()['session_id'], db_response['session_id']
        )

    @attr(env=['test'], priority=1)
    def test_user_session_invalid_cookie_value(self):
        """
        GATEKEEPER_USER_SESSION_API_003 test_user_session_invalid_cookie_value
        Creates a session through a POST to the login API and then verifies
        that a user cannot access an url using a session with
        invalid cookie value
        """

        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        # set cookie to invalid value
        cookie_value = "fake"

        my_cookie = dict(name='sso_cookie', value=cookie_id)
        response = self.gk_service.user_session(
            cookie_id=cookie_value,
            session=session
        )

        self.assertEquals(response.status_code, requests.codes.not_found)
        self.assertTrue("Cookie does not exist" in response.json()['error'])

    @attr(env=['test'], priority=1)
    def test_user_session_no_cookie_id(self):
        """
        GATEKEEPER_USER_SESSION_API_004 test_user_session_no_cookie_id
        creates a session through a POST to the login API and then
        verifies that a user cannot access an url using a session with
        no cookieid/session id.
        """

        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        # set cookie to empty value
        cookie_value = ''

        response = self.gk_service.user_session(
            cookie_id=cookie_value,
            session=session
        )

        self.assertEquals(response.status_code, requests.codes.bad_request)
        json_data = response.json()
        self.assertTrue('error' in json_data)
        self.assertEqual(json_data['error'], "Missing parameters: cookie")

    @attr(env=['test'], priority=1)
    def test_user_session_with_invalid_session(self):
        """
        GATEKEEPER_USER_SESSION_API_005 test_user_session_with_invalid_session
        Creates a session through a POST to the login API and then verifies
        that a user cannot access an url using an invalid session
        """

        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        # set the cookie dict being passed to the session as invalid value
        fake_value = 'fake'
        my_cookie = dict(name='sso_cookie', value=fake_value)

        response = self.gk_service.user_session(
            cookie_id=cookie_id,
            session=self.gk_service.create_requests_session_with_cookie(
                my_cookie
            )
        )
        self.assertEquals(response.status_code, requests.codes.forbidden)
        self.assertTrue(
            self.gk_service.SESSION_NOT_ALLOWED in response.json()['error']
        )

    @attr(env=['test'], priority=1)
    def test_user_session_app_filter_no_app(self):
        """
        GATEKEEPER_USER_SESSION_API_006 test_user_session_app_filter_no_app
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

        response = self.gk_service.user_session(
            cookie_id=cookie_id,
            session=session,
            application=application
        )

        # 200
        self.assertEquals(response.status_code, requests.codes.ok)
        # obtain session id and user id from database
        db_response = self.gk_dao.get_session_by_cookie_id(self.db, cookie_id)

        # assert against database
        self.assertEquals(response.json()['user_id'], db_response['user_id'])
        self.assertEquals(
            response.json()['session_id'], db_response['session_id']
        )

    @attr(env=['test'], priority=1)
    def test_user_session_appfilter_invalid_app(self):
        """
        GATEKEEPER_USER_SESSION_API_007 test_user_session_appfilter_invalid_app
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
        response = self.gk_service.user_session(
            cookie_id=cookie_id,
            session=session,
            application=application
        )

        # ensure that the request is forbidden (403)
        self.assertEquals(response.status_code, requests.codes.forbidden)
        # ensure the correct message is returned
        error_message = self.gk_service.SESSION_FORBIDDEN % (cookie_id)
        self.assertTrue(error_message in response.json()['error'])
