"""
"""
import unittest
import requests
from nose.plugins.attrib import attr
from testconfig import config

from framework.utility.utility import Utility
from framework.db.base_dao import BaseDAO
from framework.service.courier import CourierService, SERVICE_NAME
from framework.db.courier import CourierDao


class ContentApiTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Things that need to be done once
        cls.db = BaseDAO(config[SERVICE_NAME]['db']['connection'])

    @classmethod
    def tearDownClass(cls):
        # Things that need to be done once.
        cls.db.close()

    def setUp(self):
        self.gk_service = CourierService()
        self.gk_dao = CourierDao(self.db)
        self.util = Utility()

    @attr(env=['test'], priority=1)
    def test_create(self):
        self.assertTrue(True)
