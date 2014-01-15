"""
@summary: Contains a set of test cases for the users API of the
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


class TestGateKeeperUsersGroupsListingAPI(unittest.TestCase):

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
    def test_grp_perms_api(self):
        """
        GATEKEEPER_GRP_PERMS_API_001 test_grp_perms_api
        Ensure all the grp_perm information stored is returned
        """
        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        # return list of all users
        response = self.gk_service.gk_assocation_listing(
            session, resource="grp_perm"
        )

        # 200
        self.assertEquals(response.status_code, requests.codes.ok)

        # ensure that the count of the users returned
        # is matched by the count in the database
        api_count = response.json().__len__()
        db_count = self.gk_dao.get_grp_perm_count(self.db)['count']
        self.assertEquals(api_count, db_count, "count mismatch")

    @attr(env=['test'], priority=1)
    def test_grp_perms_filter(self):
        """
        GATEKEEPER_GRP_PERMS_API_002 test_grp_perms_filter
        Ensure the name filer works correctly
        """

        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        grp_perm_data = self.gk_service.create_grp_perm_data(session)

        # create an association
        create_response = self.gk_service.gk_crud(
            session, method='POST', resource="grp_perm", data=grp_perm_data
        )
        # ensure a 201 is returned
        self.assertEquals(create_response.status_code, requests.codes.created)

        # set group_id
        group_id = create_response.json()['group_id']
        # set permission_id
        permission_id = create_response.json()['permission_id']

        dict_matrix = [
            {'permission_id': permission_id},
            {'group_id': group_id},
            {'permission_id': permission_id, 'group_id': group_id}
        ]

        for params in dict_matrix:
            # return just the newly created user fron the list of users
            response = self.gk_service.gk_assocation_listing(
                session,
                resource="grp_perm",
                params=params
            )
            # 200
            self.assertEquals(response.status_code, requests.codes.ok)

            # ensure only one result is returned
            api_count = response.json().__len__()
            self.assertEquals(api_count, 1, "count mismatch")

            # verify the contents of the users API
            self.assertEquals(
                response.json()[0]['permission_id'],
                permission_id)
            self.assertEquals(response.json()[0]['group_id'], group_id)

        # clean up - delete the user
        del_response = self.gk_service.gk_crud(
            session,
            method='DELETE',
            resource="grp_perm",
            id=group_id,
            id2=permission_id
        )
        # ensure a 204 is returned
        self.assertEquals(del_response.status_code, requests.codes.no_content)

    @attr(env=['test'], priority=1)
    def test_users_apps_api_filter_no_data(self):
        """
        GATEKEEPER_GRP_PERMS_API_003 test_users_apps_api_filter_no_data
        Ensure the name filer works correctly when no
        or invalid data is entered
        """

        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        grp_perm_data = self.gk_service.create_grp_perm_data(session)

        # create an association
        create_response = self.gk_service.gk_crud(
            session, method='POST', resource="grp_perm", data=grp_perm_data
        )
        # ensure a 201 is returned
        self.assertEquals(create_response.status_code, requests.codes.created)

        # set group_id
        group_id = create_response.json()['group_id']
        # set permission_id
        permission_id = create_response.json()['permission_id']

        rand_int = self.util.random_int()

        dict_matrix = [
            {'permission_id': ''},
            {'group_id': ''},
            {'permission_id': '', 'group_id': ''}
        ]

        for params in dict_matrix:
            # return just the newly created user fron the list of users
            response = self.gk_service.gk_assocation_listing(
                session,
                resource="grp_perm",
                params=params
            )
            # BUG: https://www.pivotaltracker.com/story/show/63735728
            # 200
            self.assertEquals(response.status_code, requests.codes.ok)

        # clean up - delete the user
        del_response = self.gk_service.gk_crud(
            session,
            method='DELETE',
            resource="grp_perm",
            id=group_id,
            id2=permission_id
        )
        # ensure a 204 is returned
        self.assertEquals(del_response.status_code, requests.codes.no_content)

    @attr(env=['test'], priority=1)
    def test_users_apps_api_filter_invalid_data(self):
        """
        GATEKEEPER_GRP_PERMS_API_004 test_users_apps_api_filter_invalid_data
        Ensure the name filer works correctly when no
        or invalid data is entered
        """

        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        grp_perm_data = self.gk_service.create_grp_perm_data(session)

        # create an association
        create_response = self.gk_service.gk_crud(
            session, method='POST', resource="grp_perm", data=grp_perm_data
        )
        # ensure a 201 is returned
        self.assertEquals(create_response.status_code, requests.codes.created)

        # set group_id
        group_id = create_response.json()['group_id']
        # set permission_id
        permission_id = create_response.json()['permission_id']

        rand_int = self.util.random_int()

        dict_matrix = [
            {'permission_id': rand_int},
            {'group_id': rand_int},
            {'permission_id': rand_int, 'group_id': rand_int}
        ]

        for params in dict_matrix:
            # return just the newly created user fron the list of users
            response = self.gk_service.gk_assocation_listing(
                session,
                resource="grp_perm",
                params=params
            )
            # 200
            self.assertEquals(response.status_code, requests.codes.ok)
            # length 2 i.e empty array
            self.assertEquals(len(response.content), 2)

        # clean up - delete the user
        del_response = self.gk_service.gk_crud(
            session,
            method='DELETE',
            resource="grp_perm",
            id=group_id,
            id2=permission_id
        )
        # ensure a 204 is returned
        self.assertEquals(del_response.status_code, requests.codes.no_content)
