"""
@summary: Contains a set of test cases for the permissions API of the
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


class TestGatePermissionsAPI(unittest.TestCase):

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
    def test_permissions_api(self):
        """
        GATEKEEPER_PERMISSIONS_API_001 test_permissions_api
        Ensure all the user information stored is returned
        """
        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        # return list of all permissions
        response = self.gk_service.gk_listing(
            session,
            resource="permission"
        )

        # 200
        self.assertEquals(response.status_code, requests.codes.ok)

        # ensure that the count of the permissions returned
        # is matched by the count in the database
        api_count = response.json().__len__()
        db_count = self.gk_dao. get_permission_count(self.db)['count']
        self.assertEquals(api_count, db_count, "count mismatch")

    @attr(env=['test'], priority=2)
    def test_permissions_api_name_filter(self):
        """
        GATEKEEPER_PERMISSIONS_API_002 test_permissions_api_name_filter
        Ensure the name filer works correctly
        """
        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        # get an application id
        app_db_data = self.gk_dao.get_app_by_app_name(
            self.db, self.gk_service.ANOTHER_TEST_APP
            )
        app_id = app_db_data['application_id']
        app_name = app_db_data['name']
        app_default_url = app_db_data['default_url']

        # create data
        perms_dict = {'application_id': app_id}
        permission_data = self.gk_service.create_permission_data(
            session,
            dict=perms_dict
        )

        # create a new permission
        create_response = self.gk_service.gk_crud(
            session, method='POST', resource="permission", data=permission_data
        )
        # ensure a 201 is returned
        self.assertEquals(create_response.status_code, requests.codes.created)

        # set permission name
        permission_name = create_response.json()['name']
         # set permission_id
        permission_id = create_response.json()['permission_id']
        # get permission data directly from database
        permission_info = self.gk_dao.get_permission_by_name(
            self.db, permission_name, app_id
        )

        # return just the newly created user fron the list of users
        response = self.gk_service.gk_listing(
            session,
            resource="permission",
            name=permission_name
        )

        # field count check form read
        # 4 fields should be returned
        self.assertEquals(len(response.json()[0]), 4)

        # 200
        self.assertEquals(response.status_code, requests.codes.ok)

        # ensure only one result is returned
        api_count = response.json().__len__()
        self.assertEquals(api_count, 1, "count mismatch")

        # verify the contents of the permissions API
        self.assertEquals(
            create_response.json()['name'], permission_info['name']
        )
        self.assertEquals(
            create_response.json()['permission_id'],
            permission_info['permission_id']
        )
        self.assertEquals(
            create_response.json()['application_id'],
            permission_info['application_id']
        )

        # verify the creation of the permission POST action
        self.assertEquals(
            create_response.json()['application']['name'],
            app_db_data['name']
        )
        self.assertEquals(
            create_response.json()['application']['default_url'],
            app_db_data['default_url']
        )

        self.assertEquals(
            create_response.json()['application']['application_id'],
            app_db_data['application_id']
        )

        # clean up - delete the user
        del_response = self.gk_service.gk_crud(
            session, method='DELETE', resource="permission", id=permission_id
        )
        # ensure a 204 is returned
        self.assertEquals(del_response.status_code, requests.codes.no_content)

    @attr(env=['test'], priority=1)
    def test_perms_api_name_filter_invalid_name(self):
        """
        GATEKEEPER_PERMISSIONS_API_003 test_perms_api_name_filter_invalid_name
        Ensure the name filer works correctly
        """
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        permission_name = "sofake"
        # return just the newly created user from the list of permissions
        response = self.gk_service.gk_listing(
            session,
            resource="permission",
            name=permission_name
        )

        # 200
        self.assertEquals(response.status_code, requests.codes.ok)
        # length 2 i.e empty array
        self.assertEquals(len(response.content), 2)
