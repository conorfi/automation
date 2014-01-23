"""
DB access functionality for Courier service DBs.
"""
from sqlalchemy.sql import table, column


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

    def create_user(self, user):
        """
        Create a new user in the user table, returns updated user with new DB
        ID.

        :param user:
        """
        user_data = user.to_data(exclude_empty=True)
        if 'password' in user_data:
            del user_data['password']
        query = self.user_table.insert().values(**user_data).\
            returning(self.user_table.c.id)

        result = self.db.execute(query)
        user.user_id = result[0]['id']
        return user

    def delete_user(self, user):
        """
        Deletes the given user.

        :param user:
        """
        query = self.user_table.delete().\
            where(self.user_table.c.username == user.username)
        return self.db.execute(query)

    def create_group(self, group):
        """
        Create a new group in the group table, returns updated group with new
        DB ID.

        :param group:
        """
        query = self.group_table.insert().\
            values(**group.to_data(exclude_empty=True)).\
            returning(self.group_table.c.id)

        result = self.db.execute(query)
        group.group_id = result[0]['id']
        return group

    def read_group(self, group):
        """
        Returns the group data from the DB for this group.

        :param group:
        """
        query = self.group_table.select().\
            where(self.group_table.c.name == group.name)
        return self.db.execute(query)

    def delete_group(self, group):
        """
        Deletes the given group.

        :param group:
        """
        query = self.group_table.delete().\
            where(self.group_table.c.name == group.name)
        return self.db.execute(query)
