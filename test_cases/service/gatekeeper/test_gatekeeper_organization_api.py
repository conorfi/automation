"""
@summary: Contains a set of test cases for the org API of the
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


class TestGatekeeperOrgAPI(ApiTestCase):

    @attr(env=['test'], priority=1)
    def test_org_api_create(self):
        """
        GATEKEEPER_ORG_API_001 test_org_api_create
        create a new org using the org api,
        clean up the data (implictly tests DELETE and GET)
        """
        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        # create a new org
        create_response = self.gk_service.gk_crud(
            session, method='POST', resource="organization"
        )

        # ensure a 201 is returned
        self.assertEquals(create_response.status_code, requests.codes.created)

        # set orgname
        orgname = create_response.json()['name']
         # set org_id
        org_id = create_response.json()['organization_id']
        # get org data directly from database
        org_info = self.gk_dao.get_org_by_orgname(self.db, orgname)

        # verify the creation of the org POST action
        self.assertOrgData(create_response.json(), org_info)

        # clean up - delete the org
        del_response = self.gk_service.gk_crud(
            session, method='DELETE', resource="organization", id=org_id
        )
        # ensure a 204 is returned
        self.assertEquals(del_response.status_code, requests.codes.no_content)

    @attr(env=['test'], priority=1)
    def test_org_api_create_json(self):
        """
        GATEKEEPER_ORG_API_001A test_org_api_create_json
        create a new org using the org api,
        Uses json data
        clean up the data (implictly tests DELETE and GET)
        """
        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        # create a new org
        create_response = self.gk_service.gk_crud(
            session, method='POST', resource="organization", type='json'
        )

        # ensure a 201 is returned
        self.assertEquals(create_response.status_code, requests.codes.created)

        # set orgname
        orgname = create_response.json()['name']
         # set org_id
        org_id = create_response.json()['organization_id']
        # get org data directly from database
        org_info = self.gk_dao.get_org_by_orgname(self.db, orgname)

        # verify the creation of the org POST action
        self.assertOrgData(create_response.json(), org_info)

        # clean up - delete the org
        del_response = self.gk_service.gk_crud(
            session, method='DELETE', resource="organization", id=org_id
        )
        # ensure a 204 is returned
        self.assertEquals(del_response.status_code, requests.codes.no_content)

    @attr(env=['test'], priority=1)
    def test_org_api_create_no_data(self):
        """
        GATEKEEPER_ORG_API_002 test_org_api_create_no_data
        attempt to create a new org using the org api with no data
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
            session, method='POST', resource="organization", data=no_data
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
    def test_org_api_create_invalid_data(self):
        """
        GATEKEEPER_ORG_API_003 test_org_api_create_invalid_data
        attempt to create a new org using the org api with incorrect params
        """
        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        # list of dicts with missing data
        no_data = {'fake': 'fake'}

        create_response = self.gk_service.gk_crud(
            session, method='POST', resource="organization", data=no_data
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
    def test_org_api_create_duplicate_orgname(self):
        """
        GATEKEEPER_ORG_API_004 test_org_api_create_duplicate_orgname
        attempt to create a new org using the org api with same params
        """

        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        org_data = self.gk_service.create_org_data()
        # create a new org
        create_response = self.gk_service.gk_crud(
            session, method='POST', resource="organization", data=org_data
        )

        # ensure a 201 is returned
        self.assertEquals(create_response.status_code, requests.codes.created)

        create_response = self.gk_service.gk_crud(
            session, method='POST', resource="organization", data=org_data
        )

        self.assertEquals(
            create_response.status_code, requests.codes.conflict
        )
        self.assertTrue(
            self.gk_service.DUPLICATE_KEY in create_response.json()['error']
        )

    @attr(env=['test'], priority=1)
    def test_org_api_update(self):
        """
        GATEKEEPER_ORG_API_005 test_org_api_update
        update all the org data using the org api
        """

        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        # create a new org
        create_response = self.gk_service.gk_crud(
            session, method='POST', resource="organization"
        )

        # ensure a 201 is returned
        self.assertEquals(create_response.status_code, requests.codes.created)
        # set org_id
        org_id = create_response.json()['organization_id']

        # update org
        update_response = self.gk_service.gk_crud(
            session, method='PUT', resource="organization", id=org_id
        )

        # set orgname
        orgname = update_response.json()['name']

        # get org_info directly from database
        org_info = self.gk_dao.get_org_by_orgname(self.db, orgname)

        # verify the update of the org POST action
        self.assertOrgData(update_response.json(), org_info)

        # clean up - delete the org
        del_response = self.gk_service.gk_crud(
            session, method='DELETE', resource="organization", id=org_id
        )
        # ensure a 204 is returned
        self.assertEquals(del_response.status_code, requests.codes.no_content)

    @attr(env=['test'], priority=1)
    def test_org_api_update_duplicate_name(self):
        """
        GATEKEEPER_ORG_API_006 test_org_api_update_duplicate_name
        attempt to update an org using the org api but
        the orgname should not be unique
        clean up the data (implictly tests DELETE and GET)
        """

        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        org_one_data = self.gk_service.create_org_data()
        org_two_data = self.gk_service.create_org_data()
        # create org one
        org_one_response = self.gk_service.gk_crud(
            session, method='POST', resource="organization", data=org_one_data
        )
        # ensure correct status code is returned
        self.assertEquals(
            org_one_response.status_code, requests.codes.created
        )
        org_id_one = org_one_response.json()['organization_id']

        # create org two
        org_two_response = self.gk_service.gk_crud(
            session, method='POST', resource="organization", data=org_two_data
        )
        # ensure correct status code is returned
        self.assertEquals(
            org_two_response.status_code, requests.codes.created
        )
        org_id_two = org_two_response.json()['organization_id']

        # update the org one with org two data
        update_response = self.gk_service.gk_crud(
            session,
            method='PUT',
            resource="organization",
            data=org_two_data,
            id=org_id_one
        )

        # ensure correct status code is returned
        self.assertEquals(update_response.status_code, requests.codes.conflict)
        self.assertTrue(
            self.gk_service.DUPLICATE_KEY in update_response.json()['error']
        )
        # clean up - delete the org
        del_response = self.gk_service.gk_crud(
            session, method='DELETE', resource="organization", id=org_id_one
        )
        # ensure correct status code is returned
        self.assertEquals(del_response.status_code, requests.codes.no_content)

         # clean up - delete the org
        del_response = self.gk_service.gk_crud(
            session, method='DELETE', resource="organization", id=org_id_two
        )
        # ensure correct status code is returned
        self.assertEquals(del_response.status_code, requests.codes.no_content)

    @attr(env=['test'], priority=1)
    def test_org_api_update_non_existant_org_id(self):
        """
        GATEKEEPER_ORG_API_007 test_org_api_update_non_existant_org_id
        attempt to update a non existant org id
        """
        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        org_id = self.util.random_int()
        update_response = self.gk_service.gk_crud(
            session, method='PUT', resource="organization", id=org_id
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
    def test_org_api_read(self):
        """
        GATEKEEPER_ORG_API_008 test_org_api_read
        verify the read(GET) response
        """

        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        # create a new org
        create_response = self.gk_service.gk_crud(
            session, method='POST', resource="organization"
        )

        # ensure a 201 is returned
        self.assertEquals(create_response.status_code, requests.codes.created)

        # set org_id
        org_id = create_response.json()['organization_id']
        # set orgname
        orgname = create_response.json()['name']
        # get org_info directly from database
        org_info = self.gk_dao.get_org_by_orgname(self.db, orgname)

        # read(GET) org data
        read_response = self.gk_service.gk_crud(
            session, method='GET', resource="organization", id=org_id
        )

        # ensure a 200 is returned
        self.assertEquals(read_response.status_code, requests.codes.ok)

        # field count check form read
        # 4 fields should be returned
        self.assertEquals(len(read_response.json()), 2)

        # verify the creation of the org POST action
        self.assertOrgData(read_response.json(), org_info)

        # clean up - delete the org
        del_response = self.gk_service.gk_crud(
            session, method='DELETE', resource="organization", id=org_id
        )
        # ensure a 204 is returned
        self.assertEquals(del_response.status_code, requests.codes.no_content)

        # read the new org data
        read_response = self.gk_service.gk_crud(
            session, method='GET', resource="organization", id=org_id
        )
        # ensure a 404 is returned
        self.assertEquals(read_response.status_code, requests.codes.not_found)

        self.assertTrue(
            self.gk_service.NO_DATA_ERROR in read_response.json()['error']
        )

    @attr(env=['test'], priority=1)
    def test_org_api_read_non_existant_org_id(self):
        """
        GATEKEEPER_ORG_API_009 test_org_api_read_non_existant_org_id
        attempt to get a non existant org id
        """
        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        org_id = self.util.random_int()
        update_response = self.gk_service.gk_crud(
            session, method='GET', resource="organization", id=org_id
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
    def test_org_api_delete(self):
        """
        GATEKEEPER_ORG_API_010 test_org_api_delete
        explicit test case for delete functionality
        """

        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        # create a new org
        create_response = self.gk_service.gk_crud(
            session, method='POST', resource="organization"
        )

        # ensure a 201 is returned
        self.assertEquals(create_response.status_code, requests.codes.created)

        # set org_id
        org_id = create_response.json()['organization_id']
        # clean up - delete the org
        del_response = self.gk_service.gk_crud(
            session, method='DELETE', resource="organization", id=org_id
        )
        # ensure a 204 is returned
        self.assertEquals(del_response.status_code, requests.codes.no_content)
        # ensure no response is returned
        self.assertEquals(len(del_response.content), 0)

        # read the new org data
        read_response = self.gk_service.gk_crud(
            session, method='GET', resource="organization", id=org_id
        )
        # ensure a 404 is returned
        self.assertEquals(read_response.status_code, requests.codes.not_found)

        self.assertTrue(
            self.gk_service.NO_DATA_ERROR in read_response.json()['error']
        )

    @attr(env=['test'], priority=1)
    def test_org_api_data_validation(self):
        """
        GATEKEEPER_ORG_API_011 test_org_api_data_validation
        attempt to create org with invalid data
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
                session, method='POST', resource="organization", data=bad_dict
            )
            self.assertEquals(
                create_response.status_code, requests.codes.bad_request
            )

            if 'name' in bad_dict.keys():
                self.assertTrue(
                    self.gk_service.NAME_VALIDATION
                    in create_response.json()['error']
                )
            elif'fake' in bad_dict.keys():
                self.assertTrue(
                    self.gk_service.PARAM_NOT_ALLOWED
                    in create_response.json()['error']
                )

    @attr(env=['test'], priority=1)
    def test_org_api_delete_aam_org(self):
        """
        GATEKEEPER_ORG_API_012 test_org_api_delete_aam_org
        Ensure seed data such as aam org cannot be deleted
        """

        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        # verify if aam organisation is in the org db table
        response = self.gk_dao.get_org_by_orgname(
            self.db, self.gk_service.ORG_AAM)

        if response is not None:
            aam_org_id = response['organization_id']

            # Attempt for the admin user to delete themselves
            # self.default_test_user is the admin user id
            del_response = self.gk_service.gk_crud(
                session,
                method='DELETE',
                resource="organization",
                id=aam_org_id
            )

            # ensure a 403 is returned
            self.assertEquals(
                del_response.status_code,
                requests.codes.forbidden
            )
            # correct error message
            self.assertTrue(
                self.gk_service.DELETE_DATA
                in del_response.json()['error']
            )
