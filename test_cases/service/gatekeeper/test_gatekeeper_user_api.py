"""
@summary: Contains a set of test cases for the user API of the
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


class TestGateUserAPI(unittest.TestCase):

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
    def test_user_api_create(self):
        """
        GATEKEEPER_USER_API_001 test_user_api_create
        create a new user using the user api,
        clean up the data (implictly tests DELETE and GET)
        """
        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        # create a new user
        create_response = self.gk_service.user(
            session, method='POST'
        )

        # ensure a 201 is returned
        self.assertEquals(create_response.status_code, requests.codes.created)

        # set username
        username = create_response.json()['username']
        # get user data directly from database
        user_info = self.gk_dao.get_user_by_username(self.db, username)

        # verify the creation of the user POST action
        self.assertEquals(
            create_response.json()['username'], user_info['username']
        )
        self.assertEquals(
            create_response.json()['user_id'], user_info['user_id']
        )
        self.assertEquals(create_response.json()['name'], user_info['name'])
        self.assertEquals(create_response.json()['phone'], user_info['phone'])
        self.assertEquals(create_response.json()['email'], user_info['email'])
        self.assertEquals(
            create_response.json()['last_logged_in'],
            user_info['last_logged_in']
        )

        # set user_id
        user_id = create_response.json()['user_id']
        # clean up - delete the user
        del_response = self.gk_service.user(
            session, method='DELETE', user_id=user_id
        )
        # ensure a 204 is returned
        self.assertEquals(del_response.status_code, requests.codes.no_content)

        # read the new user data
        read_response = self.gk_service.user(
            session, method='GET', user_id=user_id
        )
        self.assertTrue(
            self.gk_service.NO_DATA_ERROR in read_response.json()['error']
        )

    @attr(env=['test'], priority=1)
    def test_user_api_create_missing_params(self):
        """
        GATEKEEPER_USER_API_002 test_user_api_create_missing_params
        attempt to create a new user using the user api with missing params
        """
        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        # list of dicts with missing data
        no_data = [
            {'username': None},
            {'name': None},
            {'phone': None},
            {'email': None},
            {'password': None}
        ]

        for user_dict in no_data:

            user_data = self.gk_service.create_user_data(user_dict)
            create_response = self.gk_service.user(
                session, method='POST', user_data=user_data
            )
            self.assertEquals(
                create_response.status_code, requests.codes.bad_request
            )
            self.assertTrue(
                self.gk_service.MISSING_PARAM
                in create_response.json()['error']
            )

    @attr(env=['test'], priority=1)
    def test_user_api_create_no_data(self):
        """
        GATEKEEPER_USER_API_003 test_user_api_create_no_data
        attempt to create a new user using the user api with missing params
        """
        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        # must set content length to zero
        # otherwise a 411 will be returned i.e no data error
        # but we want to send up no data to get the relevant error message
        session.headers.update({'Content-Length': 0})

        # create empty dict
        no_data = {'username': None}

        create_response = self.gk_service.user(
            session, method='POST', user_data=no_data
        )

        # 400
        self.assertEquals(
            create_response.status_code,
            requests.codes.bad_request
        )
        self.assertTrue(
            self.gk_service.NO_PARAM_SUPPLIED
            in create_response.json()['error']
        )

    @attr(env=['test'], priority=1)
    def test_user_api_create_duplicate_username(self):
        """
        GATEKEEPER_USER_API_004 test_user_api_create_duplicate_username
        attempt to create a new user using the user api with same params
        """

        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        user_data = self.gk_service.create_user_data()
        # create a new user
        create_response = self.gk_service.user(
            session, method='POST', user_data=user_data
        )

        # ensure a 201 is returned
        self.assertEquals(create_response.status_code, requests.codes.created)

        create_response = self.gk_service.user(
            session, method='POST', user_data=user_data
        )

        self.assertEquals(
            create_response.status_code, requests.codes.conflict
        )
        self.assertTrue(
            self.gk_service.DUPLICATE_KEY in create_response.json()['error']
        )

    @attr(env=['test'], priority=1)
    def test_user_api_update(self):
        """
        GATEKEEPER_USER_API_005 test_user_api_update
        update all the user data using the user api
        """

        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        # create a new user
        create_response = self.gk_service.user(
            session, method='POST'
        )

        # ensure a 201 is returned
        self.assertEquals(create_response.status_code, requests.codes.created)
        # set user_id
        user_id = create_response.json()['user_id']

        # update user
        update_response = self.gk_service.user(
            session, method='PUT', user_id=user_id
        )

        # set username
        username = update_response.json()['username']

        # get user_info directly from database
        user_info = self.gk_dao.get_user_by_username(self.db, username)

        # verify the creation of the user POST action
        self.assertEquals(
            update_response.json()['username'], user_info['username']
        )
        self.assertEquals(
            update_response.json()['user_id'], user_info['user_id']
        )
        self.assertEquals(
            update_response.json()['name'], user_info['name']
        )
        self.assertEquals(
            update_response.json()['phone'], user_info['phone']
        )
        self.assertEquals(
            update_response.json()['email'], user_info['email']
        )
        self.assertEquals(
            update_response.json()['last_logged_in'],
            user_info['last_logged_in']
        )

        # clean up - delete the user
        del_response = self.gk_service.user(
            session, method='DELETE', user_id=user_id
        )
        # ensure a 204 is returned
        self.assertEquals(del_response.status_code, requests.codes.no_content)

        # read the new user data
        read_response = self.gk_service.user(
            session, method='GET', user_id=user_id
        )
        self.assertTrue(
            self.gk_service.NO_DATA_ERROR in read_response.json()['error']
        )

    @attr(env=['test'], priority=1)
    def test_user_api_update_duplicate_name(self):
        """
        GATEKEEPER_USER_API_006 test_user_api_update_duplicate_name
        attempt to update an user using the user api but
        the username should not be unique
        clean up the data (implictly tests DELETE and GET)
        """

        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        rand_username = self.util.random_str(5)
        user_one_data = self.gk_service.create_user_data()
        user_two_data = self.gk_service.create_user_data()
        # create user one
        user_one_response = self.gk_service.user(
            session, method='POST', user_data=user_one_data
        )
        # ensure correct status code is returned
        self.assertEquals(
            user_one_response.status_code, requests.codes.created
        )
        user_id_one = user_one_response.json()['user_id']

        # create user two
        user_two_response = self.gk_service.user(
            session, method='POST', user_data=user_two_data
        )
        # ensure correct status code is returned
        self.assertEquals(
            user_two_response.status_code, requests.codes.created
        )
        # update the user one with user two data
        update_response = self.gk_service.user(
            session, method='PUT', user_data=user_two_data, user_id=user_id_one
        )

        # ensure correct status code is returned
        self.assertEquals(update_response.status_code, requests.codes.conflict)
        self.assertTrue(
            self.gk_service.DUPLICATE_KEY in update_response.json()['error']
        )
        # clean up - delete the user
        del_response = self.gk_service.user(
            session, method='DELETE', user_id=user_id_one
        )
        # ensure correct status code is returned
        self.assertEquals(del_response.status_code, requests.codes.no_content)

        # read the new user data
        read_response = self.gk_service.user(
            session, method='GET', user_id=user_id_one
        )
        self.assertTrue(
            self.gk_service.NO_DATA_ERROR in read_response.json()['error']
        )

    @attr(env=['test'], priority=1)
    def test_user_api_update_individually(self):
        """
        GATEKEEPER_USER_API_007 test_user_api_update_individually
        update fields individually
        """
        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        # create a new user
        create_response = self.gk_service.user(
            session, method='POST'
        )

        # ensure a 201 is returned
        self.assertEquals(create_response.status_code, requests.codes.created)
        # set user_id
        user_id = create_response.json()['user_id']

        # create individual dicts for updating each paramater
        rand_str = self.util.random_str(5)
        phone = self.util.phone_number()
        email = self.util.random_email()
        user_dict = [
            {'username': rand_str},
            {'name': rand_str},
            {'phone': phone},
            {'email': email},
            {'password': rand_str}
        ]

        for data in user_dict:
            user_data = self.gk_service.create_user_data(data)
            update_response = self.gk_service.user(
                session, method='PUT', user_data=user_data, user_id=user_id
            )

        # set username
        username = update_response.json()['username']

        # get user_info directly from database
        user_info = self.gk_dao.get_user_by_username(self.db, username)

        # verify the creation of the user POST action
        self.assertEquals(
            update_response.json()['username'], user_info['username']
        )
        self.assertEquals(
            update_response.json()['user_id'], user_info['user_id']
        )
        self.assertEquals(
            update_response.json()['name'], user_info['name']
        )
        self.assertEquals(
            update_response.json()['phone'], user_info['phone']
        )
        self.assertEquals(update_response.json()['email'], user_info['email'])
        self.assertEquals(
            update_response.json()['last_logged_in'],
            user_info['last_logged_in']
        )

        # clean up - delete the user
        del_response = self.gk_service.user(
            session, method='DELETE', user_id=user_id
        )
        # ensure a 204 is returned
        self.assertEquals(del_response.status_code, requests.codes.no_content)

        # read the new user data
        read_response = self.gk_service.user(
            session, method='GET', user_id=user_id
        )
        self.assertTrue(
            self.gk_service.NO_DATA_ERROR in read_response.json()['error']
        )

    @attr(env=['test'], priority=1)
    def test_user_api_update_non_existant_user_id(self):
        """
        GATEKEEPER_USER_API_008 test_user_api_update_non_existant_user_id
        attempt to update a non existant user id
        """
        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        user_id = self.util.random_int()
        update_response = self.gk_service.user(
            session, method='PUT', user_id=user_id
        )

        # 404 response
        self.assertEquals(
            update_response.status_code, requests.codes.not_found
        )
        # verify that the error message is correct
        self.assertTrue(
            self.gk_service.NO_DATA_ERROR in update_response.json()['error']
        )

    @attr(env=['test'], priority=1)
    def test_user_api_read(self):
        """
        GATEKEEPER_USER_API_009 test_user_api_read
        verify the read(GET) response
        """

        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        # create a new user
        create_response = self.gk_service.user(
            session, method='POST'
        )

        # ensure a 201 is returned
        self.assertEquals(create_response.status_code, requests.codes.created)

        # set user_id
        user_id = create_response.json()['user_id']
        # set username
        username = create_response.json()['username']
        # get user_info directly from database
        user_info = self.gk_dao.get_user_by_username(self.db, username)

        # read(GET) user data
        read_response = self.gk_service.user(
            session, method='GET', user_id=user_id
        )

        # verify the creation of the user POST action
        self.assertEquals(
            read_response.json()['username'], user_info['username']
        )
        self.assertEquals(
            read_response.json()['user_id'], user_info['user_id']
        )
        self.assertEquals(read_response.json()['name'], user_info['name'])
        self.assertEquals(read_response.json()['phone'], user_info['phone'])
        self.assertEquals(read_response.json()['email'], user_info['email'])
        self.assertEquals(
            create_response.json()['last_logged_in'],
            user_info['last_logged_in']
        )

        # clean up - delete the user
        del_response = self.gk_service.user(
            session, method='DELETE', user_id=user_id
        )
        # ensure a 204 is returned
        self.assertEquals(del_response.status_code, requests.codes.no_content)

        # read the new user data
        read_response = self.gk_service.user(
            session, method='GET', user_id=user_id
        )
        self.assertTrue(
            self.gk_service.NO_DATA_ERROR in read_response.json()['error']
        )

    @attr(env=['test'], priority=1)
    def test_user_api_read_existant_user_id(self):
        """
        GATEKEEPER_USER_API_010 test_user_api_read_existant_user_id
        attempt to get a non existant user id
        """
        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        user_id = self.util.random_int()
        update_response = self.gk_service.user(
            session, method='GET', user_id=user_id
        )

        # 404 response
        self.assertEquals(
            update_response.status_code, requests.codes.not_found
        )
        # verify that the error message is correct
        self.assertTrue(
            self.gk_service.NO_DATA_ERROR in update_response.json()['error']
        )

    @attr(env=['test'], priority=1)
    def test_user_api_delete(self):
        """
        GATEKEEPER_USER_API_011 test_user_api_delete
        explicit test case for delete functionality
        """

        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        # create a new user
        create_response = self.gk_service.user(
            session, method='POST'
        )

        # ensure a 201 is returned
        self.assertEquals(create_response.status_code, requests.codes.created)

        # set user_id
        user_id = create_response.json()['user_id']
        # clean up - delete the user
        del_response = self.gk_service.user(
            session, method='DELETE', user_id=user_id
        )
        # ensure a 204 is returned
        self.assertEquals(del_response.status_code, requests.codes.no_content)
        # ensure no response is returned
        self.assertEquals(len(del_response.content), 0)

        # read the new user data
        read_response = self.gk_service.user(
            session, method='GET', user_id=user_id
        )
        self.assertTrue(
            self.gk_service.NO_DATA_ERROR in read_response.json()['error']
        )

    @attr(env=['test'], priority=1)
    def test_user_api_read_non_existant_user_id(self):
        """
        GATEKEEPER_USER_API_012 test_user_api_get_non_existant_user_id
        attempt to get a non existant user id
        """
        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        user_id = self.util.random_int()
        update_response = self.gk_service.user(
            session, method='DELETE', user_id=user_id
        )

        # 404 response
        self.assertEquals(
            update_response.status_code, requests.codes.not_found
        )
        # verify that the error message is correct
        self.assertTrue(
            self.gk_service.NO_DATA_ERROR in update_response.json()['error']
        )

    @attr(env=['test'], priority=1)
    def test_user_api_user_login(self):
        """
        GATEKEEPER_USER_API_013 test_user_api_user_login
        login as newly created,updated and deleted user
        """

        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        # create username and apssword
        rand_str = self.util.random_str()
        credentials = {
            'username': rand_str,
            'password': rand_str
        }
        user_data = self.gk_service.create_user_data(user_dict=credentials)

        # create a new user
        create_response = self.gk_service.user(
            session, method='POST', user_data=user_data
        )
        # ensure a 201 is returned
        self.assertEquals(create_response.status_code, requests.codes.created)

        # login in as new user
        response = self.gk_service.create_session_urlencoded(
            allow_redirects=False, credentials=credentials
        )
        # 303 response
        self.assertEquals(response.status_code, requests.codes.other)

        # set user_id
        user_id = create_response.json()['user_id']

        # update username and password
        rand_str = self.util.random_str()
        credentials = {
            'username': rand_str,
            'password': rand_str
        }
        user_data = self.gk_service.create_user_data(user_dict=credentials)

        # update user
        update_response = self.gk_service.user(
            session, method='PUT', user_id=user_id, user_data=user_data
        )

        # login in as updated user
        response = self.gk_service.create_session_urlencoded(
            allow_redirects=False, credentials=credentials
        )
        # 303 response
        self.assertEquals(response.status_code, requests.codes.other)

        # clean up - delete the user
        del_response = self.gk_service.user(
            session, method='DELETE', user_id=user_id
        )
        # ensure a 204 is returned
        self.assertEquals(del_response.status_code, requests.codes.no_content)

        # BUG: https://www.pivotaltracker.com/story/show/62791020
        # login in as new user

        response = self.gk_service.create_session_urlencoded(
            allow_redirects=False, credentials=credentials
        )
        assert response.status_code, requests.codes
