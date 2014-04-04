"""
@summary: Contains a set of test cases for the user organization API
of the gatekeeper(single sign on) project
These test cases realted to the association between user_id and organization_id
Note: only 1 factor authentication test cases

These test have a number of dependencies
1. the database update script updates the gatekeepr schema - the script can be
found at the root of the gatekeeper app
2. the build script starts the gatekeeper app with ssl enbaled by default
3. the build script starts the dummy app with ssl enabled
and application_name is adfuser
@since: Created on 10th January 2014
@author: Conor Fitzgerald
"""

import requests
from nose.plugins.attrib import attr
from . import ApiTestCase


class TestGateUserAppAssocationAPI(ApiTestCase):
    @attr(env=['test'], priority=1)
    def test_user_org_assoc_api_create(self):
        """
        GATEKEEPER_USER_ORG_ASSOC_API_001 test_user_org_assoc_api_create
        create a new user app assocation,
        clean up the data (implictly tests DELETE and GET)
        """
        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        user_org_data = self.gk_service.create_user_org_data(session)
        # create an association
        create_response = self.gk_service.gk_crud(
            session, method='POST', resource="user_org", data=user_org_data
        )
        # ensure a 201 is returned
        self.assertEquals(create_response.status_code, requests.codes.created)

        #verify API
        self.assertUserOrgData(create_response.json(), user_org_data)

        # clean up
        del_response = self.gk_service.gk_crud(
            session,
            method='DELETE',
            resource="user_org",
            id=user_org_data['user_id'],
            id2=user_org_data['organization_id']
        )
        # ensure a 204 is returned
        self.assertEquals(del_response.status_code, requests.codes.no_content)

        # clean up - delete the user
        del_response = self.gk_service.gk_crud(
            session,
            method='DELETE',
            resource="user",
            id=user_org_data['user_id']
        )
        # ensure correct status code is returned
        self.assertEquals(del_response.status_code, requests.codes.no_content)

        # clean up - delete the org
        del_response = self.gk_service.gk_crud(
            session,
            method='DELETE',
            resource="organization",
            id=user_org_data['organization_id']
        )
        # ensure a 204 is returned
        self.assertEquals(del_response.status_code, requests.codes.no_content)

    @attr(env=['test'], priority=1)
    def test_user_org_assoc_api_miss_params(self):
        """
        GATEKEEPER_USER_ORG_ASSOC_API_002 test_user_org_assoc_api_miss_params
        Attempt to create a new assocation with missing parameters
        clean up the data (implictly tests DELETE and GET)
        """
        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        data = self.gk_service.create_user_org_data(session)
        # list of dicts with missing data
        no_data = [
            {'organization_id': data['organization_id'], 'user_id': None},
            {'organization_id': None, 'user_id': data['user_id']}
        ]

        for n_dict in no_data:
            create_response = self.gk_service.gk_crud(
                session, method='POST', resource="user_org", data=n_dict
            )
            # verify the status code and error message
            self.assertEquals(
                create_response.status_code, requests.codes.bad_request
            )
            self.assertTrue(
                self.gk_service.MISSING_PARAM
                in create_response.json()['error']
            )

        # clean up - delete the user
        del_response = self.gk_service.gk_crud(
            session,
            method='DELETE',
            resource="user",
            id=data['user_id']
        )
        # ensure correct status code is returned
        self.assertEquals(del_response.status_code, requests.codes.no_content)

        # clean up - delete the org
        del_response = self.gk_service.gk_crud(
            session,
            method='DELETE',
            resource="organization",
            id=data['organization_id']
        )
        # ensure a 204 is returned
        self.assertEquals(del_response.status_code, requests.codes.no_content)

    @attr(env=['test'], priority=1)
    def test_user_org_assoc_api_no_data(self):
        """
        GATEKEEPER_USER_ORG_ASSOC_API_003 test_user_org_assoc_api_no_data
        attempt to create a bew ssocation with no data
        """
        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        # must set content length to zero
        # otherwise a 411 will be returned i.e no data error
        # but we want to send up no data to get the relevant error message
        session.headers.update({'Content-Length': 0})

        no_data = {'organization_id': None, 'user_id': None}

        create_response = self.gk_service.gk_crud(
            session, method='POST', resource="user_org", data=no_data
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
    def test_user_org_assoc_api_create_dup(self):
        """
        GATEKEEPER_USER_ORG_ASSOC_API_004 test_user_org_assoc_api_create_dup
        attempt to create a duplciation assocation
        clean up the data (implictly tests DELETE and GET)
        """
        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        user_org_data = self.gk_service.create_user_org_data(session)

        # create a new association
        create_response = self.gk_service.gk_crud(
            session, method='POST', resource="user_org", data=user_org_data
        )
        # ensure a 201 is returned
        self.assertEquals(create_response.status_code, requests.codes.created)

        # try to re-create the same association
        create_response = self.gk_service.gk_crud(
            session, method='POST', resource="user_org", data=user_org_data
        )

        self.assertEquals(
            create_response.status_code, requests.codes.conflict
        )
        self.assertTrue(
            self.gk_service.DUPLICATE_KEY in create_response.json()['error']
        )

        # clean up
        del_response = self.gk_service.gk_crud(
            session,
            method='DELETE',
            resource="user_org",
            id=user_org_data['user_id'],
            id2=user_org_data['organization_id']
        )
        # ensure a 204 is returned
        self.assertEquals(del_response.status_code, requests.codes.no_content)

        # clean up - delete the user
        del_response = self.gk_service.gk_crud(
            session,
            method='DELETE',
            resource="user",
            id=user_org_data['user_id']
        )
        # ensure correct status code is returned
        self.assertEquals(del_response.status_code, requests.codes.no_content)

        # clean up - delete the org
        del_response = self.gk_service.gk_crud(
            session,
            method='DELETE',
            resource="organization",
            id=user_org_data['organization_id']
        )
        # ensure a 204 is returned
        self.assertEquals(del_response.status_code, requests.codes.no_content)

    @attr(env=['test'], priority=1)
    def test_user_org_assoc_api_no_update(self):
        """
        GATEKEEPER_USER_ORG_ASSOC_API_005 test_user_org_assoc_api_no_update
        update not allowed,
        clean up the data (implictly tests DELETE and GET)
        """
        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        user_org_data = self.gk_service.create_user_org_data(session)

        # create a new assocation
        create_response = self.gk_service.gk_crud(
            session, method='POST', resource="user_org", data=user_org_data
        )
        # ensure a 201 is returned
        self.assertEquals(create_response.status_code, requests.codes.created)

        # ensure update is not allowed
        create_response = self.gk_service.gk_crud(
            session,
            method='PUT',
            resource="user_org",
            data=user_org_data,
            id=user_org_data['user_id'],
            id2=user_org_data['organization_id']
        )
        # ensure a 405 is returned
        self.assertEquals(
            create_response.status_code, requests.codes.method_not_allowed
        )

        self.assertTrue(
            self.gk_service.METHOD_NOT_AVAILABLE
            in create_response.json()['error']
        )

        # clean up
        del_response = self.gk_service.gk_crud(
            session,
            method='DELETE',
            resource="user_org",
            id=user_org_data['user_id'],
            id2=user_org_data['organization_id']
        )
        # ensure a 204 is returned
        self.assertEquals(del_response.status_code, requests.codes.no_content)

        # clean up - delete the user
        del_response = self.gk_service.gk_crud(
            session,
            method='DELETE',
            resource="user",
            id=user_org_data['user_id']
        )
        # ensure correct status code is returned
        self.assertEquals(del_response.status_code, requests.codes.no_content)

        # clean up - delete the org
        del_response = self.gk_service.gk_crud(
            session,
            method='DELETE',
            resource="organization",
            id=user_org_data['organization_id']
        )
        # ensure a 204 is returned
        self.assertEquals(del_response.status_code, requests.codes.no_content)

    @attr(env=['test'], priority=1)
    def test_user_org_assoc_api_read(self):
        """
        GATEKEEPER_USER_ORG_ASSOC_API_006 test_user_org_assoc_api_read
        read the data
        clean up the data (implictly tests DELETE)
        """
        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        user_org_data = self.gk_service.create_user_org_data(session)

        # create a new association
        create_response = self.gk_service.gk_crud(
            session, method='POST', resource="user_org", data=user_org_data
        )
        # ensure a 201 is returned
        self.assertEquals(create_response.status_code, requests.codes.created)

        # read the new association
        read_response = self.gk_service.gk_crud(
            session,
            method='GET',
            resource="user_org",
            id=user_org_data['user_id'],
            id2=user_org_data['organization_id']
        )

        # ensure a 200 is returned
        self.assertEquals(read_response.status_code, requests.codes.ok)
        # field count
        # 2 fields should be returned
        self.assertEquals(len(read_response.json()), 2)
        #verify API
        self.assertUserOrgData(read_response.json(), user_org_data)

        # clean up
        del_response = self.gk_service.gk_crud(
            session,
            method='DELETE',
            resource="user_org",
            id=user_org_data['user_id'],
            id2=user_org_data['organization_id']
        )
        # ensure a 204 is returned
        self.assertEquals(del_response.status_code, requests.codes.no_content)

        # clean up - delete the user
        del_response = self.gk_service.gk_crud(
            session,
            method='DELETE',
            resource="user",
            id=user_org_data['user_id']
        )
        # ensure correct status code is returned
        self.assertEquals(del_response.status_code, requests.codes.no_content)

        # clean up - delete the org
        del_response = self.gk_service.gk_crud(
            session,
            method='DELETE',
            resource="organization",
            id=user_org_data['organization_id']
        )
        # ensure a 204 is returned
        self.assertEquals(del_response.status_code, requests.codes.no_content)

    @attr(env=['test'], priority=1)
    def test_user_org_assoc_api_read_not_exis(self):
        """
        GATEKEEPER_USER_ORG_ASSOC_API_007 test_user_org_assoc_api_read_not_exis
        attempt to read data that dosen't exist
        clean up the data (implictly tests DELETE)
        """
        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        user_org_data = self.gk_service.create_user_org_data(session)

        # create a new association
        create_response = self.gk_service.gk_crud(
            session, method='POST', resource="user_org", data=user_org_data
        )
        # ensure a 201 is returned
        self.assertEquals(create_response.status_code, requests.codes.created)

        # list of dicts non existant data
        non_existant_data = [
            {'organization_id': self.util.random_int(),
             'user_id': self.util.random_int()},
            {'organization_id': self.util.random_int(),
             'user_id': user_org_data['user_id']},
            {'organization_id': user_org_data['organization_id'],
             'user_id': self.util.random_int()}
        ]
        for n_dict in non_existant_data:
            # read
            read_response = self.gk_service.gk_crud(
                session,
                method='GET',
                resource="user_org",
                id=n_dict['user_id'],
                id2=n_dict['organization_id']
            )

            # 404 response
            self.assertEquals(
                read_response.status_code, requests.codes.not_found
            )
            # verify that the error message is correct
            self.assertTrue(
                self.gk_service.NO_DATA_ERROR in read_response.json()['error']
            )

        # clean up
        del_response = self.gk_service.gk_crud(
            session,
            method='DELETE',
            resource="user_org",
            id=user_org_data['user_id'],
            id2=user_org_data['organization_id']
        )
        # ensure a 204 is returned
        self.assertEquals(del_response.status_code, requests.codes.no_content)

        # clean up - delete the user
        del_response = self.gk_service.gk_crud(
            session,
            method='DELETE',
            resource="user",
            id=user_org_data['user_id']
        )
        # ensure correct status code is returned
        self.assertEquals(del_response.status_code, requests.codes.no_content)

        # clean up - delete the org
        del_response = self.gk_service.gk_crud(
            session,
            method='DELETE',
            resource="organization",
            id=user_org_data['organization_id']
        )
        # ensure a 204 is returned
        self.assertEquals(del_response.status_code, requests.codes.no_content)

    @attr(env=['test'], priority=1)
    def test_user_org_assoc_api_read_no_data(self):
        """
        GATEKEEPER_USER_ORG_ASSOC_API_008 test_user_org_assoc_api_read_no_data
        attempt to read no data
        clean up the data (implictly tests DELETE and GET)
        """
        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        # read with 2 non existant ids
        read_response = self.gk_service.gk_crud(
            session,
            method='GET',
            resource="user_org",
            id='',
            id2='',
        )

        # 400 response
        self.assertEquals(
            read_response.status_code, requests.codes.bad_request
        )
        # verify that the error message is correct
        self.assertTrue(
            self.gk_service.MISSING_PARAMETERS in read_response.json()['error']
        )

    @attr(env=['test'], priority=1)
    def test_user_org_assoc_api_delete(self):
        """
        GATEKEEPER_USER_ORG_ASSOC_API_009 test_user_org_assoc_api_delete
        delete assocation
        """
        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        user_org_data = self.gk_service.create_user_org_data(session)

        # create a app user assocation
        create_response = self.gk_service.gk_crud(
            session, method='POST', resource="user_org", data=user_org_data
        )
        # ensure a 201 is returned
        self.assertEquals(create_response.status_code, requests.codes.created)

        # clean up
        del_response = self.gk_service.gk_crud(
            session,
            method='DELETE',
            resource="user_org",
            id=user_org_data['user_id'],
            id2=user_org_data['organization_id']
        )
        # ensure a 204 is returned
        self.assertEquals(del_response.status_code, requests.codes.no_content)

        # ensure no response is returned
        self.assertEquals(len(del_response.content), 0)

        # read the data
        read_response = self.gk_service.gk_crud(
            session,
            method='GET',
            resource="user_org",
            id=user_org_data['user_id'],
            id2=user_org_data['organization_id']
        )
        self.assertTrue(
            self.gk_service.NO_DATA_ERROR in read_response.json()['error']
        )

        # clean up - delete the user
        del_response = self.gk_service.gk_crud(
            session,
            method='DELETE',
            resource="user",
            id=user_org_data['user_id']
        )
        # ensure correct status code is returned
        self.assertEquals(del_response.status_code, requests.codes.no_content)

        # clean up - delete the org
        del_response = self.gk_service.gk_crud(
            session,
            method='DELETE',
            resource="organization",
            id=user_org_data['organization_id']
        )
        # ensure a 204 is returned
        self.assertEquals(del_response.status_code, requests.codes.no_content)

    @attr(env=['test'], priority=1)
    def test_user_org_assoc_api_del_no_data(self):
        """
        GATEKEEPER_USER_ORG_ASSOC_API_010 test_user_org_assoc_api_del_no_data
        attempt to delete the data when no data is provided
        clean up the data (implictly tests DELETE and GET)
        """
        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        # read with 2 non existant ids
        read_response = self.gk_service.gk_crud(
            session,
            method='DELETE',
            resource="user_org",
            id='',
            id2='',
        )

        # 400 response
        self.assertEquals(
            read_response.status_code, requests.codes.bad_request
        )
        # verify that the error message is correct
        self.assertTrue(
            self.gk_service.MISSING_PARAMETERS in read_response.json()['error']
        )

    @attr(env=['test'], priority=1)
    def test_user_org_assoc_api_del_not_exist(self):
        """
        GATEKEEPER_USER_ORG_ASSOC_API_011 test_user_org_assoc_api_del_not_exist
        attempt to delete identifiers that do not exist
        """
        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        user_org_data = self.gk_service.create_user_org_data(session)

        # create a new association
        create_response = self.gk_service.gk_crud(
            session, method='POST', resource="user_org", data=user_org_data
        )
        # ensure a 201 is returned
        self.assertEquals(create_response.status_code, requests.codes.created)

        # list of dicts non existant data
        non_existant_data = [
            {'organization_id': self.util.random_int(),
             'user_id': self.util.random_int()},
            {'organization_id': self.util.random_int(),
             'user_id': user_org_data['user_id']},
            {'organization_id': user_org_data['organization_id'],
             'user_id': self.util.random_int()}
        ]
        for n_dict in non_existant_data:
            # delete
            read_response = self.gk_service.gk_crud(
                session,
                method='DELETE',
                resource="user_org",
                id=n_dict['user_id'],
                id2=n_dict['organization_id']
            )

            # 404 response
            self.assertEquals(
                read_response.status_code, requests.codes.not_found
            )
            # verify that the error message is correct
            self.assertTrue(
                self.gk_service.NO_DATA_ERROR in read_response.json()['error']
            )

        # clean up
        del_response = self.gk_service.gk_crud(
            session,
            method='DELETE',
            resource="user_org",
            id=user_org_data['user_id'],
            id2=user_org_data['organization_id']
        )
        # ensure a 204 is returned
        self.assertEquals(del_response.status_code, requests.codes.no_content)

        # clean up - delete the user
        del_response = self.gk_service.gk_crud(
            session,
            method='DELETE',
            resource="user",
            id=user_org_data['user_id']
        )
        # ensure correct status code is returned
        self.assertEquals(del_response.status_code, requests.codes.no_content)

        # clean up - delete the org
        del_response = self.gk_service.gk_crud(
            session,
            method='DELETE',
            resource="organization",
            id=user_org_data['organization_id']
        )
        # ensure a 204 is returned
        self.assertEquals(del_response.status_code, requests.codes.no_content)
