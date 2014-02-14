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


class TestGateKeeper2FaAPI(ApiTestCase):

    @attr(env=['test'], priority=1)
    def test_can_login_two_factor(self):
        """
        GATEKEEPER-2FA-API001 test_can_login_two_factor
        verify basic 2FA functionality from gatekeeper application
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

    @attr(env=['test'], priority=1)
    def test_invalid_verification_code(self):
        """
        GATEKEEPER-2FA-API004 test_invalid_verifcation_code -
        Ensure that an invalid verification is not accepted,
        but a valid verification code can still be entered after
        an invalid code is entered
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

        # fake verificaton code
        verification_code = 123456
        payload = {'verification_code': verification_code}

        # try the invalid verification code
        response = self.gk_service.submit_verification_code(
            session,
            payload, allow_redirects=False
        )
        # 302 response(as allow_redirects=False)
        # ensure the url encoded error message is correct
        self.assertEquals(response.status_code, requests.codes.found)
        self.assertTrue(
            self.gk_service.INVALID_VERIFCATION_CODE in response.text
        )

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
            cookie_id_sso)
        self.assertEquals(db_response['cookie_id'], cookie_id_sso)

    @attr(env=['test'], priority=1)
    def test_expired_verification_code(self):
        """
        GATEKEEPER-2FA-API005 test_expired_verification_code
        Ensure than an expired verification code is not accepted
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

        verification_code = self.gk_dao.get_verification_code_by_user_id(
            self.db,
            self.default_test_user
        )['verification_code']

        # expire the verification code
        self.assertTrue(
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
        # 302 response(as allow_redirects=False)
        # ensure the url encoded error message is correct
        self.assertEquals(response.status_code, requests.codes.found)
        self.assertTrue(
            self.gk_service.INVALID_VERIFCATION_CODE in response.text
        )

    @attr(env=['test'], priority=1)
    def test_only_latest_verification_code_is_valid(self):
        """
        GATEKEEPER-2FA-API006 test_only_latest_verification_code_is_valid
        Test to ensure that if multiple verifications are created,
        that only the most recent verification code is accepted
        """
        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False,
            cookie_type="CRED"
        )

        verification_code_one = self.gk_dao.get_verification_code_by_user_id(
            self.db,
            self.default_test_user
        )['verification_code']

        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False,
            cookie_type="CRED"
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
        # 302 response(as allow_redirects=False)
        # ensure the url encoded error message is correct
        self.assertEquals(response.status_code, requests.codes.found)
        self.assertTrue(
            self.gk_service.INVALID_VERIFCATION_CODE in response.text
        )

        payload = {'verification_code': verification_code_two}
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

    @attr(env=['test'], priority=1)
    def test_invalid_credientials_cookie_value_in_session(self):
        """
        GATEKEEPER-2FA-API007  test_invalid_credientials_cook_value_in_session
        verify that a verification code cannot be posted when the session
        contains an incorrect cookie value
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

        fake_cookie_value = "fakecredCookie"

        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False,
            cookie_type="CRED",
            cookie_value=fake_cookie_value
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

        # 302 response(as allow_redirects=False)
        # ensure the url encoded error message is correct
        self.assertEquals(response.status_code, requests.codes.found)
        no_cookie_found = \
            "No+session+with+cookie+%s+found" % fake_cookie_value
        self.assertTrue(no_cookie_found in response.text)

    @attr(env=['test'], priority=1)
    def test_no_verifcation_code(self):
        """
        GATEKEEPER-2FA-API008 - test_no_verifcation_code Verify the behaviour
        when no verification code is provided
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

        verification_code_blank = ''
        # print    verification_code
        payload = {'verification_code': verification_code_blank}

        response = self.gk_service.submit_verification_code(
            session,
            payload, allow_redirects=False
        )
        # 302 response(as allow_redirects=False)
        # ensure the url encoded error message is correct
        self.assertEquals(response.status_code, requests.codes.found)
        self.assertTrue(
            self.gk_service.INVALID_VERIFCATION_CODE in response.text
        )
