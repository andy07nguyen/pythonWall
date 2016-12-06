from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text

# create a class that will give us an object that we can use to connect to database

class MySQLConnection(object):
    def __init__(self, app, db):
        config = {
                'host': 'localhost',
                'database': db,
                'user': 'root',
                'password': 'root',
                'port': '8889'
        }
        DATABASE_URI = "mysql://{}:{}@127.0.0.1:{}/{}".format(config['user'], config['password'], config['port'], config['database'])
        app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=True
        #establish connection to database
        self.db = SQLAlchemy(app)
    def query_db(self, query, data=None):
        result = self.db.session.execute(text(query), data)
        if query[0:6].lower() == 'select':
            #if the query was a select
            #convert the result to a list of dictionaries
            list_result = [dict(r) for r in result]
            #return the results as a list of dictionaries
            return list_result
        elif query[0:6].lower() == 'insert':
            #return the id of the commit changes
            self.db.session.commit()
            return result.lastrowid
        else:
            #if query is update or delete, return nothing, commit changes
            self.db.session.commit()

def MySQLConnector(app, db):
    return MySQLConnection(app, db)
