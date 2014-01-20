"""
DB access functionality for Courier service DBs.
"""


class CourierDao(object):

    def __init__(self, db):
        super(CourierDao, self).__init__()
        self.db = db
