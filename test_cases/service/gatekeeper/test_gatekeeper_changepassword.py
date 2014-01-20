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
from framework.service.gatekeeper.gatekeeper_service import SERVICE_NAME, \
    GateKeeperService
from framework.db.base_dao import BaseDAO
from framework.db.gate_keeper_dao import GateKeeperDAO
from framework.utility.utility import Utility
import Cookie
from multiprocessing import Process
import time
import unittest


class TestGateKeeperRecoverAccount(unittest.TestCase):

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
    def test_change_password(self):
        """
        GATEKEEPER_CHANGE_PASSWORD_001 test_change_password
        A user can change their email
        full test case where user is has exceeded 5 attempts
        """

        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )
        # create username and password
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

        # set email and user_id
        email = create_response.json()['email']
        user_id = create_response.json()['user_id']

        # ensure a 201 is returned
        self.assertEquals(create_response.status_code, requests.codes.created)

        # ensure user can login in
        # login in as new user
        response = self.gk_service.create_session_urlencoded(
            allow_redirects=False, credentials=credentials
        )
        # assert false
        self.assertFalse(
            self.gk_service.INVALID_USERNAME_PASSWORD_HTML in response.text
        )

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

        # create email dictionary
        email_dict = {'email': email}

        # recover call
        response = self.gk_service.recover_account(
            email_dict, allow_redirects=False
        )

        self.assertTrue(
            config['api'][SERVICE_NAME]['recover_account_v1']['param'] in
            response.headers['location']
        )
        self.assertFalse(
            'error' in
            response.headers['location']
        )

        # ensure new token has been created
        token = self.gk_dao.get_token_by_user_id(
            self.db, user_id
        )['token_id']

        password = {'password': self.util.random_str(8)}
        response = self.gk_service.change_password(token, password)

        # 200
        # ensure a 201 is returned
        self.assertEquals(response.status_code, requests.codes.ok)
        self.assertTrue("redirect" and "/" in response.text)

        # failed count reset to zero
        fail_login_count = self.gk_dao.get_user_by_username(
            self.db, username=credentials['username']
        )['failed_login_count']
        self.assertEquals(fail_login_count, 0)

         # clean up - delete the user
        del_response = self.gk_service.gk_crud(
            session, method='DELETE', resource="user", id=user_id
        )
        # ensure a 204 is returned
        self.assertEquals(del_response.status_code, requests.codes.no_content)

    @attr(env=['test'], priority=1)
    def test_change_password_simple_flow(self):
        """
        GATEKEEPER_CHANGE_PASSWORD_002 test_change_password_simple_flow
        Simple flow - just reset password
        """

        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )
        # create username and password
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

        # set email and user_id
        email = create_response.json()['email']
        user_id = create_response.json()['user_id']

        # ensure a 201 is returned
        self.assertEquals(create_response.status_code, requests.codes.created)

        # ensure user can login in
        # login in as new user
        response = self.gk_service.create_session_urlencoded(
            allow_redirects=False, credentials=credentials
        )
        # assert false
        self.assertFalse(
            self.gk_service.INVALID_USERNAME_PASSWORD_HTML in response.text
        )

        # create email dictionary
        email_dict = {'email': email}

        # recover call
        response = self.gk_service.recover_account(
            email_dict, allow_redirects=False
        )

        self.assertTrue(
            config['api']['gk']['recover_account_v1']['param'] in
            response.headers['location']
        )
        self.assertFalse(
            'error' in
            response.headers['location']
        )

        # ensure new token has been created
        token = self.gk_dao.get_token_by_user_id(
            self.db, user_id
        )['token_id']

        password = {'password': self.util.random_str(8)}
        response = self.gk_service.change_password(token, password)

        # 200
        # ensure a 201 is returned
        self.assertEquals(response.status_code, requests.codes.ok)
        self.assertTrue("redirect" and "/" in response.text)

        # clean up - delete the user
        del_response = self.gk_service.gk_crud(
            session, method='DELETE', resource="user", id=user_id
        )
        # ensure a 204 is returned
        self.assertEquals(del_response.status_code, requests.codes.no_content)

    @attr(env=['test'], priority=1)
    def test_change_password_no_pswd_provided(self):
        """
        GATEKEEPER_CHANGE_PASSWORD_003 test_change_password_no_pswd_provided
        No password provided on password change
        """

        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )
        # create username and password
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

        # set email and user_id
        email = create_response.json()['email']
        user_id = create_response.json()['user_id']

        # ensure a 201 is returned
        self.assertEquals(create_response.status_code, requests.codes.created)

        # ensure user can login in
        # login in as new user
        response = self.gk_service.create_session_urlencoded(
            allow_redirects=False, credentials=credentials
        )
        # assert false
        self.assertFalse(
            self.gk_service.INVALID_USERNAME_PASSWORD_HTML in response.text
        )

        # create email dictionary
        email_dict = {'email': email}

        # recover call
        response = self.gk_service.recover_account(
            email_dict, allow_redirects=False
        )

        self.assertTrue(
            config['api']['gk']['recover_account_v1']['param'] in
            response.headers['location']
        )
        self.assertFalse(
            'error' in
            response.headers['location']
        )

        # ensure new token has been created
        token = self.gk_dao.get_token_by_user_id(
            self.db, user_id
        )['token_id']

        password = None
        response = self.gk_service.change_password(token, password)

        # BUG - https://www.pivotaltracker.com/story/show/64051294
        # TODO- add assertion when defect is resolved

        # clean up - delete the user
        del_response = self.gk_service.gk_crud(
            session, method='DELETE', resource="user", id=user_id
        )
        # ensure a 204 is returned
        self.assertEquals(del_response.status_code, requests.codes.no_content)

    @attr(env=['test'], priority=1)
    def test_change_password_pswd_validation(self):
        """
        GATEKEEPER_CHANGE_PASSWORD_004 test_change_password_pswd_validation
        No password provided on password change
        """

        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )
        # create username and password
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

        # set email and user_id
        email = create_response.json()['email']
        user_id = create_response.json()['user_id']

        # ensure a 201 is returned
        self.assertEquals(create_response.status_code, requests.codes.created)

        # ensure user can login in
        # login in as new user
        response = self.gk_service.create_session_urlencoded(
            allow_redirects=False, credentials=credentials
        )
        # assert false
        self.assertFalse(
            self.gk_service.INVALID_USERNAME_PASSWORD_HTML in response.text
        )

        # create email dictionary
        email_dict = {'email': email}

        # recover call
        response = self.gk_service.recover_account(
            email_dict, allow_redirects=False
        )

        self.assertTrue(
            config['api']['gk']['recover_account_v1']['param'] in
            response.headers['location']
        )
        self.assertFalse(
            'error' in
            response.headers['location']
        )

        # ensure new token has been created
        token = self.gk_dao.get_token_by_user_id(
            self.db, user_id
        )['token_id']

         # list of dicts with missing data
        bad_data = [
            # {'password': self.util.random_str(7)},
            # {'password': self.util.random_str(101)},
            # {'password': '^!\$%&/()=?{[]}+~#-_.:,;<>|\\'},
            {'fake': self.util.random_str()}
        ]

        for dict in bad_data:
            response = self.gk_service.change_password(token, dict)
            self.assertEquals(
                response.status_code, requests.codes.bad_request
            )

            if('password' in dict.keys()):
                self.assertTrue(
                    self.gk_service.PASSWORD_VALIDATION
                    in response.json()['error']
                )
            elif('fake' in dict.keys()):
                # BUG - https://www.pivotaltracker.com/story/show/64145128
                # TODO: update message in assertion clause below
                self.assertTrue(
                    self.gk_service.UNEXPECTED_PARAM
                    in response.json()['error']
                )

        # clean up - delete the user
        del_response = self.gk_service.gk_crud(
            session, method='DELETE', resource="user", id=user_id
        )
        # ensure a 204 is returned
        self.assertEquals(del_response.status_code, requests.codes.no_content)
