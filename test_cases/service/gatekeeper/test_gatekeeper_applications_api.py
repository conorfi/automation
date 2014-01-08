"""
@summary: Contains a set of test cases for the applications API of the
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


class TestGateUsersAPI(unittest.TestCase):

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
    def test_users_api(self):
        """
        GATEKEEPER_USERS_API_001 test_users_api
        Ensure all the user information stored is returned
        """
        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        # return list of all applications
        response = self.gk_service.applications(
            session
        )

        # 200
        self.assertEquals(response.status_code, requests.codes.ok)

        # ensure that the count of the applications returned
        # is matched by the count in the database
        api_count = response.json().__len__()
        db_count = self.gk_dao.get_app_count(self.db)['count']
        self.assertEquals(api_count, db_count, "count mismatch")

    @attr(env=['test'], priority=1)
    def test_users_api_name_filter(self):
        """
        GATEKEEPER_USERS_API_002 test_users_api_name_filter
        Ensure the name filer works correctly
        """
        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        # create a new application
        create_response = self.gk_service.application(
            session, method='POST'
        )
        # ensure correct status code is returned
        self.assertEquals(create_response.status_code, requests.codes.created)

        # set ap_id and app name
        app_id = create_response.json()['application_id']
        appname = create_response.json()['name']
        # get app data from db
        app_data = self.gk_dao.get_app_by_app_name(
            self.db,
            appname
        )

        # return just the newly created app from the list of apps
        response = self.gk_service.applications(
            session,
            name=appname
        )
        # 200
        self.assertEquals(response.status_code, requests.codes.ok)

        # ensure only one result is returned
        api_count = response.json().__len__()
        self.assertEquals(api_count, 1, "count mismatch")

        # verify the users API against the db data
        self.assertEquals(
            response.json()[0]['application_id'],
            app_data['application_id']
        )
        self.assertEquals(
            response.json()[0]['name'],
            app_data['name']
        )
        self.assertEquals(
            response.json()[0]['default_url'],
            app_data['default_url']
        )

        # clean up - delete the application
        del_response = self.gk_service.application(
            session, method='DELETE', app_id=app_id
        )
        # ensure correct status code is returned
        self.assertEquals(del_response.status_code, requests.codes.no_content)

    @attr(env=['test'], priority=1)
    def test_users_api_name_filter_invalid_name(self):
        """
        GATEKEEPER_USERS_API_003 test_users_api_name_filter_invalid_name
        Ensure the name filer works correctly
        """
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        appname = "sofake"
        # return just the newly created user from the list of users
        response = self.gk_service.applications(
            session,
            name=appname
        )

        # BUG: https://www.pivotaltracker.com/story/show/63208364
        self.assertEquals(response.status_code, requests.codes.not_found)
