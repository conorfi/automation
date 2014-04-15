"""
@summary: Contains a set of database functions for the producer project

@since: Created on March 14th 2014

@author: Will Ellis
(template: screen_writer.py)

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
        query = """select *
            from pack
            where uuid='%s'
            """ % uuid
        result = db.query(query)
        if not result:
            return None
        else:
            return result[0]

    @staticmethod
    def set_title(db, uuid=None, name=None):
        """
        updates session info to be expired based on a specific session ID
        @param db: the database connection that will be utilized
        @param uuid: uuid
        @param name: name
        created by a post
        @return: dict of session info
        """
        if uuid is None:
            uuid = "70b86c59-4018-4d2f-bca6-be9bb16a0e45"
        if name is None:
            name = "title_title"
        query = """
                insert into
                title (uuid,name,created,last_modified,year)
                values ('%s','%s','','','');
                """ % (uuid, name)
        result = db.trans(query)
        return result

    @staticmethod
    def set_placeholder(db, uuid=None, name=None):
        """
        updates session info to be expired based on a specific session ID
        @param db: the database connection that will be utilized
        @param uuid: uuid
        @param name: name
        created by a post
        @return: dict of session info
        """
        if uuid is None:
            uuid = "45b86c59-4018-4d2f-bca6-be9bb16a0e89"
        if name is None:
            name = "placeholder_name_set"
        query = """
                insert into
                placeholder (uuid,name,created,last_modified)
                values ('%s','%s','','');
                """ % (uuid, name)
        result = db.trans(query)
        return result

    @staticmethod
    def get_screen_by_uuid(db, uuid):
        """
        Returns pack  info based on a UUID
        @param db: the database connection that will be utilized
        @param uuid: pack identifier
        @return: dict of pack info
        """
        query = """select *
            from screen
            where uuid='%s'
            """ % uuid
        result = db.query(query)
        if not result:
            return None
        else:
            return result[0]

    @staticmethod
    def get_title_by_uuid(db, uuid):
        """
        Returns pack  info based on a UUID
        @param db: the database connection that will be utilized
        @param uuid: pack identifier
        @return: dict of pack info
        """
        query = """select *
            from title
            where uuid='%s'
            """ % uuid
        result = db.query(query)
        if not result:
            return None
        else:
            return result[0]

    @staticmethod
    def get_placeholder_by_uuid(db, uuid):
        """
        Returns pack  info based on a UUID
        @param db: the database connection that will be utilized
        @param uuid: pack identifier
        @return: dict of pack info
        """
        query = """select *
            from placeholder
            where uuid='%s'
            """ % uuid
        result = db.query(query)
        if not result:
            return None
        else:
            return result[0]

    @staticmethod
    def get_pack_by_uuid(db, uuid):
        """
        Returns pack  info based on a UUID
        @param db: the database connection that will be utilized
        @param uuid: pack identifier
        @return: dict of pack info
        """

        query = """select p.*, ph.name as placeholder_name
            from pack p
            join placeholder ph
            on p.placeholder_uuid = ph.uuid
            where p.uuid='%s'
            """ % uuid
        result = db.query(query)
        if not result:
            return None
        else:
            result_dict = result[0]
        return result_dict

    @staticmethod
    def del_screen_by_uuid(db, uuid):
        """
        deletes a user and cascade deletes from user_application
        @param db: the database connection that will be utilized
        @param user_id: user identifier
        @return: boolean
        """
        query = """
            delete
            from screen
            where uuid='%s'
            """ % uuid
        result = db.trans(query)
        return result

    @staticmethod
    def del_title_by_uuid(db, uuid):
        """
        deletes a user and cascade deletes from user_application
        @param db: the database connection that will be utilized
        @param uuid: uuid
        @return: boolean
        """
        query = """
            delete
            from title
            where uuid='%s'
            """ % uuid
        result = db.trans(query)
        return result

    @staticmethod
    def del_placeholder_by_uuid(db, uuid):
        """
        deletes a user and cascade deletes from user_application
        @param db: the database connection that will be utilized
        @param user_id: user identifier
        @return: boolean
        """
        query = """
            delete
            from placeholder
            where uuid='%s'
            """ % uuid
        result = db.trans(query)
        return result