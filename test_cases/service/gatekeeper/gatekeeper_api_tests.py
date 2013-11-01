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
from gatekeeper_service import GateKeeperService


class TestGateKeeperAPI:

    @classmethod
    def setUpClass(self):
        '''Things that need to be once.'''
                 
    def setup(self):
        '''Things to run before each test.'''                      
        
    def __init__(self):              
        '''Things to be initalized'''
        self.gk_service = GateKeeperService()  
       
    @attr(env=['test'],priority =1)
    def test_can_create_session(self):        
        '''   
        creates a session through a POST to the login API   
        '''       
        response=self.gk_service.create_session()
        assert response.status_code == requests.codes.ok
     
    @attr(env=['test'],priority =1)    
    def test_can_validate_session(self):
        '''   
        creates a session through a POST to the login API and then validates the 
        user_id and session_id(cookie value)   
        '''
        
        response=self.gk_service.create_session()
        assert response.status_code == requests.codes.ok 
        json_response = json.loads(response.text)
        
        
        val_response=self.gk_service.validate_session(session_id=json_response['session_id'])        
        json_val_response = json.loads(val_response.text)
        assert json_val_response['user_id'] == json_response['user_id']
        assert json_val_response['session_id'] == json_response['session_id']
    
    @attr(env=['test'],priority =1)
    def test_can_validate_cookie(self):
        '''   
        creates a session through a POST to the login API and then verifies that a user
        can access an url using a session with a valid cookie
        '''        
        response=self.gk_service.create_session()
        assert response.status_code == requests.codes.ok 
        json_response = json.loads(response.text)
        cookie_value = json_response['session_id']               
                 
         
        my_cookie = dict(name='sso_cookie',value=cookie_value)   
        response = self.gk_service.validate_url_with_cookie(self.gk_service.create_requests_session_with_cookie(my_cookie))        
        assert response.status_code == requests.codes.ok   
        assert 'Super awesome test' in response.text        
       
    @attr(env=['test'],priority =1)
    def test_expired_client_cookie(self):
        '''   
        creates a session through a POST to the login API and then verifies that a user
        cannot access an url using an expired cookie
        '''
        response=self.gk_service.create_session()
        assert response.status_code == requests.codes.ok 
        json_response = json.loads(response.text)
        cookie_value = json_response['session_id']
         
        my_cookie = dict(name='sso_cookie',value=cookie_value,expires = -1)   
        response = self.gk_service.validate_url_with_cookie(self.gk_service.create_requests_session_with_cookie(my_cookie)) 
                
        assert response.status_code == requests.codes.ok   
        assert '<title>Gatekeeper / Arts Alliance Media</title>' in response.text       
       