'''
@summary: 
@since: Created on November 28th 2013

@author: Conor Fitzgerald

'''
import json
import requests
from testconfig import config
from nose.plugins.attrib import attr
from framework.service.gatekeeper.gatekeeper_service import GateKeeperService
from framework.db.base_dao import BaseDAO
from framework.db.gate_keeper_dao import GateKeeperDAO
import Cookie
import random
import string

import imaplib
import email

#admin user is 'admin' and is used as the default user
ADMIN_USER = 'admin'

class TestGateKeeper2FaAPI:

    @classmethod
    def setUpClass(self):
        '''Things that need to be done once.'''
        
                 
    def setup(self):
        '''Things to run before each test.''' 
                         
        self.db = BaseDAO(config['gatekeeper']['db']['connection'])
        self.gk_service = GateKeeperService() 
        self.gk_dao = GateKeeperDAO()
        self.DEFAULT_TEST_USER = self.gk_dao.get_user_id_by_username(self.db, ADMIN_USER)['user_id']
        
    def __init__(self):              
        '''Things to be initalized'''
        
         
    def teardown(self):
        '''Things to run after each test.'''  
        self.db.connection.close()

    @attr(env=['test'],priority =1)   
    def test_can_login_two_factor_default_redirect(self):        
        '''   
        GATEKEEPER-2FA-API001 
        '''
        #create a session - do not allow redirects       
        response=self.gk_service.create_session_urlencoded(allow_redirects=False)
        #303 response
        assert response.status_code == requests.codes.other      
          
        #covert Set_Cookie response header to simple cookie object
        cookie = Cookie.SimpleCookie()
        cookie.load(response.headers['Set-Cookie'])
        cookie_id   = cookie['sso_credentials'].value        
        #assert against database
        db_response =self.gk_dao.get_session_by_cookie_id(self.db,cookie_id)       
        assert db_response['cookie_id'] == cookie_id  
        assert db_response['user_id'] == self.DEFAULT_TEST_USER                
        
                  
        my_cookie = dict(name='sso_credentials',value=cookie_id)  
        session = self.gk_service.create_requests_session_with_cookie(my_cookie)  
        
        verification_code = self.gk_dao.get_verification_code_by_user_id(self.db,self.DEFAULT_TEST_USER)['verification_code']    
        #print    verification_code    
        payload = {'verification_code' : verification_code}
        #print payload
        response = self.gk_service.submit_verification_code(session,payload,allow_redirects=False)
        
        assert response.ok
        
        #print response.headers
        
        cookie = Cookie.SimpleCookie()
        cookie.load(response.headers['Set-Cookie'])
        #print cookie
        #cookie_id_cred   = cookie['sso_credentials'].value
        #cookie_id_verf   = cookie['sso_verifcation_code'].value
        cookie_id_sso    = cookie['sso_cookie'].value
        
        #print cookie_id_sso 
        
        
        cookie.load(response.headers['set-cookie'])
        print  cookie
        
        
        