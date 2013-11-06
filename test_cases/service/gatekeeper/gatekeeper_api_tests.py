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
from framework.service.gatekeeper.gatekeeper_service import GateKeeperService
from framework.db.base_dao import BaseDAO
from framework.db.gate_keeper_dao import GateKeeperDAO


class TestGateKeeperAPI:

    @classmethod
    def setUpClass(self):
        '''Things that need to be done once.'''
                 
    def setup(self):
        '''Things to run before each test.''' 
                         
        self.db = BaseDAO(config['gatekeeper']['db']['connection'])
        self.gk_service = GateKeeperService() 
        self.gk_dao = GateKeeperDAO()
        
    def __init__(self):              
        '''Things to be initalized'''
         
         
    def teardown(self):
        '''Things to run after each test.'''  
        self.db.connection.close()
             
    @attr(env=['test'],priority =1)
    def test_can_create_session_json(self):        
        '''   
        creates a session through a POST to the login API using json body  
        '''       
        response=self.gk_service.create_session_json()
        assert response.status_code == requests.codes.ok
        json_response = json.loads(response.text)
        
        #assert against database
        db_response =self.gk_dao.get_session_by_session_id(self.db,json_response['session_id'])        
        assert db_response['user_id'] == json_response['user_id']
        assert db_response['session_id'] == json_response['session_id']
        
       
    @attr(env=['test'],priority =1)
    def test_can_create_session_urlencoded(self):        
        '''   
        creates a session through a POST to the login API using urlencoded body   
        '''       
        response=self.gk_service.create_session_urlencoded()
        assert response.status_code == requests.codes.ok 
        json_response = json.loads(response.text)
        
        #assert against database
        db_response =self.gk_dao.get_session_by_session_id(self.db,json_response['session_id'])        
        assert db_response['user_id'] == json_response['user_id']
        assert db_response['session_id'] == json_response['session_id']      
         
    @attr(env=['test'],priority =1)    
    def test_can_validate_json_session(self):
        '''   
        creates a session through a POST to the login API and then validates the 
        user_id and session_id(cookie value)   
        '''
        
        #json post
        response=self.gk_service.create_session_json()
        assert response.status_code == requests.codes.ok 
        json_response = json.loads(response.text)
        #assert againist database
        
        val_response=self.gk_service.validate_session(session_id=json_response['session_id'])        
        json_val_response = json.loads(val_response.text)
        assert json_val_response['user_id'] == json_response['user_id']
        assert json_val_response['session_id'] == json_response['session_id']
    
    
    @attr(env=['test'],priority =1)    
    def test_can_validate_urlencoded_session(self):
        '''   
        creates a session through a POST to the login API and then validates the 
        user_id and session_id(cookie value)   
        '''
        
        #urlencoded post
        response=self.gk_service.create_session_urlencoded()
        assert response.status_code == requests.codes.ok 
        json_response = json.loads(response.text)
        
        
        val_response=self.gk_service.validate_session(session_id=json_response['session_id'])        
        json_val_response = json.loads(val_response.text)
        assert json_val_response['user_id'] == json_response['user_id']
        assert json_val_response['session_id'] == json_response['session_id']             
    
    @attr(env=['test'],priority =1)
    def test_can_validate_json_cookie(self):
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
    def test_can_validate_urlencoded_cookie(self):
        '''   
        creates a session through a POST to the login API and then verifies that a user
        can access an url using a session with a valid cookie
        '''        
        response=self.gk_service.create_session_urlencoded()
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
        cannot access an url using an expired cookie on the client side
        '''
                
        response=self.gk_service.create_session_json()
        
        assert response.status_code == requests.codes.ok 
        
        json_response = json.loads(response.text)
        
        cookie_value = json_response['session_id']
                 
        my_cookie = dict(name='sso_cookie',value=cookie_value,expires = -1)   
        session = self.gk_service.create_requests_session_with_cookie(my_cookie)
        response = self.gk_service.validate_url_with_cookie(session) 
                
        assert response.status_code == requests.codes.ok           
        assert '<title>Gatekeeper / Arts Alliance Media</title>' in response.text  
    
    @attr(env=['test'],priority =1)
    def test_expired_client_cookie_urlencoded(self):
        '''   
        creates a session through a POST to the login API and then verifies that a user
        cannot access an url using an expired cookie on the client side
        '''
                
        response=self.gk_service.create_session_urlencoded()
        
        assert response.status_code == requests.codes.ok 
        
        json_response = json.loads(response.text)
        
        cookie_value = json_response['session_id']        
                 
        my_cookie = dict(name='sso_cookie',value=cookie_value,expires = -1)   
        session = self.gk_service.create_requests_session_with_cookie(my_cookie)
        response = self.gk_service.validate_url_with_cookie(session) 
                
        assert response.status_code == requests.codes.ok           
        assert '<title>Gatekeeper / Arts Alliance Media</title>' in response.text  
    
             
    @attr(env=['test'],priority =1)
    def test_expired_server_cookie_json(self):
        '''   
        creates a session through a POST to the login API and then verifies that a user
        cannot access an url using an expired cookie on the server side
        '''
                
        response=self.gk_service.create_session_json()
        
        assert response.status_code == requests.codes.ok 
        
        json_response = json.loads(response.text)
        
        cookie_value = json_response['session_id']
        
        #update cookie in the database so thats its expired
        assert(self.gk_dao.set_session_to_expire_by_session_id(self.db,json_response['session_id']))        
                 
        my_cookie = dict(name='sso_cookie',value=cookie_value)   
        session = self.gk_service.create_requests_session_with_cookie(my_cookie)
        response = self.gk_service.validate_url_with_cookie(session) 
                
        assert response.status_code == requests.codes.ok           
        assert '<title>Gatekeeper / Arts Alliance Media</title>' in response.text  
        
    @attr(env=['test'],priority =2)
    def test_expired_server_cookie_urlencoded(self):
        '''   
        creates a session through a POST to the login API and then verifies that a user
        cannot access an url using an expired cookie on the server side
        '''
                
        response=self.gk_service.create_session_urlencoded()
        
        assert response.status_code == requests.codes.ok 
        
        json_response = json.loads(response.text)
        
        cookie_value = json_response['session_id']        
        
        #update cookie in the database so thats its expired
        assert(self.gk_dao.set_session_to_expire_by_session_id(self.db,json_response['session_id']))  
                 
        my_cookie = dict(name='sso_cookie',value=cookie_value)   
        session = self.gk_service.create_requests_session_with_cookie(my_cookie)
        response = self.gk_service.validate_url_with_cookie(session) 
                
        assert response.status_code == requests.codes.ok           
        assert '<title>Gatekeeper / Arts Alliance Media</title>' in response.text  