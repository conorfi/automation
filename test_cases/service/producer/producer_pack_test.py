"""
@summary: first test file for testing api
@since: Created on April 15th 2014
@author: Will Ellis
"""
from nose.plugins.attrib import attr
from . import ApiTestCase
import requests

class FirstTestRun(ApiTestCase):

    @attr(env=['test'], priority=1)
    def test_get_packs(self):
        """
        PRODUCER_PACK_API_001 test_get_packs
        Test that the API can call the packs API successfully
        """
        response = self.packs_service.test_pack_api("packs")
        self.assertEqual(response.status_code,requests.codes.ok)

