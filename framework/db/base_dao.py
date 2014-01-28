'''
@summary: Contains a set of base/core database functions

@since: Created on November 6th 2013

@author: Conor Fitzgerald

'''

from sqlalchemy import create_engine


class BaseDAO(object):

    def __init__(self, db_config):

        self.db_conn = create_engine(db_config)
        self.connection = self.db_conn.connect()

    def close(self):
        self.connection.close()
        self.db_conn.dispose()

    def query(self, query):
        """
        function to run raw select queries

        @param query: query e.g select a from b where c=123

        @return: list of dicts representing the table rows

        """
        results = self.connection.execute(query)
        fetched_results = results.fetchall()
        rows_as_dict = []
        for row in fetched_results:
            rows_as_dict.append(dict(row))

        return rows_as_dict

    def trans(self, query, **kwargs):
        """
        function to run raw updates,commits and delete queries

        @param query: query e.g select a from b where c=123
        @param kwargs:

        @return:

        """
        trans = self.connection.begin()
        try:
            self.connection.execute(query, **kwargs)
            trans.commit()
        except:
            trans.rollback()
            raise
        return True

    def execute(self, query):
        """
        Runs raw updates,commits and delete queries and returns any results.

        @param query: query e.g select a from b where c=123

        @return: result of the execution

        """
        raw_result = self.connection.execute(query)
        # translate raw ResultProxy into consistent list response
        if raw_result.is_insert:
            raw_results = [dict(raw_result.fetchone())]
        elif raw_result.returns_rows:
            raw_results = []
            for raw_row in raw_result.fetchall():
                raw_results.append(dict(raw_row))
        else:
            raw_results = []
        return raw_results
