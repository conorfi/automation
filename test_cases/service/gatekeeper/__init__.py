from testconfig import config
from framework.service.gatekeeper.gatekeeper_service import SERVICE_NAME, \
    GateKeeperService
from framework.db.base_dao import BaseDAO
from framework.db.gate_keeper_dao import GateKeeperDAO
from framework.utility.utility import Utility
import testy as unittest
import requests

class ApiTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Things that need to be done once
        cls.db = BaseDAO(config[SERVICE_NAME]['db']['connection'])

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

    def assertAppData(self, actual_data, expected_data):
        self.assertDictContains(actual_data, 'application_id')
        self.assertEquals(
            actual_data['application_id'],
            expected_data['application_id']
        )
        self.assertDictContains(actual_data, 'name')
        self.assertEquals(
            actual_data['name'],
            expected_data['name']
        )
        self.assertDictContains(actual_data, 'default_url')
        self.assertEquals(
            actual_data['default_url'],
            expected_data['default_url']
        )

    def assertGroupData(self, actual_data, expected_data):
        self.assertDictContains(actual_data, 'name')
        self.assertEquals(expected_data['name'], actual_data['name'])
        self.assertDictContains(actual_data, 'group_id')
        self.assertEquals(expected_data['group_id'], actual_data['group_id'])

    def assertOrgData(self, expected_data, actual_data):
        self.assertDictContains(actual_data, 'name')
        self.assertEquals(expected_data['name'], actual_data['name'])
        self.assertDictContains(actual_data, 'organization_id')
        self.assertEquals(
            expected_data['organization_id'],
            actual_data['organization_id']
        )

    def assertPermData(self, actual_data, expected_data):
        # verify the creation of the permission POST action
        self.assertDictContains(actual_data, 'name')
        self.assertEquals(
            expected_data['name'], actual_data['name']
        )
        self.assertDictContains(actual_data, 'permission_id')
        self.assertEquals(
            expected_data['permission_id'],
            actual_data['permission_id']
        )
        self.assertDictContains(actual_data, 'name')
        self.assertEquals(
            expected_data['application_id'],
            actual_data['application_id']
        )

    def assertUserData(self, actual_data, expected_data):
        #7 of 11 fields tested here
        #other 4 fields org,group,permission will be tested seperately
        self.assertDictContains(actual_data, 'username')
        self.assertEquals(expected_data['username'], actual_data['username'])
        self.assertDictContains(actual_data, 'user_id')
        self.assertEquals(expected_data['user_id'], actual_data['user_id'])
        self.assertDictContains(actual_data, 'name')
        self.assertEquals(expected_data['name'], actual_data['name'])
        self.assertDictContains(actual_data, 'phone')
        self.assertEquals(expected_data['phone'], actual_data['phone'])
        self.assertDictContains(actual_data, 'email')
        self.assertEquals(expected_data['email'], actual_data['email'])
        self.assertDictContains(actual_data, 'last_logged_in')
        self.assertEquals(
            expected_data['last_logged_in'], actual_data['last_logged_in']
        )
        self.assertDictContains(actual_data, 'failed_login_count')
        self.assertEquals(
            expected_data['failed_login_count'],
            actual_data['failed_login_count']
        )

    def assertGroupAppData(self, actual_data, expected_data):
        self.assertDictContains(actual_data, 'application_id')
        self.assertEquals(
            expected_data['application_id'],
            actual_data['application_id']
        )
        self.assertDictContains(actual_data, 'group_id')
        self.assertEquals(
            expected_data['group_id'],
            actual_data['group_id']
        )

    def assertGroupPermData(self, actual_data, expected_data):
        self.assertDictContains(actual_data, 'group_id')
        self.assertEquals(
            expected_data['group_id'],
            actual_data['group_id']
        )
        self.assertDictContains(actual_data, 'permission_id')
        self.assertEquals(
            expected_data['permission_id'],
            actual_data['permission_id']
        )

    def assertUserAppData(self, actual_data, expected_data):
        self.assertDictContains(actual_data, 'application_id')
        self.assertEquals(
            expected_data['application_id'],
            actual_data['application_id']
        )
        self.assertDictContains(actual_data, 'user_id')
        self.assertEquals(
            expected_data['user_id'],
            actual_data['user_id']
        )

    def assertUserGrpData(self, actual_data, expected_data):
        self.assertDictContains(actual_data, 'group_id')
        self.assertEquals(
            expected_data['group_id'],
            actual_data['group_id']
        )
        self.assertDictContains(actual_data, 'user_id')
        self.assertEquals(
            expected_data['user_id'],
            actual_data['user_id']
        )

    def assertUserOrgData(self, actual_data, expected_data):
        self.assertDictContains(actual_data, 'organization_id')
        self.assertEquals(
            expected_data['organization_id'],
            actual_data['organization_id']
        )
        self.assertDictContains(actual_data, 'user_id')
        self.assertEquals(
            expected_data['user_id'],
            actual_data['user_id']
        )


    def assertUserPermData(self, actual_data, expected_data):
        self.assertDictContains(actual_data, 'permission_id')
        self.assertEquals(
            expected_data['permission_id'],
            actual_data['permission_id']
        )
        self.assertDictContains(actual_data, 'user_id')
        self.assertEquals(
            expected_data['user_id'],
            actual_data['user_id']
        )

    def assertUserAppDisplay(
            self,
            actual_data,
            expected_user_data,
            expected_grp_data=None,
            expected_perm_data=None,
            expected_org_data=None):


        # 7 fields should be returned
        self.assertEquals(len(actual_data), 7)

        self.assertDictContains(actual_data, 'username')
        self.assertEquals(
            expected_user_data['username'],
            actual_data['username']
        )
        self.assertDictContains(actual_data, 'user_id')
        self.assertEquals(
            str(expected_user_data['user_id']),
            actual_data['user_id']
        )
        self.assertDictContains(actual_data, 'fullname')
        self.assertEquals(
            expected_user_data['name'],
            actual_data['fullname']
        )
        self.assertDictContains(actual_data, 'email')
        self.assertEquals(
            expected_user_data['email'],
            actual_data['email']
        )

        self.assertDictContains(actual_data, 'permissions')
        self.assertDictContains(actual_data, 'organizations')
        self.assertDictContains(actual_data, 'groups')

        if expected_perm_data is None:
            self.assertEquals(actual_data['permissions'], [])
        else:
            for item in expected_perm_data:
                self.assertTrue(item in actual_data['permissions'])
        if expected_org_data is None:
            self.assertEquals(actual_data['organizations'], [])
        else:
            for item in expected_org_data:
                self.assertTrue(item in actual_data['organizations'])
        if expected_grp_data is None:
            self.assertEquals(actual_data['groups'], [])
        else:
            for item in expected_grp_data:
                self.assertTrue(item in actual_data['groups'])

    def data_clean_up(self, application_protected=False, **kwargs):
        """
        Cleans data from the service and asserts the clean up was successful.
        :param application_protected: if application shouldn't be deleted even
         if in the kwargs
        :param kwargs: data to be deleted from the service
        """

        if application_protected:
            del kwargs['application_id']

        # cleans data from the service
        del_responses = self.gk_service.data_clean_up(**kwargs)

        # ensure a 204 is returned from every response
        for del_response in del_responses:
            self.assertEquals(
                del_response.status_code,
                requests.codes.no_content
            )