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

    def resource_request(self, resource,
                         method='get', data=None, session=None):
        """
        Makes a request for a named resource, optionally specifying the method
        and data sent (if PUT or POST). May also specify a requests session
        to use instead of basic requests module.

        :param resource:
        :param method:
        :param data:
        :param session:
        """
        url = self._get_resource_url(resource, method=method)
        request_module = session if session is not None else requests
        return (getattr(request_module, method.lower())
                (url, data=data, verify=False))

    def create_random_user(self, level='admin', group_id=None):
        """
        Creates a random user. By default, creates an admin user with no
        linked group and default password.
        Returns the newly created user object.

        :param level:
        :param group_id:
        """
        username = self.util.random_str(10)
        user = self.dao.create_user(username, self._DEFAULT_PASSWORD_HASH,
                                    level, group_id=group_id)
        user.password = self.DEFAULT_PASSWORD
        return user

    def remove_user(self, user):
        """
        Deletes the user defined by the given user, if possible

        :param user:
        """
        if user.username is not None:
            self.dao.delete_user(user)

    def create_random_group(self, name=None):
        """
        Creates a random group. Returns the newly created group object.

        :param name:
        """
        if name is None:
            name = self.util.random_str(10)
        return self.dao.create_group(name)

    def remove_group(self, group):
        """
        Deletes the group, if possible

        :param group:
        """
        if group.name is not None:
            self.dao.delete_group(group)

    def authenticate(self, username, password):
        """
        Authenticates with the given username and password. If authenticated
        successfully, returns response and new requests session. If auth
        fails, returns response and None

        :param username:
        :param password:
        """
        response = self.resource_request(
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
