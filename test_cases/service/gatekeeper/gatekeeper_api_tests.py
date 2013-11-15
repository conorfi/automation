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
import Cookie

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
    def test_can_create_session(self):        
        '''   
        GATEKEEPER-API001 creates a session through a POST to the login API using urlencoded body   
        '''
        #create a session - do not allow redirects       
        response=self.gk_service.create_session_urlencoded(allow_redirects=False)
        #303 response
        assert response.status_code == requests.codes.other        
        #covert Set_Cookie response header to simple cookie object
        cookie = Cookie.SimpleCookie()
        cookie.load(response.headers['Set-Cookie'])
        session_id   = cookie['sso_cookie'].value        
        #assert against database
        db_response =self.gk_dao.get_session_by_session_id(self.db,session_id)       
        assert db_response['session_id'] == session_id  
        
        #create a session - allow redirects   
        response=self.gk_service.create_session_urlencoded(allow_redirects=True)
        #200 response
        assert response.status_code == requests.codes.ok
        assert 'Example Domain' in response.text  
       
    @attr(env=['test'],priority =1)    
    def test_can_validate_urlencoded(self):
        '''   
        GATEKEEPER-API002 creates a session through a POST to the login API and then validates the 
        user_id and session_id(cookie value)   
        '''
        
        #urlencoded post
        #create a session - do not allow redirects       
        response=self.gk_service.create_session_urlencoded(allow_redirects=False)
        #303 response
        assert response.status_code == requests.codes.other        
        #covert Set_Cookie response header to simple cookie object
        cookie = Cookie.SimpleCookie()
        cookie.load(response.headers['Set-Cookie'])
        session_id   = cookie['sso_cookie'].value    
                
        val_response=self.gk_service.validate_session(session_id=session_id)
        assert val_response.status_code == requests.codes.ok        
        json_val_response = json.loads(val_response.text)
        
        #obtain session id and user id from database
        db_response =self.gk_dao.get_session_by_session_id(self.db,session_id)   
        
        #assert against database
        assert json_val_response['user_id']    == db_response['user_id']
        assert json_val_response['session_id'] == db_response['session_id']             
    
   
    @attr(env=['test'],priority =2)
    def test_can_validate_cookie(self):
        '''   
        GATEKEEPER-API003 creates a session through a POST to the login API and then verifies that a user
        can access an url using a session with a valid cookie
        '''   
        #urlencoded post
        #create a session - do not allow redirects       
        response=self.gk_service.create_session_urlencoded(allow_redirects=False)
        #303 response
        assert response.status_code == requests.codes.other        
        #covert Set_Cookie response header to simple cookie object
        cookie = Cookie.SimpleCookie()
        cookie.load(response.headers['Set-Cookie'])
        cookie_value  = cookie['sso_cookie'].value   
            
        my_cookie = dict(name='sso_cookie',value=cookie_value)   
        response = self.gk_service.validate_url_with_cookie(self.gk_service.create_requests_session_with_cookie(my_cookie))        
        assert response.status_code == requests.codes.ok   
        assert 'Example Domain' in response.text  
           
   
    @attr(env=['test'],priority =1)
    def test_expired_client_cookie(self):
        '''   
        GATEKEEPER-API004 creates a session through a POST to the login API and then verifies that a user
        cannot access an url using an expired cookie on the client side
        '''              
        #urlencoded post
        #create a session - do not allow redirects       
        response=self.gk_service.create_session_urlencoded(allow_redirects=False)
        #303 response
        assert response.status_code == requests.codes.other        
        #covert Set_Cookie response header to simple cookie object
        cookie = Cookie.SimpleCookie()
        cookie.load(response.headers['Set-Cookie'])
        cookie_value  = cookie['sso_cookie'].value           
                 
        my_cookie = dict(name='sso_cookie',value=cookie_value,expires = -1)
        response = self.gk_service.validate_url_with_cookie(self.gk_service.create_requests_session_with_cookie(my_cookie))         
         
        assert response.status_code == requests.codes.ok           
        assert '<title>Gatekeeper / Arts Alliance Media</title>' in response.text  
      
    @attr(env=['test'],priority =1)
    def test_expired_server_cookie(self):
        '''   
        GATEKEEPER-API005 creates a session through a POST to the login API and then verifies that a user
        cannot access an url using an expired cookie on the server side
        '''
        #urlencoded post
        #create a session - do not allow redirects       
        response=self.gk_service.create_session_urlencoded(allow_redirects=False)
        #303 response
        assert response.status_code == requests.codes.other        
        #covert Set_Cookie response header to simple cookie object
        cookie = Cookie.SimpleCookie()
        cookie.load(response.headers['Set-Cookie'])
        cookie_value  = cookie['sso_cookie'].value           
        
        #update cookie in the database so thats its expired
        assert(self.gk_dao.set_session_to_expire_by_session_id(self.db,cookie_value)) 
                        
        my_cookie = dict(name='sso_cookie',value=cookie_value)    
        response = self.gk_service.validate_url_with_cookie(self.gk_service.create_requests_session_with_cookie(my_cookie))    
        assert response.status_code == requests.codes.ok           
        assert '<title>Gatekeeper / Arts Alliance Media</title>' in response.text  
        
        #reopen another db connection - :TODO investigate a cleaner solution than this
        self.db = BaseDAO(config['gatekeeper']['db']['connection'])        
        #USER LOGINS CAUSED EXPIRED COOKIE TO BE DELETED
        response=self.gk_service.create_session_urlencoded(allow_redirects=False)
        
        #assert againist the database - ensure it no longer exists
        db_response = self.gk_dao.get_session_by_session_id(self.db,cookie_value)  
        #Code GOT OVERWRIITEN WHEN LOGIN api WAS REMOVED
        assert db_response== None
        
    @attr(env=['test'],priority =1)    
    def test_header_verification_urlencoded_session(self):
        '''   
        GATEKEEPER-API006 creates a session through a POST to the login API and then validates the 
        user_id and session_id(cookie value). Ensure httponly header is present   
        '''
        #urlencoded post
        #create a session - do not allow redirects       
        response=self.gk_service.create_session_urlencoded(allow_redirects=False)
        #303 response
        assert response.status_code == requests.codes.other        
                    
        headers = response.headers['Set-Cookie'] 
        #assert that the header httponly is present 
        assert 'httponly' in headers    
   
        
    
    @attr(env=['test'],priority =1)
    def test_can_delete_session_urlencoded(self):
        '''   
        GATEKEEPER-API007 Ensures a user session can be deleted using single logout(for a json created session)
        '''        
        #urlencoded post
        #create a session - do not allow redirects       
        response=self.gk_service.create_session_urlencoded(allow_redirects=False)
        #303 response
        assert response.status_code == requests.codes.other        
        #covert Set_Cookie response header to simple cookie object
        cookie = Cookie.SimpleCookie()
        cookie.load(response.headers['Set-Cookie'])
        cookie_value  = cookie['sso_cookie'].value                      
                 
        my_cookie = dict(name='sso_cookie',value=cookie_value)
        session = self.gk_service.create_requests_session_with_cookie(my_cookie)
        
        response = self.gk_service.validate_url_with_cookie(session)        
        assert response.status_code == requests.codes.ok   
        assert 'Example Domain' in response.text    
        
        response = self.gk_service.delete_user_session(session)
        assert response.status_code == requests.codes.ok  
               
        response = self.gk_service.validate_url_with_cookie(session)    
        assert response.status_code == requests.codes.ok           
        assert '<title>Gatekeeper / Arts Alliance Media</title>' in response.text
        
        #assert againist the database - ensure it no longer exists
        db_response =self.gk_dao.get_session_by_session_id(self.db,cookie_value)  
        assert db_response== None