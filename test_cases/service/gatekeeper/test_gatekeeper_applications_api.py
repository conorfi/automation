"""
@summary: Contains a set of test cases for the applications API of the
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

from nose.plugins.attrib import attr
import requests

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

        # return list of all applications
        response = self.gk_service.gk_listing(
            session,
            resource="application"
        )

        # 200
        self.assertEquals(response.status_code, requests.codes.ok)

        # ensure that the count of the applications returned
        # is matched by the count in the database
        api_count = response.json().__len__()
        db_count = self.gk_dao.get_app_count(self.db)['count']
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

        # create a new application
        create_response = self.gk_service.gk_crud(
            session, method='POST', resource='application'
        )
        # ensure correct status code is returned
        self.assertEquals(create_response.status_code, requests.codes.created)

        # set ap_id and app name
        app_id = create_response.json()['application_id']
        appname = create_response.json()['name']
        # get app data from db
        app_data = self.gk_dao.get_app_by_app_name(
            self.db,
            appname
        )

        # return just the newly created app from the list of apps
        response = self.gk_service.gk_listing(
            session,
            resource="application",
            name=appname
        )

        # 200
        self.assertEquals(response.status_code, requests.codes.ok)

        # ensure only one result is returned
        api_count = response.json().__len__()
        self.assertEquals(api_count, 1, "count mismatch")

        # field count check form read
        # 3 fields should be returned
        self.assertEquals(len(response.json()[0]), 3)

        # verify the users API against the db data
        self.assertAppData(response.json()[0],app_data)

        # clean up - delete the application
        del_response = self.gk_service.gk_crud(
            session, method='DELETE', resource='application', id=app_id
        )
        # ensure correct status code is returned
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

        appname = "sofake"
        # return just the newly created user from the list of users
        response = self.gk_service.gk_listing(
            session,
            resource="application",
            name=appname
        )

        # 200
        self.assertEquals(response.status_code, requests.codes.ok)
        # length 2 i.e empty array
        self.assertEquals(len(response.content), 2)
