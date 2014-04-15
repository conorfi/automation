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
    def test_get_datatables_required_params(self):
        """
        Test that the API can call a pack datatable successfully
        """
        response = self.packs_service.test_pack_api("datatables")
        self.assertResponse(response, message=self.msgs.saved_msg)
        self.packs_service.pack_clean_up(response)
