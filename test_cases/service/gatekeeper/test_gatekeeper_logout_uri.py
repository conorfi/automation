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
from framework.service.gatekeeper.gatekeeper_service import SERVICE_NAME, \
    GateKeeperService
from nose.plugins.attrib import attr
from . import ApiTestCase


class TestGateKeeperLogoutURI(ApiTestCase):

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
            redirect_url=config[SERVICE_NAME]['redirect']
        )

        response = self.gk_service.validate_url_with_cookie(
            session,
            redirect_url=config[SERVICE_NAME]['redirect']
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
