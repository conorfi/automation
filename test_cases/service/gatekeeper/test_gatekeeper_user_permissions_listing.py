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


class TestGateKeeperUsersGroupsListingAPI(ApiTestCase):

    @attr(env=['test'], priority=1)
    def test_user_perms_api(self):
        """
        GATEKEEPER_USER_PERMS_API_001 test_user_perms_api
        Ensure all the user_perm information stored is returned
        """
        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        # return list of all users
        response = self.gk_service.gk_association_listing(
            session, resource="user_perm"
        )

        # 200
        self.assertEquals(response.status_code, requests.codes.ok)

        # ensure that the count of the users returned
        # is matched by the count in the database
        api_count = response.json().__len__()
        db_count = self.gk_dao.get_user_perm_count(self.db)['count']
        self.assertEquals(api_count, db_count, "count mismatch")

    @attr(env=['test'], priority=1)
    def test_user_perms_filter(self):
        """
        GATEKEEPER_USER_PERMS_API_002 test_user_perms_filter
        Ensure the name filer works correctly
        """

        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        user_perm_data = self.gk_service.create_user_perm_data(session)

        # create an association
        create_response = self.gk_service.gk_crud(
            session, method='POST', resource="user_perm", data=user_perm_data
        )
        # ensure a 201 is returned
        self.assertEquals(create_response.status_code, requests.codes.created)

        # set user_id
        user_id = create_response.json()['user_id']
        # set permission_id
        permission_id = create_response.json()['permission_id']

        dict_matrix = [
            {'permission_id': permission_id},
            {'user_id': user_id},
            {'permission_id': permission_id, 'user_id': user_id}
        ]

        for params in dict_matrix:
            # return just the newly created user fron the list of users
            response = self.gk_service.gk_association_listing(
                session,
                resource="user_perm",
                params=params
            )
            # 200
            self.assertEquals(response.status_code, requests.codes.ok)

            # ensure only one result is returned
            api_count = response.json().__len__()
            self.assertEquals(api_count, 1, "count mismatch")

            # field count
            # 2 fields should be returned
            self.assertEquals(len(response.json()[0]), 2)

            # verify the contents of the users API
            #verify API
            self.assertUserPermData(response.json()[0], user_perm_data)

        # clean up - delete the user
        del_response = self.gk_service.gk_crud(
            session,
            method='DELETE',
            resource="user_perm",
            id=user_id,
            id2=permission_id
        )
        # ensure a 204 is returned
        self.assertEquals(del_response.status_code, requests.codes.no_content)

        # clean up - delete the user
        del_response = self.gk_service.gk_crud(
            session,
            method='DELETE',
            resource="user",
            id=user_perm_data['user_id']
        )
        # ensure correct status code is returned
        self.assertEquals(del_response.status_code, requests.codes.no_content)

        # clean up - delete the app
        #get app_id associated with perm id
        app_id = self.gk_dao.get_app_id_by_perm_id(
            self.db,
            user_perm_data['permission_id'],
        )['application_id']

        # clean up - delete the application
        del_response = self.gk_service.gk_crud(
            session,
            method='DELETE',
            resource="application",
            id=app_id
        )

    @attr(env=['test'], priority=1)
    def test_users_apps_api_filter_invalid_no_data(self):
        """
        GATEKEEPER_USER_PERMS_API_003 test_users_apps_api_filter_no_data
        Ensure the name filer works correctly when no
        or invalid data is entered
        """

        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        user_perm_data = self.gk_service.create_user_perm_data(session)

        # create an association
        create_response = self.gk_service.gk_crud(
            session, method='POST', resource="user_perm", data=user_perm_data
        )
        # ensure a 201 is returned
        self.assertEquals(create_response.status_code, requests.codes.created)

        # set user_id
        user_id = create_response.json()['user_id']
        # set permission_id
        permission_id = create_response.json()['permission_id']

        dict_matrix = [
            {'permission_id': ''},
            {'user_id': ''},
            {'permission_id': '', 'user_id': ''}
        ]

        for params in dict_matrix:
            # return just the newly created user fron the list of users
            response = self.gk_service.gk_association_listing(
                session,
                resource="user_perm",
                params=params
            )
            # 200
            self.assertEquals(response.status_code, requests.codes.ok)

            # all results returned - so ensure that the count returned
            # is matched by the count in the database
            api_count = response.json().__len__()
            db_count = self.gk_dao.get_user_perm_count(self.db)['count']
            self.assertEquals(api_count, db_count, "count mismatch")

        # clean up - delete the user
        del_response = self.gk_service.gk_crud(
            session,
            method='DELETE',
            resource="user_perm",
            id=user_id,
            id2=permission_id
        )
        # ensure a 204 is returned
        self.assertEquals(del_response.status_code, requests.codes.no_content)

    @attr(env=['test'], priority=1)
    def test_users_apps_api_filter_invalid_invalid_data(self):
        """
        GATEKEEPER_USER_PERMS_API_004 test_users_apps_api_filter_invalid_data
        Ensure the name filer works correctly when no
        or invalid data is entered
        """

        # login and create session
        session, cookie_id, response = self.gk_service.login_create_session(
            allow_redirects=False
        )

        user_perm_data = self.gk_service.create_user_perm_data(session)

        # create an association
        create_response = self.gk_service.gk_crud(
            session, method='POST', resource="user_perm", data=user_perm_data
        )
        # ensure a 201 is returned
        self.assertEquals(create_response.status_code, requests.codes.created)

        # set user_id
        user_id = create_response.json()['user_id']
        # set permission_id
        permission_id = create_response.json()['permission_id']

        rand_int = self.util.random_int()

        dict_matrix = [
            {'permission_id': rand_int},
            {'user_id': rand_int},
            {'permission_id': rand_int, 'user_id': rand_int}
        ]

        for params in dict_matrix:
            # return just the newly created user fron the list of users
            response = self.gk_service.gk_association_listing(
                session,
                resource="user_perm",
                params=params
            )
            # 200
            self.assertEquals(response.status_code, requests.codes.ok)
            # length 2 i.e empty array
            self.assertEquals(len(response.content), 2)

        # clean up - delete the user
        del_response = self.gk_service.gk_crud(
            session,
            method='DELETE',
            resource="user_perm",
            id=user_id,
            id2=permission_id
        )
        # ensure a 204 is returned
        self.assertEquals(del_response.status_code, requests.codes.no_content)

        # clean up - delete the user
        del_response = self.gk_service.gk_crud(
            session,
            method='DELETE',
            resource="user",
            id=user_perm_data['user_id']
        )
        # ensure correct status code is returned
        self.assertEquals(del_response.status_code, requests.codes.no_content)

        # clean up - delete the app
        #get app_id associated with perm id
        app_id = self.gk_dao.get_app_id_by_perm_id(
            self.db,
            user_perm_data['permission_id'],
        )['application_id']

        # clean up - delete the application
        del_response = self.gk_service.gk_crud(
            session,
            method='DELETE',
            resource="application",
            id=app_id
        )
