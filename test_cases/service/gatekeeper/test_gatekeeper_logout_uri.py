"""
@summary: Contains a set of test cases for the logout URI of the
gatekeeper(single sign on) project
Note: only 1 factor authentication test cases

These test have a number of dependencies
1. the database update script updates the gatekeepr schema - the script can be
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


class TestGateKeeperLogoutURI(unittest.TestCase):

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
    def test_can_logout_with_redirect(self):
        """
        GATEKEEPER_LOGOUT_URI_001 test_can_logout_with_redirect
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

    @attr(env=['test'], priority=1)
    def test_can_logout_default_redirect(self):
        """
        GATEKEEPER_LOGOUT_URI_002 test_can_logout_default_redirect
        Ensures a user session can be deleted using single logout
        using a POST
        Default redirect on logout
        """

        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        response = self.gk_service.validate_url_with_cookie(session)
        self.assertEquals(response.status_code, requests.codes.ok)

        # logout with a post
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

    @attr(env=['test'], priority=1)
    def test_can_logout_get(self):
        """
        GATEKEEPER_LOGOUT_URI_003 test_can_logout_default_redirect
        Ensures the logout confirmation button is returned
        when the logout is called with a get
        Note: the python-request library can not be used for web based tests
        so cannot click the confirmation button
        """

        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        response = self.gk_service.validate_url_with_cookie(session)
        self.assertEquals(response.status_code, requests.codes.ok)

        # logout using GET call
        response = self.gk_service.logout_user_session_get(session)
        self.assertEquals(response.status_code, requests.codes.ok)
        self.assertTrue(self.gk_service.CONFIRM_LOGOUT in response.text)
