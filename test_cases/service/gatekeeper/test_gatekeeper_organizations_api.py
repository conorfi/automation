"""
@summary: Contains a set of test cases for the organizations API of the
gatekeeper(single sign on) project
Note: only 1 factor authentication test cases

These test have a number of dependencies
1. the database update script updates the gatekeepr schema - the script can be
found at the root of the gatekeeper org
2. the build script starts the gatekeeper app with ssl enbaled by default
3. the build script starts the dummy app with ssl enabled
and organization_name is adfuser
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
    def test_orgs_api(self):
        """
        GATEKEEPER_ORGANIZATIONS_API_001 test_orgs_api
        Ensure all the organization information stored is returned
        """
        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        # return list of all organizations
        response = self.gk_service.orgs(
            session
        )

        # 200
        self.assertEquals(response.status_code, requests.codes.ok)

        # ensure that the count of the organizations returned
        # is matched by the count in the database
        api_count = response.json().__len__()
        db_count = self.gk_dao.get_org_count(self.db)['count']
        self.assertEquals(api_count, db_count, "count mismatch")

    @attr(env=['test'], priority=1)
    def test_orgs_api_name_filter(self):
        """
        GATEKEEPER_ORGANIZATIONS_API_002 test_orgs_api_name_filter
        Ensure the name filer works correctly
        """
        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        # create a new organization
        create_response = self.gk_service.org(
            session, method='POST'
        )
        # ensure correct status code is returned
        self.assertEquals(create_response.status_code, requests.codes.created)

        # set ap_id and org name
        org_id = create_response.json()['organization_id']
        org_name = create_response.json()['name']
        # get org data from db
        org_data = self.gk_dao.get_org_by_org_name(
            self.db,
            org_name
        )

        # return just the newly created org from the list of orgs
        response = self.gk_service.orgs(
            session,
            name=org_name
        )
        # 200
        self.assertEquals(response.status_code, requests.codes.ok)

        # ensure only one result is returned
        api_count = response.json().__len__()
        self.assertEquals(api_count, 1, "count mismatch")

        # verify the organizations API against the db data
        self.assertEquals(
            response.json()[0]['organization_id'],
            org_data['organization_id']
        )
        self.assertEquals(
            response.json()[0]['name'],
            org_data['name']
        )

        # clean up - delete the organization
        del_response = self.gk_service.org(
            session, method='DELETE', org_id=org_id
        )
        # ensure correct status code is returned
        self.assertEquals(del_response.status_code, requests.codes.no_content)

    @attr(env=['test'], priority=1)
    def test_orgs_api_name_filter_invalid_name(self):
        """
        GATEKEEPER_ORGANIZATIONS_API_003 test_orgs_api_name_filter_invalid_name
        Ensure the name filer works correctly
        """
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        org_name = "sofake"
        # return just the newly created organization from the list of orgs
        response = self.gk_service.orgs(
            session,
            name=org_name
        )

        # 200
        self.assertEquals(response.status_code, requests.codes.ok)
        # length 2 i.e empty array
        self.assertEquals(len(response.content), 2)
