'''
@summary: Contains a set of API tests for the
gate keeper(single sign on) project

@since: Created on October 31st 2013

@author: Conor Fitzgerald

'''

from nose.plugins.attrib import attr
from framework.service.packs.pack_service import PackService



class TestGateKeeperAPI:

    @classmethod
    def setUpClass(self):
        '''Things that need to be done once.'''

    def setup(self):
        '''Things to run before each test.'''
        self.packs_service = PackService()

    def __init__(self):
        '''Things to be initalized'''

    def teardown(self):
        '''Things to run after each test.'''
        # self.db.connection.close()

    @attr(env=['test'], priority=1)
    def test_save_json_pack(self):
        response = self.packs_service.save_pack_json()

    @attr(env=['test'], priority=1)
    def test_save_xml_pack(self):
        response = self.packs_service.save_pack_xml()
