"""
@summary: Contains a set of database functions for the gatekeeper project

@since: Created on November 6th 2013

@author: Conor Fitzgerald

"""


class GateKeeperDAO(object):

    def get_session_by_cookie_id(self, db, cookie_id):
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
            if (not result):
                return None
            else:
                return result[0]

    def get_user_by_username(self, db, username):
            """
            Returns user info based on a specific user name
            @param db: the database connection that will be utilized
            @param session_id: session_id(cookie value) of the session created
            by a post
            @return: dict of session info

            """
            query = """select *
                        from gatekeeper_user
                         where username='%s'""" % username
            result = db.query(query)
            if (not result):
                return None
            else:
                return result[0]

    def get_user_count(self, db):
            """
            Returns user info based on a specific user name
            @param db: the database connection that will be utilized
            @param session_id: session_id(cookie value) of the session created
            by a post
            @return: dict of session info

            """
            query = """select count(*) from gatekeeper_user"""
            result = db.query(query)
            if (not result):
                return None
            else:
                return result[0]

    def get_app_count(self, db):
            """
            Returns user info based on a specific user name
            @param db: the database connection that will be utilized
            @param session_id: session_id(cookie value) of the session created
            by a post
            @return: dict of session info

            """
            query = """select count(*) from application"""
            result = db.query(query)
            if (not result):
                return None
            else:
                return result[0]

    def get_org_count(self, db):
            """
            Returns count of orgnizations
            @param db: the database connection that will be utilized
            @param session_id: session_id(cookie value) of the session created
            by a post
            @return: dict of session info

            """
            query = """select count(*) from organization"""
            result = db.query(query)
            if (not result):
                return None
            else:
                return result[0]

    def get_group_count(self, db):
            """
            Returns count of groups
            @param db: the database connection that will be utilized
            @param session_id: session_id(cookie value) of the session created
            by a post
            @return: dict of session info

            """
            query = """select count(*) from gatekeeper_group"""
            result = db.query(query)
            if (not result):
                return None
            else:
                return result[0]

    def get_app_by_app_name(self, db, app_name):
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
            if (not result):
                return None
            else:
                return result[0]

    def get_org_by_org_name(self, db, org_name):
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
            if (not result):
                return None
            else:
                return result[0]

    def get_permission_by_name(self, db, per_name, app_id):
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
            if (not result):
                return None
            else:
                return result[0]

    def get_group_by_name(self, db, grp_name):
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
            if (not result):
                return None
            else:
                return result[0]

    def get_verification_code_by_user_id(self, db, user_id):
            """
            deletes a user and cascade deletes from user_application

            @param db: the database connection that will be utilized

            @param app_id: application identifier
            @param user_id: user identifier
            @return: boolean

            """
            query = """
            select verification_code from verification
            where user_id=%d
            order by verification_id desc""" % (user_id)

            result = db.query(query)
            if (not result):
                return None
            else:
                return result[0]

    def get_org_by_orgname(self, db, orgname):
            """
            Returns user info based on a specific user name
            @param db: the database connection that will be utilized
            @param session_id: session_id(cookie value) of the session created
            by a post
            @return: dict of session info

            """
            query = """select *
                        from organization
                        where name='%s'""" % orgname
            result = db.query(query)
            if (not result):
                return None
            else:
                return result[0]

    def set_session_to_expire_by_session_id(self, db, cookie_id):
            """
            updates session info to be expired based on a specific session ID
            @param db: the database connection that will be utilized
            @param session_id: session_id(cookie value) of the session
            created by a post
            @return: dict of session info

            """
            query = """update cookie
                        set expiry_date = '2000-01-01 01:01:01'
                         where cookie_id='%s'""" % cookie_id

            result = db.trans(query)
            return result

    def set_gk_user(self, db, username, password, email, name, phone):
            """
            create a new user in the user_gatekeeper table
            @param db: the database connection that will be utilized
            @param session_id: session_id(cookie value) of the session
            created by a post
            @param db,username,password, email, name, phone: user details
            @return: boolean
            """

            query = """INSERT INTO
            gatekeeper_user(username, password, email, name, phone)
            VALUES ('%s','%s','%s','%s','%s');
            """ % (username, password, email, name, phone)

            result = db.trans(query)
            return result

    def set_gk_group(self, db, name):
            """
            create a new group in the group_gatekeeper table
            @param db: the database connection that will be utilized
            @param session_id: session_id(cookie value) of the session
            created by a post
            @param  name : group name
            @return: boolean

            """
            query = """INSERT INTO
            gatekeeper_group(name)
            VALUES ('%s');
            """ % (name)

            result = db.trans(query)
            return result

    def set_user_group(self, db, user_id, grp_id):
            """
            associate user with a group

            @param db: the database connection that will be utilized

            @param user_id: user id

            @param group_id : group_id

            @return: boolean

            """
            query = """INSERT INTO
            user_group(user_id,group_id)
            VALUES (%d,%d);
            """ % (user_id, grp_id)

            result = db.trans(query)
            return result

    def set_group_permission(self, db, grp_id, per_id):
            """
            associate a permission with a group

            @param db: the database connection that will be utilized

            @param per_id: permisions id

            @param group_id : group_id

            @return: boolean

            """
            query = """INSERT INTO
            group_permission(group_id,permission_id)
            VALUES (%d,%d);
            """ % (grp_id, per_id)

            result = db.trans(query)
            return result

    def set_app(self, db, app_name):
            """
            create a new application in the application table

            @param db: the database connection that will be utilized

            @param app_name: application_name

            @return: boolean

            """
            query = """INSERT INTO
            application(name)
            VALUES ('%s');
            """ % (app_name)

            result = db.trans(query)
            return result

    def set_user_app_id(self, db, app_id, user_id):
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

    def set_group_app_id(self, db, app_id, grp_id):
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

    def set_user_permissions_id(self, db, user_id, per_id):
            """
            associate a user with an application

            @param db: the database connection that will be utilized

            @param app_id: application identifier
            @param user_id: user identifier
            @return: boolean

            """
            query = """
            INSERT INTO
            user_permission(user_id,permission_id)
            VALUES (%d,%d);
            """ % (user_id, per_id)
            result = db.trans(query)
            return result

    def set_verification_code_to_expire_by_verification_code(
            self,
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

    def del_gk_user(self, db, user_id):
            """
            deletes a user and cascade deletes from user_application

            @param db: the database connection that will be utilized
            @param user_id: user identifier
            @return: boolean

            """
            query = """
            delete
            from gatekeeper_user
            where user_id='%s'""" % (user_id)
            result = db.trans(query)
            return result

    def del_gk_group(self, db, grp_id):
            """
            deletes a group and cascade deletes

            @param db: the database connection that will be utilized
            @param grp_id: froup identifier
            @return: boolean

            """
            query = """
            delete
            from gatekeeper_group
            where group_id=%d""" % (grp_id)
            result = db.trans(query)
            return result

    def del_app(self, db, app_id):
            """
            deletes an application

            @param db: the database connection that will be utilized

            @param app_id: application identifier
            @param user_id: user identifier
            @return: boolean

            """
            query = """
            delete
            from application
            where application_id=%d""" % (app_id)
            result = db.trans(query)
            return result
