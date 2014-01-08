"""
@summary: Contains a set of test cases for the groups API of the
gatekeeper(single sign on) project
Note: only 1 factor authentication test cases

These test have a number of dependencies
1. the database update script updates the gatekeepr schema - the script can be
found at the root of the gatekeeper group
2. the build script starts the gatekeeper app with ssl enbaled by default
3. the build script starts the dummy app with ssl enabled
and group_name is adfuser
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
        self.util = Utility()

    @attr(env=['test'], priority=1)
    def test_groups_api(self):
        """
        GATEKEEPER_GROUPS_API_001 test_groups_api
        Ensure all the group information stored is returned
        """
        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        # return list of all groups
        response = self.gk_service.groups(
            session
        )

        # 200
        # BUG: https://www.pivotaltracker.com/story/show/63375258
        self.assertEquals(response.status_code, requests.codes.ok)

        # ensure that the count of the groups returned
        # is matched by the count in the database
        api_count = response.json().__len__()
        db_count = self.gk_dao.get_group_count(self.db)['count']
        self.assertEquals(api_count, db_count, "count mismatch")

    @attr(env=['test'], priority=1)
    def test_groups_api_name_filter(self):
        """
        GATEKEEPER_GROUPS_API_002 test_groups_api_name_filter
        Ensure the name filer works correctly
        """
        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        # create a new group
        create_response = self.gk_service.group(
            session, method='POST'
        )
        # ensure correct status code is returned
        self.assertEquals(create_response.status_code, requests.codes.created)

        # set ap_id and group name
        group_id = create_response.json()['group_id']
        group_name = create_response.json()['name']
        # get group data from db
        group_data = self.gk_dao.get_group_by_name(
            self.db,
            group_name
        )

        # return just the newly created group from the list of groups
        response = self.gk_service.groups(
            session,
            name=group_name
        )
        # 200
        self.assertEquals(response.status_code, requests.codes.ok)

        # ensure only one result is returned
        api_count = response.json().__len__()
        self.assertEquals(api_count, 1, "count mismatch")

        # verify the groups API against the db data
        self.assertEquals(
            response.json()[0]['group_id'],
            group_data['group_id']
        )
        self.assertEquals(
            response.json()[0]['name'],
            group_data['name']
        )
        # BUG: https://www.pivotaltracker.com/story/show/63208364
        self.assertEquals(
            response.json()[0]['default_url'],
            group_data['default_url']
        )

        # clean up - delete the group
        del_response = self.gk_service.group(
            session, method='DELETE', group_id=group_id
        )
        # ensure correct status code is returned
        self.assertEquals(del_response.status_code, requests.codes.no_content)

    @attr(env=['test'], priority=1)
    def test_groups_api_name_filter_invalid_name(self):
        """
        GATEKEEPER_GROUPS_API_003 test_groups_api_name_filter_invalid_name
        Ensure the name filer works correctly
        """
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        group_name = "sofake"
        # return just the newly created group from the list of groups
        response = self.gk_service.groups(
            session,
            name=group_name
        )

        # BUG:: https://www.pivotaltracker.com/story/show/63208364
        self.assertEquals(response.status_code, requests.codes.not_found)
