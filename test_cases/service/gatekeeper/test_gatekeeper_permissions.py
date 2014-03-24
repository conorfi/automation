"""
@summary: Contains a set of test cases for the permissions API of the
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


class TestGatePermissionsAPI(ApiTestCase):

    @attr(env=['test'], priority=1)
    def test_permissions_api(self):
        """
        GATEKEEPER_PERMISSIONS_API_001 test_permissions_api
        Ensure all the user information stored is returned
        """
        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        # return list of all permissions
        response = self.gk_service.gk_listing(
            session,
            resource="permission"
        )

        # 200
        self.assertEquals(response.status_code, requests.codes.ok)

        # ensure that the count of the permissions returned
        # is matched by the count in the database
        api_count = response.json().__len__()
        db_count = self.gk_dao. get_permission_count(self.db)['count']
        self.assertEquals(api_count, db_count, "count mismatch")

    @attr(env=['test'], priority=1)
    def test_permissions_api_name_filter(self):
        """
        GATEKEEPER_PERMISSIONS_API_002 test_permissions_api_name_filter
        Ensure the name filer works correctly
        """

        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        # create a new permission
        create_response = self.gk_service.gk_crud(
            session=session,
            method='POST',
            resource="permission"
        )

        # ensure a 201 is returned
        self.assertEquals(create_response.status_code, requests.codes.created)

        # get app data from the db
        app_db_data = self.gk_dao.get_app_by_app_name(
            self.db, create_response.json()['application']['name']
        )

        #set app id
        app_id = app_db_data['application_id']

        # set permission name
        permission_name = create_response.json()['name']

        # get permission data directly from database
        perm_db_data = self.gk_dao.get_permission_by_name(
            self.db, permission_name, app_id
        )

        # return just the newly created user fron the list of users
        read_response = self.gk_service.gk_listing(
            session,
            resource="permission",
            name=permission_name
        )
        # ensure a 200 is returned
        self.assertEquals(read_response.status_code, requests.codes.ok)

        # field count check form read
        # 4 fields should be returned
        self.assertEquals(len(read_response.json()[0]), 4)

        # 200
        self.assertEquals(read_response.status_code, requests.codes.ok)

        # ensure only one result is returned
        api_count = read_response.json().__len__()
        self.assertEquals(api_count, 1, "count mismatch")
        # verify the creation of the permission POST action
        self.assertPermData(read_response.json()[0], perm_db_data)
        self.assertAppData(read_response.json()[0]['application'], app_db_data)
        # clean up - delete the application(and related permission)
        del_response = self.gk_service.gk_crud(
            session, method='DELETE', resource="application", id=app_id
        )
        # ensure a 204 is returned
        self.assertEquals(del_response.status_code, requests.codes.no_content)

    @attr(env=['test'], priority=1)
    def test_perms_api_name_filter_invalid_name(self):
        """
        GATEKEEPER_PERMISSIONS_API_003 test_perms_api_name_filter_invalid_name
        Ensure the name filer works correctly
        """
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        permission_name = "sofake"
        # return just the newly created user from the list of permissions
        response = self.gk_service.gk_listing(
            session,
            resource="permission",
            name=permission_name
        )

        # 200
        self.assertEquals(response.status_code, requests.codes.ok)
        # length 2 i.e empty array
        self.assertEquals(len(response.content), 2)
