"""
@summary: Contains a set of test cases for the login URI of the
gatekeeper(single sign on) project
Note: only 1 factor authentication test cases

These test have a number of dependencies
1. the database update script updates the gatekeeper schema - the script can be
found at the root of the gatekeeper app
2. the build script starts the gatekeeper app with ssl enbaled by default
3. the build script starts the dummy app with ssl enabled
and application_name is adfuser
@since: Created on 4th January 2014
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
import unittest


class TestGateKeeperLoginURI(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Things that need to be done once
        cls.db = BaseDAO(config['gatekeeper']['db']['connection'])

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
    def test_can_login_with_redirect(self):
        """
        GATEKEEPER_LOGIN_URI_001 test_can_login_with_redirect
        Creates a session through a POST to the login API
        using urlencoded body. Specified redirect
        """
        # login and create session - allow_redirects=False
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False,
            redirect_url=config['gatekeeper']['redirect']
        )

        # assert against database
        db_response = self.gk_dao.get_session_by_cookie_id(self.db, cookie_id)
        self.assertEquals(db_response['cookie_id'], cookie_id)
        self.assertEquals(db_response['user_id'], self.default_test_user)

        # create a session - allow_redirects=True
        response = self.gk_service.create_session_urlencoded(
            allow_redirects=True,
            redirect_url=config['gatekeeper']['redirect']
        )
        # 200 response
        self.assertEquals(response.status_code, requests.codes.ok)
        self.assertTrue('Example Domain' in response.text)

    @attr(env=['test'], priority=1)
    def test_can_login_default_redirect(self):
        """
        GATEKEEPER_LOGIN_URI_002 test_can_login_default_redirect
        creates a session through a POST to the login API using urlencoded
        body. Default redirect
        """

        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        # assert against database
        db_response = self.gk_dao.get_session_by_cookie_id(self.db, cookie_id)
        self.assertEquals(db_response['cookie_id'], cookie_id)
        self.assertEquals(db_response['user_id'], self.default_test_user)

        # create a session - allow redirects
        response = self.gk_service.create_session_urlencoded(
            allow_redirects=True
        )

        # 200 response
        self.assertEquals(response.status_code, requests.codes.ok)

    @attr(env=['test'], priority=1)
    def test_login_default_redirect_validate_url(self):
        """
        GATEKEEPER_LOGIN_URI_003 test_login_default_redirect_validate_url
        Creates a session through a POST to the login API and then
        validates the user_id and session_id(cookie value)
        """

        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
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
    def test_login_with_redirect_validate_url(self):
        """
        GATEKEEPER_LOGIN_URI_004 test_login_with_redirect_validate_url
        Creates a session through a POST to the login API and then verifies
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
        self.assertEquals(response.status_code, requests.codes.ok)
        self.assertTrue('Example Domain' in response.text)

    @attr(env=['test'], priority=1)
    def test_login_with_invalid_data(self):
        """
        GATEKEEPER_LOGIN_URI_004 test_login_with_invalid_data
        combinations of fake username and password
        test for redirects true and false
        """

        # list of dicts with missing data
        bad_data = [
            {'username': '', 'password': ''},
            {'username': self.util.random_str(), 'password': ''},
            {'username': '', 'password':  self.util.random_str()},
            {'username': self.util.random_str(),
                'password': self.util.random_str()}
        ]

        for dict in bad_data:

            # create a session - allow_redirects=FALSE
            response = self.gk_service.create_session_urlencoded(
                allow_redirects=False,
                redirect_url=config['gatekeeper']['redirect'],
                credentials=dict
                )

            self.assertTrue(
                self.gk_service.INVALID_USERNAME_PASSWORD in response.text
            )
            # 302
            self.assertEquals(response.status_code, requests.codes.found)

             # create a session - allow_redirects=True
            response = self.gk_service.create_session_urlencoded(
                allow_redirects=True,
                redirect_url=config['gatekeeper']['redirect'],
                credentials=dict
                )

            self.assertTrue(
                self.gk_service.INVALID_USERNAME_PASSWORD_HTML
                in response.text
            )
            # 302
            self.assertEquals(response.status_code, requests.codes.ok)

    @attr(env=['test'], priority=1)
    def test_can_login_default_redirect_json(self):
        """
        GATEKEEPER_LOGIN_URI_005 test_can_login_default_redirect_json
        creates a session through a POST to the login API using json
        body. Default redirect
        The vast majority of tests are urlencoded - this is as simple login
        using json
        """

        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False, type='json'
        )

        # assert against database
        db_response = self.gk_dao.get_session_by_cookie_id(self.db, cookie_id)
        self.assertEquals(db_response['cookie_id'], cookie_id)
        self.assertEquals(db_response['user_id'], self.default_test_user)

        # 302 response
        self.assertEquals(response.status_code, requests.codes.found)

    @attr(env=['test'], priority=1)
    def test_can_login_default_redirect_json(self):
        """
        GATEKEEPER_LOGIN_URI_006 test_login_max_retries
        A user can only attempt to login a maximum of 5 times
        """

            # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        # create username and apssword
        rand_str = self.util.random_str()
        credentials = {
            'username': self.util.random_str(4),
            'password': self.util.random_str(8)
        }

        user_data = self.gk_service.create_user_data(user_dict=credentials)

        # create a new user
        create_response = self.gk_service.gk_crud(
            session, method='POST', resource="user", data=user_data
        )
        # ensure a 201 is returned
        self.assertEquals(create_response.status_code, requests.codes.created)

        user_id = create_response.json()['user_id']

        # ensure user can login in
         # login in as new user
        response = self.gk_service.create_session_urlencoded(
            allow_redirects=False, credentials=credentials
        )
        # 302 response
        self.assertEquals(response.status_code, requests.codes.found)

        # attempt to login in 5 times with a wrong password
        # set password to a different password to cause failed logins
        bad_credentials = {
            'username': credentials['username'],
            'password': self.util.random_str(8)
        }

        # decrementing for loop
        for attempt_login in range(self.gk_service.MAX_ATTEMPT_LOGIN, 0, -1):
            # login in as new user
            response = self.gk_service.create_session_urlencoded(
                credentials=bad_credentials
            )
            # 200 response
            self.assertEquals(response.status_code, requests.codes.ok)

            # 5th and 4th attempt
            # just invalid user name and password error message
            if (attempt_login > self.gk_service.THREE_ATTEMPTS_LOGIN):
                self.assertTrue(self.gk_service.INVALID_USERNAME_PASSWORD_HTML
                                in response.text)
            # 3rd and 2nd attempt
            # user informed of final two attempts
            elif(attempt_login <= self.gk_service.THREE_ATTEMPTS_LOGIN
                    and attempt_login > 1):
                error_message = self.gk_service.LOGIN_ATTEMPTS % (
                    attempt_login - 1
                    )
                self.assertTrue(error_message in response.text)
            # last attempt
            # user informed that attempts has been exceeded
            else:
                self.assertTrue(self.gk_service.INVALID_USERNAME_PASSWORD_HTML
                                in response.text)
                self.assertTrue(self.gk_service.LOGIN_ATTEMPTS_EXCEEDED
                                in response.text)

        # ensure user can no longer login using the correct credentials
        response = self.gk_service.create_session_urlencoded(
            credentials=credentials
        )
        # 200 response
        self.assertEquals(response.status_code, requests.codes.ok)
        self.assertTrue(
            self.gk_service.LOGIN_ATTEMPTS_EXCEEDED
            in response.text
        )
        # ensure the attempted count in the database is 5
        fail_login_count = self.gk_dao.get_user_by_username(
            self.db, username=credentials['username']
        )['failed_login_count']
        self.assertEquals(fail_login_count, self.gk_service.MAX_ATTEMPT_LOGIN)

        # clean up - delete the user
        del_response = self.gk_service.gk_crud(
            session, method='DELETE', resource="user", id=user_id
        )
        # ensure a 204 is returned
        self.assertEquals(del_response.status_code, requests.codes.no_content)
