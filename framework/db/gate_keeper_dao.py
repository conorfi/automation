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
        
    