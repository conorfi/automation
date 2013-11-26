'''
@summary: Contains a set oF API tests for the gate keeper(single sign on) project
these test have a number of dependencies 
1. the database update script updates the gatekeepr schema - the script can be found at the root of the gatekeeper app
2. the build script starts the gatekkper app with ssl enbaled by default
4. the build script starts the dummy app with ssl enabled and application_name is adfuser
4. The dummy app is pre-configure with two permissions 'ADFUSER_USER' and 'ADFUSER_ADMIN'

@since: Created on October 31st 2013

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

#adfuser is the defaut test application
DEFAULT_TEST_APP = "adfuser"
#admin user is 'admin' and is used as the default user
ADMIN_USER = 'admin'

#default user permission configured for adfuser in the dummy app
DEFAULT_ADFUSER_USER  = 'ADFUSER_USER'
#default admin permission configured for adfuser in the dummy app
DEFAULT_ADFUSER_ADMIN = 'ADFUSER_ADMIN'

# hash of the password test - using this rather than implementing the gatekeeper hashing function
# if the hashing function ever change sit will break a number of these functions
HASH_PASSWORD_TEST = "pbkdf2_sha256$12000$m5uwpzIW9qaO$88pIM25AqnXu4Fgt/Xgtpp3AInYgk5sxaxJmxxpcR8A="

class TestGateKeeperAPI:

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
    def test_can_create_session_with_redirect(self):        
        '''   
        GATEKEEPER-API001 creates a session through a POST to the login API using urlencoded body. Specified redirect   
        '''
        #create a session - do not allow redirects       
        response=self.gk_service.create_session_urlencoded(allow_redirects=False,redirect_url=config['gatekeeper']['redirect'])
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
         
        #create a session - allow redirects   
        response=self.gk_service.create_session_urlencoded(allow_redirects=True,redirect_url=config['gatekeeper']['redirect'])
        #200 response
        assert response.status_code == requests.codes.ok
        assert 'Example Domain' in response.text  
       
    @attr(env=['test'],priority =1)
    def test_can_create_session_default_redirect(self):        
        '''   
        GATEKEEPER-API002 creates a session through a POST to the login API using urlencoded body. Default redirect   
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
        
        #create a session - allow redirects   
        response=self.gk_service.create_session_urlencoded(allow_redirects=True)
        #200 response
        assert response.status_code == requests.codes.ok
            
    @attr(env=['test'],priority =1)    
    def test_can_validate_session_with_valid_session_cookie(self):
        '''   
        GATEKEEPER-API003 creates a session through a POST to the login API and then validates the 
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
        cookie_id   = cookie['sso_credentials'].value    
        
        
        my_cookie = dict(name='sso_credentials',value=cookie_id)
        val_response = self.gk_service.validate_session(cookie_id=cookie_id,session=self.gk_service.create_requests_session_with_cookie(my_cookie))    
      
        assert val_response.status_code == requests.codes.ok        
        json_val_response = json.loads(val_response.text)
        
        #obtain session id and user id from database
        db_response =self.gk_dao.get_session_by_cookie_id(self.db,cookie_id)   
        
        #assert against database
        assert json_val_response['user_id']    == db_response['user_id']
        assert json_val_response['session_id'] == db_response['session_id']             
    
    @attr(env=['test'],priority =1)
    def test_can_validate_session_cookie_with_redirect(self):
        '''   
        GATEKEEPER-API004 creates a session through a POST to the login API and then verifies that a user
        can access an url using a session with a valid cookie. Specified redirect
        '''   
        #urlencoded post
        #create a session - do not allow redirects       
        response=self.gk_service.create_session_urlencoded(allow_redirects=False,redirect_url=config['gatekeeper']['redirect'])
        #303 response
        assert response.status_code == requests.codes.other        
        #covert Set_Cookie response header to simple cookie object
        cookie = Cookie.SimpleCookie()
        cookie.load(response.headers['Set-Cookie'])
        cookie_value  = cookie['sso_credentials'].value   
            
        my_cookie = dict(name='sso_credentials',value=cookie_value)   
        response = self.gk_service.validate_url_with_cookie(self.gk_service.create_requests_session_with_cookie(my_cookie),redirect_url=config['gatekeeper']['redirect'])        
        assert response.status_code == requests.codes.ok   
        assert 'Example Domain' in response.text  
          
    
    @attr(env=['test'],priority =1)
    def test_validate_session_with_invalid_cookie(self):
        '''   
        GATEKEEPER-API005 creates a session through a POST to the login API and then verifies that a user
        cannot access an url using a session with invalid cookie.
        '''   
        #urlencoded post
        #create a session - do not allow redirects       
        response=self.gk_service.create_session_urlencoded(allow_redirects=False,redirect_url=config['gatekeeper']['redirect'])
        #303 response
        assert response.status_code == requests.codes.other        
        #covert Set_Cookie response header to simple cookie object
        cookie = Cookie.SimpleCookie()
        cookie.load(response.headers['Set-Cookie'])
        cookie_value  = ""   
            
        my_cookie = dict(name='sso_credentials',value=cookie_value)   
        response = self.gk_service.validate_url_with_cookie(self.gk_service.create_requests_session_with_cookie(my_cookie),redirect_url=config['gatekeeper']['redirect'])        
        assert response.status_code == requests.codes.ok  
        assert '<title>Gatekeeper / Arts Alliance Media</title>' in response.text 
            
    @attr(env=['test'],priority =1)
    def test_can_validate_url_with_cookie_default_redirect(self):
        '''   
        GATEKEEPER-API006 creates a session through a POST to the login API and then verifies that a user
        can access an url using a session with a valid cookie. Default redirect
        '''   
        #urlencoded post
        #create a session - do not allow redirects       
        response=self.gk_service.create_session_urlencoded(allow_redirects=False)
        #303 response
        assert response.status_code == requests.codes.other        
        #covert Set_Cookie response header to simple cookie object
        cookie = Cookie.SimpleCookie()
        cookie.load(response.headers['Set-Cookie'])
        cookie_value  = cookie['sso_credentials'].value   
            
        my_cookie = dict(name='sso_credentials',value=cookie_value)   
        response = self.gk_service.validate_url_with_cookie(self.gk_service.create_requests_session_with_cookie(my_cookie))        
        assert response.status_code == requests.codes.ok  
        assert "/logout/" in response.text 
    
    @attr(env=['test'],priority =1)
    def test_validate_url_with_cookie_invalid_session(self):
        '''   
        GATEKEEPER-API007 creates a session through a POST to the login API and then verify that a user
        CANNOT access an url using a session with a invalid cookie.
        As the session cookie is invalid the user will be prompted for a username and password
        '''   
        #urlencoded post
        #create a session - do not allow redirects       
        response=self.gk_service.create_session_urlencoded(allow_redirects=False)
        #303 response
        assert response.status_code == requests.codes.other        
        #covert Set_Cookie response header to simple cookie object
        cookie = Cookie.SimpleCookie()
        cookie.load(response.headers['Set-Cookie'])        
        cookie_value  =  "fakecookie"    
            
        my_cookie = dict(name='sso_credentials',value=cookie_value)   
        response = self.gk_service.validate_url_with_cookie(self.gk_service.create_requests_session_with_cookie(my_cookie))  
        assert response.status_code == requests.codes.ok  
        assert '<title>Gatekeeper / Arts Alliance Media</title>' in response.text 
                                        
    @attr(env=['test'],priority =1)
    def test_expired_client_cookie(self):
        '''   
        GATEKEEPER-API008 creates a session through a POST to the login API and then verifies that a user
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
        cookie_value  = cookie['sso_credentials'].value           
                 
        my_cookie = dict(name='sso_credentials',value=cookie_value,expires = -1)
        response = self.gk_service.validate_url_with_cookie(self.gk_service.create_requests_session_with_cookie(my_cookie))         
         
        assert response.status_code == requests.codes.ok           
        assert '<title>Gatekeeper / Arts Alliance Media</title>' in response.text  
      
    @attr(env=['test'],priority =1)
    def test_expired_server_cookie(self):
        '''   
        GATEKEEPER-API009 creates a session through a POST to the login API and then verifies that a user
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
        cookie_value  = cookie['sso_credentials'].value           
        
        #update cookie in the database so thats its expired
        assert(self.gk_dao.set_session_to_expire_by_session_id(self.db,cookie_value)) 
                        
        my_cookie = dict(name='sso_credentials',value=cookie_value)    
        response = self.gk_service.validate_url_with_cookie(self.gk_service.create_requests_session_with_cookie(my_cookie))    
        assert response.status_code == requests.codes.ok           
        assert '<title>Gatekeeper / Arts Alliance Media</title>' in response.text  
        
        #reopen another db connection 
        # TODO: investigate a cleaner solution than this
        self.db = BaseDAO(config['gatekeeper']['db']['connection'])        
        #User login causes expired coookie to be deleted
        response=self.gk_service.create_session_urlencoded(allow_redirects=False)
        
        #assert againist the database - ensure it no longer exists
        db_response = self.gk_dao.get_session_by_session_id(self.db,cookie_value)
        assert db_response== None
        
    @attr(env=['test'],priority =1)    
    def test_header_verification_urlencoded_session(self):
        '''   
        GATEKEEPER-API010 creates a session through a POST to the login API and then validates the 
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
    def test_can_delete_session_with_redirect(self):
        '''   
        GATEKEEPER-API011 Ensures a user session can be deleted using single logout(for a json created session)
        Specified redirect on logout
        '''        
        #urlencoded post
        #create a session - do not allow redirects       
        response=self.gk_service.create_session_urlencoded(allow_redirects=False,redirect_url=config['gatekeeper']['redirect'])
        #303 response
        assert response.status_code == requests.codes.other        
        #covert Set_Cookie response header to simple cookie object
        cookie = Cookie.SimpleCookie()
        cookie.load(response.headers['Set-Cookie'])
        cookie_value  = cookie['sso_credentials'].value                      
                 
        my_cookie = dict(name='sso_credentials',value=cookie_value)
        session = self.gk_service.create_requests_session_with_cookie(my_cookie)
        
        response = self.gk_service.validate_url_with_cookie(session,redirect_url=config['gatekeeper']['redirect'])        
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
        
    @attr(env=['test'],priority =1)
    def test_can_delete_session_default_redirect(self):
        '''   
        GATEKEEPER-API012 Ensures a user session can be deleted using single logout(for a json created session)
        Default redirect on logout
        '''        
        #urlencoded post
        #create a session - do not allow redirects       
        response=self.gk_service.create_session_urlencoded(allow_redirects=False)
        #303 response
        assert response.status_code == requests.codes.other        
        #covert Set_Cookie response header to simple cookie object
        cookie = Cookie.SimpleCookie()
        cookie.load(response.headers['Set-Cookie'])
        cookie_value  = cookie['sso_credentials'].value                      
                 
        my_cookie = dict(name='sso_credentials',value=cookie_value)
        session = self.gk_service.create_requests_session_with_cookie(my_cookie)
        
        response = self.gk_service.validate_url_with_cookie(session)        
        assert response.status_code == requests.codes.ok  
        
        
        response = self.gk_service.delete_user_session(session)
        assert response.status_code == requests.codes.ok  
               
        response = self.gk_service.validate_url_with_cookie(session)    
        assert response.status_code == requests.codes.ok           
        assert '<title>Gatekeeper / Arts Alliance Media</title>' in response.text
        
        #assert againist the database - ensure it no longer exists
        db_response =self.gk_dao.get_session_by_session_id(self.db,cookie_value)  
        assert db_response== None
        
    @attr(env=['test'],priority =2)
    def test_validate_user_api_and_authorization_app_only_permissions(self):
        '''   
        GATEKEEPER-API013 - test user api and permissions for user with only app access  
        Part a - Ensures user info can be return from the user api when a valid session,
        ,user id and application is provided for a user
        Part b  - Using the dummy application verify the end points the user can access
        when the user only has access to the dummy app
        
        '''        
        
        '''
        create a user and associate user with relevant pre confiured application for dummy app 
        '''
        username = 'automation_' + self.random_str(5)
        appname =  DEFAULT_TEST_APP
        fullname = 'automation ' + self.random_str(5)
        email    = self.random_str(5) + '@' + self.random_str(5) + '.com'
        
        #create basic user - no permisssions
        assert (self.gk_dao.set_gk_user(self.db, username, HASH_PASSWORD_TEST, email , fullname, '123-456-789123456'))
        
        #get user_id
        user_id = self.gk_dao.get_user_id_by_username(self.db, username)['user_id']
        
        #get app id                
        app_id = self.gk_dao.get_app_id_by_app_name(self.db,appname)['application_id']
                
        #associate user with app
        assert(self.gk_dao.set_user_app_id(self.db,app_id, user_id))
        
        
        '''
        create a session for the user
        '''
        credentials_payload = {'username': username , 'password': 'test'}  
        #create a session - do not allow redirects - urlencoded post        
        response=self.gk_service.create_session_urlencoded(allow_redirects=False,payload=credentials_payload)
        #303 response
        assert response.status_code == requests.codes.other      
        #covert Set_Cookie response header to simple cookie object
        cookie = Cookie.SimpleCookie()
        cookie.load(response.headers['Set-Cookie'])
        cookie_value  = cookie['sso_credentials'].value                    
        my_cookie = dict(name='sso_credentials',value=cookie_value)        
        session = self.gk_service.create_requests_session_with_cookie(my_cookie)
        
        
        '''
        Verify the user API
        '''
        
        response = self.gk_service.user_info(session,user_id,appname) 
        assert response.status_code == requests.codes.ok                        
                   
        assert username     in response.json()['username']
        assert []           == response.json()['organizations']
        assert str(user_id) in response.json()['user_id']  
        assert []           == response.json()['groups']       
        assert fullname     in response.json()['fullname']   
        assert email        in response.json()['email']
        assert []           == response.json()['permissions']

        '''
        Using the dummy application verify the permissions the user is authorized for
        '''
        #verify the dummy applcation can be accessed
        response = self.gk_service.validate_end_point(session)        
        assert response.status_code == requests.codes.ok  
        
        #verify the user end point cannot be accessed
        response = self.gk_service.validate_end_point(session,end_point=config['gatekeeper']['dummy']['user_endpoint'])        
        assert response.status_code == requests.codes.forbidden 
          
        #verify the admin end point cannot be accessed
        response = self.gk_service.validate_end_point(session,end_point=config['gatekeeper']['dummy']['admin_endpoint'])        
        assert response.status_code == requests.codes.forbidden 
        
        
        '''
        delete the user and application
        '''        
        #delete user - cascade delete by default
        assert (self.gk_dao.del_gk_user(self.db, user_id))        
        
    @attr(env=['test'],priority =1)
    def test_validate_user_api_and_authorization_user_permissions(self):
        '''   
        GATEKEEPER-API014 test user api and permissions for user with user_permission access  
        Part a - Using the dummy application verify the end points the user can access
        when the user has permissions configured for the with user permissions in the user_permissions table
        Part b  - Ensures user info can be return from the user api when a valid session,
        ,user id and application is provided for a user
        
        '''        
        
        '''
        create a user and associate user with relevant pre confiured application for dummy app 
        '''
        username = 'automation_' + self.random_str(5)
        appname =  DEFAULT_TEST_APP
        fullname = 'automation ' + self.random_str(5)
        email    = self.random_str(5) + '@' + self.random_str(5) + '.com'
        user_permission  =  self.gk_dao.get_permission_id_by_name(self.db,DEFAULT_ADFUSER_USER)['permission_id']
        admin_permission = self.gk_dao.get_permission_id_by_name(self.db,DEFAULT_ADFUSER_ADMIN)['permission_id']
        
        #create basic user - no permisssions
        assert (self.gk_dao.set_gk_user(self.db, username, HASH_PASSWORD_TEST, email , fullname, '123-456-789123456'))
        
        #get user_id
        user_id = self.gk_dao.get_user_id_by_username(self.db, username)['user_id']
        
        #get app id                
        app_id = self.gk_dao.get_app_id_by_app_name(self.db,appname)['application_id']
                
        #associate user with app
        assert(self.gk_dao.set_user_app_id(self.db,app_id, user_id))
        
              
        
        '''
        create a session for the user
        '''
        credentials_payload = {'username': username , 'password': 'test'}  
        #create a session - do not allow redirects - urlencoded post        
        response=self.gk_service.create_session_urlencoded(allow_redirects=False,payload=credentials_payload)
        #303 response
        assert response.status_code == requests.codes.other      
        #covert Set_Cookie response header to simple cookie object
        cookie = Cookie.SimpleCookie()
        cookie.load(response.headers['Set-Cookie'])
        cookie_value  = cookie['sso_credentials'].value                    
        my_cookie = dict(name='sso_credentials',value=cookie_value)        
        session = self.gk_service.create_requests_session_with_cookie(my_cookie)
        
        
        '''
        set the user permissions for the app i.e user can only access the dummy application and user end point
        '''        
        assert (self.gk_dao.set_user_permissions_id(self.db, user_id,user_permission))
        
        '''
        Using the dummy application verify the permissions the user is authorized
        '''
        #verify the dummy applcation can be accessed
        response = self.gk_service.validate_end_point(session)        
        assert response.status_code == requests.codes.ok  
        
        #verify the user end point can be accessed
        response = self.gk_service.validate_end_point(session,end_point=config['gatekeeper']['dummy']['user_endpoint'])        
        assert response.status_code == requests.codes.ok  
          
        #verify the admin end point cannot be accessed
        response = self.gk_service.validate_end_point(session,end_point=config['gatekeeper']['dummy']['admin_endpoint'])        
        assert response.status_code == requests.codes.forbidden 
        
        
        '''
        set the admin permissions for the app i.e user can  access admin end point
        '''        
        assert (self.gk_dao.set_user_permissions_id(self.db, user_id,admin_permission))
                
        '''
        Using the dummy application verify the permissions the user is authorized
        '''
        #verify the dummy applcation can be accessed
        response = self.gk_service.validate_end_point(session)        
        assert response.status_code == requests.codes.ok  
        
        #verify the user end point can be accessed
        response = self.gk_service.validate_end_point(session,end_point=config['gatekeeper']['dummy']['user_endpoint'])        
        assert response.status_code == requests.codes.ok  
          
        #verify the admin end point can be accessed
        response = self.gk_service.validate_end_point(session,end_point=config['gatekeeper']['dummy']['admin_endpoint'])        
        assert response.status_code == requests.codes.ok
                
        
        '''
        Verify the user API
        '''
        response = self.gk_service.user_info(session,user_id,appname) 
        assert response.status_code == requests.codes.ok                        
                   
        assert username             in response.json()['username']
        assert []                   == response.json()['organizations']
        assert str(user_id)         in response.json()['user_id']  
        assert []                   == response.json()['groups']       
        assert fullname             in response.json()['fullname']   
        assert email                in response.json()['email']
        assert DEFAULT_ADFUSER_ADMIN == response.json()['permissions'][0]
        assert DEFAULT_ADFUSER_USER  == response.json()['permissions'][1]
         
        '''
        delete the user
        '''        
        #delete user - cascade delete by default
        assert (self.gk_dao.del_gk_user(self.db, user_id))        
        
    
    
    @attr(env=['test'],priority =1)
    def test_validate_user_api_and_authorization_group_permissions(self):
        '''   
        GATEKEEPER-API015 - test user api and permissions for user with group_permission access
        Part a - Using the dummy application verify the end points the user can access
        when the user has permissions configured for the with user permissions in the group_permissions table
        Part b  - Ensures user info can be return from the user api when a valid session,
        ,user id and application is provided for a user
        
        '''        
        
        
        '''
        create a user and associate user with relevant pre confiured application for dummy app 
        '''
        username = 'automation_' + self.random_str(5)
        appname =  DEFAULT_TEST_APP
        fullname = 'automation ' + self.random_str(5)
        email    = self.random_str(5) + '@' + self.random_str(5) + '.com'
        user_permission  = self.gk_dao.get_permission_id_by_name(self.db,DEFAULT_ADFUSER_USER)['permission_id']
        admin_permission = self.gk_dao.get_permission_id_by_name(self.db,DEFAULT_ADFUSER_ADMIN)['permission_id']
        grp_name = 'automation_' + self.random_str(5)
        grp_name_2 = 'automation_' + self.random_str(5)
        
        #create basic user - no permisssions
        assert (self.gk_dao.set_gk_user(self.db, username, HASH_PASSWORD_TEST, email , fullname, '123-456-789123456'))
        
        #get user_id
        user_id = self.gk_dao.get_user_id_by_username(self.db, username)['user_id']
        
        #get app id                
        app_id = self.gk_dao.get_app_id_by_app_name(self.db,appname)['application_id']
        
        #associate user with app
        assert(self.gk_dao.set_user_app_id(self.db,app_id, user_id))
                
        #creat gatekeeper group  
        assert (self.gk_dao.set_gk_group(self.db,grp_name))
        #get group id
        group_id = self.gk_dao.get_gk_group_id_by_name(self.db, grp_name)['group_id']
        
        #associate user with group
        assert(self.gk_dao.set_user_group(self.db,user_id, group_id))        
                
        #associate group with application
        assert(self.gk_dao.set_group_app_id(self.db, app_id, group_id))
        
        
        '''
        create a session for the user
        '''
        credentials_payload = {'username': username , 'password': 'test'}  
        #create a session - do not allow redirects - urlencoded post        
        response=self.gk_service.create_session_urlencoded(allow_redirects=False,payload=credentials_payload)
        #303 response
        assert response.status_code == requests.codes.other      
        #covert Set_Cookie response header to simple cookie object
        cookie = Cookie.SimpleCookie()
        cookie.load(response.headers['Set-Cookie'])
        cookie_value  = cookie['sso_credentials'].value                    
        my_cookie = dict(name='sso_credentials',value=cookie_value)        
        session = self.gk_service.create_requests_session_with_cookie(my_cookie)
        
              
        '''
        set the group permissions for the app i.e user can only access the dummy application and user end point
        '''      
                
        #set group permission for user access
        assert(self.gk_dao.set_group_permission(self.db, group_id, user_permission))                
        
        
        '''
        Using the dummy application verify the permissions the user is authorized
        '''
        #verify the dummy applcation can be accessed
        response = self.gk_service.validate_end_point(session)        
        assert response.status_code == requests.codes.ok  
        
        #verify the user end point can be accessed
        response = self.gk_service.validate_end_point(session,end_point=config['gatekeeper']['dummy']['user_endpoint'])        
        assert response.status_code == requests.codes.ok  
          
        #verify the admin end point cannot be accessed
        response = self.gk_service.validate_end_point(session,end_point=config['gatekeeper']['dummy']['admin_endpoint'])        
        assert response.status_code == requests.codes.forbidden 
        
        
        '''
        set the group permissions for the app i.e user can access the admin endpoint
        '''      
        #set group permission for admin access
        assert(self.gk_dao.set_group_permission(self.db, group_id, admin_permission))                
        
        
        '''
        Using the dummy application verify the permissions the user is authorized
        '''
        #verify the dummy applcation can be accessed
        response = self.gk_service.validate_end_point(session)        
        assert response.status_code == requests.codes.ok  
        
        #verify the user end point can be accessed
        response = self.gk_service.validate_end_point(session,end_point=config['gatekeeper']['dummy']['user_endpoint'])        
        assert response.status_code == requests.codes.ok  
          
        #verify the admin end point cannot be accessed
        response = self.gk_service.validate_end_point(session,end_point=config['gatekeeper']['dummy']['admin_endpoint'])        
        assert response.status_code == requests.codes.ok
        
        '''
        Verify the user API                                    
        '''
        response = self.gk_service.user_info(session,user_id,appname) 
        assert response.status_code == requests.codes.ok        
                   
        assert username             in response.json()['username']
        assert []                   == response.json()['organizations']
        assert str(user_id)         in response.json()['user_id']  
        assert grp_name             in response.json()['groups'] [0]      
        assert fullname             in response.json()['fullname']   
        assert email                in response.json()['email']
        assert DEFAULT_ADFUSER_ADMIN == response.json()['permissions'][0]
        assert DEFAULT_ADFUSER_USER  == response.json()['permissions'][1]
         
         
        '''
        create another group, associate with the user but not the application
        this group should NOT be retured by the API
        '''
        #create gatekeeper group  
        assert (self.gk_dao.set_gk_group(self.db,grp_name_2))
        #get group id
        group_id_2 = self.gk_dao.get_gk_group_id_by_name(self.db, grp_name_2)['group_id']
        
        #associate user with group
        assert(self.gk_dao.set_user_group(self.db,user_id, group_id_2))    
        
        #user API response
        response = self.gk_service.user_info(session,user_id,appname) 
        assert response.status_code == requests.codes.ok
                         
        assert 1 == len(response.json()['groups'])
        #ensure that only 1 group is associate with the application/user
        
         
        '''
        delete the group and user
        '''     
        
        #delete the group
        assert (self.gk_dao.del_gk_group(self.db, group_id))
           
        #delete user - cascade delete by default
        assert (self.gk_dao.del_gk_user(self.db, user_id))        
        
        
                     
    @attr(env=['test'],priority =1)
    def test_user_info_with_invalid_cookie_session(self):
        '''   
        GATEKEEPER-API016 Ensures user info CANNOT be return from the user api when a invalid session,
        is provided
        '''        
        #urlencoded post
        #create a session - do not allow redirects       
        response=self.gk_service.create_session_urlencoded(allow_redirects=False,redirect_url=config['gatekeeper']['redirect'])
        #303 response
        assert response.status_code == requests.codes.other        
        #covert Set_Cookie response header to simple cookie object
        cookie = Cookie.SimpleCookie()
        cookie.load(response.headers['Set-Cookie'])
        cookie_value  =  "fakecookie"                 
                 
        my_cookie = dict(name='sso_credentials',value=cookie_value)
        session = self.gk_service.create_requests_session_with_cookie(my_cookie)
        response = self.gk_service.user_info(session,self.DEFAULT_TEST_USER,DEFAULT_TEST_APP)
        #ensure that the request is forbidden(403) without a valid session cookie 
        assert response.status_code == requests.codes.forbidden          
        assert "User is either not logged in or not the same user as the user described in the resource URI" in response.json()['error']
        
    @attr(env=['test'],priority =1)
    def test_return_user_info_with_invalid_application(self):
        '''   
        GATEKEEPER-API017 Ensures user info CANNOT be return from the user api when a invalid 
        application is provided
        '''        
        #urlencoded post
        #create a session - do not allow redirects       
        response=self.gk_service.create_session_urlencoded(allow_redirects=False,redirect_url=config['gatekeeper']['redirect'])
        #303 response
        assert response.status_code == requests.codes.other        
        #covert Set_Cookie response header to simple cookie object
        cookie = Cookie.SimpleCookie()
        cookie.load(response.headers['Set-Cookie'])
        cookie_value  = cookie['sso_credentials'].value                     
        my_cookie = dict(name='sso_credentials',value=cookie_value)
        session = self.gk_service.create_requests_session_with_cookie(my_cookie)
        fake_application ="fake"
        response = self.gk_service.user_info(session,self.DEFAULT_TEST_USER,fake_application) 
        #ensure it returns a 404 not found
        assert response.status_code == requests.codes.not_found 
                      
        assert "No user with id" in response.json()['error']
        assert "found for application" in response.json()['error']
    
    @attr(env=['test'],priority =1)
    def test_return_user_info_with_invalid_user_id(self):
        '''   
        GATEKEEPER-API018 Ensures user info CANNOT be return from the user api when a invalid 
        user id is provided
        '''        
        #urlencoded post
        #create a session - do not allow redirects       
        response=self.gk_service.create_session_urlencoded(allow_redirects=False,redirect_url=config['gatekeeper']['redirect'])
        #303 response
        assert response.status_code == requests.codes.other        
        #covert Set_Cookie response header to simple cookie object
        cookie = Cookie.SimpleCookie()
        cookie.load(response.headers['Set-Cookie'])
        cookie_value  = cookie['sso_credentials'].value                    
        my_cookie = dict(name='sso_credentials',value=cookie_value)
        session = self.gk_service.create_requests_session_with_cookie(my_cookie)
        
        # TODO: when db function to return user id is created, simply increment it
        random_user_id = 1111
        response = self.gk_service.user_info(session,random_user_id,DEFAULT_TEST_APP)        
        #ensure that the request is forbidden(403) without a valid session cookie 
        assert response.status_code == requests.codes.forbidden         
        assert "User is either not logged in or not the same user as the user described in the resource URI" in response.json()['error']
    
   
    def random_str(self,n):
        return "".join(random.choice(string.ascii_lowercase) for x in xrange(n))