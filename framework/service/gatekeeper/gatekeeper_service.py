'''
@summary: Contains a set of test functions for the gate keeper(single sign on) project

@since: Created on October 31st 2013

@author: Conor Fitzgerald

'''

import json
import requests
from testconfig import config

class GateKeeperService(object):
       
                        
    def create_session_urlencoded(self,url=None,payload=None):
        '''    
        creates a session through the login API
    
        @param url: Optional. request url of API
    
        @param payload: Optional. The credentials of the user
    
        @return: a request object
        
        '''    
        if(url==None):
            url = 'https://{0}:{1}/{2}'.format(config['gatekeeper']['host'],config['gatekeeper']['port']
                                           ,config['api']['user']['session']['create_v1'])
        #requests is url-encoded by default
        if(payload==None):
            payload = config['gatekeeper']['credentials']  
        #url encoded
        r = requests.post(url, data=payload,verify=False)        
        return r
    
    def create_session_json(self,url=None,payload=None):
        '''    
        creates a session through the login API
    
        @param url: Optional. request url of API
    
        @param payload: Optional. The credentials of the user
    
        @return: a request object
        
        '''    
        if(url==None):
            url = 'https://{0}:{1}/{2}'.format(config['gatekeeper']['host'],config['gatekeeper']['port']
                                           ,config['api']['user']['session']['create_v1'])
        #requests is url-encoded by default
        if(payload==None):
            payload = config['gatekeeper']['credentials']  
        #json encoded     
        r = requests.post(url, data=json.dumps(payload),verify=False)                
        return r
    
    
    def validate_session(self,session_id,url=None):
        
        '''    
        validates a session_id
    
        @param session_id: which is the cookie value
    
        @param url: Optional. request url of API
    
        @return: a request object
        
        '''                      
            
        url = 'https://{0}:{1}/{2}'.format(config['gatekeeper']['host'],config['gatekeeper']['port']
                                               ,config['api']['user']['session']['validate_v1'])
        
        request_url = url + '/%s'               
        request_url = request_url % (session_id)
        r = requests.get(request_url,verify=False)
        return r      

    def create_requests_session_with_cookie(self,cookie): 
        
        '''    
        creates a requests session object and set an associated cookie value
    
        @param cookie: cookie dict   
       
        @return: a request session object
        
        '''         
        session = requests.session() 
        session.cookies.set(**cookie)
        return session
    
    def validate_url_with_cookie(self,session,url=None):
        
        '''    
        Validates whether a particular with session and associated cookie
        can access a resource/url
    
        @param session:  session object and associated cookie
         
        @param url: Optional. request url of API
       
        @return: a request session object
        
        '''      
         
        if(url==None): 
            url = 'https://{0}:{1}/home'.format(config['gatekeeper']['host'],config['gatekeeper']['port'])     
        response = session.get(url,verify=False)         
        return response 
    
    def delete_user_session(self,session,url=None):
        
        '''    
        single sign out, deletes user session
    
        @param session:  session object and associated cookie
         
        @param url: Optional. request url of API
       
        @return: a request session object
        
        '''      
         
        if(url==None): 
            url = 'https://{0}:{1}/{2}'.format(config['gatekeeper']['host'],config['gatekeeper']['port'],config['api']['user']['session']['delete_v1'])     
        response = session.post(url,verify=False)         
        return response 