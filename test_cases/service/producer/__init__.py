
from testconfig import config
import testy as unittest
from framework.service.producer.producer_service import PackService
from framework.common_env import SERVICE_NAME_PRODUCER as SERVICE_NAME
from framework.db.base_dao import BaseDAO
from framework.db.producer_dao import Packs


class ApiTestCase(unittest.TestCase):

      def setUp(self):
        # Things to run before each test.
        self.packs_service = PackService()
        self.packs_db = Packs()
