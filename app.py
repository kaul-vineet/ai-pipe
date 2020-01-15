from flask import Flask, render_template,request
import psycopg2
import sys, os
import numpy as np
import pandas as pd
import datetime

import pandas as pd
import numpy as np
import json

#visualisation
#import matplotlib.pyplot as plt
import seaborn as sns
#import matplotlib.animation as animation

from flask import Flask, render_template,request
import plotly
import plotly.graph_objs as go

app = Flask(__name__)

@app.route('/')
@app.route('/index')
def index():
    feature = 'Bar'
    bar = create_plot(feature)
    return render_template('index.html', plot=bar)

def create_plot(feature):
    if feature == 'Bar':
        N = 40
        x = np.linspace(0, 1, N)
        y = np.random.randn(N)
        df = pd.DataFrame({'x': x, 'y': y}) # creating a sample dataframe
        data = [
            go.Bar(
                x=df['x'], # assign x as the dataframe column 'x'
                y=df['y']
            )
        ]
    else:
        N = 1000
        random_x = np.random.randn(N)
        random_y = np.random.randn(N)

        # Create a trace
        data = [go.Scatter(
            x = random_x,
            y = random_y,
            mode = 'markers'
        )]


    graphJSON = json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)

    return graphJSON

@app.route('/bar', methods=['GET', 'POST'])
def change_features():

    feature = request.args['selected']
    graphJSON= create_plot(feature)




    return graphJSON

def load_data(schema, table, conn):
    # DATABASE_URL = os.environ['DATABASE_URL']
    DATABASE_URL = 'postgres://hmbadfwsbybxwc:6a9dd36753cacb0db21da38307159a534d85b41a1c511a40f0099cabc04f9680@ec2-107-21-97-5.compute-1.amazonaws.com:5432/dc7d4entntij7b'
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    print("Connected!")

    score = load_data('salesforce', 'case', conn)

    sql_command = "SELECT * FROM {}.{};".format(str(schema), str(table))
    print(sql_command)

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

    cur = conn.cursor()
    cur.execute("INSERT INTO public.modelmetrics(model_score, model_timestamp) VALUES (%s, %s)", (truncate(score, 3), str(datetime.datetime.now())))
    conn.commit()

    return str(score)


def truncate(n, decimals=0):
    multiplier = 10 ** decimals
    return int(n * multiplier) / multiplier

if __name__ == '__main__':
    app.run()
    