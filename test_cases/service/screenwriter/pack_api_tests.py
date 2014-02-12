"""
@summary: Contains a set of test cases for screen_writer(tms) packs API
@since: Created on October 31st 2013
@author: Conor Fitzgerald
"""

from nose.plugins.attrib import attr
from . import ApiTestCase


class ScreenWriterPacksAPI(ApiTestCase):

    @attr(env=['test'], priority=1)
    def test_save_pack_required_params(self):
        """
        SW_PACK_API_001 test_save_pack_required_params
        Ensure save API works correctly when required fields are provided
        Json request and response
        """
        response = self.packs_service.save_pack_json()
        self.assertResponseSuccess(response,message=self.msgs.saved_msg)
        self.assertDbPack(response)
        print response
        print response.json()

    @attr(env=['test'], priority=1)
    def test_save_json_pack_optional_parms(self):
        """
        SW_PACK_API_002 test_save_json_pack_optional_parms
        Ensure save API works correctly with option fields
        Json request and response
        """
        ads = self.packs_service.create_dict_pack(clips=1,packs=2,title_name="something")
        response = self.packs_service.save_pack_json(pack=ads)
        self.assertResponseSuccess(response, message="Saved")
        print response
        print response.json()

    @attr(env=['test'], priority=1)
    def test_save_xml_pack(self):
        response = self.packs_service.save_pack_xml()
        print response
