"""
DB access functionality for Courier service DBs.
"""
import time
from sqlalchemy.sql import text


class CourierDao(object):

    def __init__(self, db):
        super(CourierDao, self).__init__()
        self.db = db

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

        query = text(
            'INSERT INTO "user" '
            '(created, last_modified, username, group_id, level, hash) '
            'VALUES (:created, :last_modified, :username, :group_id, '
            ':level, :password_hash)')
        params = {
            'created': created, 'last_modified': created,
            'username': username,
            'group_id': group_id, 'level': level,
            'password_hash': password_hash
        }

        return self.db.trans(query, **params)

    def delete_user(self, username):
        """
        Deletes the user with the given username.

        :param username:
        """
        query = text('DELETE FROM "user" WHERE username = :username')
        return self.db.trans(query, username=username)
