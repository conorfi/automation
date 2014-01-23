"""
Model representations of standard data retrieved from Courier service.
"""
import json
import time

from . import BaseModel


class User(BaseModel):

    LEVEL_ADMIN = 'admin'
    LEVEL_STANDARD = 'standard'
    LEVEL_READONLY = 'readonly'

    def __init__(self, user_id=None, username=None, group_id=None,
                 password=None, level=None, hash=None,
                 created=None, last_modified=None):
        self.user_id = user_id
        self.username = username
        self.group_id = group_id
        self.password = password
        self.level = level
        self.hash = hash
        self.created = created or time.time()
        self.last_modified = last_modified or self.created


class Group(BaseModel):

    CREDENTIALS_KEY_PUBLIC = 'public_key'
    CREDENTIALS_KEY_PRIVATE = 'private_key'
    CREDENTIALS_KEY_BUCKET = 'bucket'

    def __init__(self, group_id=None, name=None, upload_credentials=None):
        self.group_id = group_id
        self.name = name
        self.upload_credentials = upload_credentials

    def to_post_data(self, exclude_empty=False):
        """
        Returns the group data formatted in the required layout.
        Groups have a special organisation for POSTing data to the server.

        :param exclude_empty:
        """
        data = self.to_data(exclude_empty=exclude_empty)

        # POST expects id not group_id
        if 'group_id' in data:
            data['id'] = data['group_id']
            del data['group_id']

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
