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

    @attr(env=['test'], priority=2)
    def test_login_with_invalid_data(self):
        """
        GATEKEEPER_LOGIN_URI_004 test_login_with_invalid_data
        combinations of fake username and password
        test for redirects true and false
        """

        # list of dicts with missing data
        bad_data = [
                    {'username': '', 'password': ''},
                    # {'username': None, 'password': None},
                    {'username': self.util.random_str(), 'password': ''},
                    # {'username': self.util.random_str(), 'password': None},
                    {'username': '', 'password':  self.util.random_str()},
                    # {'username': None, 'password':  self.util.random_str()},
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



