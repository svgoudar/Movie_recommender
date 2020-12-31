# from flaskext.mysql import MySQL

# from flask_sqlalchemy import SQLAlchemy
from psycopg2 import connect
import os

def connection(app):
    # mysql = MySQL()
    # connection = connect(user="ytxlxwlysehdbe",
    #                               password="f48ba2aec3b7f09a41bc2d0b4d48644c202b01d7fd9499a54833c0be9282bf8d",
    #                               host="ec2-75-101-232-85.compute-1.amazonaws.com",
    #                               port="5432",
    #                               database="ddlj5rrgii4pdl")
   conn = connect(user="ytxlxwlysehdbe",
                                  password="f48ba2aec3b7f09a41bc2d0b4d48644c202b01d7fd9499a54833c0be9282bf8d",
                                  host="ec2-75-101-232-85.compute-1.amazonaws.com",
                                  port="5432",
                                  database="ddlj5rrgii4pdl"
                                  )

    # app.config['MYSQL_DATABASE_USER'] = config.dbuser
    # app.config['MYSQL_DATABASE_PASSWORD'] = config.dbpassword
    # app.config['MYSQL_DATABASE_DB'] = config.dbname
    # app.config['MYSQL_DATABASE_HOST'] = config.dbhost
    cursor = conn.cursor()
    # mysql.init_app(app)
    # conn = mysql.connect()
    # cursor = conn.cursor()
    # SQLAlchemy(app)
    return cursor, conn
