"""
@summary: Contains a set of database functions for the gatekeeper project

@since: Created on November 6th 2013

@author: Conor Fitzgerald

"""


class GateKeeperDAO(object):
    @staticmethod
    def get_session_by_cookie_id(db, cookie_id):
        """
        Returns session info based on a specific session ID
        @param db: the database connection that will be utilized
        @param cookie_id: cookie_id(cookie value) of the session created
        by a post
        @return: dict of session info
        """
        query = """select s.session_id, s.user_id,
            c.cookie_id,c.type_name,c.expiry_date
            from cookie c
            join session s on c.session_id = s.session_id
            where c.cookie_id='%s'
            """ % cookie_id

        result = db.query(query)
        if not result:
            return None
        else:
            return result[0]

    @staticmethod
    def get_user_by_username(db, username):
        """
        Returns user info based on a specific user name
        @param db: the database connection that will be utilized
        @param username: username
        @return: dict of session info
        """
        query = """select *
                        from gatekeeper_user
                         where username='%s'""" % username
        result = db.query(query)
        if not result:
            return None
        else:
            return result[0]

    @staticmethod
    def get_user_count(db):
        """
        Returns user info based on a specific user name
        @param db: the database connection that will be utilized
        @return: dict of session info
        """
        query = """select count(*) from gatekeeper_user"""
        result = db.query(query)
        if not result:
            return None
        else:
            return result[0]

    @staticmethod
    def get_app_count(db):
        """
        Returns user info based on a specific user name
        @param db: the database connection that will be utilized
        @return: dict of session info
        """
        query = """select count(*) from application"""
        result = db.query(query)
        if not result:
            return None
        else:
            return result[0]

    @staticmethod
    def get_org_count(db):
        """
        Returns count of orgnizations
        @param db: the database connection that will be utilized
        @return: dict of session info
        """
        query = """select count(*) from organization"""
        result = db.query(query)
        if not result:
            return None
        else:
            return result[0]

    @staticmethod
    def get_group_count(db):
        """
        Returns count of groups
        @param db: the database connection that will be utilized
        @return: dict of session info
        """
        query = """select count(*) from gatekeeper_group"""
        result = db.query(query)
        if not result:
            return None
        else:
            return result[0]

    @staticmethod
    def get_permission_count(db):
        """
        Returns count of permissions
        @param db: the database connection that will be utilized
        by a post
        @return: dict of session info

        """
        query = """select count(*) from permission"""
        result = db.query(query)
        if not result:
            return None
        else:
            return result[0]

    @staticmethod
    def get_user_app_count(db):
        """
        Returns count of user_app
        @param db: the database connection that will be utilized
        @return: count

        """
        query = """select count(*) from user_application"""
        result = db.query(query)
        if not result:
            return None
        else:
            return result[0]

    @staticmethod
    def get_grp_app_count(db):
        """
        Returns count of grp_app
        @param db: the database connection that will be utilized
        @return: count

        """
        query = """select count(*) from group_application"""
        result = db.query(query)
        if not result:
            return None
        else:
            return result[0]

    @staticmethod
    def get_user_grp_count(db):
        """
        Returns count of grp_app
        @param db: the database connection that will be utilized
        @return: count

        """
        query = """select count(*) from user_group"""
        result = db.query(query)
        if not result:
            return None
        else:
            return result[0]

    @staticmethod
    def get_grp_perm_count(db):
        """
        Returns count of grp_app
        @param db: the database connection that will be utilized
        @return: count

        """
        query = """select count(*) from group_permission"""
        result = db.query(query)
        if not result:
            return None
        else:
            return result[0]

    @staticmethod
    def get_user_perm_count(db):
        """
        Returns count of grp_app
        @param db: the database connection that will be utilized
        @return: count

        """
        query = """select count(*) from user_permission"""
        result = db.query(query)
        if not result:
            return None
        else:
            return result[0]

    @staticmethod
    def get_user_org_count(db):
        """
        Returns count of user_org
        @param db: the database connection that will be utilized
        @return: count

        """
        query = """select count(*) from user_organization"""
        result = db.query(query)
        if not result:
            return None
        else:
            return result[0]

    @staticmethod
    def get_token_count(db):
        """
        Returns token count
        @param db: the database connection that will be utilized
        @return: count

        """
        query = """select count(*) from token"""
        result = db.query(query)
        if not result:
            return None
        else:
            return result[0]

    @staticmethod
    def get_app_by_app_name(db, app_name):
        """
        Returns app data based on app name

        @param db: the database connection that will be utilized
        @param app_name: application name
        @return: dict of app info

        """
        query = """select *
                        from application
                         where name='%s'""" % app_name
        result = db.query(query)
        if not result:
            return None
        else:
            return result[0]

    @staticmethod
    def get_org_by_org_name(db, org_name):
        """
        Returns app data based on app name

        @param db: the database connection that will be utilized
        @param org_name: organization name
        @return: dict of app info

        """
        query = """select *
                        from organization
                        where name='%s'""" % org_name
        result = db.query(query)
        if not result:
            return None
        else:
            return result[0]

    @staticmethod
    def get_permission_by_name(db, per_name, app_id):
        """
        Returns permission id based on per name

        @param db: the database connection that will be utilized

        @param per_name: permission name

        @return: permission id

        """
        query = """select *
                        from permission
                         where name='%s'
                         and application_id=%d""" % (per_name, app_id)
        result = db.query(query)
        if not result:
            return None
        else:
            return result[0]

    @staticmethod
    def get_group_by_name(db, grp_name):
        """
        Returns group id based on group name

        @param db: the database connection that will be utilized

        @param grp_name: group name

        @return: group id

        """
        query = """select *
                        from gatekeeper_group
                        where name='%s'""" % grp_name
        result = db.query(query)
        if not result:
            return None
        else:
            return result[0]

    @staticmethod
    def get_token_by_user_id(db, user_id):
        """
        get the latest token  from the database
        @param db: the database connection that will be utilized
        @return: token info

        """

        query = """
            select * from token
            where user_id=%d""" % user_id

        result = db.query(query)
        if not result:
            return None
        else:
            return result[0]

    @staticmethod
    def get_verification_code_by_user_id(db, user_id):
        """
        deletes a user and cascade deletes from user_application
        @param db: the database connection that will be utilized
        @param user_id: user identifier
        @return: boolean
        """
        query = """
            select verification_code from verification
            where user_id=%d
            order by verification_id desc""" % user_id

        result = db.query(query)
        if not result:
            return None
        else:
            return result[0]

    @staticmethod
    def get_org_by_orgname(db, orgname):
        """
        Returns user info based on a specific user name
        @param db: the database connection that will be utilized
        @param orgname: orgname
        by a post
        @return: dict of session info

        """
        query = """select *
                        from organization
                        where name='%s'""" % orgname
        result = db.query(query)
        if not result:
            return None
        else:
            return result[0]

    @staticmethod
    def get_user_grp_by_user_id(db, user_id):
        """
        Returns user grp info
        @param db: the database connection that will be utilized
        @param user_id: user id
        by a post
        @return: dict of session info

        """
        query = """select gk.group_id,gk.name
                    from user_group ug
                    join gatekeeper_group gk on ug.group_id=gk.group_id
                    where ug.user_Id=%d""" % user_id
        result = db.execute(query)
        if not result:
            return None
        else:
            return result[0]

    @staticmethod
    def get_app_id_by_perm_id(db, perm_id):
        """
        Returns user grp info
        @param db: the database connection that will be utilized
        @param perm_id: perm_id
        by a post
        @return: dict of session info

        """
        query = """
                select application_id from permission where permission_id =%d
                """ % perm_id

        result = db.execute(query)
        if not result:
            return None
        else:
            return result[0]

    35;

    @staticmethod
    def set_session_to_expire_by_session_id(db, cookie_id):
        """
        updates session info to be expired based on a specific session ID
        @param db: the database connection that will be utilized
        @param cookie_id: (cookie value) of the session
        created by a post
        @return: dict of session info
        """
        query = """update cookie
                        set expiry_date = '2000-01-01 01:01:01'
                         where cookie_id='%s'""" % cookie_id

        result = db.trans(query)
        return result

    @staticmethod
    def set_gk_user(db, username, password, email, name, phone):
        """
        create a new user in the user_gatekeeper table
        @param db,username,password, email, name, phone: user details
        @return: boolean
        """

        query = """INSERT INTO
            gatekeeper_user(username, password, email, name, phone)
            VALUES ('%s','%s','%s','%s','%s');
            """ % (username, password, email, name, phone)

        result = db.trans(query)
        return result

    @staticmethod
    def set_gk_group(db, name):
        """
        create a new group in the group_gatekeeper table
        @param db: the database connection that will be utilized
        @param  name : group name
        @return: boolean

        """
        query = """INSERT INTO
            gatekeeper_group(name)
            VALUES ('%s');
            """ % name

        result = db.trans(query)
        return result

    @staticmethod
    def set_user_group(db, user_id, grp_id):
        """
        associate user with a group

        @param db: the database connection that will be utilized

        @param user_id: user id

        @param grp_id : group_id

        @return: boolean

        """
        query = """INSERT INTO
            user_group(user_id,group_id)
            VALUES (%d,%d);
            """ % (user_id, grp_id)

        result = db.trans(query)
        return result

    @staticmethod
    def set_group_permission(db, grp_id, per_id):
        """
        associate a permission with a group

        @param db: the database connection that will be utilized

        @param per_id: permissions id

        @param grp_id : group_id

        @return: boolean

        """
        query = """INSERT INTO
            group_permission(group_id,permission_id)
            VALUES (%d,%d);
            """ % (grp_id, per_id)

        result = db.trans(query)
        return result

    @staticmethod
    def set_app(db, app_name):
        """
        create a new application in the application table

        @param db: the database connection that will be utilized

        @param app_name: application_name

        @return: boolean

        """
        query = """INSERT INTO
            application(name)
            VALUES ('%s');
            """ % app_name

        result = db.trans(query)
        return result

    @staticmethod
    def set_user_app_id(db, app_id, user_id):
        """
        associate a user with an application

        @param db: the database connection that will be utilized

        @param app_id: application identifier
        @param user_id: user identifier
        @return: boolean

        """
        query = """
            INSERT INTO
            user_application(application_id, user_id)
            VALUES (%d,%d);
            """ % (app_id, user_id)
        result = db.trans(query)
        return result

    @staticmethod
    def set_user_org_id(db,org_id,user_id):
        """
        associate a user with an organisation

        @param db: the database connection that will be utilized

        @param org_id: organisation identifier
        @param user_id: user identifier
        @return: boolean
        """
        query = """
            INSERT INTO
            user_organization(organization_id, user_id)
            VALUES (%d,%d);
            """ % (org_id, user_id)
        result = db.trans(query)
        return result

    @staticmethod
    def set_group_app_id(db, app_id, grp_id):
        """
        associate a user with an application

        @param db: the database connection that will be utilized

        @param app_id: application identifier
        @param grp_id: group identifier
        @return: boolean

        """
        query = """
            INSERT INTO
            group_application(application_id, group_id)
            VALUES (%d,%d);
            """ % (app_id, grp_id)
        result = db.trans(query)
        return result

    @staticmethod
    def set_user_permissions_id(db, user_id, per_id):
        """
        associate a user with an application
        @param db: the database connection that will be utilized
        @param user_id: user identifier
        @param per_id: user identifier
        @return: boolean
        """
        query = """
            INSERT INTO
            user_permission(user_id,permission_id)
            VALUES (%d,%d);
            """ % (user_id, per_id)
        result = db.trans(query)
        return result

    @staticmethod
    def set_verification_code_to_expire_by_verification_code(
            db,
            verification_code
    ):
        """
        updates verification code to be expired based
        on a specific verification code
        @param db: the database connection that will be utilized
        @param verification_code: verification_code that is used as
        the second authentication factor
        @return: boolean
        """
        query = """update verification
                        set expiry_date = '2000-01-01 01:01:01'
                         where verification_code='%s'""" % verification_code

        result = db.trans(query)
        return result

    @staticmethod
    def del_gk_user(db, user_id):
        """
        deletes a user and cascade deletes from user_application
        @param db: the database connection that will be utilized
        @param user_id: user identifier
        @return: boolean
        """
        query = """
            delete
            from gatekeeper_user
            where user_id='%s'""" % user_id
        result = db.trans(query)
        return result

    @staticmethod
    def del_gk_group(db, grp_id):
        """
        deletes a group and cascade deletes
        @param db: the database connection that will be utilized
        @param grp_id: group identifier
        @return: boolean
        """
        query = """
            delete
            from gatekeeper_group
            where group_id=%d""" % grp_id
        result = db.trans(query)
        return result

    @staticmethod
    def del_app(db, app_id):
        """
        deletes an application
        @param db: the database connection that will be utilized
        @param app_id: application identifier
        @return: boolean

        """
        query = """
            delete
            from application
            where application_id=%d""" % app_id
        result = db.trans(query)
        return result

    @staticmethod
    def del_perm(db, perm_id):
        """
        deletes an application
        @param db: the database connection that will be utilized
        @param perm_id: permission identifier
        @return: boolean

        """
        query = """
            delete
            from permission
            where permission_id=%d""" % perm_id
        result = db.trans(query)
        return result

    @staticmethod
    def del_org(db, org_id):
        """
        deletes an organization
        @param db: the database connection that will be utilized
        @param org_id: org identifier
        @return: boolean

        """
        query = """
            delete
            from organization
            where organization_id=%d""" % org_id
        result = db.trans(query)
        return result

    @staticmethod
    def del_tokens(db):
        """
        deletes all tokens
        @param db: the database connection that will be utilized
        @return: boolean
        """
        query = """
            delete
            from token """
        result = db.trans(query)
        return result

    @staticmethod
    def del_sessions(db):
        """
        deletes all sessions
        @param db: the database connection that will be utilized
        @return: boolean
        """
        query = """
            delete
            from session """
        result = db.trans(query)
        return result

    @staticmethod
    def del_cookies(db):
        """
        deletes all sessions
        @param db: the database connection that will be utilized
        @return: boolean
        """
        query = """
            delete
            from cookie """
        result = db.trans(query)
        return result

