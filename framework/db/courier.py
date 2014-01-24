"""
DB access functionality for Courier service DBs.
"""
from .model.courier import *
from .model import ModelCrud


class CourierDao(object):

    def __init__(self, db, tablify):
        super(CourierDao, self).__init__()
        self.db = db
        self.tablify = tablify

        self.users = ModelCrud(db=self.db,
                               tablify=self.tablify,
                               klass=User,
                               id='user_id',
                               unique_key='username')

        self.groups = ModelCrud(db=self.db,
                                tablify=self.tablify,
                                klass=Group,
                                id='group_id',
                                unique_key='name')

        self.clients = ModelCrud(db=self.db,
                                 tablify=self.tablify,
                                 klass=Client,
                                 id='client_uuid',
                                 unique_key='name')

        self.content_servers = ModelCrud(db=self.db,
                                         tablify=self.tablify,
                                         klass=ContentServer,
                                         id='content_server_id',
                                         unique_key='id')

        self.content = ModelCrud(db=self.db,
                                 tablify=self.tablify,
                                 klass=Content,
                                 id='content_id',
                                 unique_key='uuid')

    def clear_cache(self):
        """
        Clears the cache of DB instances generated via this DAO instance.
        Removes the underlying DB data.
        """
        self.users.clear_cache()
        self.groups.clear_cache()
        self.clients.clear_cache()
        self.content_servers.clear_cache()
        self.content.clear_cache()
