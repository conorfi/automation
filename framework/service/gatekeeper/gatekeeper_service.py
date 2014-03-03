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
import json

from framework.common_env import SERVICE_NAME_GATEKEEPER as SERVICE_NAME


class GateKeeperService(object):
    def __init__(self):

        # initialize utility class
        self.util = Utility()
        # adfuser is the default test dummy application
        self.DEFAULT_TEST_APP = "adfuser"
        # another test dummy app
        self.ANOTHER_TEST_APP = "anotherapp"
        # gatekeeper app
        self.GK_APP = "gatekeeper"
        # admin user is 'admin' and is used as the default user
        self.ADMIN_USER = 'admin'
        # default user permission configured for adfuser in the dummy app
        self.DEFAULT_ADFUSER_USER = 'ADFUSER_USER'
        self.DEFAULT_ADFUSER_ADMIN = 'ADFUSER_ADMIN'
        # special permission that allows acess to the gk admin end point
        self.GK_ALL_PERMISSION = "gatekeeper_all"
        self.MAX_ATTEMPT_LOGIN = 5
        self.THREE_ATTEMPTS_LOGIN = 3

        self.ORG_AAM = "Arts Alliance Media"

        # hash of the password test - using this rather than implementing the
        # gatekeeper hashing function if the hashing function ever change sit
        # will break a number of these functions
        self.HASH_PASSWORD_TEST = "pbkdf2_sha256$12000$m5uwpzIW9qaO$88p" \
                                  "IM25AqnXu4Fgt/Xgtpp3AInYgk5sxaxJmxxpcR8A="

        self.GATEKEEPER_TITLE = "<title>Gatekeeper /" \
                                " Arts Alliance Media</title>"

        # Error messages
        self.USER_ERROR = (
            "User is either not logged in or not the same"
            " user as the user described in the resource URI"
        )
        self.SESSION_FORBIDDEN = "Forbidden session with cookie %s" \
                                 " for application fake"
        self.SESSION_NOT_ALLOWED = 'User not allowed access this session!'
        self.MISSING_PARAMETERS = "Missing parameters: "
        self.MISSING_APP_NAME = "Missing parameters: application_name"
        self.MISSING_APP_ID = "Missing parameters: user_id"
        self.CONFIRM_LOGOUT = "Please confirm logout"
        self.NO_DATA_ERROR = "No data for ID"
        self.DUPLICATE_KEY = "duplicate key value violates unique constraint"
        self.MISSING_PARAM = "Missing parameter(s)"
        self.NOT_LOGGED_IN = "Not logged in"
        self.INVALID_VERIFCATION_CODE = "Verification+code+not+valid"
        self.INVALID_USERNAME_PASSWORD = "Username+or+password+not+valid"
        self.INVALID_USERNAME_PASSWORD_HTML = "Username or password not valid"
        self.FK_ERROR = "violates foreign key constraint"
        self.PARAM_NOT_ALLOWED = "not allowed"
        self.NO_PARAM_SUPPLIED = "No parameter(s) supplied."
        self.METHOD_NOT_AVAILABLE = "not currently available"
        self.USERNAME_VALIDATION = "Alphanumeric characters required with a" \
                                   " minimum length of 4 and maximum length " \
                                   "of 64"
        self.NAME_VALIDATION = "Word characters required with a" \
                               " minimum length of 1 and maximum length of 100"
        self.PASSWORD_VALIDATION = "Alphanumeric characters required with" \
                                   " a minimum length of 8 and maximum length" \
                                   " " \
                                   "of 100"
        self.PHONE_VALIDATION = "E.164 formatted number required" \
                                " e.g. +44 20 7751 7500"
        self.EMAIL_VALIDATION = "Valid email format required, maximum" \
                                " 254 characters in length e.g. test@test.com"
        self.EMAIL_VALIDATION_HTML = "Valid+email+format+required%2C" \
                                     "+maximum+254+characters+in+length+e.g" \
                                     ".+test%40test.com"
        self.DEFAULT_URL_VALIDATION = "A valid http/https" \
                                      " URL e.g. http://localhost/test"
        self.PERM_NAME_VALIDATION = "Alphanumeric characters required with" \
                                    " a minimum length of 1 and maximum " \
                                    "length of 512"
        self.APP_ID_VALIDATION = "Valid application ID required"
        self.PARAM_NOT_ALLOWED = "not allowed"
        self.DELETE_THEMSELVES = "Users are not allowed to delete themselves."
        self.DELETE_DATA = "Cannot delete data"
        self.NOT_PRESENT = "is not present"
        self.LOGIN_ATTEMPTS = "Username or password not valid." \
                              " Attempts left: %d"
        self.LOGIN_ATTEMPTS_EXCEEDED = "Exceeded maximum login attempts." \
                                       " Please reset your password or " \
                                       "contact the site administrator."
        self.RECOVER_RESPONSE = "you should now have received the email with"
        self.UNEXPECTED_PARAM = "Unexpected body parameters"

    def _create_url(self,
                    path,
                    host=config[SERVICE_NAME]['host'],
                    port=config[SERVICE_NAME]['port']):
        if config[SERVICE_NAME]['port'] is None:
            return '{0}://{1}/{2}'.format(
                config[SERVICE_NAME]['scheme'], host, path)
        else:
            return '{0}://{1}:{2}/{3}'.format(
                config[SERVICE_NAME]['scheme'], host, port, path)

    def create_session_urlencoded(
        self,
        url=None,
        verify=None,
        allow_redirects=None,
        redirect_url=None,
        credentials=None,
        type='urlencoded',
        headers=None
    ):
        """
        creates a session through the login API
        @param url: Optional. request url of API
        @param redirect_url: Url to redirect
        @param verify: boolean to determine if SSL cert will be verified
        @param allow_redirects: boolean determines if SSL cert will be verified
        @param credentials: username and password
        @param type: json or urlencoded
        @return: a request object

        """
        if url is None:
            url = self._create_url(
                config['api'][SERVICE_NAME]['session']['create_v1'])

        # requests is url-encoded by default
        if credentials is None:
            credentials = config[SERVICE_NAME]['credentials']

        if redirect_url is not None:
            url = url + redirect_url

        # requests is url-encoded by default
        if verify is None:
            verify = False

        if allow_redirects is None:
            allow_redirects = True

        if type == 'json':
            headers = {}
            credentials = json.dumps(credentials)
            headers['Content-Type'] = 'application/json'

        # url encoded
        response = requests.post(
            url=url,
            data=credentials,
            verify=verify,
            allow_redirects=allow_redirects,
            headers=headers
        )
        return response

    def user_session(self, cookie_id, session, url=None, application=None):

        """
        validates a session_id
        @param session: which is the cookie value
        @param url: Optional. request url of API
        @param  application: app to use
        @return: a request object

        """

        if url is None:
            url = self._create_url(
                config['api'][SERVICE_NAME]['session']['validate_v1'])

        request_url = url + '/%s'
        request_url = request_url % cookie_id

        if application is not None:
            request_url += '/?application_name=%s'
            request_url = request_url % application
        response = session.get(request_url, verify=False)
        return response

    @staticmethod
    def create_requests_session_with_cookie(cookie):

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
        if url is None:
            url = self._create_url(
                config['api'][SERVICE_NAME]['session']['create_v1'])
        if redirect_url is not None:
            url = url + redirect_url
        if verify is None:
            verify = False
        if allow_redirects is None:
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

        if url is None:
            url = self._create_url(
                config['api'][SERVICE_NAME]['session']['logout_v1'])
        response = session.post(url, verify=False)
        return response

    def logout_user_session_get(self, session, url=None):

        """
        single sign out, deletes user session using get

        @param session:  session object and associated cookie

        @param url: Optional. request url of API

        @return: a request session object

        """

        if url is None:
            url = self._create_url(
                config['api'][SERVICE_NAME]['session']['logout_v1'])
        response = session.get(url, verify=False)
        return response

    def user_app(self, session, user_id, application, url=None, verify=None):

        """
        Returns user info for a valid user id,application and session cookie

        @param session:  session object and associated cookie

        @param url: Optional. request url of API
        @param user_id: user id we are querying
        @param application: application that we will filter on
        @param verify: boolean to determine if SSL cert will be verified
        @return: a request session object containing the user info

        """

        if url is None:
            url = self._create_url(
                config['api'][SERVICE_NAME]['session']['user_info_v1'])
        request_url = url % (user_id, application)
        if verify is None:
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
        Returns user info for a valid user id and session cookie on dummy app

        @param session:  session object and associated cookie

        @param url: Optional. request url of API
        @param session: session
        @param end_point: end point to be tested
        @param verify: boolean to determine if SSL cert will be verified
        @param allow_redirects: boolean to determine if redirects are allowed
        @return: a request session object containing the user info

        """
        if parameters is None:
            parameters = {}

        if url is None:
            url = self._create_url('',
                                   host=config[SERVICE_NAME]['dummy']['host'],
                                   port=config[SERVICE_NAME]['dummy']['port'])
        if end_point is not None:
            url = url + end_point

        if verify is None:
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
        if url is None:
            url = self._create_url(
                config['api'][SERVICE_NAME]['session'][
                    'submit_verification_v1'])
        if redirect_url is not None:
            url = url + redirect_url

        # requests is url-encoded by default
        if verify is None:
            verify = False

        if allow_redirects is None:
            allow_redirects = True

        # url encoded
        response = session.post(
            url=url,
            data=payload,
            verify=verify,
            allow_redirects=allow_redirects
        )

        return response

    def create_user_data(self, user_dict=None):

        """
        Creation of a user dict
        @param user_dict: optional dict - can be merged with a default dict
        @return: a user data dict

        """
        # create user data
        # strings set to minimum length
        # except name which is set to 4 rather than 1-for quality of test data
        # phone and email set to correct format
        user_data = {
            'username': self.util.random_str(4),
            'name': self.util.random_str(4),
            'phone': self.util.phone_number(),
            'email': self.util.random_email(),
            'password': self.util.random_str(8)
        }
        if user_dict is not None:
            user_data.update(user_dict)

        return user_data

    def create_app_data(self, app_dict=None):

        """
        Creation of a user dict
        @param app_dict: optional dict - can be merged with a default dict
        @return: a user data dict

        """
        new_app = self.util.random_str(5)
        new_url = self.util.random_url(5)
        app_data = {'name': new_app, 'default_url': new_url}

        if app_dict is not None:
            app_data.update(app_dict)

        return app_data

    @staticmethod
    def extract_sso_cookie_value(headers):
        """
        Extract data from cookie
        @return: cookie value
        """

        cookie = Cookie.SimpleCookie()
        cookie.load(headers['Set-Cookie'])
        cookie_id = cookie['sso_cookie'].value
        return cookie_id

    @staticmethod
    def extract_cred_cookie_value(headers):
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
        Accesses the dummy app page with a valid cookie n number of times
        @param cookie: cookie from logged in user
        @param iterations: cookie from logged in user
        @param cookie: cookie from logged in user
        @return: asserts true/false

        """
        url = self._create_url('/')
        session = requests.session()
        session.cookies['sso_cookie'] = cookie
        for index in range(iterations):
            response = session.get(url, verify=False)
            assert response.status_code == requests.codes.ok
            time.sleep(wait_time)

    def login_create_session(
            self,
            cookie_type="SSO",
            cookie_value=None,
            **kwargs
    ):

        """
        login user and create session
        @param cookie_type: sso or credentials cookie
        @param cookie_value: cookie value to be set
        @param **kwargs: arguments for create_session_urlencoded
        @return: session, cookie_id, response

        """
        cookie_id = " "
        my_cookie = {}

        # login user
        response = self.create_session_urlencoded(**kwargs)
        # 303
        assert response.status_code == requests.codes.found

        # SSO cookie
        if cookie_type == "SSO":
            cookie_id = self.extract_sso_cookie_value(response.headers)

            if cookie_value is not None:
                cookie_id = cookie_value

            my_cookie = dict(name='sso_cookie', value=cookie_id)

        elif cookie_type == "CRED":
            cookie_id = self.extract_cred_cookie_value(response.headers)

            if cookie_value is not None:
                cookie_id = cookie_value

            my_cookie = dict(name='sso_credentials', value=cookie_id)

        session = self.create_requests_session_with_cookie(my_cookie)
        return session, cookie_id, response

    def create_org_data(self):

        """
        Creation of a organisation dict
        @return: an org data dict

        """
        rand_str = self.util.random_str(5)
        org_data = {
            'name': rand_str
        }

        return org_data

    def create_group_data(self):

        """
        Creation of a organisation dict
        @return: an org data dict

        """
        rand_str = self.util.random_str(5)
        group_data = {
            'name': rand_str
        }

        return group_data

    @staticmethod
    def _http_method_generator(
            session, method, request_url, verify, data, headers=None
    ):
        response = None

        if method == 'GET':
            response = session.get(url=request_url, verify=verify,
                                   headers=headers)
        if method == 'POST':
            response = session.post(
                url=request_url, data=data, verify=verify, headers=headers
            )
        if method == 'PUT':
            response = session.put(
                url=request_url, data=data, verify=verify, headers=headers
            )
        if method == 'DELETE':
            response = session.delete(url=request_url, verify=verify,
                                      headers=headers)

        return response

    def gk_crud(
            self,
            session,
            method,
            resource,
            id=None,
            id2=None,
            data=None,
            verify=None,
            type='urlencoded'
    ):
        """
        test function for GK API CRUD operations

        @param session:  session object and associated cookie
        @param: method i.e GET,POST,PUT or DELETE
        @param resource: resource under test
        @param id: id for put,delete,get
        @param id2: id for put,delete,get
        @param data: data for PUT and DELETE
        @param verify: boolean to determine if SSL cert will be verified
        @param type: urlencoded or json
        @return: a request session object containing the user info

        """
        if method == 'POST':
            # check the resource and set the post URI
            request_url = self._set_post_url(resource)
        else:
            # check the resource and set the put URI
            request_url = self._set_put_del_read_url(resource, id, id2)

        # if data must be created
        if (method == 'POST' or method == 'PUT') and data is None:
            # check the resource so that the data can be set
            data = self._set_data(resource, session)

        if verify is None:
            verify = False

        headers = {}
        if type == 'json':
            data = json.dumps(data)
            headers['Content-Type'] = 'application/json'

        response = self._http_method_generator(
            session,
            method,
            request_url,
            verify,
            data,
            headers=headers
        )

        return response

    def _set_post_url(self, resource):

        request_url = " "

        if resource == "application":
            request_url = self._create_url(
                config['api'][SERVICE_NAME]['application_v1']['post']
            )
        elif resource == "organization":
            request_url = self._create_url(
                config['api'][SERVICE_NAME]['org_v1']['post']
            )
        elif resource == "user":
            request_url = self._create_url(
                config['api'][SERVICE_NAME]['user_v1']['post']
            )
        elif resource == "group":
            request_url = self._create_url(
                config['api'][SERVICE_NAME]['group_v1']['post']
            )
        elif resource == "permission":
            request_url = self._create_url(
                config['api'][SERVICE_NAME]['permission_v1']['post']
            )
        elif resource == "user_app":
            request_url = self._create_url(
                config['api'][SERVICE_NAME]['user_app_v1']['post']
            )
        elif resource == "user_grp":
            request_url = self._create_url(
                config['api'][SERVICE_NAME]['user_grp_v1']['post']
            )
        elif resource == "user_org":
            request_url = self._create_url(
                config['api'][SERVICE_NAME]['user_org_v1']['post']
            )
        elif resource == "grp_perm":
            request_url = self._create_url(
                config['api'][SERVICE_NAME]['grp_perm_v1']['post']
            )
        elif resource == "user_perm":
            request_url = self._create_url(
                config['api'][SERVICE_NAME]['user_perm_v1']['post']
            )
        elif resource == "grp_app":
            request_url = self._create_url(
                config['api'][SERVICE_NAME]['grp_app_v1']['post']
            )
        return request_url

    def _set_put_del_read_url(self, resource, id, id2):

        request_url = " "

        if resource == "application":
            request_url = self._create_url(
                config['api'][SERVICE_NAME]['application_v1']['id']
            )
            request_url = request_url % id
        elif resource == "organization":
            request_url = self._create_url(
                config['api'][SERVICE_NAME]['org_v1']['id']
            )
            request_url = request_url % id
        elif resource == "user":
            request_url = self._create_url(
                config['api'][SERVICE_NAME]['user_v1']['id']
            )
            request_url = request_url % id
        elif resource == "group":
            request_url = self._create_url(
                config['api'][SERVICE_NAME]['group_v1']['id']
            )
            request_url = request_url % id
        elif resource == "permission":
            request_url = self._create_url(
                config['api'][SERVICE_NAME]['permission_v1']['id']
            )
            request_url = request_url % id
        elif resource == "user_app":
            request_url = self._create_url(
                config['api'][SERVICE_NAME]['user_app_v1']['id']
            )
            request_url = request_url % (id, id2)
        elif resource == "user_grp":
            request_url = self._create_url(
                config['api'][SERVICE_NAME]['user_grp_v1']['id']
            )
            request_url = request_url % (id, id2)
        elif resource == "user_org":
            request_url = self._create_url(
                config['api'][SERVICE_NAME]['user_org_v1']['id']
            )
            request_url = request_url % (id, id2)
        elif resource == "grp_perm":
            request_url = self._create_url(
                config['api'][SERVICE_NAME]['grp_perm_v1']['id']
            )
            request_url = request_url % (id, id2)
        elif resource == "user_perm":
            request_url = self._create_url(
                config['api'][SERVICE_NAME]['user_perm_v1']['id']
            )
            request_url = request_url % (id, id2)
        elif resource == "grp_app":
            request_url = self._create_url(
                config['api'][SERVICE_NAME]['grp_app_v1']['id']
            )
            request_url = request_url % (id, id2)

        return request_url

    def _set_data(self, resource, session):

        data = {}

        if resource == "application":
            data = self.create_app_data()
        elif resource == "organization":
            data = self.create_org_data()
        elif resource == "user":
            data = self.create_user_data()
        elif resource == "group":
            data = self.create_group_data()
        elif resource == "permission":
            data = self.create_permission_data(session)
        elif resource == "user_app":
            data = self.create_user_app_data(session)
        elif resource == "user_app":
            data = self.create_user_grp_data(session)
        elif resource == "user_org":
            data = self.create_user_org_data(session)
        elif resource == "grp_perm":
            data = self.create_grp_perm_data(session)
        elif resource == "user_perm":
            data = self.create_user_perm_data(session)
        elif resource == "grp_app":
            data = self.create_grp_app_data(session)
        return data

    def gk_listing(
            self,
            session,
            resource,
            name=None,
            verify=None
    ):
        """
        Test function for listing results from gk APIs
        @param session:  session object and associated cookie
        @param name: name to filter on
        @param verify: boolean to determine if SSL cert will be verified
        @return: a request session object containing the user info

        """

        request_url = self._set_listing_url(resource)

        if name is not None:
            request_url += '/?name=%s'
            request_url = request_url % name

        if verify is None:
            verify = False

        response = session.get(url=request_url, verify=verify)

        return response

    def _set_listing_url(self, resource):

        request_url = ""

        if resource == "application":
            request_url = self._create_url(
                config['api'][SERVICE_NAME]['applications_v1']
            )
        elif resource == "organization":
            request_url = self._create_url(
                config['api'][SERVICE_NAME]['orgs_v1']
            )
        elif resource == "user":
            request_url = self._create_url(
                config['api'][SERVICE_NAME]['users_v1']
            )
        elif resource == "group":
            request_url = self._create_url(
                config['api'][SERVICE_NAME]['groups_v1']
            )
        elif resource == "permission":
            request_url = self._create_url(
                config['api'][SERVICE_NAME]['permissions_v1']
            )
        return request_url

    def create_user_app_data(self, session, dict=None):

        """
        Creation of user_app_data
        @param dict: optional dict - can be merged with a default dict
        @return: a user app data dict

        """
        app_id = self.gk_crud(
            session, method='POST', resource='application'
        ).json()['application_id']
        user_id = self.gk_crud(
            session, method='POST', resource='user'
        ).json()['user_id']

        data = {'user_id': user_id, 'application_id': app_id}

        if dict is not None:
            data.update(dict)

        return data

    def create_user_grp_data(self, session, dict=None):

        """
        Creation of group app_data
        @param dict: optional dict - can be merged with a default dict
        @return: a user group data dict

        """
        group_id = self.gk_crud(
            session, method='POST', resource='group'
        ).json()['group_id']
        user_id = self.gk_crud(
            session, method='POST', resource='user'
        ).json()['user_id']

        data = {'user_id': user_id, 'group_id': group_id}

        if dict is not None:
            data.update(dict)

        return data

    def create_user_org_data(self, session, dict=None):
        """
        Creation of group app_data
        @param dict: optional dict - can be merged with a default dict
        @return: a user org data dict

        """
        org_id = self.gk_crud(
            session, method='POST', resource='organization'
        ).json()['organization_id']
        user_id = self.gk_crud(
            session, method='POST', resource='user'
        ).json()['user_id']

        data = {'user_id': user_id, 'organization_id': org_id}

        if dict is not None:
            data.update(dict)

        return data

    def create_grp_perm_data(self, session, dict=None):
        """
        Creation of group app_data
        @param dict: optional dict - can be merged with a default dict
        @return: a user org data dict

        """
        group_id = self.gk_crud(
            session, method='POST', resource='group'
        ).json()['group_id']
        perm_id = self.gk_crud(
            session, method='POST', resource='permission'
        ).json()['permission_id']

        data = {'group_id': group_id, 'permission_id': perm_id}

        if dict is not None:
            data.update(dict)

        return data

    def create_user_perm_data(self, session, dict=None):
        """
        Creation of user perm data
        @param dict: optional dict - can be merged with a default dict
        @return: a user org data dict

        """
        user_id = self.gk_crud(
            session, method='POST', resource='user'
        ).json()['user_id']
        perm_id = self.gk_crud(
            session, method='POST', resource='permission'
        ).json()['permission_id']

        data = {'user_id': user_id, 'permission_id': perm_id}

        if dict is not None:
            data.update(dict)

        return data

    def create_grp_app_data(self, session, dict=None):
        """
        Creation of grp application data
        @param dict: optional dict - can be merged with a default dict
        @return: a grp app data dict

        """
        group_id = self.gk_crud(
            session, method='POST', resource='group'
        ).json()['group_id']
        app_id = self.gk_crud(
            session, method='POST', resource='application'
        ).json()['application_id']

        data = {'group_id': group_id, 'application_id': app_id}

        if dict is not None:
            data.update(dict)

        return data

    def create_permission_data(self, session, dict=None):

        """
        Creation of a organisation dict
        @return: an org data dict

        """
        app_id = self.gk_crud(
            session, method='POST', resource='application'
        ).json()['application_id']
        rand_str = self.util.random_str(5)

        data = {
            'name': rand_str,
            'application_id': app_id
        }

        if dict is not None:
            data.update(dict)

        return data

    def gk_association_listing(
            self,
            session,
            resource,
            params=None,
            verify=None
    ):
        """
        Test function for listing results from gk APIs
        @param session:  session object and associated cookie
        @param resource: resource under test
        @param params: params
        @param verify: boolean to determine if SSL cert will be verified
        @return: a request session object containing the user info

        """

        request_url = self._set_association_listing_url(resource)

        if verify is None:
            verify = False

        response = session.get(url=request_url, verify=verify, params=params)

        return response

    def _set_association_listing_url(self, resource):

        request_url = ""

        if resource == "user_app":
            request_url = self._create_url(
                config['api'][SERVICE_NAME]['user_apps_v1']
            )
        elif resource == "user_org":
            request_url = self._create_url(
                config['api'][SERVICE_NAME]['user_orgs_v1']
            )
        elif resource == "user_perm":
            request_url = self._create_url(
                config['api'][SERVICE_NAME]['user_perms_v1']
            )
        elif resource == "user_grp":
            request_url = self._create_url(
                config['api'][SERVICE_NAME]['user_grps_v1']
            )
        elif resource == "grp_perm":
            request_url = self._create_url(
                config['api'][SERVICE_NAME]['grp_perms_v1']
            )
        elif resource == "grp_app":
            request_url = self._create_url(
                config['api'][SERVICE_NAME]['grp_apps_v1']
            )
        return request_url

    def recover_account(self, email, verify=None, allow_redirects=None):

        """
        Used to recover a users account
        @param email: users email
        @param verify: verify secure connections
        @param allow_redirects: allow_redirects
        @return: a confirmation message

        """
        url = self._create_url(
            config['api'][SERVICE_NAME]['recover_account_v1']['post']
        )

        if allow_redirects is None:
            allow_redirects = True

        if verify is None:
            verify = False

        response = requests.post(
            url, data=email, verify=verify, allow_redirects=allow_redirects
        )

        return response

    def change_password(
            self, token, password, verify=None, allow_redirects=None
    ):

        """
        Used to change a users password

        @param token: cookie session
        @param password: password
        @param verify: verify secure connections
        @param allow_redirects: allow_redirects
        @return: a confirmation message

        """

        url = self._create_url(
            config['api'][SERVICE_NAME]['change_password_v1']['post']
        )
        url = url % token

        if allow_redirects is None:
            allow_redirects = True

        if verify is None:
            verify = False

        response = requests.post(
            url, data=password, verify=verify, allow_redirects=allow_redirects
        )

        return response

    def create_user_app_api_display_data(
            self,
            app_id=None,
            **kwargs
    ):

        """
        Used to create date for the user application display api

        @param app_id: specified application id
        @param kwargs: 'user_permission' - associate user with permission
        @param kwargs: 'user_group' - associate user with group
        @param kwargs: 'group_permission' - associate permission with group
        @param kwargs: 'user_organization' - associate user with org
        @return: a dict of user app data

        """

        # admin - login and create session
        a_session, cookie_id, response = self.login_create_session(
            allow_redirects=False
        )

        response = self.gk_crud(
            session=a_session,
            method='POST',
            resource="permission"
        )
        permission_id = response.json()['permission_id']
        permission_name = response.json()['name']
        application_id = response.json()['application_id']
        application_name = response.json()['application']['name']

        # credentials
        credentials_payload = {
            'username': self.util.random_str(8),
            'password': self.util.random_str(8)
        }
        user_data = self.create_user_data(user_dict=credentials_payload)

        # create a new user
        create_response = self.gk_crud(
            a_session, method='POST', resource="user", data=user_data
        )

        # get user_id
        user_id = create_response.json()['user_id']

        if app_id is not None:
            #delete created app and related permission
            self.data_clean_up(application_id=application_id)
            #use the specified  application identifier
            application_id = app_id
            application_name = None

        # associate user with app
        user_app_data = {'user_id': user_id, 'application_id': application_id}
        self.gk_crud(
            a_session,
            method='POST',
            resource="user_app",
            data=user_app_data
        )

        # create a new group
        response = self.gk_crud(
            session=a_session,
            method='POST',
            resource="group"
        )
        group_id = response.json()["group_id"]
        group_name = response.json()["name"]

        user_dict = {
            'application_id': application_id,
            'application_name': application_name,
            'user_id': user_id,
            'credentials_payload': credentials_payload,
            'permission_name': permission_name,
            'permission_id': permission_id,
            'group_id': group_id,
            'group_name': group_name
        }

        if 'user_permission' in kwargs:
            # create a new permission
            user_perm_data = {
                'user_id': user_id,
                'permission_id': permission_id
            }
            # create an association
            self.gk_crud(
                a_session,
                method='POST',
                resource="user_perm",
                data=user_perm_data

            )

        if 'user_group' in kwargs:

            # associate user with group
            user_grp_data = {'user_id': user_id, 'group_id': group_id}
            self.gk_crud(
                a_session,
                method='POST',
                resource="user_grp",
                data=user_grp_data
            )
            # associate group with application
            grp_app_data = {
                'group_id': group_id,
                'application_id': application_id
            }
            self.gk_crud(
                a_session,
                method='POST',
                resource="grp_app",
                data=grp_app_data
            )

        if 'group_permission' in kwargs:

            # create an association
            grp_perm_data = {
                'group_id': group_id,
                'permission_id': permission_id
            }
            self.gk_crud(
                a_session,
                method='POST',
                resource="grp_perm",
                data=grp_perm_data
            )

        if 'user_organization' in kwargs:
            # create a new org
            create_response = self.gk_crud(
                a_session, method='POST', resource="organization"
            )

            organization_name = create_response.json()['name']
            organization_id = create_response.json()['organization_id']

            user_dict['organization_name'] = organization_name
            user_dict['organization_id'] = organization_id

            # create an association
            user_org_data = {
                'user_id': user_id,
                'organization_id': organization_id
            }
            self.gk_crud(
                a_session,
                method='POST',
                resource="user_org",
                data=user_org_data
            )

        return user_dict

    def data_clean_up(self, **kwargs):
        """
        Cleans resources.
        :param kwargs: data to delete
        """
        # responses from the cleanup requests
        del_responses = []

        # map of resource ids and corresponding names
        resources = {'user_id': 'user',
                     'application_id': 'application',
                     'group_id': 'group',
                     'org_id': 'organization'}

        # admin - login and create session
        a_session, cookie_id, response = self.login_create_session(
            allow_redirects=False
        )

        for data_name, data_id in kwargs.iteritems():
            if data_name in resources and data_id is not None:
                #delete resource - cascade delete by default
                del_response = self.gk_crud(
                    a_session,
                    method='DELETE',
                    resource=resources.get(data_name),
                    id=data_id
                )
                del_responses.append(del_response)

        return del_responses