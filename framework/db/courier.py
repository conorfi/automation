"""
DB access functionality for Courier service DBs.
"""
from model.courier import *
from model import ModelCrud


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
