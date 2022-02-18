# -*- coding: utf8 -*-
from psycopg2 import IntegrityError, InterfaceError,DatabaseError
import psycopg2
import time
import logging
class PostgresqlBackend(object):
    def __init__(self, host=None, user=None, password=None, dbname=None):
        self.host = host
        self.user = user
        self.password = password
        self.dbname = dbname
        self.conn = self.make_connection()

    def make_connection(self):
        return psycopg2.connect(host=self.host, 
                                user=self.user, 
                                password=self.password, 
                                database=self.dbname, 
                                port=5432)

    def insert(self, db_table, item, data):
        sql = '''
        insert into %s (item, data) values ('%s', '%s');
        ''' %(db_table, item, data)
        print(sql)
        self.insert_sql(sql)

    def insert_sql(self, sql):
        while True:
            try:
                cur = self.conn.cursor()
                cur.execute(sql)
                self.conn.commit()
                return
            except IntegrityError:
                break
            except DatabaseError as e:
                logging.error('database error %s' %str(e))
                time.sleep(20)
            except InterfaceError:
                logging.error('interface error')
                time.sleep(20)
                self.conn = self.make_connection()
            except Exception as e:
                logging.error('database unknown error %s' %str(e))
                raise Exception
