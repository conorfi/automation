"""
Service functionality for working with Courier APIs and remote interfaces.
"""
import urlparse
import requests
import Cookie
from testconfig import config

from framework.utility.utility import Utility
from framework.common_env import SERVICE_NAME_COURIER as SERVICE_NAME
from framework.db.model.courier import *


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
        method = method.lower()
        versioned_resource = resource + '_' + self.api_version
        url_data = config[SERVICE_NAME]
        scheme = url_data['scheme']
        host = '%s:%s' % (url_data['host'], url_data['port'])
        path_data = config['api'][SERVICE_NAME][versioned_resource]
        path = (path_data[method]
                if method in path_data else
                path_data['default'])
        return urlparse.urlunparse((scheme, host, path, None, None, None))

    def resource_request(self, resource, parameters=None,
                         method='get', data=None, session=None):
        """
        Makes a request for a named resource, optionally specifying the method
        and data sent (if PUT or POST). May also specify a requests session
        to use instead of basic requests module.

        :param resource: resource name
        :param parameters: query string parameters
        :param method: HTTP method
        :param data: body data
        :param session: request session with session cookies
        """
        url = self._get_resource_url(resource, method=method)
        headers = {}
        if data is not None:
            # Cherrypy defaults to 411 response if no data is sent and
            # content length header not set (which requests does not do,
            # annoyingly)
            # so check if nothing is going to be sent
            is_empty_data = reduce(lambda acc, value: acc and value is None,
                                   data.values(), True)
            if is_empty_data:
                headers['Content-Length'] = 0
        request_module = session if session is not None else requests
        return (getattr(request_module, method.lower())
                (url, params=parameters, data=data, verify=False,
                 headers=headers))

    def generate_user(self, level=User.LEVEL_ADMIN, group_id=None):
        """
        Randomly generates and returns a valid user. By default, creates an
        admin user with no linked group and default password.

        :param level:
        :param group_id:
        """
        return User(username=self.util.random_str(10),
                    hash=self._DEFAULT_PASSWORD_HASH,
                    password=self.DEFAULT_PASSWORD,
                    level=level,
                    group_id=group_id)

    def create_random_user(self, level=User.LEVEL_ADMIN, group_id=None):
        """
        Creates a random user in the DB.
        Returns the newly created user object.

        :param level:
        :param group_id:
        """
        user = self.generate_user(level=level, group_id=group_id)
        self.dao.users.create(user)
        return user

    def remove_user(self, user):
        """
        Deletes the user defined by the given user, if possible

        :param user:
        """
        self.dao.users.delete(user)

    def generate_group(self, name=None, credentials=None):
        """
        Randomly generates and returns a valid group.

        :param name:
        :param credentials:
        """
        return Group(name=(name or self.util.random_str(10)),
                     upload_credentials=credentials)

    def generate_group_credentials(self, public_key=None):
        """
        Returns randomly generated payload for group upload credentials

        :param public_key:
        """
        return json.dumps({
            Group.CREDENTIALS_KEY_PUBLIC: public_key or self.util.random_str(),
            Group.CREDENTIALS_KEY_PRIVATE: self.util.random_str(),
            Group.CREDENTIALS_KEY_BUCKET: self.util.random_str()
        })

    def create_random_group(self, name=None, credentials=None):
        """
        Creates a random group in the DB. Returns the newly created group
        object.

        :param name:
        :param credentials:
        """
        group = self.generate_group(name=name, credentials=credentials)
        self.dao.groups.create(group)
        return group

    def group_exists(self, group):
        """
        Returns True if group exists, False otherwise.

        :param group:
        """
        group_data = self.dao.groups.read(group)
        return len(group_data) == 1

    def remove_group(self, group):
        """
        Deletes the group, if possible

        :param group:
        """
        self.dao.groups.delete(group)

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

    def generate_client(self,
                        group_id=None):
        """
        Randomly generates and returns a valid client.

        :param group_id:
        """
        return Client(client_uuid=self.util.random_str(10),
                      name=self.util.random_str(10),
                      speedtest_pending=False,
                      version='',
                      group_id=group_id)

    def create_random_client(self, group_id=None):
        """
        Creates a random client in the DB.
        Returns the newly created client object.

        :param group_id:
        """
        client = self.generate_client(group_id=group_id)
        self.dao.clients.create(client)
        return client

    def remove_client(self, client):
        """
        Deletes the client defined by the given client, if possible

        :param client:
        """
        self.dao.clients.delete(client)