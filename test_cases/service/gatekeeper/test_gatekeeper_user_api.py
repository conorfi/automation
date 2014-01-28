"""
@summary: Contains a set of test cases for the user API of the
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


class TestGateUserAPI(ApiTestCase):

    @attr(env=['test'], priority=1)
    def test_user_api_create(self):
        """
        GATEKEEPER_USER_API_001 test_user_api_create
        create a new user using the user api,
        clean up the data (implictly tests DELETE and GET)
        """
        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        # create a new user
        create_response = self.gk_service.gk_crud(
            session, method='POST', resource="user"
        )

        # ensure a 201 is returned
        self.assertEquals(create_response.status_code, requests.codes.created)

        # set username
        username = create_response.json()['username']
        # get user data directly from database
        user_info = self.gk_dao.get_user_by_username(self.db, username)

        # verify the creation of the user POST action
        self.assertEquals(
            create_response.json()['username'], user_info['username']
        )
        self.assertEquals(
            create_response.json()['user_id'], user_info['user_id']
        )
        self.assertEquals(create_response.json()['name'], user_info['name'])
        self.assertEquals(create_response.json()['phone'], user_info['phone'])
        self.assertEquals(create_response.json()['email'], user_info['email'])
        self.assertEquals(
            create_response.json()['last_logged_in'],
            user_info['last_logged_in']
        )

        # set user_id
        user_id = create_response.json()['user_id']
        # clean up - delete the user
        del_response = self.gk_service.gk_crud(
            session, method='DELETE', resource="user", id=user_id
        )
        # ensure a 204 is returned
        self.assertEquals(del_response.status_code, requests.codes.no_content)

        # read the new user data
        read_response = self.gk_service.gk_crud(
            session, method='GET', resource="user", id=user_id
        )
        self.assertTrue(
            self.gk_service.NO_DATA_ERROR in read_response.json()['error']
        )

    @attr(env=['test'], priority=1)
    def test_user_api_create_json(self):
        """
        GATEKEEPER_USER_API_002 test_user_api_create_json
        create a new user using the user api,
        clean up the data (implictly tests DELETE and GET)
        """
        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        # create a new user
        create_response = self.gk_service.gk_crud(
            session, method='POST', resource="user", type='json'
        )

        # ensure a 201 is returned
        self.assertEquals(create_response.status_code, requests.codes.created)

        # set username
        username = create_response.json()['username']
        # get user data directly from database
        user_info = self.gk_dao.get_user_by_username(self.db, username)

        # verify the creation of the user POST action
        self.assertEquals(
            create_response.json()['username'], user_info['username']
        )
        self.assertEquals(
            create_response.json()['user_id'], user_info['user_id']
        )
        self.assertEquals(create_response.json()['name'], user_info['name'])
        self.assertEquals(create_response.json()['phone'], user_info['phone'])
        self.assertEquals(create_response.json()['email'], user_info['email'])
        self.assertEquals(
            create_response.json()['last_logged_in'],
            user_info['last_logged_in']
        )

        # set user_id
        user_id = create_response.json()['user_id']
        # clean up - delete the user
        del_response = self.gk_service.gk_crud(
            session, method='DELETE', resource="user", id=user_id
        )
        # ensure a 204 is returned
        self.assertEquals(del_response.status_code, requests.codes.no_content)

        # read the new user data
        read_response = self.gk_service.gk_crud(
            session, method='GET', resource="user", id=user_id
        )
        self.assertTrue(
            self.gk_service.NO_DATA_ERROR in read_response.json()['error']
        )

    @attr(env=['test'], priority=1)
    def test_user_api_create_missing_params(self):
        """
        GATEKEEPER_USER_API_003 test_user_api_create_missing_params
        attempt to create a new user using the user api with missing params
        """
        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        # list of dicts with missing data
        no_data = [
            {'username': None},
            {'name': None},
            {'phone': None},
            {'email': None},
            {'password': None}
        ]

        for user_dict in no_data:

            user_data = self.gk_service.create_user_data(user_dict)
            create_response = self.gk_service.gk_crud(
                session, method='POST', resource="user", data=user_data
            )
            self.assertEquals(
                create_response.status_code, requests.codes.bad_request
            )
            self.assertTrue(
                self.gk_service.MISSING_PARAM
                in create_response.json()['error']
            )

    @attr(env=['test'], priority=1)
    def test_user_api_create_no_data(self):
        """
        GATEKEEPER_USER_API_004 test_user_api_create_no_data
        attempt to create a new user using the user api with missing params
        """
        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        # must set content length to zero
        # otherwise a 411 will be returned i.e no data error
        # but we want to send up no data to get the relevant error message
        session.headers.update({'Content-Length': 0})

        # create empty dict
        no_data = {'username': None}

        create_response = self.gk_service.gk_crud(
            session, method='POST', resource="user", data=no_data
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
    def test_user_api_create_duplicate_fields(self):
        """
        GATEKEEPER_USER_API_005 test_user_api_create_duplicate_fields
        attempt to create a new user using the user api with same params
        """

        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        # create a new user
        create_response = self.gk_service.gk_crud(
            session, method='POST', resource="user"
        )

        user_dict = [
            {'username': create_response.json()['username']},
            {'email': create_response.json()['email']}

        ]

        for data in user_dict:
            user_data = self.gk_service.create_user_data(data)
            create_response = self.gk_service.gk_crud(
                session,
                method='POST',
                resource="user",
                data=user_data
            )

            self.assertEquals(
                create_response.status_code, requests.codes.conflict
            )
            self.assertTrue(
                self.gk_service.DUPLICATE_KEY
                in create_response.json()['error']
            )

    @attr(env=['test'], priority=1)
    def test_user_api_update(self):
        """
        GATEKEEPER_USER_API_006 test_user_api_update
        update all the user data using the user api
        """

        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        # create a new user
        create_response = self.gk_service.gk_crud(
            session, method='POST', resource="user"
        )

        # ensure a 201 is returned
        self.assertEquals(create_response.status_code, requests.codes.created)
        # set user_id
        user_id = create_response.json()['user_id']

        # update user
        update_response = self.gk_service.gk_crud(
            session, method='PUT', resource="user", id=user_id
        )

        # set username
        username = update_response.json()['username']

        # get user_info directly from database
        user_info = self.gk_dao.get_user_by_username(self.db, username)

        # verify the creation of the user POST action
        self.assertEquals(
            update_response.json()['username'], user_info['username']
        )
        self.assertEquals(
            update_response.json()['user_id'], user_info['user_id']
        )
        self.assertEquals(
            update_response.json()['name'], user_info['name']
        )
        self.assertEquals(
            update_response.json()['phone'], user_info['phone']
        )
        self.assertEquals(
            update_response.json()['email'], user_info['email']
        )
        self.assertEquals(
            update_response.json()['last_logged_in'],
            user_info['last_logged_in']
        )

        # clean up - delete the user
        del_response = self.gk_service.gk_crud(
            session, method='DELETE', resource="user", id=user_id
        )
        # ensure a 204 is returned
        self.assertEquals(del_response.status_code, requests.codes.no_content)

        # read the new user data
        read_response = self.gk_service.gk_crud(
            session, method='GET', resource="user", id=user_id
        )
        self.assertTrue(
            self.gk_service.NO_DATA_ERROR in read_response.json()['error']
        )

    @attr(env=['test'], priority=1)
    def test_user_api_update_duplicate_fields(self):
        """
        GATEKEEPER_USER_API_007 test_user_api_update_duplicate_fields
        attempt to update an user using the user api but
        the username should not be unique
        clean up the data (implictly tests DELETE and GET)
        """

        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        rand_username = self.util.random_str(5)
        user_one_data = self.gk_service.create_user_data()
        user_two_data = self.gk_service.create_user_data()
        # create user one
        user_one_response = self.gk_service.gk_crud(
            session, method='POST', resource="user", data=user_one_data
        )
        # ensure correct status code is returned
        self.assertEquals(
            user_one_response.status_code, requests.codes.created
        )
        user_id_one = user_one_response.json()['user_id']

        # create user two
        user_two_response = self.gk_service.gk_crud(
            session, method='POST', resource="user", data=user_two_data
        )
        # ensure correct status code is returned
        self.assertEquals(
            user_two_response.status_code, requests.codes.created
        )

        user_dict = [
            {'username': user_two_response.json()['username']},
            {'email': user_two_response.json()['email']}

        ]

        for data in user_dict:
            user_data = self.gk_service.create_user_data(data)
            create_response = self.gk_service.gk_crud(
                session,
                method='PUT',
                resource="user",
                data=user_data,
                id=user_id_one
            )

            self.assertEquals(
                create_response.status_code, requests.codes.conflict
            )
            self.assertTrue(
                self.gk_service.DUPLICATE_KEY
                in create_response.json()['error']
            )

        # clean up - delete the user
        del_response = self.gk_service.gk_crud(
            session, method='DELETE', resource="user", id=user_id_one
        )
        # ensure correct status code is returned
        self.assertEquals(del_response.status_code, requests.codes.no_content)

        # read the new user data
        read_response = self.gk_service.gk_crud(
            session, method='GET', resource="user", id=user_id_one
        )
        self.assertTrue(
            self.gk_service.NO_DATA_ERROR in read_response.json()['error']
        )

    @attr(env=['test'], priority=1)
    def test_user_api_update_individually(self):
        """
        GATEKEEPER_USER_API_008 test_user_api_update_individually
        update fields individually
        """
        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        # create a new user
        create_response = self.gk_service.gk_crud(
            session, method='POST', resource="user"
        )

        # ensure a 201 is returned
        self.assertEquals(create_response.status_code, requests.codes.created)
        # set user_id
        user_id = create_response.json()['user_id']

        # create individual dicts for updating each paramater
        rand_str = self.util.random_str(5)
        phone = self.util.phone_number()
        email = self.util.random_email()
        user_dict = [
            {'username': self.util.random_str(4)},
            {'name': self.util.random_str(1)},
            {'phone': self.util.phone_number()},
            {'email': self.util.random_email()},
            {'password': self.util.random_str(8)}
        ]

        for data in user_dict:
            user_data = self.gk_service.create_user_data(data)
            update_response = self.gk_service.gk_crud(
                session,
                method='PUT',
                resource="user",
                data=user_data,
                id=user_id
            )

        # set username
        username = update_response.json()['username']

        # get user_info directly from database
        user_info = self.gk_dao.get_user_by_username(self.db, username)

        # verify the creation of the user POST action
        self.assertEquals(
            update_response.json()['username'], user_info['username']
        )
        self.assertEquals(
            update_response.json()['user_id'], user_info['user_id']
        )
        self.assertEquals(
            update_response.json()['name'], user_info['name']
        )
        self.assertEquals(
            update_response.json()['phone'], user_info['phone']
        )
        self.assertEquals(update_response.json()['email'], user_info['email'])
        self.assertEquals(
            update_response.json()['last_logged_in'],
            user_info['last_logged_in']
        )

        # clean up - delete the user
        del_response = self.gk_service.gk_crud(
            session, method='DELETE', resource="user", id=user_id
        )
        # ensure a 204 is returned
        self.assertEquals(del_response.status_code, requests.codes.no_content)

        # read the new user data
        read_response = self.gk_service.gk_crud(
            session, method='GET', resource="user", id=user_id
        )
        self.assertTrue(
            self.gk_service.NO_DATA_ERROR in read_response.json()['error']
        )

    @attr(env=['test'], priority=1)
    def test_user_api_update_non_existant_user_id(self):
        """
        GATEKEEPER_USER_API_009 test_user_api_update_non_existant_user_id
        attempt to update a non existant user id
        """
        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        user_id = self.util.random_int()
        update_response = self.gk_service.gk_crud(
            session, method='PUT', resource="user", id=user_id
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
    def test_user_api_read(self):
        """
        GATEKEEPER_USER_API_010 test_user_api_read
        verify the read(GET) response
        """

        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        # create a new user
        create_response = self.gk_service.gk_crud(
            session, method='POST', resource="user"
        )

        # ensure a 201 is returned
        self.assertEquals(create_response.status_code, requests.codes.created)

        # set user_id
        user_id = create_response.json()['user_id']
        # set username
        username = create_response.json()['username']
        # get user_info directly from database
        user_info = self.gk_dao.get_user_by_username(self.db, username)

        # read(GET) user data
        read_response = self.gk_service.gk_crud(
            session, method='GET', resource="user", id=user_id
        )

        # field count check form read
        # 4 fields should be returned
        self.assertEquals(len(read_response.json()), 11)

        # verify the creation of the user POST action
        self.assertEquals(
            read_response.json()['username'], user_info['username']
        )
        self.assertEquals(
            read_response.json()['user_id'], user_info['user_id']
        )
        self.assertEquals(read_response.json()['name'], user_info['name'])
        self.assertEquals(read_response.json()['phone'], user_info['phone'])
        self.assertEquals(read_response.json()['email'], user_info['email'])
        self.assertEquals(
            create_response.json()['last_logged_in'],
            user_info['last_logged_in']
        )

        # clean up - delete the user
        del_response = self.gk_service.gk_crud(
            session, method='DELETE', resource="user", id=user_id
        )
        # ensure a 204 is returned
        self.assertEquals(del_response.status_code, requests.codes.no_content)

        # read the new user data
        read_response = self.gk_service.gk_crud(
            session, method='GET', resource="user", id=user_id
        )
        self.assertTrue(
            self.gk_service.NO_DATA_ERROR in read_response.json()['error']
        )

    @attr(env=['test'], priority=1)
    def test_user_api_read_existant_user_id(self):
        """
        GATEKEEPER_USER_API_011 test_user_api_read_existant_user_id
        attempt to get a non existant user id
        """
        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        user_id = self.util.random_int()
        update_response = self.gk_service.gk_crud(
            session, method='GET', resource="user", id=user_id
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
    def test_user_api_delete(self):
        """
        GATEKEEPER_USER_API_012 test_user_api_delete
        explicit test case for delete functionality
        """

        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        # create a new user
        create_response = self.gk_service.gk_crud(
            session, method='POST', resource="user"
        )

        # ensure a 201 is returned
        self.assertEquals(create_response.status_code, requests.codes.created)

        # set user_id
        user_id = create_response.json()['user_id']
        # clean up - delete the user
        del_response = self.gk_service.gk_crud(
            session, method='DELETE', resource="user", id=user_id
        )
        # ensure a 204 is returned
        self.assertEquals(del_response.status_code, requests.codes.no_content)
        # ensure no response is returned
        self.assertEquals(len(del_response.content), 0)

        # read the new user data
        read_response = self.gk_service.gk_crud(
            session, method='GET', resource="user", id=user_id
        )
        self.assertTrue(
            self.gk_service.NO_DATA_ERROR in read_response.json()['error']
        )

    @attr(env=['test'], priority=1)
    def test_user_api_read_non_existant_user_id(self):
        """
        GATEKEEPER_USER_API_013 test_user_api_get_non_existant_user_id
        attempt to get a non existant user id
        """
        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        user_id = self.util.random_int()
        update_response = self.gk_service.gk_crud(
            session, method='DELETE', resource="user", id=user_id
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
    def test_user_api_user_login(self):
        """
        GATEKEEPER_USER_API_014 test_user_api_user_login
        login as newly created,updated and deleted user
        """

        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        # create username and apssword
        rand_str = self.util.random_str()
        credentials = {
            'username': self.util.random_str(4),
            'password': self.util.random_str(8)
        }
        user_data = self.gk_service.create_user_data(user_dict=credentials)

        # create a new user
        create_response = self.gk_service.gk_crud(
            session, method='POST', resource="user", data=user_data
        )
        # ensure a 201 is returned
        self.assertEquals(create_response.status_code, requests.codes.created)

        # login in as new user
        response = self.gk_service.create_session_urlencoded(
            allow_redirects=False, credentials=credentials
        )
        # 302 response
        self.assertEquals(response.status_code, requests.codes.found)

        # set user_id
        user_id = create_response.json()['user_id']

        # update username and password
        rand_str = self.util.random_str()
        credentials = {
            'username': rand_str,
            'password': rand_str
        }
        user_data = self.gk_service.create_user_data(user_dict=credentials)

        # update user
        update_response = self.gk_service.gk_crud(
            session, method='PUT', resource="user", id=user_id, data=user_data
        )

        # login in as updated user
        response = self.gk_service.create_session_urlencoded(
            allow_redirects=False, credentials=credentials
        )
        # 303 response
        self.assertEquals(response.status_code, requests.codes.found)

        # clean up - delete the user
        del_response = self.gk_service.gk_crud(
            session, method='DELETE', resource="user", id=user_id
        )
        # ensure a 204 is returned
        self.assertEquals(del_response.status_code, requests.codes.no_content)

        # login in as new user

        response = self.gk_service.create_session_urlencoded(
            allow_redirects=False, credentials=credentials
        )
        assert response.status_code, requests.codes

    @attr(env=['test'], priority=1)
    def test_user_data_validation_individual(self):
        """
        GATEKEEPER_USER_API_015 test_user_api_create_missing_params
        attempt to create a new user using the user api with missing params
        """
        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        # list of dicts with missing data
        bad_data = [
            {'username': self.util.random_str(3)},
            {'username': self.util.random_str(65)},
            {'username': '^!\$%&/()=?{[]}+~#-_.:,;<>|\\'},
            {'name': ''},
            {'name': self.util.random_str(101)},
            {'name': '^!\$%&/()=?{[]}+~#-_.:,;<>|\\'},
            {'phone': 123},
            {'password': self.util.random_str(7)},
            {'password': self.util.random_str(101)},
            {'password': '^!\$%&/()=?{[]}+~#-_.:,;<>|\\'},
            # empty string
            {'email': ''},
            # either side of the email will be 127
            {'email': self.util.random_email(len=127)},
            # domain less than 2 characters
            {'email': "1@1.1"},
            {'email': self.util.random_str()},
            {'fake': self.util.random_str()},
        ]

        for dict in bad_data:
            user_data = self.gk_service.create_user_data(dict)
            create_response = self.gk_service.gk_crud(
                session, method='POST', resource="user", data=user_data
            )
            self.assertEquals(
                create_response.status_code, requests.codes.bad_request
            )

            if('username' in dict.keys()):
                self.assertTrue(
                    self.gk_service.USERNAME_VALIDATION
                    in create_response.json()['error']
                )
            elif('name' in dict.keys()):
                self.assertTrue(
                    self.gk_service.NAME_VALIDATION
                    in create_response.json()['error']
                )
            elif('password' in dict.keys()):
                self.assertTrue(
                    self.gk_service.PASSWORD_VALIDATION
                    in create_response.json()['error']
                )
            elif('phone' in dict.keys()):
                self.assertTrue(
                    self.gk_service.PHONE_VALIDATION
                    in create_response.json()['error']
                )

            elif('email' in dict.keys()):
                self.assertTrue(
                    self.gk_service.EMAIL_VALIDATION
                    in create_response.json()['error']
                )
            elif('fake' in dict.keys()):
                self.assertTrue(
                    self.gk_service.PARAM_NOT_ALLOWED
                    in create_response.json()['error']
                )

    @attr(env=['test'], priority=1)
    def test_user_data_validation_multiple_fields(self):
        """
        GATEKEEPER_USER_API_016 test_user_api_create_missing_params
        attempt to create a new user using the user api with missing params
        """
        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        # list of dicts with missing data
        bad_data = [
            {'username': self.util.random_str(3), 'name': ''},
            {'password': self.util.random_str(101),
                'email': self.util.random_str()},
            {'username': self.util.random_str(65),
                'phone': 123,
                'password': self.util.random_str(7)},
            {'name': self.util.random_str(101),
                'email': self.util.random_email(len=127),
                'password': self.util.random_str(101)}
        ]

        for dict in bad_data:
            data = self.gk_service.create_user_data(dict)
            create_response = self.gk_service.gk_crud(
                session, method='POST', resource="user", data=data
            )

            self.assertEquals(
                create_response.status_code, requests.codes.bad_request
            )

            # BUG: https://www.pivotaltracker.com/story/show/63796662
            # if this defect is resolved this verification
            # will have to be altered if seperate error message per field

            if('username' in dict.keys()
                    and 'name' in dict.keys()):
                self.assertTrue(
                    self.gk_service.USERNAME_VALIDATION
                    in create_response.json()['error']
                )
                self.assertTrue(
                    self.gk_service.NAME_VALIDATION
                    in create_response.json()['error']
                )

            elif ('username' in dict.keys()
                    and 'phone' in dict.keys()
                    and 'password' in dict.keys()):

                self.assertTrue(
                    self.gk_service.USERNAME_VALIDATION
                    in create_response.json()['error']
                )
                self.assertTrue(
                    self.gk_service.PHONE_VALIDATION
                    in create_response.json()['error']
                )
                self.assertTrue(
                    self.gk_service.PASSWORD_VALIDATION
                    in create_response.json()['error'])

            elif ('name' in dict.keys()
                    and 'email' in dict.keys()
                    and 'password' in dict.keys()):

                self.assertTrue(
                    self.gk_service.NAME_VALIDATION
                    in create_response.json()['error']
                )
                self.assertTrue(
                    self.gk_service.EMAIL_VALIDATION
                    in create_response.json()['error']
                )
                self.assertTrue(
                    self.gk_service.PASSWORD_VALIDATION
                    in create_response.json()['error'])

            elif('password' in dict.keys()
                    and 'email' in dict.keys()):
                self.assertTrue(
                    self.gk_service.PASSWORD_VALIDATION
                    in create_response.json()['error']
                )
                self.assertTrue(
                    self.gk_service.EMAIL_VALIDATION
                    in create_response.json()['error']
                )

    @attr(env=['test'], priority=1)
    def test_user_api_delete_admin_delete_itself(self):
        """
        GATEKEEPER_USER_API_017 test_user_api_delete_admin_delete_itself
        Ensure users cannot delete themseves
        """

        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        # Attempt for the admin user to delete themselves
        # self.default_test_user is the admin user id
        del_response = self.gk_service.gk_crud(
            session,
            method='DELETE',
            resource="user",
            id=self.default_test_user
        )

        # ensure a 403 is returned
        self.assertEquals(del_response.status_code, requests.codes.forbidden)
        # correct error message
        self.assertTrue(
            self.gk_service.DELETE_THEMSELVES
            in del_response.json()['error']
        )
