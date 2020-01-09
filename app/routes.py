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

    DATABASE_URL = os.environ['DATABASE_URL']

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
