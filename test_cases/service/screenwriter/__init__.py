from testconfig import config
import testy as unittest
import requests
from framework.service.screen_writer.screen_writer_service import PackService
from framework.service.screen_writer.screen_writer_service import Messages
from framework.common_env import SERVICE_NAME_SCREEN_WRITER as SERVICE_NAME
from framework.db.base_dao import BaseDAO
from framework.db.screen_writer import Packs
from framework.utility.utility import Utility
import json


class ApiTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Things that need to be done once
        cls.db = BaseDAO(config[SERVICE_NAME]['db']['connection'])
        # sqlite disk IO errors, altered journal_mode
        cls.db.execute("PRAGMA journal_mode = MEMORY")
        cls.db.execute("PRAGMA cache_size = 500000")

    @classmethod
    def tearDownClass(cls):
        # Things that need to be done once.
        cls.db.close()

    def setUp(self):
        # Things to run before each test.
        self.packs_service = PackService()
        self.packs_db = Packs()
        self.msgs = Messages()
        self.util = Utility()
        #screen
        self.set_screen_data()
        #title
        self.set_title_data()
        #placeholder
        self.set_placeholder_data()
        #optional data dict
        self.create_optional_data()

    def tearDown(self):
        self.packs_db.del_screen_by_uuid(self.db, self.screen_uuid)
        self.packs_db.del_title_by_uuid(self.db, self.title_uuid)
        self.packs_db.del_title_by_uuid(self.db, self.placeholder_uuid)

    def set_screen_data(self):
        self.screen_uuid = self.util.random_screen_uuid()
        self.screen_identifier = self.util.random_int(6)
        self.screen_title = self.util.random_str(8)
        self.packs_db.set_screen(
            self.db,
            self.screen_uuid,
            self.screen_identifier,
            self.screen_title
        )

    def set_title_data(self):
        #title seems to be the same format as screen UUID
        self.title_uuid = self.util.random_screen_uuid()
        self.title_name = self.util.random_str(8)
        self.packs_db.set_title(
            self.db,
            self.title_uuid,
            self.title_name
        )

    def set_placeholder_data(self):
        #title seems to be the same format as screen UUID
        self.placeholder_uuid = self.util.random_screen_uuid()
        self.placeholder_name = self.util.random_str(8)
        self.packs_db.set_placeholder(
            self.db,
            self.placeholder_uuid,
            self.placeholder_name
        )
        self.packs_db.get_placeholder_by_uuid(
            self.db,
            self.placeholder_uuid
        )

    def create_optional_data(self):
        self.optional_dict = {
            'uuid': self.util.random_uuid(),
            'date_from': "2015-07-25",
            'date_to': "2015-07-25",
            'time_from': "00:00:01",
            'time_to': "23:59:59",
            'print_no': 1,
            'priority': 2,
            'issuer': 'issuer' + self.util.random_str(),
            'placeholder_uuid': self.placeholder_uuid,
            'title_name': self.title_name,
            'cpl_id': self.util.random_uuid(),
            'text': "USAIN-BOLT-3D_RTG_F_U-CERT_EN-XX_UK-U_51_2K_20090626_TEU",
            'duration_in_frames': 4376,
            'edit_rate': '24 1',
            'duration_in_seconds': 13,
            'title_rating': "PG",
            'title_region': "UK",
            'screen_identifiers': [self.screen_identifier],
            'screen_uuids': [self.screen_uuid],
            "external_show_attribute_maps": [
                {
                    "source": 'source' + self.util.random_str(),
                    "external_id": "3D"
                }
            ],
            'title_uuid': self.title_uuid,
            "ratings": [
                {'territory': "UK",
                 'rating': "PG"}
            ]
        }

    def assertResponse(self, response, **kwargs):
        """
        Asserts that the given response is OK and has JSON payload in the
        most common formats:
        {
            "data": <some_data>
            "messages": [
                {
                    <some_more_data>
                    "type": "success"
                }
            ]
        }

        OR

        {
            "data": <some_data>
            "messages": []
        }
        """

        msg_on_fail = lambda msg: '%s\nFull Response:\n %s\n' % \
                                  (msg, response.content)

        self.assertEqual(
            response.status_code, requests.codes.ok,
            msg_on_fail('Invalid status code "%d"' % response.status_code)
        )
        try:
            json_data = response.json()
        except ValueError:
            json_data = None
        self.assertTrue(json_data is not None,
                        msg_on_fail('Response not in JSON format'))

        messages = json_data.get('messages')
        self.assertIsInstance(messages, list,
                              msg_on_fail('Messages non-existent or not list'))

        if len(messages) > 0:
            #prehaps put the assertion before the length of the message?
            self.assertNotEqual(len(messages), 0,
                                msg_on_fail(
                                    'Messages must be list of length 1'))
            for msg_cnt in range(len(messages)):
                message = messages[msg_cnt]
                self.assertIsInstance(message, dict,
                                      msg_on_fail('Message must be dict'))
                #verify message text if provided
                if "message" in kwargs:
                    self.assertTrue(kwargs["message"] in message["message"])
                    #verify message
                # default to success if it doesn't exist
                type_message = message.get('type', 'success')
                if type_message == 'success':
                    self.assertEqual(type_message, 'success',
                                     msg_on_fail(
                                         'Message type - not type success'))
                else:
                    self.assertEqual(type_message, 'error',
                                     msg_on_fail(
                                         'Message type -not type error'))

    def assert_find_pack_data(self, response, **kwargs):

        msg_on_fail = lambda msg: '%s\nFull Response:\n %s\n' % \
                                  (msg, response.content)

        try:
            json_data = response.json()
        except ValueError:
            json_data = None
        self.assertTrue(json_data is not None,
                        msg_on_fail('Response not in JSON format'))

        data = json_data.get('data')
        self.assertIsInstance(data, dict,
                              msg_on_fail('Data non-existent or not dict'))
        if len(data) > 0:
            if 'cpl_id' in kwargs:
                cpl_value = kwargs.get('cpl_id')
                cpl_dict = data.get(cpl_value)
                self.assertEqual(cpl_dict['uuid'], kwargs['uuid'],
                                 msg_on_fail('Incorrect uuid'))
                self.assertEqual(cpl_dict['name'], kwargs['name'],
                                 msg_on_fail('Incorrect name'))
                self.assertEqual(cpl_dict['placeholder_uuid'],
                                 kwargs['placeholder_uuid'],
                                 msg_on_fail('Incorrect placeholder_uuid'))

    def assert_packs_data(self, response, **kwargs):

        msg_on_fail = lambda msg: '%s\nFull Response:\n %s\n' % \
                                  (msg, response.content)

        try:
            json_data = response.json()
        except ValueError:
            json_data = None
        self.assertTrue(json_data is not None,
                        msg_on_fail('Response not in JSON format'))

        data = json_data.get('data')
        self.assertIsInstance(data, dict,
                              msg_on_fail('Data non-existent or not dict'))
        if len(data) > 0:
            actual = {}
            expected = {}
            # TODO: coding needs work work to test more of the values
            # TODO: in no_verify
            no_verify = {
                'clips': True,
                'screens': True,
                'external_show_attribute_maps': True,
                'placeholder_name': True,
                'date_to': True,
                'time_to': True,
                'ratings': True

            }
            if 'pack_uuids' in kwargs:
                uuid_value = kwargs.get('pack_uuids')
                actual = data.get(uuid_value[0])
                expected = self.packs_db.get_pack_by_uuid(
                    self.db,
                    kwargs['pack_uuids'][0]
                )

            #temp dict used to store
            temp_dict = {}
            del_key_list = []

            #clean up data loop
            for key, value in actual.iteritems():

                if type(value) is list and key not in no_verify:
                    if not value:
                        actual[key] = None
                    else:
                        for list_value in value:
                            if type(list_value) is dict:
                                del_key_list.append(key)
                                for k, v in list_value.iteritems():
                                    temp_dict[k] = v
                            else:
                                actual[key] = list_value
                    #swap the name of 'date_from' and 'time_from':
                if key == 'date_from':
                    actual['playback_date_range_end'] = actual.pop(key)
                if key == 'time_from':
                    actual['playback_time_range_start'] = actual.pop(key)
                    if expected['playback_time_range_start']:
                        expected['playback_time_range_start'] = \
                            expected['playback_time_range_start'].rpartition(
                                '.')[0]

            actual.update(temp_dict)
            #delete keys with that had a list of dicts
            for del_key in del_key_list:
                del actual[del_key]

            #assertion loop
            for key, value in actual.iteritems():

                if value is not None and key not in no_verify:
                    self.assertTrue(key in expected,
                                    msg_on_fail('pack key error'))
                    self.assertEqual(value, expected[key],
                                     msg_on_fail('pack value error'))

                if key == 'clips':
                    clips_actual = actual['clips'][0]
                    clips_expected = json.loads(expected['clips'])[0]
                    for key, value in clips_actual.iteritems():
                        self.assertTrue(key in clips_expected,
                                        msg_on_fail('clips key error'))
                        self.assertEqual(value, clips_expected[key],
                                         msg_on_fail('clips value error'))

    def assertDbPack(self, response, uuid=None):

        if uuid is None:
            uuid = response.json()['messages'][0]['uuid']
        db_packs = self.packs_db.get_pack_by_uuid(self.db, uuid)
        self.assertEquals(db_packs['uuid'], uuid)

        """
        {'packs': [{'clips': [{'edit_rate': '24 1', 'text':
        '16554TPG1799UN_ADV_F_EN-XX_AU_51_2K_20130111_DAU_OV',
        'duration_in_frames': 1080, 'cpl_id':
        'abb5f47f-014d-4a11-8d1e-a820470f01a7'}], 'name': 'pack name',
        'placeholder_name': 'place holder name'}]}
        """
        """
        {u'title_uuid': None, u'title_rating': None, u'title_region': None,
        u'duration': None, u'title_name': None, u'placeholder_uuid':
        u'4db18b19-65ca-4a63-81a1-f611ff6a4874',
        u'playback_date_range_start': None, u'screen_external_ids': None,
        u'issuer': u'TMS', u'title_external_ids': None, u'issue_date':
        u'2014-02-06 16:18:24.362887', u'uuid':
        u'1a5f1970-24e4-49ac-8962-983ae334d33a', u'priority': 1000,
        u'version': None, u'last_modified': 1392130155.3486171,
        u'playback_time_range_end': None, u'print_no': None, u'name': u'pack
        name', u'created': 1392130155.3451469,
         u'clips': u'[{"duration_in_frames": 1080, "cpl_id":
         "abb5f47f-014d-4a11-8d1e-a820470f01a7", "edit_rate": "24 1", "text": "16554TPG1799UN_ADV_F_EN-XX_AU_51_2K_20130111_DAU_OV", "automation": [], "duration_in_seconds": null, "type": "composition"}]', u'playback_date_range_end': None, u'playback_time_range_start': None}
        """



