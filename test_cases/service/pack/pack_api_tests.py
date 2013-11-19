'''
@summary: Contains a set oF API tests for the gate keeper(single sign on) project

@since: Created on October 31st 2013

@author: Conor Fitzgerald

'''
import json
import requests
from testconfig import config
from nose.plugins.attrib import attr
from sqlalchemy import create_engine
from framework.service.packs.pack_service import PackService
#from framework.db.base_dao import BaseDAO
#from framework.db.gate_keeper_dao import GateKeeperDAO


class TestGateKeeperAPI:

    @classmethod
    def setUpClass(self):
        '''Things that need to be done once.'''
                 
    def setup(self):
        '''Things to run before each test.''' 
                         
        #self.db = BaseDAO(config['gatekeeper']['db']['connection'])
        #self.gk_service = GateKeeperService() 
        #self.gk_dao = GateKeeperDAO()
        self.packs_service = PackService()
        
    def __init__(self):              
        '''Things to be initalized'''
         
         
    def teardown(self):
        '''Things to run after each test.'''  
        #self.db.connection.close()
             
    
       
    @attr(env=['test'],priority =1)
    def test_save_pack(self):  
        response = self.packs_service.save_pack()
        print response