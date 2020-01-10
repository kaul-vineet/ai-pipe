from app import app
import psycopg2
import sys, os
import numpy as np
import pandas as pd

@app.route('/')
@app.route('/index')
def index():
    import os
    import psycopg2

    # DATABASE_URL = os.environ['DATABASE_URL']
    DATABASE_URL = 'postgres://hmbadfwsbybxwc:6a9dd36753cacb0db21da38307159a534d85b41a1c511a40f0099cabc04f9680@ec2-107-21-97-5.compute-1.amazonaws.com:5432/dc7d4entntij7b'
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    print("Connected!")
    
    data = load_data('salesforce', 'case', conn)
    
    return "Hello, World!"

def load_data(schema, table, conn):

    sql_command = "SELECT * FROM {}.{};".format(str(schema), str(table))
    print (sql_command)

    # Load the data
    data = pd.read_sql(sql_command, conn)

    print(data.shape)
    return (data)
