"""
@summary: first test file for testing api
@since: Created on April 15th 2014
@author: Will Ellis
"""
from nose.plugins.attrib import attr
<<<<<<< HEAD
from . import ApiTestCase
=======
from test_cases.service import ApiTestCase
>>>>>>> 4d7d3578ff84dd31e22232360eacdb4a2a8165f8
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
