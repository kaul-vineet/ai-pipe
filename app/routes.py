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
    
    score = load_data('salesforce', 'case', conn)
    
    return score

def load_data(schema, table, conn):

    sql_command = "SELECT * FROM {}.{};".format(str(schema), str(table))
    print (sql_command)

    # Load the data
    data = pd.read_sql(sql_command, conn)
    

    data = data.drop(['external_id__c','subject','systemmodstamp','createddate','customer_type__c',
                  'isdeleted','casenumber','sfid','id','_hc_lastop','_hc_err'], axis=1)
    data['db_case_duration_hours__c'] = data['db_case_duration_hours__c'].fillna(data['db_case_duration_hours__c'].mode()[0])

    cat_columns = ["priority", "origin"]
    data = pd.get_dummies(data, prefix_sep="__", columns=cat_columns)

    X_train, X_test, y_train, y_test = train_test_split(data.drop('isclosed',axis=1), data['isclosed'], test_size=0.30, random_state=101)

    # instantiate the model (using the default parameters)
    logreg = LogisticRegression()

    # fit the model with data
    logreg.fit(X_train,y_train)

    #
    y_pred=logreg.predict(X_test)

    # Use score method to get accuracy of model
    score = logreg.score(X_test, y_test)
    return score
