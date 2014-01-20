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
    def test_can_recover_account(self):
        """
        GATEKEEPER_RECOVER_ACCOUNT_001 test_can_recover_account
        A user can recover their account through their email
        """

       # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        # create a new user
        create_response = self.gk_service.gk_crud(
            session, method='POST', resource="user"
        )

        # ensure a 201 is returned
        self.assertEquals(create_response.status_code, requests.codes.created)

        email = create_response.json()['email']
        user_id = create_response.json()['user_id']
        email_dict = {'email': email}

        # check that there is no token in database
        token_one = self.gk_dao.get_token_by_user_id(
            self.db, user_id
        )
        self.assertTrue(
            token_one is None
        )

        # recover call
        response = self.gk_service.recover_account(
            email_dict, allow_redirects=False
        )

        self.assertTrue(
            config['api'][SERVICE_NAME]['recover_account_v1']['post'] in
            response.headers['location']
        )
        self.assertFalse(
            'error' in
            response.headers['location']
        )

        # ensure new token has been created
        token_two = self.gk_dao.get_token_by_user_id(
            self.db, user_id
        )
        self.assertFalse(
            token_two is None
        )

        # clean up - delete the user
        del_response = self.gk_service.gk_crud(
            session, method='DELETE', resource="user", id=user_id
        )
        # ensure a 204 is returned
        self.assertEquals(del_response.status_code, requests.codes.no_content)

    @attr(env=['test'], priority=1)
    def test_can_recover_account_no_email_acc(self):
        """
        GATEKEEPER_RECOVER_ACCOUNT_002 test_can_recover_account_no_email_acc
        No token create if no
        """

        email_dict = {'email': self.util.random_email()}

        # check token count in the database
        token_count_one = self.gk_dao.get_token_count(self.db)

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

        # check token count in the database
        token_count_two = self.gk_dao.get_token_count(self.db)
        self.assertEquals(
            token_count_one, token_count_two
        )
