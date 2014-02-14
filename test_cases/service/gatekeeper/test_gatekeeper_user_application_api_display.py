"""
@summary: Contains a set of test cases for the user application API of the
gatekeeper(single sign on) project
Note: only 1 factor authentication test cases
These test have a number of dependencies
1. the database update script updates the gatekeepr schema - the script can be
found at the root of the gatekeeper app
2. the build script starts the gatekeeper app with ssl enbaled by default
3. the build script starts the dummy app with ssl enabled
and application_name is adfuser
4. The dummy app is pre-configure with two permissions
'ADFUSER_USER' and 'ADFUSER_ADMIN'
@since: Created on 3rd January 2014
@author: Conor Fitzgerald
"""

import requests
from nose.plugins.attrib import attr
from . import ApiTestCase
from testconfig import config
from framework.service.gatekeeper.gatekeeper_service import SERVICE_NAME, \
    GateKeeperService


class TestGateKeeperUserApplicationAPI(ApiTestCase):
    @attr(env=['test'], priority=1)
    def test_user_app_and_auth_app_perms(self):
        """
        GATEKEEPER_USER_SESSION_API_001 test_user_app_and_auth_app_perms
        test user api and permissions for user with only app access
        Ensures user info can be return from the user api when
        a valid session,user id and application is provided for a user
        """
        #create user and app assocation
        user_app_dict = self.gk_service.create_user_app_api_display_data()

        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False,
            credentials=user_app_dict['credentials_payload']
        )

        # get user data directly from database
        user_info = self.gk_dao.get_user_by_username(
            self.db,
            user_app_dict['credentials_payload']['username']
        )

        # Verify the response from the user app API
        response = self.gk_service.user_app(
            session,
            user_app_dict['user_id'],
            user_app_dict['application_name']
        )

        #200
        self.assertEquals(response.status_code, requests.codes.ok)
        #verify the API response
        self.assertUserAppDisplay(response.json(), user_info)

        self.gk_service.data_clean_up(
            user_app_dict['user_id'],
            user_app_dict['application_id'],
            user_app_dict['group_id']
        )

    @attr(env=['test'], priority=1)
    def test_user_app_and_auth_user_perms(self):
        """
        GATEKEEPER_USER_SESSION_API_002 test_user_app_and_auth_user_perms
        test user api and permissions for user
        """
        #create user, app and perm association,
        user_app_dict = self.gk_service.create_user_app_api_display_data(
            user_permission=True
        )
        # expected data
        user_info = self.gk_dao.get_user_by_username(
            self.db,
            user_app_dict['credentials_payload']['username']
        )
        perm_info = [user_app_dict['permission_name']]

        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False,
            credentials=user_app_dict['credentials_payload']
        )

        # Verify the response from the user app API
        response = self.gk_service.user_app(
            session,
            user_app_dict['user_id'],
            user_app_dict['application_name']
        )
        # Verify the user API
        self.assertUserAppDisplay(
            response.json(), user_info, expected_perm_data=perm_info
        )
        self.gk_service.data_clean_up(
            user_app_dict['user_id'],
            user_app_dict['application_id'],
            user_app_dict['group_id']
        )

    @attr(env=['test'], priority=1)
    def test_user_app_and_auth_group_perms(self):
        """
        GATEKEEPER_USER_SESSION_API_003 test_user_app_and_auth_group_perms
        test user api and permissions for user with group permissions
        """

        #create user, app and perm association,
        user_app_dict = self.gk_service.create_user_app_api_display_data(
            user_group=True, group_permission=True
        )

        # expected data
        user_info = self.gk_dao.get_user_by_username(
            self.db,
            user_app_dict['credentials_payload']['username']
        )
        perm_info = [user_app_dict['permission_name']]
        grp_info = [user_app_dict['group_name']]

        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False,
            credentials=user_app_dict['credentials_payload']
        )

        # Verify the user API
        response = self.gk_service.user_app(
            session,
            user_app_dict['user_id'],
            user_app_dict['application_name']
        )

        self.assertEquals(response.status_code, requests.codes.ok)

        self.assertUserAppDisplay(
            response.json(), user_info, grp_info, perm_info,
        )

        self.gk_service.data_clean_up(
            user_app_dict['user_id'],
            user_app_dict['application_id'],
            user_app_dict['group_id']
        )

    @attr(env=['test'], priority=1)
    def test_user_app_and_no_gp_app_association(self):
        """
        GATEKEEPER_USER_SESSION_API_004 test_user_app_and_no_gp_app_association
        Group and app association is removed, ensuring the user app dose NOT
        return the group
        """

        # admin - login and create session
        a_session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        #create user, app and perm association,
        user_app_dict = self.gk_service.create_user_app_api_display_data(
            user_group=True
        )

        #remove group association with app
        del_response = self.gk_service.gk_crud(
            a_session,
            method='DELETE',
            resource="grp_app",
            id2=user_app_dict['application_id'],
            id=user_app_dict['group_id']
        )

        # ensure a 204 is returned
        self.assertEquals(del_response.status_code, requests.codes.no_content)

        # expected data
        user_info = self.gk_dao.get_user_by_username(
            self.db,
            user_app_dict['credentials_payload']['username']
        )

        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False,
            credentials=user_app_dict['credentials_payload']
        )

        # Verify the user API
        response = self.gk_service.user_app(
            session,
            user_app_dict['user_id'],
            user_app_dict['application_name']
        )

        self.assertEquals(response.status_code, requests.codes.ok)

        self.assertUserAppDisplay(
            response.json(),
            expected_user_data=user_info
        )

        self.gk_service.data_clean_up(
            user_app_dict['user_id'],
            user_app_dict['application_id'],
            user_app_dict['group_id']
        )

    @attr(env=['test'], priority=1)
    def test_user_app_and_org(self):
        """
        GATEKEEPER_USER_SESSION_API_005 test_user_app_and_orgs
        test user api and org
        """
        #create user, app and perm association,
        user_app_dict = self.gk_service.create_user_app_api_display_data(
            user_organization=True
        )

        # expected data
        user_info = self.gk_dao.get_user_by_username(
            self.db,
            user_app_dict['credentials_payload']['username']
        )
        org_info = [user_app_dict['organization_name']]

        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False,
            credentials=user_app_dict['credentials_payload']
        )

        # Verify the user API
        response = self.gk_service.user_app(
            session,
            user_app_dict['user_id'],
            user_app_dict['application_name']
        )

        self.assertEquals(response.status_code, requests.codes.ok)

        # Verify the user API
        self.assertUserAppDisplay(
            response.json(),
            user_info,
            expected_org_data=org_info
        )

        self.gk_service.data_clean_up(
            user_app_dict['user_id'],
            user_app_dict['application_id'],
            user_app_dict['group_id'],
            user_app_dict['organization_id']
        )

    @attr(env=['test'], priority=1)
    def test_user_app_invalid_cookie_session(self):
        """
        GATEKEEPER_USER_SESSION_API_005 test_user_app_invalid_cookie_session
        Ensures user info CANNOT be return from the user api when a invalid
        session is provided
        """

        #create user, app and perm association,
        user_app_dict = self.gk_service.create_user_app_api_display_data(
            user_organization=True
        )

        cookie_value = "fakecookie"

        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False,
            cookie_value=cookie_value,
            credentials=user_app_dict['credentials_payload']
        )

        # Verify the user API
        response = self.gk_service.user_app(
            session,
            user_app_dict['user_id'],
            user_app_dict['application_name']
        )

        # ensure that the request is forbidden(403)
        # without a valid session cookie
        self.assertEquals(response.status_code, requests.codes.forbidden)
        self.assertTrue(self.gk_service.USER_ERROR in response.json()['error'])

        self.gk_service.data_clean_up(
            user_app_dict['user_id'],
            user_app_dict['application_id'],
            user_app_dict['group_id']
        )

    @attr(env=['test'], priority=1)
    def test_user_app_invalid_application(self):
        """
        GATEKEEPER_USER_SESSION_API_006 test_user_app_invalid_application
        Ensures user info CANNOT be return from the user api when a invalid
        application is provided
        """

        #create user, app and perm association,
        user_app_dict = self.gk_service.create_user_app_api_display_data(
            user_organization=True
        )

        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False,
            credentials=user_app_dict['credentials_payload']
        )

        fake_application = "fake"
        # Verify the user API
        response = self.gk_service.user_app(
            session,
            user_app_dict['user_id'],
            fake_application
        )
        # ensure it returns a 404 not found
        self.assertEquals(response.status_code, requests.codes.not_found)

        self.assertTrue("No user with id" in response.json()['error'])
        self.assertTrue("found for application" in response.json()['error'])

        self.gk_service.data_clean_up(
            user_app_dict['user_id'],
            user_app_dict['application_id'],
            user_app_dict['group_id']
        )

    @attr(env=['test'], priority=1)
    def test_user_app_invalid_user_id(self):
        """
        GATEKEEPER_USER_SESSION_API_007 test_user_app_invalid_user_id
        Ensures user info CANNOT be return from the user api when a invalid
        user id is provided
        """

        # create first random user
        user1_data = self.gk_service.create_user_app_api_display_data()
        # create second random user, storing user ID
        user2_data = self.gk_service.create_user_app_api_display_data()

        # login with first random user
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False,
            credentials=user1_data['credentials_payload']
        )

        # attempt access to user application for second random user
        response = self.gk_service.user_app(
            session,
            user2_data['user_id'],
            user1_data['application_name']
        )

        # ensure that the request is forbidden(403)
        # without a valid session cookie
        self.assertEquals(response.status_code, requests.codes.forbidden)
        self.assertTrue(self.gk_service.USER_ERROR in response.json()['error'])

        self.gk_service.data_clean_up(
            user1_data['user_id'],
            user1_data['application_id'],
            user1_data['group_id']
        )

        self.gk_service.data_clean_up(
            user2_data['user_id'],
            user2_data['application_id'],
            user2_data['group_id']
        )

    @attr(env=['test'], priority=1)
    def test_user_app_with_no_args(self):
        """
        GATEKEEPER_USER_SESSION_API_008 test_user_app_with_no_args
        Ensures user info CANNOT be return from the user api when no
        user id or application name is provided
        """
        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        response = self.gk_service.user_app(session, '', '')

        self.assertEquals(response.status_code, requests.codes.bad_request)
        json_data = response.json()
        self.assertTrue('error' in json_data)
        self.assertTrue(
            self.gk_service.MISSING_PARAMETERS in json_data['error']
        )

    @attr(env=['test'], priority=1)
    def test_user_app_with_no_application_name(self):
        """
        GATEKEEPER_USER_SESSION_API_009 test_user_app_with_no_application_name
        Ensures user info CANNOT be return from the user api when no
        application name is provided
        """
        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        user_id = self.gk_dao.get_user_by_username(
            self.db,
            self.gk_service.ADMIN_USER
        )['user_id']

        response = self.gk_service.user_app(session, user_id, '')

        self.assertEquals(response.status_code, requests.codes.bad_request)
        json_data = response.json()
        self.assertTrue('error' in json_data)
        self.assertEqual(json_data['error'],
                         self.gk_service.MISSING_APP_NAME)

    @attr(env=['test'], priority=1)
    def test_user_app_with_no_user_id(self):
        """
        GATEKEEPER_USER_SESSION_API_010 test_user_app_with_no_user_id
        Ensures user info CANNOT be return from the user api when no
        application id is provided
        """

        # create user app dict
        user_app_dict = self.gk_service.create_user_app_api_display_data()

        # login
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False,
            credentials=user_app_dict['credentials_payload']
        )

        response = self.gk_service.user_app(
            session,
            '',
            user_app_dict['application_name']
        )
        self.assertEquals(response.status_code, requests.codes.bad_request)
        json_data = response.json()
        self.assertTrue('error' in json_data)
        self.assertEqual(json_data['error'],
                         self.gk_service.MISSING_APP_ID)

        self.gk_service.data_clean_up(
            user_app_dict['user_id'],
            user_app_dict['application_id'],
            user_app_dict['group_id']
        )
