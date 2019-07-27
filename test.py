import matplotlib.pyplot as plt
from matplotlib import figure
import mpld3
import pandas as pd
import sqlite3
from flask import Flask, request, render_template, session, flash, redirect
import sqlite3
import os


app = Flask(__name__)
app.config['DEBUG'] = True

# project_dir = os.path.dirname(os.path.abspath(__file__))
# app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///{}".format(os.path.join(project_dir, "capitalone.db"))
# app.config['SQLALCHEMY_ECHO'] = False
# db = SQLAlchemy(app)
# app.secret_key = secret_key

# car_data = pd.read_csv('sheets/2019-07-27_transaction_download.csv')

# print(car_data['Category'].unique())
# print("___________________________________")
# print(car_data.head(2))
# print("___________________________________")
# print(car_data.columns)
# print("___________________________________")

# table_data = pd.read_csv (file_name+'.csv') 
#     table_data2 = table_data[['Posted Date','Card No.','Description','Category','Debit','Credit']]
#     table_data1 = table_data[['Card No.','Category','Debit']]
#     groupby_sum1 = table_data1.groupby(['Card No.','Category']).sum() 

con = sqlite3.connect("capitalone.db")
cur = con.cursor()
cur.execute("SELECT DISTINCT Category FROM {0};".format("May2019"))
categories = cur.fetchall()
categories2 = []
for category in categories:
    categories2.append(category[0])
totals = []
category3 = []
for category in categories2:
    cur.execute("SELECT SUM(Debit) FROM {0} WHERE Category = '{1}';".format("May2019", category))
    totals.append(cur.fetchall()[0][0])
    category3.append(category)

figure = plt.figure(figsize=(12, 10))
plt.plot(category3,totals)
figure.savefig('static/images/myfig.png')

@app.route("/")
def main_page():
    return render_template('test.html')

app.run()