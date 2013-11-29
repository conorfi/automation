'''
@summary: Contains a set of test functions for the gate keeper(single sign on) project

@since: Created on October 31st 2013

@author: Conor Fitzgerald

'''

import requests
from testconfig import config


class GateKeeperService(object):

    def _create_url(self,
                    path,
                    host=config['gatekeeper']['host'],
                    port=config['gatekeeper']['port']):
        return '{0}://{1}:{2}/{3}'.format(
            config['gatekeeper']['scheme'], host, port, path)

    def create_session_urlencoded(self, url=None, payload=None, verify=None,
                                  allow_redirects=None, redirect_url=None):
        """
        creates a session through the login API

        @param url: Optional. request url of API

        @param payload: Optional. The credentials of the user

        @return: a request object

        """
        if url is None:
            url = self._create_url(
                config['api']['user']['session']['create_v1'])

        #requests is url-encoded by default
        if payload is None:
            payload = config['gatekeeper']['credentials']

        if redirect_url is not None:
            url = url + redirect_url

        #if(redirect_url == None):
        #    payload = payload.update(config['gatekeeper']['redirect'])

        #requests is url-encoded by default
        if verify is None:
            verify = False

        if allow_redirects is None:
            allow_redirects = True
        #url encoded
        r = requests.post(url=url, data=payload, verify=verify,
                          allow_redirects=allow_redirects)
        return r



    def validate_session(self,cookie_id,session,url=None,application=None):

        '''
        validates a session_id

        @param session_id: which is the cookie value

        @param url: Optional. request url of API

        @return: a request object

        '''
        url = self._create_url(
            config['api']['user']['session']['validate_v1'])

        request_url = url + '/%s'
        request_url = request_url % (cookie_id)

        if (application != None):
            request_url = request_url + '/?application_name=%s'
            request_url = request_url %  (application)
        response = session.get(request_url,verify=False)
        return response

    def create_requests_session_with_cookie(self,cookie):

        '''
        creates a requests session object and set an associated cookie value

        @param cookie: cookie dict

        @return: a request session object

        '''

        session = requests.session()
        session.cookies.set(**cookie)
        return session

    def validate_url_with_cookie(self,session,url=None,redirect_url=None,verify=None,allow_redirects=None):

        '''
        Validates whether a particular user with session and associated cookie
        can access a resource/url

        @param session:  session object and associated cookie

        @param url: Optional. request url of API
        @param redirect_url: Url to redirect
        @param verify: Verify.  boolean to determine if SSL cert will be verified
        @param allow_redirects.: allow_redirects.  boolean to determine if SSL cert will be verified
        @return: a request session object

        '''

        if(url==None):
            url = self._create_url(
                config['api']['user']['session']['create_v1'])
        if(redirect_url != None):
            url = url + redirect_url
        if(verify==None):
            verify=False
        if(allow_redirects==None):
            allow_redirects=True
        response = session.get(url=url, verify=verify,allow_redirects=allow_redirects)
        return response

    def logout_user_session(self,session,url=None):

        '''
        single sign out, deletes user session

        @param session:  session object and associated cookie

        @param url: Optional. request url of API

        @return: a request session object

        '''

        if(url==None):
            url = self._create_url(
                config['api']['user']['session']['logout_v1'])
        response = session.post(url,verify=False)
        return response

    def user_info(self,session,user_id,application,url=None,verify=None):

        '''
        Returns user info for a valid user id and session cookie

        @param session:  session object and associated cookie

        @param url: Optional. request url of API
        @param user_id: user id we are querying
        @param application: application that we will filter on
        @param verify: Verify.  boolean to determine if SSL cert will be verified
        @param allow_redirects:  boolean to determine if redirects are allowed
        @return: a request session object containg the user info

        '''

        if(url==None):
            url = self._create_url(
                config['api']['user']['session']['user_info_v1'])
        request_url = url + '/%s/?application_name=%s'
        request_url = request_url % (user_id,application)
        if(verify==None):
            verify=False
        response = session.get(url=request_url, verify=verify)
        return response


    def validate_end_point(self,session,end_point=None,url=None,verify=None):

        '''
        Returns user info for a valid user id and session cookie on dummyapp

        @param session:  session object and associated cookie

        @param url: Optional. request url of API
        @param user_id: user id we are querying
        @param application: application that we will filter on
        @param verify: Verify.  boolean to determine if SSL cert will be verified
        @param allow_redirects:  boolean to determine if redirects are allowed
        @return: a request session object containg the user info

        '''

        if(url==None):
            url = self._create_url('',
                                   host=config['gatekeeper']['dummy']['host'],
                                   port=config['gatekeeper']['dummy']['port'])
        if(end_point!=None):
            url = url + end_point
        if(verify==None):
            verify=False
        response = session.get(url=url, verify=verify)
        return response
