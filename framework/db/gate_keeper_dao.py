'''
@summary: Contains a set of database functions for the gatekeeper project

@since: Created on November 6th 2013

@author: Conor Fitzgerald

'''

from sqlalchemy import create_engine
from framework.db.base_dao import BaseDAO

class GateKeeperDAO(object):
      
    def get_session_by_session_id(self,db,session_id):
            '''    
            Returns session info based on a specific session ID
        
            @param db: the database connection that will be utilized
        
            @param session_id: session_id(cookie value) of the session created bya post
        
            @return: dict of session info
            
            ''' 
            query ="""select session_id,user_id 
                        from session
                         where session_id='%s'"""  % session_id
            result = db.query(query)
            if (not result):
                return None                
            else:
                return result[0]          
    
    def get_user_id_by_username(self,db,username):
            '''    
            Returns user id based on a specific user id
        
            @param db: the database connection that will be utilized
        
            @param session_id: session_id(cookie value) of the session created bya post
        
            @return: dict of session info
            
            ''' 
            query ="""select user_id 
                        from gatekeeper_user
                         where username='%s'"""  % username
            result = db.query(query)
            if (not result):
                return None                
            else:
                return result[0]
    
    def get_app_id_by_app_name(self,db,app_name):
            '''    
            Returns app id based on app name
        
            @param db: the database connection that will be utilized
        
            @param session_id: session_id(cookie value) of the session created bya post
        
            @return: dict of app info
            
            ''' 
            query ="""select application_id
                        from application
                         where name='%s'"""  % app_name
            result = db.query(query)
            if (not result):
                return None                
            else:
                return result[0]
    
    def get_permission_id_by_name(self,db,per_name):
            '''    
            Returns permission id based on per name
        
            @param db: the database connection that will be utilized
        
            @param per_name: permission name
        
            @return: permission id
            
            ''' 
            query ="""select permission_id
                        from permission
                         where name='%s'"""  % per_name
            result = db.query(query)
            if (not result):
                return None                
            else:
                return result[0]
    
    def get_gk_group_id_by_name(self,db,grp_name):
            '''    
            Returns group id based on group name
        
            @param db: the database connection that will be utilized
        
            @param grp_name: group name
        
            @return: group id
            
            ''' 
            query ="""select group_id
                        from gatekeeper_group
                        where name='%s'"""  % grp_name
            result = db.query(query)
            if (not result):
                return None                
            else:
                return result[0]
                                     
    def set_session_to_expire_by_session_id(self,db,session_id):
            '''    
            updates session info to be expired based on a specific session ID
        
            @param db: the database connection that will be utilized
        
            @param session_id: session_id(cookie value) of the session created bya post
        
            @return: dict of session info
            
            ''' 
            query ="""update session 
                        set expiry_date = '2000-01-01 01:01:01'
                         where session_id='%s'"""  % session_id
                                    
            result = db.trans(query)
            return result
    
    def set_gk_user(self,db,username,password, email, name, phone):
            '''    
            create a new user in the user_gatekeeper table
        
            @param db: the database connection that will be utilized
        
            @param session_id: session_id(cookie value) of the session created by a post
            
            @param db,username,password, email, name, phone: user details
        
            @return: boolean
            
            ''' 
            query = """INSERT INTO 
            gatekeeper_user(username, password, email, name, phone) 
            VALUES ('%s','%s','%s','%s','%s');
            """ % (username,password, email, name, phone)
            
            result = db.trans(query)
            return result         
    
    def set_gk_group(self,db,name):
            '''    
            create a new group in the group_gatekeeper table
        
            @param db: the database connection that will be utilized
        
            @param session_id: session_id(cookie value) of the session created by a post
            
            @param  name : group name
        
            @return: boolean
            
            ''' 
            query = """INSERT INTO 
            gatekeeper_group(name) 
            VALUES ('%s');
            """ % (name)
            
            result = db.trans(query)
            return result         
    
    def set_user_group(self,db,user_id,grp_id):
            '''    
            associate user with a group
        
            @param db: the database connection that will be utilized
        
            @param user_id: user id
            
            @param group_id : group_id
        
            @return: boolean
            
            ''' 
            query = """INSERT INTO 
            user_group(user_id,group_id) 
            VALUES (%d,%d);
            """ % (user_id,grp_id)
            
            result = db.trans(query)
            return result         
    
    def set_group_permission(self,db,grp_id,per_id):
            '''    
            associate a permission with a group
        
            @param db: the database connection that will be utilized
        
            @param per_id: permisions id
            
            @param group_id : group_id
        
            @return: boolean
            
            ''' 
            query = """INSERT INTO 
            group_permission(group_id,permission_id) 
            VALUES (%d,%d);
            """ % (grp_id,per_id)
            
            result = db.trans(query)
            return result        
                          
    def set_app(self,db,app_name):
            '''    
            create a new application in the application table
        
            @param db: the database connection that will be utilized
        
            @param app_name: application_name 
           
            @return: boolean
            
            ''' 
            query = """INSERT INTO 
            application(name) 
            VALUES ('%s');
            """ % (app_name)
            
            result = db.trans(query)
            return result     
               
    def set_user_app_id(self,db,app_id,user_id):
            '''    
            associate a user with an application
        
            @param db: the database connection that will be utilized
        
            @param app_id: application identifier
            @param user_id: user identifier
            @return: boolean
            
            ''' 
            query = """
            INSERT INTO 
            user_application(application_id, user_id)
            VALUES (%d,%d);
            """ % (app_id,user_id)            
            result = db.trans(query)
            return result      
    
    def set_group_app_id(self,db,app_id,grp_id):
            '''    
            associate a user with an application
        
            @param db: the database connection that will be utilized
        
            @param app_id: application identifier
            @param grp_id: group identifier
            @return: boolean
            
            ''' 
            query = """
            INSERT INTO 
            group_application(application_id, group_id)
            VALUES (%d,%d);
            """ % (app_id,grp_id)            
            result = db.trans(query)
            return result      
                  
    def set_user_permissions_id(self,db,user_id,per_id):
            '''    
            associate a user with an application
        
            @param db: the database connection that will be utilized
        
            @param app_id: application identifier
            @param user_id: user identifier
            @return: boolean
            
            ''' 
            query = """
            INSERT INTO 
            user_permission(user_id,permission_id)
            VALUES (%d,%d);
            """ % (user_id,per_id)            
            result = db.trans(query)
            return result                     
                
    def del_gk_user(self,db,user_id):
            '''    
            deletes a user and cascade deletes from user_application
        
            @param db: the database connection that will be utilized
            @param user_id: user identifier
            @return: boolean
            
            ''' 
            query = """
            delete 
            from gatekeeper_user
            where user_id='%s'""" % (user_id)            
            result = db.trans(query)
            return result     
        
    def del_gk_group(self,db,grp_id):
            '''    
            deletes a group and cascade deletes 
        
            @param db: the database connection that will be utilized       
            @param grp_id: froup identifier
            @return: boolean
            
            ''' 
            query = """
            delete  
            from gatekeeper_group
            where group_id=%d""" % (grp_id)            
            result = db.trans(query)
            return result       
        
    def del_app(self,db,app_id):
            '''    
            deletes an application
        
            @param db: the database connection that will be utilized
        
            @param app_id: application identifier
            @param user_id: user identifier
            @return: boolean
            
            ''' 
            query = """
            delete 
            from application
            where application_id=%d""" % (app_id)            
            result = db.trans(query)
            return result       
        
    def del_(self,db,user_id):
            '''    
            deletes a user and cascade deletes from user_application
        
            @param db: the database connection that will be utilized
        
            @param app_id: application identifier
            @param user_id: user identifier
            @return: boolean
            
            ''' 
            query = """
            delete  
            from gatekeeper_user
            where user_id=%d""" % (user_id)            
            result = db.trans(query)
            return result               