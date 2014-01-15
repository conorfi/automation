"""
@summary: Contains a set of test cases for the permission API of the
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


class TestGatePermissionAPI(unittest.TestCase):

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
    def test_permission_api_create(self):
        """
        GATEKEEPER_PERMISSION_API_001 test_permission_api_create
        create a new permission using the permission api,
        clean up the data (implictly tests DELETE and GET)
        """
        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        perm_data = self.gk_service.create_permission_data(session)

        # create a new permission
        create_response = self.gk_service.gk_crud(
            session=session,
            method='POST',
            resource="permission",
            data=perm_data
        )

        # ensure a 201 is returned
        self.assertEquals(create_response.status_code, requests.codes.created)

        # get app data from the db
        app_db_data = self.gk_dao.get_app_by_app_name(
            self.db, create_response.json()['application']['name']
            )
        app_id = app_db_data['application_id']
        app_name = app_db_data['name']
        app_default_url = app_db_data['default_url']

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

        # verify the creation of the permission POST action
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

        # clean up - delete the permission
        del_response = self.gk_service.gk_crud(
            session, method='DELETE', resource="permission", id=permission_id
        )
        # ensure a 204 is returned
        self.assertEquals(del_response.status_code, requests.codes.no_content)

        # read the new permission data
        read_response = self.gk_service.gk_crud(
            session, method='GET', resource="permission", id=permission_id
        )
        self.assertTrue(
            self.gk_service.NO_DATA_ERROR in read_response.json()['error']
        )

    @attr(env=['test'], priority=1)
    def test_permission_api_create_json(self):
        """
        GATEKEEPER_PERMISSION_API_001A test_permission_api_create_json
        create a new permission using the permission api,
        Uses json payload
        clean up the data (implictly tests DELETE and GET)
        """
        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        perm_data = self.gk_service.create_permission_data(session)

        # create a new permission
        create_response = self.gk_service.gk_crud(
            session=session,
            method='POST',
            resource="permission",
            data=perm_data,
            type='json'
        )

        # ensure a 201 is returned
        self.assertEquals(create_response.status_code, requests.codes.created)

        # get app data from the db
        app_db_data = self.gk_dao.get_app_by_app_name(
            self.db, create_response.json()['application']['name']
            )
        app_id = app_db_data['application_id']
        app_name = app_db_data['name']
        app_default_url = app_db_data['default_url']

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

        # verify the creation of the permission POST action
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

        # clean up - delete the permission
        del_response = self.gk_service.gk_crud(
            session, method='DELETE', resource="permission", id=permission_id
        )
        # ensure a 204 is returned
        self.assertEquals(del_response.status_code, requests.codes.no_content)

        # read the new permission data
        read_response = self.gk_service.gk_crud(
            session, method='GET', resource="permission", id=permission_id
        )
        self.assertTrue(
            self.gk_service.NO_DATA_ERROR in read_response.json()['error']
        )

    @attr(env=['test'], priority=1)
    def test_permission_api_create_missing_params(self):
        """
        GATEKEEPER_PERMISSION_API_002 test_permission_api_create_missing_params
        attempt to create a new permission using the permission
        api with missing params
        """
        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        rand_str = self.util.random_str()

        # create data with no name
        none_dict = {'application_id': None}
        perm_data = self.gk_service.create_permission_data(
            session, dict=none_dict
        )
        # default data has no app_id
        create_response = self.gk_service.gk_crud(
            session, method='POST', resource="permission", data=perm_data
        )

        # 400
        self.assertEquals(
            create_response.status_code,
            requests.codes.bad_request
        )
        self.assertTrue(
            self.gk_service.MISSING_PARAM
            in create_response.json()['error']
        )

        # create data with no name
        none_dict = {'name': None}
        perm_data = self.gk_service.create_permission_data(
            session, dict=none_dict
        )
                # default data has no app_id
        create_response = self.gk_service.gk_crud(
            session, method='POST', resource="permission", data=perm_data
        )

        # 400
        self.assertEquals(
            create_response.status_code,
            requests.codes.bad_request
        )
        self.assertTrue(
            self.gk_service.MISSING_PARAM
            in create_response.json()['error']
        )

    @attr(env=['test'], priority=1)
    def test_permission_api_create_no_data(self):
        """
        GATEKEEPER_PERMISSION_API_003 test_permission_api_create_no_data
        attempt to create a new permission using the permission
        api with no data
        """
        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        # must set content length to zero
        # otherwise a 411 will be returned i.e no data error
        # but we want to send up no data to get the relevant error message
        session.headers.update({'Content-Length': 0})

        # create dict with no data
        perms_dict = {'name': None}

        # default data has no app_id
        create_response = self.gk_service.gk_crud(
            session, method='POST', resource="permission", data=perms_dict
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
    def test_permission_api_duplicate_name_app(self):
        """
        GATEKEEPER_PERMISSION_API_004 test_permission_api_duplicate_name_app
        attempt to create a new permission using the permission api -
        the permission name and app_id must be unique
        """

        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        permission_data = self.gk_service.create_permission_data(session)

        # create a new permission
        create_response = self.gk_service.gk_crud(
            session, method='POST', resource="permission", data=permission_data
        )

        # ensure a 201 is returned
        self.assertEquals(create_response.status_code, requests.codes.created)

        # set permission_id
        permission_id = create_response.json()['permission_id']

        create_response = self.gk_service.gk_crud(
            session, method='POST', resource="permission", data=permission_data
        )
        self.assertEquals(
            create_response.status_code, requests.codes.conflict
        )

        # clean up - delete the permission
        del_response = self.gk_service.gk_crud(
            session, method='DELETE', resource="permission", id=permission_id
        )
        # ensure a 204 is returned
        self.assertEquals(del_response.status_code, requests.codes.no_content)

        # read the new permission data
        read_response = self.gk_service.gk_crud(
            session, method='GET', resource="permission", id=permission_id
        )
        self.assertTrue(
            self.gk_service.NO_DATA_ERROR in read_response.json()['error']
        )

    @attr(env=['test'], priority=1)
    def test_permission_api_duplicate_name(self):
        """
        GATEKEEPER_PERMISSION_API_005 test_permission_api_duplicate_name
        attempt to create a new permission using the permission api -
        The permission name may not be unique as long as the app_id
        is unique
        """

        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        # get an application id
        app_id_one = self.gk_dao.get_app_by_app_name(
            self.db, self.gk_service.ANOTHER_TEST_APP
            )['application_id']

        # get an application id
        app_id_two = self.gk_dao.get_app_by_app_name(
            self.db, self.gk_service.DEFAULT_TEST_APP
            )['application_id']

        name = self.util.random_str()
        # create data - app id one and non unique name
        perms_dict = {'application_id': app_id_one, 'name': name}

        # create a new permission
        create_response = self.gk_service.gk_crud(
            session, method='POST', resource="permission", data=perms_dict
        )

        # ensure a 201 is returned
        self.assertEquals(create_response.status_code, requests.codes.created)

        # create data - app id one and non unique name
        perms_dict = {'application_id': app_id_two, 'name': name}

        create_response = self.gk_service.gk_crud(
            session, method='POST', resource="permission", data=perms_dict
        )

        # ensure a 201 is returned
        self.assertEquals(create_response.status_code, requests.codes.created)

    @attr(env=['test'], priority=1)
    def test_permission_api_update(self):
        """
        GATEKEEPER_PERMISSION_API_006 test_permission_api_update
        update all the permission data using the permission api
        """
         # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        perm_data = self.gk_service.create_permission_data(session)

        # create a new permission
        create_response = self.gk_service.gk_crud(
            session=session,
            method='POST',
            resource="permission",
            data=perm_data
        )

        # ensure a 201 is returned
        self.assertEquals(create_response.status_code, requests.codes.created)

        # create a new application
        updated_app_data = self.gk_service.gk_crud(
            session, method='POST', resource='application'
        )

        updated_app_id = updated_app_data.json()['application_id']
        updated_app_name = updated_app_data.json()['name']
        updated_app_default_url = updated_app_data.json()['default_url']

        # create data
        perms_dict = {'application_id': updated_app_id}
        permission_data = self.gk_service.create_permission_data(
            session, dict=perms_dict
        )

        # create a new permission
        create_response = self.gk_service.gk_crud(
            session, method='POST', resource="permission", data=permission_data
        )

        # ensure a 201 is returned
        self.assertEquals(create_response.status_code, requests.codes.created)

        # set permission_id
        permission_id = create_response.json()['permission_id']

        # update permission name and application_id
        perms_dict = {
            'application_id': updated_app_id, 'name': self.util.random_str()
        }

        # update application_id
        update_response = self.gk_service.gk_crud(
            session,
            method='PUT', resource="permission",
            id=permission_id,
            data=perms_dict
        )

        # ensure a 202 is returned
        self.assertEquals(update_response.status_code, requests.codes.accepted)

        # set permission name
        permission_name = update_response.json()['name']

        # get permission_info directly from database
        permission_info = self.gk_dao.get_permission_by_name(
            self.db, permission_name, updated_app_id
        )

        # verify the update of the permission POST action
        self.assertEquals(
            update_response.json()['name'], permission_info['name']
        )
        self.assertEquals(
            update_response.json()['permission_id'],
            permission_info['permission_id']
        )
        self.assertEquals(
            update_response.json()['application_id'],
            permission_info['application_id']
        )

        # verify the creation of the permission POST action
        self.assertEquals(
            update_response.json()['application']['name'],
            updated_app_name
        )
        self.assertEquals(
            update_response.json()['application']['default_url'],
            updated_app_default_url
        )

        self.assertEquals(
            update_response.json()['application']['application_id'],
            updated_app_id
        )

        # clean up - delete the permission
        del_response = self.gk_service.gk_crud(
            session, method='DELETE', resource="permission", id=permission_id
        )
        # ensure a 204 is returned
        self.assertEquals(del_response.status_code, requests.codes.no_content)

        # read the new permission data
        read_response = self.gk_service.gk_crud(
            session, method='GET', resource="permission", id=permission_id
        )
        self.assertTrue(
            self.gk_service.NO_DATA_ERROR in read_response.json()['error']
        )

    @attr(env=['test'], priority=1)
    def test_permission_api_update_individually(self):
        """
        GATEKEEPER_PERMISSION_API_007 test_permission_api_update
        update all the permission data using the permission api
        """

        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        perm_data = self.gk_service.create_permission_data(session)

        # create a new permission
        create_response = self.gk_service.gk_crud(
            session=session,
            method='POST',
            resource="permission",
            data=perm_data
        )

        # ensure a 201 is returned
        self.assertEquals(create_response.status_code, requests.codes.created)

         # create a new application
        updated_app_data = self.gk_service.gk_crud(
            session, method='POST', resource='application'
        )

        updated_app_id = updated_app_data.json()['application_id']
        updated_app_name = updated_app_data.json()['name']
        updated_app_default_url = updated_app_data.json()['default_url']

        # create data
        perms_dict = {'application_id': updated_app_id}
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

        # set permission_id
        permission_id = create_response.json()['permission_id']

        # update application_id
        perms_dict = {'application_id': updated_app_id}

        # update application_id
        update_response = self.gk_service.gk_crud(
            session,
            method='PUT', resource="permission",
            id=permission_id,
            data=perms_dict
        )

        # ensure a 202 is returned
        self.assertEquals(update_response.status_code, requests.codes.accepted)

        # create data  for updated name
        perms_dict = {'name': self.util.random_str()}

        # update permission name
        update_response = self.gk_service.gk_crud(
            session,
            method='PUT', resource="permission",
            id=permission_id,
            data=perms_dict
        )
        # ensure a 202 is returned
        self.assertEquals(update_response.status_code, requests.codes.accepted)
        # set permission name
        permission_name = update_response.json()['name']

        # get permission_info directly from database
        permission_info = self.gk_dao.get_permission_by_name(
            self.db, permission_name, updated_app_id
        )

        # verify the update of the permission POST action
        self.assertEquals(
            update_response.json()['name'], permission_info['name']
        )
        self.assertEquals(
            update_response.json()['permission_id'],
            permission_info['permission_id']
        )
        self.assertEquals(
            update_response.json()['application_id'],
            permission_info['application_id']
        )

        # verify the creation of the permission POST action
        self.assertEquals(
            update_response.json()['application']['name'],
            updated_app_name
        )
        self.assertEquals(
            update_response.json()['application']['default_url'],
            updated_app_default_url
        )

        self.assertEquals(
            update_response.json()['application']['application_id'],
            updated_app_id
        )

        # clean up - delete the permission
        del_response = self.gk_service.gk_crud(
            session, method='DELETE', resource="permission", id=permission_id
        )
        # ensure a 204 is returned
        self.assertEquals(del_response.status_code, requests.codes.no_content)

        # read the new permission data
        read_response = self.gk_service.gk_crud(
            session, method='GET', resource="permission", id=permission_id
        )
        self.assertTrue(
            self.gk_service.NO_DATA_ERROR in read_response.json()['error']
        )

    @attr(env=['test'], priority=1)
    def test_permission_api_update_duplicate_name(self):
        """
        GATEKEEPER_PERMISSION_API_008 test_permission_api_update_duplicate_name
        attempt to update an permission using the permission api but
        the permission name can be unique
        clean up the data (implictly tests DELETE and GET)
        """

        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        perms_one_data = self.gk_service.create_permission_data(session)
        perms_two_data = self.gk_service.create_permission_data(session)

        # create permission one
        permission_one_response = self.gk_service.gk_crud(
            session, method='POST', resource="permission", data=perms_one_data
        )
        # ensure correct status code is returned
        self.assertEquals(
            permission_one_response.status_code, requests.codes.created
        )
        permission_id_one = permission_one_response.json()['permission_id']

        # create permission two
        permission_two_response = self.gk_service.gk_crud(
            session, method='POST', resource="permission", data=perms_two_data
        )
        # ensure correct status code is returned
        self.assertEquals(
            permission_two_response.status_code, requests.codes.created
        )
        permission_id_two = permission_two_response.json()['permission_id']

        # update the permission one with permission two data
        update_response = self.gk_service.gk_crud(
            session, method='PUT', resource="permission",
            data=perms_two_data,
            id=permission_id_one
        )

        # ensure correct status code is returned i.e 409 rather than 202
        self.assertEquals(update_response.status_code, requests.codes.conflict)

        # clean up - delete the permission
        del_response = self.gk_service.gk_crud(
            session,
            method='DELETE',
            resource="permission",
            id=permission_id_one
        )
        # ensure correct status code is returned
        self.assertEquals(del_response.status_code, requests.codes.no_content)

         # clean up - delete the permission
        del_response = self.gk_service.gk_crud(
            session,
            method='DELETE',
            resource="permission",
            id=permission_id_two
        )
        # ensure correct status code is returned
        self.assertEquals(del_response.status_code, requests.codes.no_content)

        # read the new permission data
        read_response = self.gk_service.gk_crud(
            session, method='GET', resource="permission", id=permission_id_one
        )
        self.assertTrue(
            self.gk_service.NO_DATA_ERROR in read_response.json()['error']
        )

    @attr(env=['test'], priority=1)
    def test_permission_api_update_invalid_perms_id(self):
        """
        GATEKEEPER_PERMISSION_API_009 test_permission_api_invalid_perms_id
        attempt to update a non existant permission id
        """
        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        permission_id = self.util.random_int()
        update_response = self.gk_service.gk_crud(
            session, method='PUT', resource="permission", id=permission_id
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
    def test_permission_api_update_invalid_app_id(self):
        """
        GATEKEEPER_PERMISSION_API_010 test_permission_api_update_invalid_app_id
        attempt to update a non existant permission id
        """
        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        # create a new permission
        create_response = self.gk_service.gk_crud(
            session, method='POST', resource="permission"
        )

        # ensure a 201 is returned
        self.assertEquals(create_response.status_code, requests.codes.created)

        # set permission_id
        permission_id = create_response.json()['permission_id']

        # get a random application id
        rand_app_id = self.util.random_int()

        # create data
        perms_dict = {'application_id': rand_app_id}

        update_response = self.gk_service.gk_crud(
            session,
            method='PUT', resource="permission",
            id=permission_id,
            data=perms_dict
        )

        # 409 response
        self.assertEquals(
            update_response.status_code, requests.codes.conflict
        )
        # verify that the error message is correct
        self.assertTrue(
            self.gk_service.FK_ERROR in update_response.json()['error']
        )

        # clean up - delete the permission
        del_response = self.gk_service.gk_crud(
            session,
            method='DELETE',
            resource="permission",
            id=permission_id
        )
        # ensure correct status code is returned
        self.assertEquals(del_response.status_code, requests.codes.no_content)

        # read the new permission data
        read_response = self.gk_service.gk_crud(
            session, method='GET', resource="permission", id=permission_id
        )
        self.assertTrue(
            self.gk_service.NO_DATA_ERROR in read_response.json()['error']
        )

    @attr(env=['test'], priority=1)
    def test_permission_api_read(self):
        """
        GATEKEEPER_PERMISSION_API_011 test_permission_api_read
        verify the read(GET) response
        """

        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        # get application data
        app_data = self.gk_service.gk_crud(
            session, method='POST', resource='application'
        )
        app_id = app_data.json()['application_id']
        app_name = app_data.json()['name']
        app_default_url = app_data.json()['default_url']

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

        # set permission_id
        permission_id = create_response.json()['permission_id']
        # set permission name
        permission_name = create_response.json()['name']
        # get permission_info directly from database
        permission_info = self.gk_dao.get_permission_by_name(
            self.db, permission_name, app_id
        )

        # read(GET) permission data
        read_response = self.gk_service.gk_crud(
            session, method='GET', resource="permission", id=permission_id
        )

        # verify the creation of the permission POST action
        self.assertEquals(
            read_response.json()['permission_id'],
            permission_info['permission_id']
        )
        self.assertEquals(
            read_response.json()['name'], permission_info['name']
        )
        self.assertEquals(
            read_response.json()['application_id'],
            permission_info['application_id']
        )

         # verify the creation of the permission POST action
        self.assertEquals(
            create_response.json()['application']['name'],
            app_name
        )
        self.assertEquals(
            create_response.json()['application']['default_url'],
            app_default_url
        )

        self.assertEquals(
            create_response.json()['application']['application_id'],
            app_id
        )

        # clean up - delete the permission
        del_response = self.gk_service.gk_crud(
            session, method='DELETE', resource="permission", id=permission_id
        )
        # ensure a 204 is returned
        self.assertEquals(del_response.status_code, requests.codes.no_content)

        # read the new permission data
        read_response = self.gk_service.gk_crud(
            session, method='GET', resource="permission", id=permission_id
        )
        self.assertTrue(
            self.gk_service.NO_DATA_ERROR in read_response.json()['error']
        )

    @attr(env=['test'], priority=1)
    def test_permission_api_read_non_exist_id(self):
        """
        GATEKEEPER_PERMISSION_API_012 test_permission_api_read_non_exist_id
        attempt to get a non existant permission id
        """
        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        permission_id = self.util.random_int()
        read_response = self.gk_service.gk_crud(
            session, method='GET', resource="permission", id=permission_id
        )

        # 404 response
        self.assertEquals(
            read_response.status_code, requests.codes.not_found
        )
        # verify that the error message is correct
        self.assertTrue(
            self.gk_service.NO_DATA_ERROR in read_response.json()['error']
        )

    @attr(env=['test'], priority=1)
    def test_permission_api_delete(self):
        """
        GATEKEEPER_PERMISSION_API_013 test_permission_api_delete
        explicit test case for delete functionality
        """

        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

       # get an application id
        app_id = self.gk_dao.get_app_by_app_name(
            self.db, self.gk_service.ANOTHER_TEST_APP
            )['application_id']

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

        # set permission_id
        permission_id = create_response.json()['permission_id']
        # clean up - delete the permission
        del_response = self.gk_service.gk_crud(
            session, method='DELETE', resource="permission", id=permission_id
        )
        # ensure a 204 is returned
        self.assertEquals(del_response.status_code, requests.codes.no_content)
        # ensure no response is returned
        self.assertEquals(len(del_response.content), 0)

        # read the new permission data
        read_response = self.gk_service.gk_crud(
            session, method='GET', resource="permission", id=permission_id
        )
        self.assertTrue(
            self.gk_service.NO_DATA_ERROR in read_response.json()['error']
        )

    @attr(env=['test'], priority=1)
    def test_perms_api_data_validation_individual(self):
        """
        GATEKEEPER_PERMISSION_API_014 test_perms_api_data_validation_individual
        attempt to create application with invalid data - individual fields
        """
        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        # list of dicts with missing data
        bad_data = [
            {'name': ''},
            {'name': self.util.random_str(513)},
            {'name': '^!\$%&/()=?{[]}+~#-_.:,;<>|\\'},
            {'application_id':  self.util.random_str()},
            {'fake': self.util.random_str()}
        ]

        for dict in bad_data:
            data = self.gk_service.create_permission_data(session, dict)
            create_response = self.gk_service.gk_crud(
                session, method='POST', resource="permission", data=data
            )
            self.assertEquals(
                create_response.status_code, requests.codes.bad_request
            )

            if('name' in dict.keys()):
                self.assertTrue(
                    self.gk_service.PERM_NAME_VALIDATION
                    in create_response.json()['error']
                )
            elif('application_id' in dict.keys()):
                self.assertTrue(
                    self.gk_service.APP_ID_VALIDATION
                    in create_response.json()['error']
                )
            elif('fake' in dict.keys()):
                self.assertTrue(
                    self.gk_service.PARAM_NOT_ALLOWED
                    in create_response.json()['error']
                )

    @attr(env=['test'], priority=1)
    def test_perms_api_data_validation_multiple(self):
        """
        GATEKEEPER_PERMISSION_API_015 test_perms_api_data_validation_multiple
        attempt to create application with invalid data - multiple fields
        """

        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        # list of dicts with missing data
        bad_data = [
            {'name': '', 'application_id':  self.util.random_str()}
        ]

        for dict in bad_data:
            data = self.gk_service.create_permission_data(session, dict)
            create_response = self.gk_service.gk_crud(
                session, method='POST', resource="permission", data=data
            )
            self.assertEquals(
                create_response.status_code, requests.codes.bad_request
            )

            if('name' in dict.keys() and 'application_id' in dict.keys()):
                self.assertTrue(
                    self.gk_service.PERM_NAME_VALIDATION
                    in create_response.json()['error']
                )
                self.assertTrue(
                    self.gk_service.APP_ID_VALIDATION
                    in create_response.json()['error']
                )
