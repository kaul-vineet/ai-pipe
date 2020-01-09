from app import app

@app.route('/')
@app.route('/index')
def index():
    import os
    import psycopg2

    DATABASE_URL = os.environ['DATABASE_URL']

    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    return "Hello, World!"
