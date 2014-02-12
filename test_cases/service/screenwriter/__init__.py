from testconfig import config
import testy as unittest
import requests
from framework.service.screen_writer.screen_writer_service import PackService
from framework.service.screen_writer.screen_writer_service import Messages
from framework.common_env import SERVICE_NAME_SCREEN_WRITER as SERVICE_NAME
from framework.db.base_dao import BaseDAO
from framework.db.screen_writer import Packs

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
        self.packs_service = PackService()
        self.packs_db  = Packs()
        self.msgs      = Messages()

    def assertResponseSuccess(self, response, **kwargs):
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

        msg_on_fail = lambda msg: '%s\nFull Response:\n %s\n' %\
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

        print "length message " + str(len(messages))
        if len(messages) > 0:
            #prehaps put the assertion before the lengh of the message?
            self.assertNotEqual(len(messages), 0,
                             msg_on_fail('Messages must be list of length 1'))
            for msg_cnt in range(len(messages)):
                message = messages[msg_cnt]
                self.assertIsInstance(message, dict,
                                      msg_on_fail('Message must be dict'))
                #verify message text if provided
                if "message" in kwargs:
                    print "message check"
                    print kwargs["message"] + " " +  message["message"]
                    self.assertTrue(kwargs["message"] in message["message"])
                #verify message
                # default to success if it doesn't exist
                type_message = message.get('type', 'success')
                self.assertEqual(type_message, 'success',
                                 msg_on_fail('Message type is error'))


    def assertDbPack(self,response,uuid=None):

        if uuid is None:
            uuid= response.json()['messages'][0]['uuid']
        db_packs = self.packs_db.get_pack_by_uuid(self.db,uuid)
        self.assertEquals(db_packs['uuid'],uuid)

        """
        {'packs': [{'clips': [{'edit_rate': '24 1', 'text': '16554TPG1799UN_ADV_F_EN-XX_AU_51_2K_20130111_DAU_OV', 'duration_in_frames': 1080, 'cpl_id': 'abb5f47f-014d-4a11-8d1e-a820470f01a7'}], 'name': 'pack name', 'placeholder_name': 'place holder name'}]}
        """
        """
        {u'title_uuid': None, u'title_rating': None, u'title_region': None, u'duration': None, u'title_name': None, u'placeholder_uuid': u'4db18b19-65ca-4a63-81a1-f611ff6a4874', u'playback_date_range_start': None, u'screen_external_ids': None, u'issuer': u'TMS', u'title_external_ids': None, u'issue_date': u'2014-02-06 16:18:24.362887', u'uuid': u'1a5f1970-24e4-49ac-8962-983ae334d33a', u'priority': 1000, u'version': None, u'last_modified': 1392130155.3486171, u'playback_time_range_end': None, u'print_no': None, u'name': u'pack name', u'created': 1392130155.3451469,
         u'clips': u'[{"duration_in_frames": 1080, "cpl_id": "abb5f47f-014d-4a11-8d1e-a820470f01a7", "edit_rate": "24 1", "text": "16554TPG1799UN_ADV_F_EN-XX_AU_51_2K_20130111_DAU_OV", "automation": [], "duration_in_seconds": null, "type": "composition"}]', u'playback_date_range_end': None, u'playback_time_range_start': None}
        """
        print "db_packs"
        print db_packs


