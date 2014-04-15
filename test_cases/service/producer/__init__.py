<<<<<<< HEAD
from testconfig import config
import testy as unittest
import requests
from framework.service.producer.producer_service import PackService
#from framework.service.producer.producer_service import Messages
from framework.common_env import SERVICE_NAME_PRODUCER as SERVICE_NAME
from framework.db.base_dao import BaseDAO
from framework.db.producer_dao import Packs
#from framework.utility.utility import Utility
#import json


class ApiTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Things that need to be done once
        cls.db = BaseDAO(config[SERVICE_NAME]['db']['credentials'])
        cls.db = BaseDAO(config[SERVICE_NAME]['db']['connection'])

    @classmethod
    def tearDownClass(cls):
        # Things that need to be done once.
        cls.db.close()

    def setUp(self):
        # Things to run before each test.
        self.packs_service = PackService()
        self.packs_db = Packs()
        #self.msgs = Messages()
       # self.util = Utility()
        #screen
        #self.set_screen_data()
        #title
       # self.set_title_data()
        #placeholder
       # self.set_placeholder_data()
        #optional data dict
       # self.create_optional_data()

    def tearDown(self):
        pass
     #   self.packs_db.del_screen_by_uuid(self.db, self.screen_uuid)
      #  self.packs_db.del_title_by_uuid(self.db, self.title_uuid)
       # self.packs_db.del_title_by_uuid(self.db, self.placeholder_uuid)


=======
>>>>>>> 4d7d3578ff84dd31e22232360eacdb4a2a8165f8

