"""
DB access functionality for Courier service DBs.
"""
from .model.courier import *
from .model import ModelCrud


class CourierDao(object):
    """
    Data access object for Courier DB data.
    """

    def __init__(self, db, tablify):
        super(CourierDao, self).__init__()
        self.db = db
        self.tablify = tablify

        model_cruds = {
            'users': {
                'args': [User, 'user_id', 'username']
            },
            'groups': {
                'args': [Group, 'group_id', 'name']
            },
            'clients': {
                'args': [Client, 'client_uuid', 'name']
            },
            'content_servers': {
                'args': [ContentServer, 'content_server_id', 'id']
            },
            'content': {
                'args': [Content, 'content_id', 'uuid']
            },
            'content_server_links': {
                'args': [ContentServers, 'id']
            }
        }
        # dynamically generate the ModelCruds described in the dict and
        # bind to this DAO instance
        for attr, func_args in model_cruds.iteritems():
            model_crud = ModelCrud(
                self.db, self.tablify, *func_args.get('args', []),
                **func_args.get('kwargs', {})
            )
            setattr(self, attr, model_crud)

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
