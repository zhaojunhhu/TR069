# -*- coding: utf-8 -*- 

import  traceback
import  os
import  sys
import  inspect
from    datetime                        import  datetime, timedelta
import  MySQLdb                         as      mdb


from    TR069.lib.common.releasecfg           import  *   # log for tr069 self or RF?
import  TR069.lib.acss.acs.webservercfg         as      webservercfg
from    TR069.lib.common.function       import  print_trace
  
# special
import  MySQLdb                         as      mdb
import  pyodbc


class Database(object):
    """
    """    
        
    def __init__(self, 
                    driver          = webservercfg.DB_DRIVER, 
                    server          = webservercfg.DB_SERVER, 
                    port            = webservercfg.DB_PORT,
                    database        = webservercfg.DB_DATABASE, 
                    uid             = webservercfg.DB_UID, 
                    pwd             = webservercfg.DB_PWD,                      
                    charset         = webservercfg.DB_CHARSET):
        """
        
        """
        self.driver         = driver
        self.server         = server 
        self.port           = port
        self.database       = database
        self.uid            = uid
        self.pwd            = pwd                
        self.charset        = charset
        
        self.conn = pyodbc.connect( driver          = self.driver,
                                    server          = self.server, 
                                    port            = self.port,
                                    database        = self.database,
                                    uid             = self.uid,
                                    pwd             = self.pwd,                                                                         
                                    charset         = self.charset,
                                    autocommit      = True)  
        self.cur = self.conn.cursor()                                            


    # auto        
    def __del__(self):
        """
        """
        try:
            self.cur.close()
        except Exception,e:
            print_trace(e)        

        try:
            self.conn.close()
        except Exception,e:
            print_trace(e) 
            

    # api ----------------------------------------------------
    def execute(self, sql):
        """
        """      
        try:
            return self.cur.execute(sql)
        except Exception,e:
            # show sql ; nwf 2014-05-30
            e_sql = "SQL execute fail:sql=%s\n%s" %(sql, e.args[1])
            raise Exception(e_sql)

    
    def fetchall(self):
        """
        """
        return self.cur.fetchall()


    def fetchone(self):
        """
        """
        return self.cur.fetchone()


    # assist  -----------------------------------------------
    def escape_string(self, string):
        return mdb.escape_string(string)


if __name__ == '__main__':
    pass
