"""
@summary: Contains a set of database functions for the screen writer project

@since: Created on February 11th 2013

@author: Conor Fitzgerald

"""

class Packs(object):
    @staticmethod
    def get_pack_by_uuid(db, uuid):
        """
        Returns pack  info based on a UUID
        @param db: the database connection that will be utilized
        @param uuid: pack identifier
        @return: dict of pack info
        """
        print "uuid" + uuid
        query = """select *
            from pack
            where uuid='%s'
            """ % uuid
        result = db.query(query)
        if not result:
            return None
        else:
            return result[0]