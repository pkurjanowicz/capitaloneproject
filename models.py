from app import db
from hashutils import make_pw_hash, make_salt, check_pw_hash
import sqlite3
import pandas as pd

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    pw_hash = db.Column(db.String(120))
    
    def __init__(self, email, password):
        self.email = email
        self.pw_hash = make_pw_hash(password)

    def __repr__(self):
        return '<User %r>' % self.email

def create_new_table(csv_data,table_name):
    #ask user for sheet name and new table name
    csv_data = str(csv_data)
    table_name = str(table_name)
    #connect to database
    con = sqlite3.connect("capitalone.db")
    cur = con.cursor()
    #create database
    cur.execute("CREATE TABLE {0} (Transaction_Date,Posted_Date,Card_No,Description,Category,Debit,Credit);".format(table_name))
    #update database with column names
    column_names = ['Stage','Transaction_Date','Posted_Date','Card_No','Description','Category','Debit','Credit']
    df = pd.read_csv(csv_data+'.csv',names=column_names) 
    df = df.iloc[1:]
    df.to_sql(table_name, con, if_exists='append', index=False)
    con.commit()
    con.close()
    return str(table_name)+" has been created!"

def create_new_user(email,password):
    user = User(email=email, password=password)
    db.session.add(user)
    db.session.commit()

def connect_to_db():
    return sqlite3.connect("capitalone.db")

def list_of_tables():
    con = connect_to_db()
    return con.execute("SELECT name FROM sqlite_master WHERE type='table';")

