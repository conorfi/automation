"""
DB access functionality for Courier service DBs.
"""
import time
from sqlalchemy.sql import table, column

from framework.db.model.courier import User, Group


class CourierDao(object):

    def __init__(self, db):
        super(CourierDao, self).__init__()
        self.db = db
        self.user_table = table(
            'user', column('id'), column('created'), column('last_modified'),
            column('username'), column('group_id'), column('level'),
            column('hash')
        )
        self.group_table = table(
            'group', column('id'), column('name'), column('upload_credentials')
        )

    def create_user(self, username, password_hash,
                    level='admin', group_id=None):
        """
        Create a new user in the user table, returns raw DB result.
        Defaults to an admin user with no group.

        :param username:
        :param level:
        :param group_id:
        :param password_hash:
        """
        created = time.time()
        params = {
            'created': created, 'last_modified': created, 'username': username,
            'group_id': group_id, 'level': level, 'hash': password_hash
        }

        query = self.user_table.insert().values(**params).\
            returning(self.user_table.c.id)

        result = self.db.execute(query)
        params['user_id'] = result[0]['id']
        return User(**params)

    def delete_user(self, user):
        """
        Deletes the given user.

        :param user:
        """
        query = self.user_table.delete().\
            where(self.user_table.c.username == user.username)
        return self.db.execute(query)

    def create_group(self, name, upload_credentials=None):
        """
        Create a new group in the group table, returns raw DB result.

        :param name:
        :param upload_credentials:
        """
        params = {
            'name': name, 'upload_credentials': upload_credentials
        }

        query = self.group_table.insert().values(**params).\
            returning(self.group_table.c.id)

        result = self.db.execute(query)
        params['group_id'] = result[0]['id']
        return Group(**params)

    def delete_group(self, group):
        """
        Deletes the given group.

        :param group:
        """
        query = self.group_table.delete().\
            where(self.group_table.c.name == group.name)
        return self.db.execute(query)
