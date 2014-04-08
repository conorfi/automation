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
from nose.plugins.attrib import attr
from . import ApiTestCase


class TestGateUsersAPI(ApiTestCase):

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
        response = self.gk_service.gk_listing(
            session, resource="group"
        )

        # 200
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
        create_response = self.gk_service.gk_crud(
            session, method='POST', resource="group"
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
        response = self.gk_service.gk_listing(
            session,
            resource="group",
            name=group_name
        )

        # field count check form read
        # 2 fields should be returned
        self.assertEquals(len(response.json()[0]), 2)

        # 200
        self.assertEquals(response.status_code, requests.codes.ok)

        # ensure only one result is returned
        api_count = response.json().__len__()
        self.assertEquals(api_count, 1, "count mismatch")

        # verify the groups API against the db data
        self.assertGroupData(create_response.json(), group_data)

        # clean up - delete the group
        del_response = self.gk_service.gk_crud(
            session, method='DELETE', resource="group", id=group_id
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
        response = self.gk_service.gk_listing(
            session,
            resource="group",
            name=group_name
        )

        # 200
        self.assertEquals(response.status_code, requests.codes.ok)
        # length 2 i.e empty array
        self.assertEquals(len(response.content), 2)
