"""
"""
import unittest
from testconfig import config

from framework.utility.utility import Utility
from framework.db.base_dao import BaseDAO
from framework.service.courier import CourierService, SERVICE_NAME
from framework.db.courier import CourierDao


class ApiTestCase(unittest.TestCase):

    SERVICE_NAME = SERVICE_NAME

    @classmethod
    def setUpClass(cls):
        cls.db = BaseDAO(config[SERVICE_NAME]['db']['connection'])

    @classmethod
    def tearDownClass(cls):
        cls.db.close()

    def setUp(self):
        super(ApiTestCase, self).setUp()
        self.dao = CourierDao(self.db)
        self.service = CourierService(self.dao)
        self.util = Utility()
