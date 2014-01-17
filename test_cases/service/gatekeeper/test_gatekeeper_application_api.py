"""
@summary: Contains a set of test cases for the application API of the
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


class TestGateApplicationAPI(unittest.TestCase):

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
    def test_application_api_create(self):
        """
        GATEKEEPER_APPLICATION_API_001 test_application_api_create
        create a new application using the application api,
        clean up the data (implictly tests DELETE and GET)
        """
        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        create_response = self.gk_service.gk_crud(
            session, method='POST', resource='application'
        )

        # ensure correct status code is returned
        self.assertEquals(create_response.status_code, requests.codes.created)

        app_id = create_response.json()['application_id']
        appname = create_response.json()['name']
        # get app data
        app_data = self.gk_dao.get_app_by_app_name(
            self.db,
            appname
        )
        # verify the post data againist the db data
        self.assertEquals(
            create_response.json()['application_id'],
            app_data['application_id']
        )
        self.assertEquals(
            create_response.json()['name'],
            app_data['name']
        )
        self.assertEquals(
            create_response.json()['default_url'],
            app_data['default_url']
        )

        # clean up - delete the application
        del_response = self.gk_service.gk_crud(
            session, method='DELETE', resource="application", id=app_id
        )
        # ensure correct status code is returned
        self.assertEquals(del_response.status_code, requests.codes.no_content)

        # read the data
        read_response = self.gk_service.gk_crud(
            session, method='GET', resource="application", id=app_id
        )
        self.assertTrue(
            self.gk_service.NO_DATA_ERROR in read_response.json()['error']
        )

    @attr(env=['test'], priority=1)
    def test_application_api_create_json(self):
        """
        GATEKEEPER_APPLICATION_API_001A test_application_api_create_json
        create a new application using the application api,
        clean up the data (implictly tests DELETE and GET)
        Use json data for the paylaod
        """
        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        create_response = self.gk_service.gk_crud(
            session, method='POST', resource='application', type='json'
        )

        # ensure correct status code is returned
        self.assertEquals(create_response.status_code, requests.codes.created)

        app_id = create_response.json()['application_id']
        appname = create_response.json()['name']
        # get app data
        app_data = self.gk_dao.get_app_by_app_name(
            self.db,
            appname
        )
        # verify the post data againist the db data
        self.assertEquals(
            create_response.json()['application_id'],
            app_data['application_id']
        )
        self.assertEquals(
            create_response.json()['name'],
            app_data['name']
        )
        self.assertEquals(
            create_response.json()['default_url'],
            app_data['default_url']
        )

        # clean up - delete the application
        del_response = self.gk_service.gk_crud(
            session, method='DELETE', resource="application", id=app_id
        )
        # ensure correct status code is returned
        self.assertEquals(del_response.status_code, requests.codes.no_content)

        # read the data
        read_response = self.gk_service.gk_crud(
            session, method='GET', resource="application", id=app_id
        )
        self.assertTrue(
            self.gk_service.NO_DATA_ERROR in read_response.json()['error']
        )

    @attr(env=['test'], priority=1)
    def test_application_api_create_dup_name(self):
        """
        GATEKEEPER_APPLICATION_API_002 test_application_api_create_dup_name
        create a new application using the application api,
        then attempt to create an application with the same name
        clean up the data (implictly tests DELETE and GET)
        """

         # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        new_app = self.util.random_str(5)
        name_dict = {'name': new_app}
        app_data = self.gk_service.create_app_data(name_dict)

        # create the new application
        response = self.gk_service.gk_crud(
            session, method='POST', resource="application", data=app_data
        )
        # capture the application id
        app_id = response.json()['application_id']
        # ensure correct status code is returned
        self.assertEquals(response.status_code, requests.codes.created)

        # attempt to use the same data with the same app name again
        response = self.gk_service.gk_crud(
            session, method='POST', resource="application", data=app_data
        )
        # ensure correct status code is returned
        self.assertEquals(response.status_code, requests.codes.conflict)
        self.assertTrue(
            self.gk_service.DUPLICATE_KEY in response.json()['error']
        )

        # clean up - delete the application
        del_response = self.gk_service.gk_crud(
            session, method='DELETE', resource="application", id=app_id
        )
        # ensure correct status code is returned
        self.assertEquals(del_response.status_code, requests.codes.no_content)

        # read the new application data
        read_response = self.gk_service.gk_crud(
            session, method='GET', resource="application", id=app_id
        )
        self.assertTrue(
            self.gk_service.NO_DATA_ERROR in read_response.json()['error']
        )

    @attr(env=['test'], priority=1)
    def test_app_api_create_missing_params(self):
        """
        GATEKEEPER_APPLICATION_API_003 test_app_api_create_missing_params
        attempt to create a new application with missing paramters
        """
        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        # list of dicts with missing data
        missing_data = [
            {'name': None},
            {'default_url': None},
        ]

        for app_dict in missing_data:

            app_data = self.gk_service.create_app_data(app_dict)
            create_response = self.gk_service.gk_crud(
                session, method='POST', resource="application", data=app_data
            )
            self.assertEquals(
                create_response.status_code,
                requests.codes.bad_request
            )
            self.assertTrue(
                self.gk_service.MISSING_PARAM
                in create_response.json()['error']
            )

    @attr(env=['test'], priority=1)
    def test_application_api_create_no_data(self):
        """
        GATEKEEPER_APPLICATION_API_004 test_application_api_create_no_data
        attempt to create a new application with no data
        """
        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        # must set content length to zero
        # otherwise a 411 will be returned i.e no data error
        # but we want to send up no data to get the relevant error message
        session.headers.update({'Content-Length': 0})

        # blank dict
        missing_data = {'name': None}

        app_data = self.gk_service.create_app_data(missing_data)
        create_response = self.gk_service.gk_crud(
            session, method='POST', resource="application", data=missing_data
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
    def test_application_api_update(self):
        """
        GATEKEEPER_APPLICATION_API_005 test_application_api_update
        update an application using the application api,
        verify the repposne with the read function
        clean up the data (implictly tests DELETE and GET)
        """

        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        # create a new application
        create_response = self.gk_service.gk_crud(
            session, method='POST', resource="application"
        )
        # ensure a 200 is returned
        self.assertEquals(create_response.status_code, requests.codes.created)
        app_id = create_response.json()['application_id']

        # update the application

        update_response = self.gk_service.gk_crud(
            session, method='PUT', resource="application", id=app_id
        )

        # ensure a 202 is returned
        self.assertEquals(update_response.status_code, requests.codes.accepted)

        app_id = update_response.json()['application_id']
        appname = update_response.json()['name']
        # get app data
        app_data = self.gk_dao.get_app_by_app_name(
            self.db,
            appname
        )

        # verify the post data againist the db data
        self.assertEquals(
            update_response.json()['application_id'],
            app_data['application_id']
        )
        self.assertEquals(
            update_response.json()['name'],
            app_data['name']
        )
        self.assertEquals(
            update_response.json()['default_url'],
            app_data['default_url']
        )

        # clean up - delete the application
        del_response = self.gk_service.gk_crud(
            session, method='DELETE', resource="application", id=app_id
        )
        # ensure a 204 is returned
        self.assertEquals(del_response.status_code, requests.codes.no_content)

        # read the new application data
        read_response = self.gk_service.gk_crud(
            session, method='GET', resource="application", id=app_id
        )
        self.assertTrue(
            self.gk_service.NO_DATA_ERROR in read_response.json()['error']
        )

    @attr(env=['test'], priority=1)
    def test_application_api_update_individually(self):
        """
        GATEKEEPER_APPLICATION_API_006 test_application_api_update_individually
        update application fields individually using the application api,
        verify the repposne with the read function
        clean up the data (implictly tests DELETE and GET)
        """
        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        # create a new application
        create_response = self.gk_service.gk_crud(
            session, method='POST', resource="application"
        )
        # ensure a 201 is returned
        self.assertEquals(create_response.status_code, requests.codes.created)
        app_id = create_response.json()['application_id']

        # update the application
        rand_str = self.util.random_str(5)
        rand_url = self.util.random_url(5)
        update_data = [
            {'name': rand_str},
            {'default_url': rand_url},
        ]

        for app_dict in update_data:
            app_data = self.gk_service.create_app_data(app_dict)
            update_response = self.gk_service.gk_crud(
                session,
                method='PUT',
                resource="application",
                data=app_data,
                id=app_id
            )
            # ensure a 202 is returned
            self.assertEquals(
                update_response.status_code,
                requests.codes.accepted
            )

        appname = update_response.json()['name']
        # get app data from db
        app_data = self.gk_dao.get_app_by_app_name(
            self.db,
            appname
        )

        # verify the update data againist the db data
        self.assertEquals(
            update_response.json()['application_id'],
            app_data['application_id']
        )
        self.assertEquals(
            update_response.json()['name'],
            app_data['name']
        )
        self.assertEquals(
            update_response.json()['default_url'],
            app_data['default_url']
        )

        # clean up - delete the application
        del_response = self.gk_service.gk_crud(
            session, method='DELETE', resource="application", id=app_id
        )
        # ensure correct status code is returned
        self.assertEquals(del_response.status_code, requests.codes.no_content)

        # read the new application data
        read_response = self.gk_service.gk_crud(
            session, method='GET', resource="application", id=app_id
        )
        self.assertTrue(
            self.gk_service.NO_DATA_ERROR in read_response.json()['error']
        )

    @attr(env=['test'], priority=1)
    def test_application_api_update_dup_name(self):
        """
        GATEKEEPER_APPLICATION_API_007 test_application_api_update_dup_name
        attempt to update an application using the application api but
        the app name should not be unique
        clean up the data (implictly tests DELETE and GET)
        """

        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        app_one = self.util.random_str(5)
        app_two = self.util.random_str(5)
        url_one = self.util.random_url(5)
        url_two = self.util.random_url(5)
        app_one_data = {'name': app_one, 'default_url': url_one}
        app_two_data = {'name': app_two, 'default_url': url_two}

        # create  application one
        app_one_response = self.gk_service.gk_crud(
            session, method='POST', resource="application", data=app_one_data
        )

        # ensure correct status code is returned
        self.assertEquals(app_one_response.status_code, requests.codes.created)
        app_id_one = app_one_response.json()['application_id']

        # create  application two
        app_two_response = self.gk_service.gk_crud(
            session, method='POST', resource="application", data=app_two_data
        )
        # ensure correct status code is returned
        self.assertEquals(app_two_response.status_code, requests.codes.created)

        # update the application one with application two data
        update_response = self.gk_service.gk_crud(
            session,
            method='PUT',
            resource="application",
            data=app_two_data,
            id=app_id_one
        )

        # ensure correct status code is returned
        self.assertEquals(update_response.status_code, requests.codes.conflict)
        self.assertTrue(
            self.gk_service.DUPLICATE_KEY in update_response.json()['error']
        )
        # clean up - delete the application
        del_response = self.gk_service.gk_crud(
            session, method='DELETE', resource="application", id=app_id_one
        )
        # ensure correct status code is returned
        self.assertEquals(del_response.status_code, requests.codes.no_content)

        # read the new application data
        read_response = self.gk_service.gk_crud(
            session, method='GET', resource="application", id=app_id_one
        )
        self.assertTrue(
            self.gk_service.NO_DATA_ERROR in read_response.json()['error']
        )

    @attr(env=['test'], priority=1)
    def test_application_api_read(self):
        """
        GATEKEEPER_APPLICATION_API_008 test_application_api_read
        read an application data using the application api
        clean up the data (implictly tests DELETE and GET)
        """
        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        # create a new application
        create_response = self.gk_service.gk_crud(
            session, method='POST', resource="application"
        )

        # ensure a 201 is returned
        self.assertEquals(create_response.status_code, requests.codes.created)
        app_id = create_response.json()['application_id']

        # read the application
        read_response = self.gk_service.gk_crud(
            session, method='GET', resource="application", id=app_id
        )

        # field count check form read
        # 3 fields should be returned
        self.assertEquals(len(read_response.json()), 3)

        # ensure a 200 is returned
        self.assertEquals(read_response.status_code, requests.codes.ok)

        app_id = read_response.json()['application_id']
        appname = read_response.json()['name']
        # get app data from db
        app_data = self.gk_dao.get_app_by_app_name(
            self.db,
            appname
        )

        # verify the post data againist the db data
        self.assertEquals(
            read_response.json()['application_id'],
            app_data['application_id']
        )
        self.assertEquals(
            read_response.json()['name'],
            app_data['name']
        )
        self.assertEquals(
            read_response.json()['default_url'],
            app_data['default_url']
        )

        # clean up - delete the application
        del_response = self.gk_service.gk_crud(
            session, method='DELETE', resource="application", id=app_id
        )
        # ensure a 204 is returned
        self.assertEquals(del_response.status_code, requests.codes.no_content)

        # read the new application data
        read_response = self.gk_service.gk_crud(
            session, method='GET', resource="application", id=app_id
        )
        self.assertTrue(
            self.gk_service.NO_DATA_ERROR in read_response.json()['error']
        )

    @attr(env=['test'], priority=1)
    def test_application_api_update_not_existant_app_id(self):
        """
        GATEKEEPER_APPLICATION_API_009 test_application_api_invalid_app_id
        attempt to update an application with an app_id that dosen't exist
        """
        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        update_app = self.util.random_str(5)
        update_url = self.util.random_url(5)
        app_data = {'name': update_app, 'default_url': update_url}

        # create random integer for the application id
        app_id = self.util.random_int()

        # update the application
        update_response = self.gk_service.gk_crud(
            session,
            method='PUT',
            resource="application",
            data=app_data,
            id=app_id
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
    def test_application_api_read_not_existant_app_id(self):
        """
        GATEKEEPER_APPLICATION_API_010 test_application_api_invalid_app_id
        attempt to read an application with an app_id that dosen't exist
        """
        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        # create random integer for the application id
        app_id = self.util.random_int()

        # read the new application data
        read_response = self.gk_service.gk_crud(
            session, method='GET', resource="application", id=app_id
        )

        # 404 response
        self.assertEquals(read_response.status_code, requests.codes.not_found)
        # verify that the error message is correct
        self.assertTrue(
            self.gk_service.NO_DATA_ERROR in read_response.json()['error']
        )

    @attr(env=['test'], priority=1)
    def test_application_api_delete(self):
        """
        GATEKEEPER_APPLICATION_API_011 test_application_api_delete
        delete an application using the application api
        This test case is to have a test case that explictly
        tests the delete functioanlity
        """
        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        new_app = self.util.random_str(5)
        new_url = self.util.random_url(5)
        app_data = {'name': new_app, 'default_url': new_url}

        # create a new application
        create_response = self.gk_service.gk_crud(
            session, method='POST', resource="application", data=app_data
        )
        # ensure correct status code is returned
        self.assertEquals(create_response.status_code, requests.codes.created)

        app_id = create_response.json()['application_id']

        # read the new application data
        read_response = self.gk_service.gk_crud(
            session, method='GET', resource="application", id=app_id
        )

        # ensure correct status code is returned
        self.assertEquals(read_response.status_code, requests.codes.ok)

        # clean up - delete the application
        del_response = self.gk_service.gk_crud(
            session, method='DELETE', resource="application", id=app_id
        )
        # ensure correct status code is returned
        self.assertEquals(del_response.status_code, requests.codes.no_content)
        # ensure no response is returned
        self.assertEquals(len(del_response.content), 0)

        # read the new application data
        read_response = self.gk_service.gk_crud(
            session, method='GET', resource="application", id=app_id
        )
        self.assertTrue(
            self.gk_service.NO_DATA_ERROR in read_response.json()['error']
        )

    @attr(env=['test'], priority=1)
    def test_application_api_delete_not_existant_app_id(self):
        """
        GATEKEEPER_APPLICATION_API_012 test_application_api_invalid_app_id
        attempt to delete an application with an app_id that dosen't exist
        """
        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        # create random integer for the application id
        app_id = self.util.random_int()

        # read the new application data
        read_response = self.gk_service.gk_crud(
            session, method='DELETE', resource="application", id=app_id
        )

        # 404 response
        self.assertEquals(read_response.status_code, requests.codes.not_found)
        # verify that the error message is correct
        self.assertTrue(
            self.gk_service.NO_DATA_ERROR in read_response.json()['error']
        )

    @attr(env=['test'], priority=1)
    def test_app_api_data_validation_individual(self):
        """
        GATEKEEPER_APPLICATION_API_013 test_app_api_data_validation_individual
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
            {'default_url':  self.util.random_str()},
            {'default_url':  self.util.random_str(513)},
            {'fake': self.util.random_str()}
        ]

        for dict in bad_data:
            data = self.gk_service.create_app_data(dict)
            create_response = self.gk_service.gk_crud(
                session, method='POST', resource="application", data=data
            )

            self.assertEquals(
                create_response.status_code, requests.codes.bad_request
            )

            if('name' in dict.keys()):
                self.assertTrue(
                    self.gk_service.NAME_VALIDATION
                    in create_response.json()['error']
                )
            elif('default_url' in dict.keys()):
                self.assertTrue(
                    self.gk_service.DEFAULT_URL_VALIDATION
                    in create_response.json()['error']
                )
            elif('fake' in dict.keys()):
                self.assertTrue(
                    self.gk_service.PARAM_NOT_ALLOWED
                    in create_response.json()['error']
                )

    @attr(env=['test'], priority=1)
    def test_application_api_data_validation_multiple(self):
        """
        GATEKEEPER_APP_API_014 test_application_api_data_validation_multiple
        attempt to create application with invalid data - multiple fields
        """
        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        # list of dicts with missing data
        bad_data = [
            {'name': '', 'default_url':  self.util.random_str()},
        ]

        for user_dict in bad_data:
            data = self.gk_service.create_app_data(user_dict)
            create_response = self.gk_service.gk_crud(
                session, method='POST', resource="application", data=data
            )

            self.assertEquals(
                create_response.status_code, requests.codes.bad_request
            )

            self.assertTrue(
                self.gk_service.NAME_VALIDATION
                in create_response.json()['error']
            )

            self.assertTrue(
                self.gk_service.DEFAULT_URL_VALIDATION
                in create_response.json()['error']
            )

    @attr(env=['test'], priority=1)
    def test_application_api_delete_gk_app(self):
        """
        GATEKEEPER_APP_API_015 test_application_api_delete_gk_app
        Ensure seed data such as gatekeeper application cannot be deleted
        """

        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        gk_app_id = self.gk_dao.get_app_by_app_name(
            self.db, self.gk_service.GK_APP)['application_id']

        # Attempt for the admin user to delete themselves
        # self.default_test_user is the admin user id
        del_response = self.gk_service.gk_crud(
            session,
            method='DELETE',
            resource="application",
            id=gk_app_id
        )

        # ensure a 403 is returned
        self.assertEquals(del_response.status_code, requests.codes.forbidden)
        # correct error message
        self.assertTrue(
            self.gk_service.DELETE_DATA
            in del_response.json()['error']
        )
