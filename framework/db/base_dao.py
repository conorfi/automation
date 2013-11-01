from sqlalchemy import create_engine
from testconfig import config

class BaseDAO():

    def __init__(self,config):
        if :    
        self.db_conn = self.create_engine(config['tms']['db_type'] + config['tms']['db'])    
        connection = self.db_conn.connect() 
               
    def query(self,query): 			
		result = connection.execute(query)		        

        