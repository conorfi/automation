"""
Model representations of standard data retrieved from Courier service.
"""


class User(object):

    def __init__(self, user_id=None, username=None, group_id=None,
                 password=None, level=None, hash=None,
                 created=None, last_modified=None):
        self.user_id = user_id
        self.username = username
        self.group_id = group_id
        self.password = password
        self.level = level
        self.hash = hash
        self.created = created
        self.last_modified = last_modified


class Group(object):

    def __init__(self, group_id=None, name=None, upload_credentials=None):
        self.group_id = group_id
        self.name = name
        self.upload_credentials = upload_credentials
