"""
Model representations of standard data retrieved from Courier service.
"""
import json
import time

from . import BaseModel


class User(BaseModel):

    TABLE_NAME = 'user'

    LEVEL_ADMIN = 'admin'
    LEVEL_STANDARD = 'standard'
    LEVEL_READONLY = 'readonly'

    def __init__(self, id=None, user_id=None, username=None, group_id=None,
                 password=None, level=None, hash=None,
                 created=None, last_modified=None):
        super(User, self).__init__(alias={'user_id': 'id'},
                                   db_ignore=['password'])
        self.user_id = id or user_id
        self.username = username
        self.group_id = group_id
        self.password = password
        self.level = level
        self.hash = hash
        self.created = created or time.time()
        self.last_modified = last_modified or self.created

    def to_response_data(self):
        """
        Response from server for user data doesn't contain some fields
        """
        data = super(User, self).to_response_data()
        del data['password']
        del data['hash']
        del data['created']
        del data['last_modified']
        return data

    def to_request_data(self):
        """
        User data sent to server has different username field and no hash.
        """
        data = super(User, self).to_request_data()
        data['edit_username'] = data['username']
        del data['id']
        del data['hash']
        del data['created']
        del data['last_modified']
        del data['username']
        return data


class Group(BaseModel):

    TABLE_NAME = 'group'
    CREDENTIALS_KEY_PUBLIC = 'public_key'
    CREDENTIALS_KEY_PRIVATE = 'private_key'
    CREDENTIALS_KEY_BUCKET = 'bucket'

    def __init__(self, id=None, group_id=None, name=None,
                 upload_credentials=None):
        super(Group, self).__init__(alias={'group_id': 'id'})
        self.group_id = id or group_id
        self.name = name
        self.upload_credentials = upload_credentials

    def to_request_data(self):
        """
        Returns the group data formatted in the required layout.
        Groups have a special organisation for POSTing data to the server.
        """
        data = super(Group, self).to_request_data()

        # convert JSON-ed upload credentials to data for POSTing
        if 'upload_credentials' in data \
                and data['upload_credentials'] is not None:
            try:
                credentials = json.loads(data['upload_credentials'])
                data['upload_credentials'] = credentials
            except TypeError:
                credentials = {}
            if 'public_key' in credentials:
                data['public'] = credentials[self.CREDENTIALS_KEY_PUBLIC]
                data['private'] = credentials[self.CREDENTIALS_KEY_PRIVATE]
                data['bucket'] = credentials[self.CREDENTIALS_KEY_BUCKET]

        return data


class Client(BaseModel):

    TABLE_NAME = 'client'

    def __init__(self, client_uuid=None, name=None, group_id=None,
                 site_code=None, live=None, approved=None, ping=None,
                 download=None, upload=None, speedtest_pending=None,
                 remaining_disk_space=None, used_disk_space=None,
                 total_disk_space=None, version=None,
                 created=None, last_modified=None):

        super(Client, self).__init__(alias={'client_uuid': 'uuid'})
        self.client_uuid = client_uuid
        self.name = name
        self.group_id = group_id
        self.site_code = site_code
        self.live = live
        self.approved = approved
        self.ping = ping
        self.download = download
        self.upload = upload
        self.speedtest_pending = speedtest_pending
        self.remaining_disk_space = remaining_disk_space
        self.used_disk_space = used_disk_space
        self.total_disk_space = total_disk_space
        self.version = version
        self.created = created or time.time()
        self.last_modified = last_modified or self.created


class ContentServer(BaseModel):

    TABLE_NAME = 'content_server'

    def __init__(self, id=None, content_server_id=None,
                 type=None, source=None):

        super(ContentServer, self).__init__(alias={'content_server_id': 'id'})
        self.content_server_id = id or content_server_id
        self.type = type
        self.source = source


class Content(BaseModel):

    TABLE_NAME = 'content'

    def __init__(self, uuid=None, content_id=None, name=None, size=None,
                 cpl_id=None, cpl_uri=None, tags=None, deleted=False,
                 created=None, last_modified=None):

        super(Content, self).__init__(alias={'content_id': 'uuid'})
        self.content_server_id = uuid or content_id
        self.name = name
        self.size = size
        self.cpl_id = cpl_id
        self.cpl_uri = cpl_uri
        self.tags = tags
        self.deleted = deleted
        self.created = created or time.time()
        self.last_modified = last_modified or self.created
