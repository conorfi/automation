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
    def test_can_create_session_json(self):        
        '''   
        creates a session through a POST to the login API using json body  
        '''       
        response=self.gk_service.create_session_json()
        assert response.status_code == requests.codes.ok
    
    @attr(env=['test'],priority =1)
    def test_can_create_session_urlencoded(self):        
        '''   
        creates a session through a POST to the login API using urlencoded body   
        '''       
        response=self.gk_service.create_session_urlencoded()
        assert response.status_code == requests.codes.ok
         
    @attr(env=['test'],priority =1)    
    def test_can_validate_session(self):
        '''   
        creates a session through a POST to the login API and then validates the 
        user_id and session_id(cookie value)   
        '''
        
        response=self.gk_service.create_session_json()
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
        response=self.gk_service.create_session_json()
        assert response.status_code == requests.codes.ok 
        json_response = json.loads(response.text)
        cookie_value = json_response['session_id']               
                 
         
        my_cookie = dict(name='sso_cookie',value=cookie_value)   
        response = self.gk_service.validate_url_with_cookie(self.gk_service.create_requests_session_with_cookie(my_cookie))        
        assert response.status_code == requests.codes.ok   
        assert 'Super awesome test' in response.text        
       
    @attr(env=['test'],priority =1)
    def test_expired_client_cookie_json(self):
        '''   
        creates a session through a POST to the login API and then verifies that a user
        cannot access an url using an expired cookie
        '''
                
        response=self.gk_service.create_session_json()
        
        assert response.status_code == requests.codes.ok 
        
        json_response = json.loads(response.text)
        
        cookie_value = json_response['session_id']
        
        print cookie_value
         
        my_cookie = dict(name='sso_cookie',value=cookie_value,expires = -1)   
        session = self.gk_service.create_requests_session_with_cookie(my_cookie)
        response = self.gk_service.validate_url_with_cookie(session) 
                
        assert response.status_code == requests.codes.ok           
        assert '<title>Gatekeeper / Arts Alliance Media</title>' in response.text  
    
    @attr(env=['test'],priority =1)
    def test_expired_client_cookie_urlencoded(self):
        '''   
        creates a session through a POST to the login API and then verifies that a user
        cannot access an url using an expired cookie
        '''
                
        response=self.gk_service.create_session_urlencoded()
        
        assert response.status_code == requests.codes.ok 
        
        json_response = json.loads(response.text)
        
        cookie_value = json_response['session_id']
        
        print cookie_value
         
        my_cookie = dict(name='sso_cookie',value=cookie_value,expires = -1)   
        session = self.gk_service.create_requests_session_with_cookie(my_cookie)
        response = self.gk_service.validate_url_with_cookie(session) 
                
        assert response.status_code == requests.codes.ok           
        assert '<title>Gatekeeper / Arts Alliance Media</title>' in response.text  
    
    @attr(env=['test'],priority =1)
    def test_data_both(self):   
        
        jresponse=self.gk_service.create_session_json()        
        uresponse=self.gk_service.create_session_urlencoded()
                     
        print jresponse.text
        print uresponse.text
        
        json_jresponse = json.loads(jresponse.text)
        json_uresponse = json.loads(uresponse.text)
        
        print  json_jresponse
        print  json_uresponse
        
        cookie_valuej = json_jresponse['session_id']
        cookie_valueu = json_uresponse['session_id']
        
        print cookie_valuej  
        print cookie_valueu  
        
        histroryj = jresponse.history
        histroryu = uresponse.history
        
        print histroryj  
        print histroryu
        
        
        my_cookiej = dict(name='sso_cookie',value=cookie_valuej,expires = -1)   
        my_cookieu = dict(name='sso_cookie',value=cookie_valueu,expires = -1)   
        
        print my_cookiej 
        print my_cookieu
        
        sessionj = self.gk_service.create_requests_session_with_cookie(my_cookiej)
        sessionu = self.gk_service.create_requests_session_with_cookie(my_cookieu)
        
        print sessionj
        print sessionu
        
        responsej = self.gk_service.validate_url_with_cookie(sessionj)
        responseu = self.gk_service.validate_url_with_cookie(sessionu) 
               
        
        print responsej 
        print responseu
        print responsej.history 
        print responseu.history 
        print responseu.status_code 
        print responsej.status_code 
        
        assert responseu.status_code == requests.codes.ok           
        assert '<title>Gatekeeper / Arts Alliance Media</title>' in responseu.text  
        
        assert responsej.status_code == requests.codes.ok           
        assert '<title>Gatekeeper / Arts Alliance Media</title>' in responsej.text          
