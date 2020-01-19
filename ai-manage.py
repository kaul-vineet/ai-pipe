from flask_script import Manager

from app import app

import psycopg2
import sys, os
import numpy as np
import pandas as pd
import datetime

import pandas as pd
import numpy as np

#visualisation
#import matplotlib.pyplot as plt
#import seaborn as sns

#prep 
from sklearn.model_selection import train_test_split, GridSearchCV, RandomizedSearchCV
from sklearn.preprocessing import LabelEncoder, StandardScaler, MaxAbsScaler, QuantileTransformer, OneHotEncoder

#models
from sklearn.linear_model import LogisticRegression, LogisticRegressionCV, LinearRegression, Ridge, RidgeCV

#database
import os
import psycopg2

    
manager = Manager(app)


@manager.command
def calculatemetrics():
    # DATABASE_URL = os.environ['DATABASE_URL']

    schema = "salesforce"
    table = "case"
    
    DATABASE_URL = 'postgres://hmbadfwsbybxwc:6a9dd36753cacb0db21da38307159a534d85b41a1c511a40f0099cabc04f9680@ec2-107-21-97-5.compute-1.amazonaws.com:5432/dc7d4entntij7b'
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    print("CONNECTED TO DATABASE!")
    
    
    sql_command = "SELECT * FROM {}.{};".format(str(schema), str(table))
    # Load the data
    data = pd.read_sql(sql_command, conn)
    dfsize = data.size
    print(str(dfsize) + " RECORDS LOADED TO PANDAS!")
    
    data = data.drop(['valid__c','reason','external_id__c','subject','systemmodstamp','createddate','customer_type__c',
                  'isdeleted','casenumber','sfid','id','_hc_lastop','_hc_err'], axis=1)
    data['db_case_duration_hours__c'] = data['db_case_duration_hours__c'].fillna(data['db_case_duration_hours__c'].mode()[0])
    cat_columns = ["priority", "origin", "type"]
    data = pd.get_dummies(data, prefix_sep="__", columns=cat_columns)
    X_train, X_test, y_train, y_test = train_test_split(data.drop('isclosed',axis=1), data['isclosed'], test_size=0.30, random_state=101)
    print("DATA PREPARED FOR TRAINING AND TESTING!")
    
    # instantiate the model (using the default parameters)
    logreg = LogisticRegression()

    # fit the model with data
    logreg.fit(X_train,y_train)
    y_pred=logreg.predict(X_test)
    print("MODEL TRAINED!")

    # Use score method to get accuracy of model
    score = logreg.score(X_test, y_test)
    print("SCORE CALCULATED!")
    
    cur = conn.cursor()
    cur.execute("INSERT INTO public.modelmetrics(model_score, model_timestamp, model_recordcount) VALUES (%s, %s, %s)", (truncate(score, 3), str(datetime.datetime.now())), dfsize)
    conn.commit()
    print("SCORE DETAILS SAVED!")
    print("METRICS CALCULATION COMPLETED")

def truncate(n, decimals=0):
    multiplier = 10 ** decimals
    return int(n * multiplier) / multiplier

if __name__ == "__main__":
    manager.run()
