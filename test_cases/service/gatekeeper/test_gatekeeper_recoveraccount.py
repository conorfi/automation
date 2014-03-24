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
from nose.plugins.attrib import attr
from . import ApiTestCase
from testconfig import config
from framework.service.gatekeeper.gatekeeper_service import SERVICE_NAME, \
    GateKeeperService


class TestGateKeeperRecoverAccount(ApiTestCase):

    @attr(env=['test'], priority=1)
    def test_can_recover_account(self):
        """
        GATEKEEPER_RECOVER_ACCOUNT_001 test_can_recover_account
        A user can recover their account through their email
        Tests that the token is created
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

        # ensure a 302 is returned
        self.assertTrue(response.status_code in [requests.codes.found,
                                                 requests.codes.see_other])

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
    def test_can_recover_account_email_no_exits(self):
        """
        GATEKEEPER_RECOVER_ACCOUNT_002 test_can_recover_account_email_no_exits
        No token create if the email is not associated with a customer
        """

        email_dict = {'email': self.util.random_email()}

        # check token count in the database
        token_count_one = self.gk_dao.get_token_count(self.db)

        # recover call
        response = self.gk_service.recover_account(
            email_dict, allow_redirects=False
        )

        # ensure a 302 is returned
        self.assertTrue(response.status_code in [requests.codes.found,
                                                 requests.codes.see_other])

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

    @attr(env=['test'], priority=1)
    def test_can_recover_acc_email_not_provided(self):
        """
        GATEKEEPER_RECOVER_ACCOUNT_003 test_can_recover_acc_email_not_provided
        No token create if the email is not associated with a customer
        """
        # TODO: update/add assertion after this defect is resolved
        # BUG: - https://www.pivotaltracker.com/story/show/64051184

        """
        email_dict = None

        # check token count in the database
        token_count_one = self.gk_dao.get_token_count(self.db)

        # recover call
        response = self.gk_service.recover_account(
            email_dict, allow_redirects=False
        )
        # ensure a 400 is returned
        self.assertEquals(response.status_code, requests.codes.bad_request)

        self.assertTrue(
            config['api']['gk']['recover_account_v1']['param'] in
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
        """

    @attr(env=['test'], priority=1)
    def test_can_recover_acc_empty_email(self):
        """
        GATEKEEPER_RECOVER_ACCOUNT_004 test_can_recover_acc_empty_email
        No token create if the email is not associated with a customer
        """
        # list of dicts with missing data
        bad_data = [
            # empty string
            {'email': ''},
            # either side of the email will be 127
            {'email': self.util.random_email(len=127)},
            # domain less than 2 characters
            {'email': "1@1.1"},
            {'email': self.util.random_str()},
            # BUG - https://www.pivotaltracker.com/story/show/64143024
            # TODO: re-add fake dict when above bug is resolved
            # {'fake': self.util.random_str()}
        ]

        # check token count in the database
        token_count_one = self.gk_dao.get_token_count(self.db)

        for bad_dict in bad_data:
            # recover call
            response = self.gk_service.recover_account(
                bad_dict,
                allow_redirects=False
            )
            # ensure a 302 is returned
            self.assertTrue(response.status_code in [requests.codes.found,
                                                     requests.codes.see_other])

            self.assertTrue(
                'error' in
                response.headers['location']
            )

            if 'email' in bad_dict.keys():
                self.assertTrue(
                    self.gk_service.EMAIL_VALIDATION_HTML
                    in response.headers['location']
                )
            elif 'fake' in bad_dict.keys():
                self.assertTrue(
                    self.gk_service.PARAM_NOT_ALLOWED
                    in urllib2.unquote(response.headers['location'])
                )

        # check token count in the database
        token_count_two = self.gk_dao.get_token_count(self.db)
        self.assertEquals(
            token_count_one, token_count_two
        )
