"""
@summary: Contains a set of test functions
for the gate keeper(single sign on) project

@since: Created on October 31st 2013

@author: Conor Fitzgerald

"""

import requests
from testconfig import config
from framework.utility.utility import Utility
import Cookie
import time


class GateKeeperService(object):

    def _create_url(self,
                    path,
                    host=config['gatekeeper']['host'],
                    port=config['gatekeeper']['port']):
        return '{0}://{1}:{2}/{3}'.format(
            config['gatekeeper']['scheme'], host, port, path)

    def create_session_urlencoded(self, url=None, payload=None, verify=None,
                                  allow_redirects=None, redirect_url=None,
                                  credentials=None):
        """
        creates a session through the login API
        @param url: Optional. request url of API
        @param payload: Optional. The credentials of the user
        @param redirect_url: Url to redirect
        @param verify: boolean to determine if SSL cert will be verified
        @param allow_redirects: boolean determines if SSL cert will be verified

        @return: a request object

        """
        if url is None:
            url = self._create_url(
                config['api']['user']['session']['create_v1'])

        # requests is url-encoded by default
        if credentials is None:
            credentials = config['gatekeeper']['credentials']

        if redirect_url is not None:
            url = url + redirect_url

        # if(redirect_url == None):
        #    payload = payload.update(config['gatekeeper']['redirect'])

        # requests is url-encoded by default
        if verify is None:
            verify = False

        if allow_redirects is None:
            allow_redirects = True
        # url encoded
        response = requests.post(
            url=url,
            data=credentials,
            verify=verify,
            allow_redirects=allow_redirects
        )
        return response

    def validate_session(self, cookie_id, session, url=None, application=None):

        """
        validates a session_id

        @param session_id: which is the cookie value

        @param url: Optional. request url of API

        @return: a request object

        """
        url = self._create_url(
            config['api']['user']['session']['validate_v1'])

        request_url = url + '/%s'
        request_url = request_url % (cookie_id)

        if (application is not None):
            request_url = request_url + '/?application_name=%s'
            request_url = request_url % (application)
        response = session.get(request_url, verify=False)
        return response

    def create_requests_session_with_cookie(self, cookie):

        """
        creates a requests session object and set an associated cookie value

        @param cookie: cookie dict

        @return: a request session object

        """

        session = requests.session()
        session.cookies.set(**cookie)
        return session

    def validate_url_with_cookie(
            self,
            session,
            url=None,
            redirect_url=None,
            verify=None,
            allow_redirects=None,
            parameters=None
            ):

        """
        Validates whether a particular user with session and associated cookie
        can access a resource/url

        @param session:  session object and associated cookie

        @param url: Optional. request url of API
        @param redirect_url: Url to redirect
        @param verify: boolean to determine if SSL cert will be verified
        @param allow_redirects:boolean determines if SSL cert will be verified
        @return: a request session object

        """

        if parameters is None:
            parameters = {}
        if(url is None):
            url = self._create_url(
                config['api']['user']['session']['create_v1'])
        if(redirect_url is not None):
            url = url + redirect_url
        if(verify is None):
            verify = False
        if(allow_redirects is None):
            allow_redirects = True
        response = session.get(
            url=url,
            verify=verify,
            allow_redirects=allow_redirects,
            params=parameters
        )
        return response

    def logout_user_session(self, session, url=None):

        """
        single sign out, deletes user session using post

        @param session:  session object and associated cookie

        @param url: Optional. request url of API

        @return: a request session object

        """

        if(url is None):
            url = self._create_url(
                config['api']['user']['session']['logout_v1'])
        response = session.post(url, verify=False)
        return response

    def logout_user_session_get(self, session, url=None):

        """
        single sign out, deletes user session using get

        @param session:  session object and associated cookie

        @param url: Optional. request url of API

        @return: a request session object

        """

        if(url is None):
            url = self._create_url(
                config['api']['user']['session']['logout_v1'])
        response = session.get(url, verify=False)
        return response

    def user_info(self, session, user_id, application, url=None, verify=None):

        """
        Returns user info for a valid user id and session cookie

        @param session:  session object and associated cookie

        @param url: Optional. request url of API
        @param user_id: user id we are querying
        @param application: application that we will filter on
        @param verify: boolean to determine if SSL cert will be verified
        @param allow_redirects:  boolean to determine if redirects are allowed
        @return: a request session object containg the user info

        """

        if(url is None):
            url = self._create_url(
                config['api']['user']['session']['user_info_v1'])
        request_url = url % (user_id, application)
        if(verify is None):
            verify = False

        response = session.get(url=request_url, verify=verify)
        return response

    def validate_end_point(
            self,
            session,
            end_point=None,
            url=None,
            verify=None,
            parameters=None,
            allow_redirects=None
            ):

        """
        Returns user info for a valid user id and session cookie on dummyapp

        @param session:  session object and associated cookie

        @param url: Optional. request url of API
        @param user_id: user id we are querying
        @param application: application that we will filter on
        @param verify: boolean to determine if SSL cert will be verified
        @param allow_redirects: boolean to determine if redirects are allowed
        @return: a request session object containg the user info

        """
        if parameters is None:
            parameters = {}

        if(url is None):
            url = self._create_url('',
                                   host=config['gatekeeper']['dummy']['host'],
                                   port=config['gatekeeper']['dummy']['port'])
        if(end_point is not None):
            url = url + end_point

        if(verify is None):
            verify = False

        if allow_redirects is None:
            allow_redirects = True
        response = session.get(
            url=url,
            verify=verify,
            params=parameters,
            allow_redirects=allow_redirects
        )
        return response

    def submit_verification_code(
            self,
            session,
            payload,
            url=None,
            verify=None,
            allow_redirects=None,
            redirect_url=None
            ):

        """
        submits the verification_code for two factor authentication

        @param session: a python-requests session object
        @param url: Optional. request url of API
        @param payload: Optional. The credentials of the user
        @param verify: boolean to determine if SSL cert will be verified
        @param redirect_url: Url to redirect
        @param allow_redirects:boolean determine if SSL cert will be verified
        @return: a request object

        """
        if(url is None):
            url = self._create_url(
                config['api']['user']['session']['submit_verification_v1'])
        if(redirect_url is not None):
            url = url + redirect_url

        # requests is url-encoded by default
        if(verify is None):
            verify = False

        if(allow_redirects is None):
            allow_redirects = True

        # url encoded
        response = session.post(
            url=url,
            data=payload,
            verify=verify,
            allow_redirects=allow_redirects
        )

        return response

    def application(
        self,
        session,
        method,
        app_id=None,
        app_data=None,
        verify=None
    ):
        """
        Application API for CRUD operations

        @param session:  session object and associated cookie
        @param: method i.e GET,POST,PUT or DELETE
        @param app_id: application id
        @param app_data: data for PUT and DELETE
        @param verify: boolean to determine if SSL cert will be verified
        @param allow_redirects:  boolean to determine if redirects are allowed
        @return: a request session object containing the user info

        """

        url = self._create_url(config['api']['user']['application_v1']['post'])

        if(app_id is not None):

            request_url = self._create_url(
                config['api']['user']['application_v1']['id']
            )
            request_url = request_url % (app_id)

        if((method == 'POST' or method == 'PUT') and app_data is None):
            app_data = self.create_app_data()

        if(verify is None):
            verify = False

        if method == 'GET':
            response = session.get(url=request_url, verify=verify)
        if method == 'POST':
            response = session.post(url=url, data=app_data, verify=verify)
        if method == 'PUT':
            response = session.put(
                url=request_url, data=app_data, verify=verify
                )
        if method == 'DELETE':
            response = session.delete(url=request_url, verify=verify)

        return response

    def user(
        self,
        session,
        method,
        user_id=None,
        user_data=None,
        verify=None
    ):
        """
        User API for CRUD operations
        @param session:  session object and associated cookie
        @param: method: i.e GET,POST,PUT or DELETE
        @param user_id: user id
        @param user_data: data for PUT and DELETE
        @param verify: boolean to determine if SSL cert will be verified
        @param allow_redirects:  boolean to determine if redirects are allowed
        @return: a request session object containing the user info

        """

        url = self._create_url(config['api']['user']['user_v1']['post'])

        if(user_id is not None):
            request_url = self._create_url(
                config['api']['user']['user_v1']['id']
            )
            request_url = request_url % (user_id)

        if((method == 'POST' or method == 'PUT') and user_data is None):
            user_data = self.create_user_data()

        if(verify is None):
            verify = False

        if method == 'GET':
            response = session.get(url=request_url, verify=verify)
        if method == 'POST':
            response = session.post(url=url, data=user_data, verify=verify)
        if method == 'PUT':
            response = session.put(
                url=request_url, data=user_data, verify=verify
                )
        if method == 'DELETE':
            response = session.delete(url=request_url, verify=verify)

        return response

    def create_user_data(self, user_dict=None):

        """
        Creation of a user dict
        @param user_dict: optional dict - can be merged with a default dict
        @return: a user data dict

        """

        self.util = Utility()
        rand_str = self.util.random_str(5)
        phone = self.util.phone_number()
        email = self.util.random_email()
        user_data = {
            'username': rand_str,
            'name': rand_str,
            'phone': phone,
            'email': email,
            'password': rand_str
        }

        if user_dict is not None:
            user_data.update(user_dict)

        return user_data

    def create_app_data(self, app_dict=None):

        """
        Creation of a user dict
        @param user_dict: optional dict - can be merged with a default dict
        @return: a user data dict

        """
        self.util = Utility()
        new_app = self.util.random_str(5)
        new_url = self.util.random_url(5)
        app_data = {'name': new_app, 'default_url': new_url}

        if app_dict is not None:
            app_data.update(app_dict)

        return app_data

    def extract_sso_cookie_value(self, headers):
        """
        Extract data from cookie
        @return: cookie value
        """

        cookie = Cookie.SimpleCookie()
        cookie.load(headers['Set-Cookie'])
        cookie_id = cookie['sso_cookie'].value
        return cookie_id

    def extract_cred_cookie_value(self, headers):
        """
        Extract data from cookie
        @return: cookie value
        """

        cookie = Cookie.SimpleCookie()
        cookie.load(headers['Set-Cookie'])
        cookie_id = cookie['sso_credentials'].value
        return cookie_id

    def run_user_test(self, cookie, iterations=10, wait_time=0.1):
        """
        Accesses the dummyapp page with a valid cookie n number of times
        @param cookie: cookie from logged in user
        @param iterations: cookie from logged in user
        @param cookie: cookie from logged in user
        @return: asserts true/false

        """
        url = self._create_url(
            '',
            host=config['gatekeeper']['dummy']['host'],
            port=config['gatekeeper']['dummy']['port']
        )
        session = requests.session()
        session.cookies['sso_cookie'] = cookie
        for index in range(iterations):
            response = session.get(url, verify=False)
            assert response.status_code == requests.codes.ok
            time.sleep(wait_time)
