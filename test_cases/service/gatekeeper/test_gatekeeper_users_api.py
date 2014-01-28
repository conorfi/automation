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
from nose.plugins.attrib import attr
from . import ApiTestCase

class TestGateUsersAPI(ApiTestCase):

    @attr(env=['test'], priority=1)
    def test_users_api(self):
        """
        GATEKEEPER_USERS_API_001 test_users_api
        Ensure all the user information stored is returned
        """
        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        # return list of all users
        response = self.gk_service.gk_listing(
            session, resource="user"
        )

        # 200
        self.assertEquals(response.status_code, requests.codes.ok)

        # ensure that the count of the users returned
        # is matched by the count in the database
        api_count = response.json().__len__()
        db_count = self.gk_dao.get_user_count(self.db)['count']
        self.assertEquals(api_count, db_count, "count mismatch")

    @attr(env=['test'], priority=1)
    def test_users_api_name_filter(self):
        """
        GATEKEEPER_USERS_API_002 test_users_api_name_filter
        Ensure the name filer works correctly
        """
        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )
        # create a new user
        response = self.gk_service.gk_crud(
            session, method='POST', resource="user"
        )

        # ensure a 201 is returned
        self.assertEquals(response.status_code, requests.codes.created)
        # set username
        username = response.json()['username']
        name = response.json()['name']
        # set user_id
        user_id = response.json()['user_id']
        # get user data directly from database
        user_info = self.gk_dao.get_user_by_username(self.db, username)

        # return just the newly created user fron the list of users
        response = self.gk_service.gk_listing(
            session,
            resource="user",
            name=name
        )
        # 200
        self.assertEquals(response.status_code, requests.codes.ok)

        # field count check form read
        # 4 fields should be returned
        self.assertEquals(len(response.json()[0]), 7)

        # verify the contents of the users API
        self.assertEquals(
            response.json()[0]['username'], user_info['username']
        )
        self.assertEquals(response.json()[0]['user_id'], user_info['user_id'])
        self.assertEquals(response.json()[0]['name'], user_info['name'])
        self.assertEquals(response.json()[0]['phone'], user_info['phone'])
        self.assertEquals(response.json()[0]['email'], user_info['email'])
        self.assertEquals(
            response.json()[0]['last_logged_in'], user_info['last_logged_in']
        )

        # clean up - delete the user
        del_response = self.gk_service.gk_crud(
            session, method='DELETE', resource="user", id=user_id
        )
        # ensure a 204 is returned
        self.assertEquals(del_response.status_code, requests.codes.no_content)

    @attr(env=['test'], priority=1)
    def test_users_api_name_filter_invalid_name(self):
        """
        GATEKEEPER_USERS_API_003 test_users_api_name_filter_invalid_name
        Ensure the name filer works correctly
        """
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        username = "sofake"
        # return just the newly created user from the list of users
        response = self.gk_service.gk_listing(
            session,
            resource="user",
            name=username
        )

        # 200
        self.assertEquals(response.status_code, requests.codes.ok)
        # length 2 i.e empty array
        self.assertEquals(len(response.content), 2)
