'''
@summary: Contains a set of base/core database functions

@since: Created on November 6th 2013

@author: Conor Fitzgerald

'''

from sqlalchemy import create_engine
from testconfig import config

class BaseDAO():

    '''def __init__(self,config=None):
        if (config == None):    
            #self.db_conn = self.create_engine(config['tms']['db_type'] + config['tms']['db'])  
            self.db_conn = create_engine('postgresql://postgres:postgres@10.20.254.142:5433/gatekeeper')   
        try:
            self.connection = self.db_conn.connect() 
        except Exception, e:            
            raise e       
    '''
    
    def __init__(self,db_config):
        
        self.db_conn = create_engine(db_config)   
        self.connection = self.db_conn.connect()      
      
    def query(self,query): 
        '''    
        function to run raw select queries
    
        @param query: query e.g select a from b where c=123  
           
        @return: list of dicts representing the table rows
        
        '''      
        results = self.connection.execute(query)  
        fetched_results = results.fetchall()
        rows_as_dict= []
        for row in fetched_results:
            rows_as_dict.append(dict(row))
                     
        return rows_as_dict  
     
    def trans(self,query):
        '''    
        function to run raw updates,commits and delete queries
    
        @param query: query e.g select a from b where c=123  
           
        @return: 
        
        '''     
        
        trans = self.connection.begin()
        try:
            self.connection.execute(query)
            trans.commit()
            return True
        except:
            trans.rollback()
            raise   
            return False
        finally:
            self.connection.close()
        