"""
Service functionality for working with Courier APIs and remote interfaces.
"""
import urlparse
import requests
import Cookie
from testconfig import config

from framework.utility.utility import Utility
from framework.common_env import SERVICE_NAME_COURIER as SERVICE_NAME


class CourierService(object):

    DEFAULT_PASSWORD = 'admin'
    _DEFAULT_PASSWORD_HASH = \
        '$6$rounds=65921$BzVxFP8u2NYjeTZk$JZ9etggvS1qrio/' \
        '1kReOlZTPy6WMkhJ/' \
        'OFd1QX2UtJRyUrq09lw7kZAsM7foVR4DZ5g3uAe3SSzvqPhGwNmg4/'

    def __init__(self, dao, api_version='v1'):
        # initialize utility class
        self.util = Utility()
        self.dao = dao
        self.api_version = api_version

    def _get_resource_url(self, resource, method='get'):
        url_data = config[SERVICE_NAME]
        scheme = url_data['scheme']
        host = '%s:%s' % (url_data['host'], url_data['port'])
        path = (config['api'][SERVICE_NAME][resource + '_' + self.api_version]
                [method.lower()])
        return urlparse.urlunparse((scheme, host, path, None, None, None))

    def _resource_request(self, resource, method='get', data=None):
        url = self._get_resource_url(resource, method=method)
        return getattr(requests, method.lower())(url, data=data, verify=False)

    def create_random_user(self, level='admin', group_id=None):
        """
        Creates a random user. By default, creates an admin user with no
        linked group and default password.
        Returns the newly created user data.
        """
        username = self.util.random_str(10)
        self.dao.create_user(username, self._DEFAULT_PASSWORD_HASH,
                             level, group_id=group_id)
        return {'username': username, 'password': self.DEFAULT_PASSWORD,
                'level': level, 'group_id': group_id}

    def remove_user(self, user_data):
        """
        Deletes the user defined by the given user data, if possible

        :param user_data:
        """
        if 'username' in user_data:
            self.dao.delete_user(user_data['username'])

    def authenticate(self, username, password):
        """
        Authenticates with the given username and password. If authenticated
        successfully, returns response and new requests session. If auth
        fails, returns response and None

        :param username:
        :param password:
        """
        response = self._resource_request(
            'authenticate', method='post',
            data={'username': username, 'password': password}
        )

        session = None
        try:
            response_data = response.json()
        except ValueError:
            response_data = None

        # authentication successful, create new session with new cookie
        if response_data is not None and response_data['result']:
            cookie = Cookie.SimpleCookie()
            cookie.load(response.headers['Set-Cookie'])
            cookie_name = 'session_id'
            session = requests.session()
            session.cookies.set(name=cookie_name,
                                value=cookie[cookie_name].value)

        return response, session
