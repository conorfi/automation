"""
@summary: Contains a set of test cases for the group API of the
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
from nose.plugins.attrib import attr
from . import ApiTestCase


class TestGateGroupAPI(ApiTestCase):

    @attr(env=['test'], priority=1)
    def test_group_api_create(self):
        """
        GATEKEEPER_GROUP_API_001 test_group_api_create
        create a new group using the group api,
        clean up the data (implictly tests DELETE and GET)
        """
        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        # create a new group
        create_response = self.gk_service.gk_crud(
            session, method='POST', resource="group"
        )

        # ensure a 201 is returned
        self.assertEquals(create_response.status_code, requests.codes.created)

        # set groupname
        groupname = create_response.json()['name']
         # set group_id
        group_id = create_response.json()['group_id']
        # get group data directly from database
        group_info = self.gk_dao.get_group_by_name(self.db, groupname)

        # verify the creation of the group POST action
        self.assertGroupData(create_response.json(), group_info)

        # clean up - delete the group
        del_response = self.gk_service.gk_crud(
            session, method='DELETE', resource="group", id=group_id
        )
        # ensure a 204 is returned
        self.assertEquals(del_response.status_code, requests.codes.no_content)

    @attr(env=['test'], priority=1)
    def test_group_api_create_json(self):
        """
        GATEKEEPER_GROUP_API_001A test_group_api_create_json
        create a new group using the group api,
        Uses json paylaod
        clean up the data (implictly tests DELETE and GET)

        """
        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        # create a new group
        create_response = self.gk_service.gk_crud(
            session, method='POST', resource="group", type='json'
        )

        # ensure a 201 is returned
        self.assertEquals(create_response.status_code, requests.codes.created)

        # set groupname
        groupname = create_response.json()['name']
         # set group_id
        group_id = create_response.json()['group_id']
        # get group data directly from database
        group_info = self.gk_dao.get_group_by_name(self.db, groupname)

        # verify the creation of the group POST action
        self.assertGroupData(create_response.json(), group_info)

        # clean up - delete the group
        del_response = self.gk_service.gk_crud(
            session, method='DELETE', resource="group", id=group_id
        )
        # ensure a 204 is returned
        self.assertEquals(del_response.status_code, requests.codes.no_content)

    @attr(env=['test'], priority=1)
    def test_group_api_create_no_data(self):
        """
        GATEKEEPER_GROUP_API_002 test_group_api_create_no_data
        attempt to create a new group using the group api with no data
        """
        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        # must set content length to zero
        # otherwise a 411 will be returned i.e no data error
        # but we want to send up no data to get the relevant error message
        session.headers.update({'Content-Length': 0})

        # list of dicts with missing data
        no_data = {'name': None}

        create_response = self.gk_service.gk_crud(
            session, method='POST', resource="group", data=no_data
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
    def test_group_api_create_invalid_data(self):
        """
        GATEKEEPER_GROUP_API_003 test_group_api_create_invalid_data
        attempt to create a new group using the group api with incorrect params
        """
        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        # list of dicts with missing data
        no_data = {'fake': 'fake'}

        create_response = self.gk_service.gk_crud(
            session, method='POST', resource="group", data=no_data
        )

        # 400
        self.assertEquals(
            create_response.status_code,
            requests.codes.bad_request
        )
        self.assertTrue(
            self.gk_service.PARAM_NOT_ALLOWED
            in create_response.json()['error']
        )

    @attr(env=['test'], priority=1)
    def test_group_api_create_duplicate_group_name(self):
        """
        GATEKEEPER_GROUP_API_004 test_group_api_create_duplicate_group_name
        attempt to create a new group using the group api with same params
        """

        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        group_data = self.gk_service.create_group_data()
        # create a new group
        create_response = self.gk_service.gk_crud(
            session, method='POST', resource="group", data=group_data
        )

        # ensure a 201 is returned
        self.assertEquals(create_response.status_code, requests.codes.created)

        create_response = self.gk_service.gk_crud(
            session, method='POST', resource="group", data=group_data
        )

        self.assertEquals(
            create_response.status_code, requests.codes.conflict
        )
        self.assertTrue(
            self.gk_service.DUPLICATE_KEY in create_response.json()['error']
        )

    @attr(env=['test'], priority=1)
    def test_group_api_update(self):
        """
        GATEKEEPER_GROUP_API_005 test_group_api_update
        update all the group data using the group api
        """

        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        # create a new group
        create_response = self.gk_service.gk_crud(
            session, method='POST', resource="group"
        )

        # ensure a 201 is returned
        self.assertEquals(create_response.status_code, requests.codes.created)
        # set group_id
        group_id = create_response.json()['group_id']

        # update group
        update_response = self.gk_service.gk_crud(
            session, method='PUT', resource="group", id=group_id
        )

        # set groupname
        groupname = update_response.json()['name']

        # get group_info directly from database
        group_info = self.gk_dao.get_group_by_name(self.db, groupname)

        # verify the update of the group POST action
        self.assertGroupData(update_response.json(), group_info)

        # clean up - delete the group
        del_response = self.gk_service.gk_crud(
            session, method='DELETE', resource="group", id=group_id
        )
        # ensure a 204 is returned
        self.assertEquals(del_response.status_code, requests.codes.no_content)

    @attr(env=['test'], priority=1)
    def test_group_api_update_duplicate_name(self):
        """
        GATEKEEPER_GROUP_API_006 test_group_api_update_duplicate_name
        attempt to update an group using the group api but
        the groupname should not be unique
        clean up the data (implictly tests DELETE and GET)
        """

        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        group_one_data = self.gk_service.create_group_data()
        group_two_data = self.gk_service.create_group_data()
        # create group one
        group_one_response = self.gk_service.gk_crud(
            session, method='POST', resource="group", data=group_one_data
        )
        # ensure correct status code is returned
        self.assertEquals(
            group_one_response.status_code, requests.codes.created
        )
        group_id_one = group_one_response.json()['group_id']

        # create group two
        group_two_response = self.gk_service.gk_crud(
            session, method='POST', resource="group", data=group_two_data
        )
        # ensure correct status code is returned
        self.assertEquals(
            group_two_response.status_code, requests.codes.created
        )
        group_id_two = group_two_response.json()['group_id']

        # update the group one with group two data
        update_response = self.gk_service.gk_crud(
            session, method='PUT', resource="group",
            data=group_two_data,
            id=group_id_one
        )

        # ensure correct status code is returned
        self.assertEquals(update_response.status_code, requests.codes.conflict)
        self.assertTrue(
            self.gk_service.DUPLICATE_KEY in update_response.json()['error']
        )
        # clean up - delete the group
        del_response = self.gk_service.gk_crud(
            session, method='DELETE', resource="group", id=group_id_one
        )
        # ensure correct status code is returned
        self.assertEquals(del_response.status_code, requests.codes.no_content)

         # clean up - delete the group
        del_response = self.gk_service.gk_crud(
            session, method='DELETE', resource="group", id=group_id_two
        )
        # ensure correct status code is returned
        self.assertEquals(del_response.status_code, requests.codes.no_content)

    @attr(env=['test'], priority=1)
    def test_group_api_update_non_existant_group_id(self):
        """
        GATEKEEPER_GROUP_API_007 test_group_api_update_non_existant_group_id
        attempt to update a non existant group id
        """
        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        group_id = self.util.random_int()
        update_response = self.gk_service.gk_crud(
            session, method='PUT', resource="group", id=group_id
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
    def test_group_api_read(self):
        """
        GATEKEEPER_GROUP_API_008 test_group_api_read
        verify the read(GET) response
        """

        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        # create a new group
        create_response = self.gk_service.gk_crud(
            session, method='POST', resource="group"
        )

        # ensure a 201 is returned
        self.assertEquals(create_response.status_code, requests.codes.created)

        # set group_id
        group_id = create_response.json()['group_id']
        # set groupname
        groupname = create_response.json()['name']
        # get group_info directly from database
        group_info = self.gk_dao.get_group_by_name(self.db, groupname)

        # read(GET) group data
        read_response = self.gk_service.gk_crud(
            session, method='GET', resource="group", id=group_id
        )

        # field count check form read
        # 2 fields should be returned
        self.assertEquals(len(read_response.json()), 2)

        # verify the creation of the group POST action
        self.assertGroupData(read_response.json(), group_info)

        # clean up - delete the group
        del_response = self.gk_service.gk_crud(
            session, method='DELETE', resource="group", id=group_id
        )
        # ensure a 204 is returned
        self.assertEquals(del_response.status_code, requests.codes.no_content)

    @attr(env=['test'], priority=1)
    def test_group_api_read_non_existant_group_id(self):
        """
        GATEKEEPER_GROUP_API_009 test_group_api_read_existant_group_id
        attempt to get a non existant group id
        """
        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        group_id = self.util.random_int()
        update_response = self.gk_service.gk_crud(
            session, method='GET', resource="group", id=group_id
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
    def test_group_api_delete(self):
        """
        GATEKEEPER_GROUP_API_010 test_group_api_delete
        explicit test case for delete functionality
        """

        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        # create a new group
        create_response = self.gk_service.gk_crud(
            session, method='POST', resource="group"
        )

        # ensure a 201 is returned
        self.assertEquals(create_response.status_code, requests.codes.created)

        # set group_id
        group_id = create_response.json()['group_id']
        # clean up - delete the group
        del_response = self.gk_service.gk_crud(
            session, method='DELETE', resource="group", id=group_id
        )
        # ensure a 204 is returned
        self.assertEquals(del_response.status_code, requests.codes.no_content)
        # ensure no response is returned
        self.assertEquals(len(del_response.content), 0)

        # read the new group data
        read_response = self.gk_service.gk_crud(
            session, method='GET', resource="group", id=group_id
        )
        self.assertTrue(
            self.gk_service.NO_DATA_ERROR in read_response.json()['error']
        )

    @attr(env=['test'], priority=1)
    def test_group_api_data_validation(self):
        """
        GATEKEEPER_GROUP_API_011 test_group_api_data_validation
        attempt to create application with invalid data - individual fields
        """
        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        # list of dicts with missing data
        bad_data = [
            {'name': ''},
            {'name': self.util.random_str(101)},
            {'name': '^!\$%&/()=?{[]}+~#-_.:,;<>|\\'},
            {'fake': self.util.random_str()}
        ]

        for bad_dict in bad_data:

            create_response = self.gk_service.gk_crud(
                session, method='POST', resource="group", data=bad_dict
            )

            self.assertEquals(
                create_response.status_code, requests.codes.bad_request
            )

            if('name' in bad_dict.keys()):
                self.assertTrue(
                    self.gk_service.NAME_VALIDATION
                    in create_response.json()['error']
                )
            elif('fake' in bad_dict.keys()):
                self.assertTrue(
                    self.gk_service.PARAM_NOT_ALLOWED
                    in create_response.json()['error']
                )
