from flask import Flask, request, render_template, session, flash, redirect
import pandas as pd
import csv
import sqlite3
from flask_sqlalchemy import SQLAlchemy 
import os
from secrets import secret_key
from hashutils import make_pw_hash, check_pw_hash
from os import walk
import matplotlib.pyplot as plt
from matplotlib import figure
from app import app, db
from models import User, create_new_table, create_new_user, list_of_tables, connect_to_db

app.secret_key = secret_key

def is_email(string):
    atsign_index = string.find('@')
    atsign_present = atsign_index >= 0
    if not atsign_present:
        return False
    else:
        domain_dot_index = string.find('.', atsign_index)
        domain_dot_present = domain_dot_index >= 0
        return domain_dot_present

def file_names_in_sheets_directory():
    names = []
    for (dirpath, dirnames, filenames) in walk('sheets'):
        names += filenames
    return names

#gathers data from CSV and takes into account credits(row 7) and debits(row 6)#
def combined_totals(csv_data):
    try:
        with open(csv_data+'.csv') as csvfile:
            csvreader = csv.reader(csvfile) 
            fields = next(csvreader) 
            Jess_amount = 0
            Pete_amount = 0
            for row in csvreader:
                if row[4] == 'Payment/Credit':
                    Pete_amount += float(row[6])
                if row[5] != '' and row[2] == "9246":
                    Pete_amount += float(row[5])
                if row[5] != '' and row[2] == "717":
                    Jess_amount += float(row[5])
                if row[6] != '' and row[2] == "9246":
                    Pete_amount -= float(row[6])
                if row[6] != '' and row[2] == "717":
                    Jess_amount -= float(row[6])
        return round(Pete_amount,2),round(Jess_amount,2)
    except FileNotFoundError:
        return ""

def adjustments(file):
    file_name = file
    jess_adjustment = request.form["jess_adjustment"]
    pete_adjustment = request.form["pete_adjustment"]
    pete_amount,jess_amount = combined_totals(file_name)
    if jess_adjustment == '' or jess_adjustment == '0':
        jess_adjustment = 0
        pete_final_amount = pete_amount
    if pete_adjustment == '' or pete_adjustment == '0':
        pete_adjustment = 0
        jess_final_amount = jess_amount
    if jess_adjustment != 0 and pete_adjustment == 0:
        pete_final_amount = pete_amount + float(jess_adjustment)
        jess_final_amount = jess_amount - float(jess_adjustment)
    if pete_adjustment != 0 and jess_adjustment == 0:
        jess_final_amount = jess_amount + float(pete_adjustment)
        pete_final_amount = pete_amount - float(pete_adjustment)
    if pete_adjustment != 0 and jess_adjustment != 0:
        difference = float(pete_adjustment) - float(jess_adjustment)
        if difference > 0:
            jess_final_amount = jess_amount + difference
            pete_final_amount = pete_amount 
        else:
            pete_final_amount = pete_amount + (difference * -1)
            jess_final_amount = jess_amount 
    pete_final_amount = round(pete_final_amount,2)
    jess_final_amount = round(jess_final_amount,2)
    return pete_final_amount, jess_final_amount, pete_adjustment, jess_adjustment

@app.route("/")
def main_page():
    file_names = file_names_in_sheets_directory()
    return render_template('htmldoc.html', do_not_display=None, file_names=file_names)

@app.route("/logout", methods=["GET"])
def logout():
    del session['user']
    return redirect("/login")

@app.route("/totals", methods=["POST", "GET"])
def totals():
    try:
        if request.form["csv_file"][:7] == "Sheets/":
            file_name = request.form["csv_file"]
            if request.form["csv_file"][-4:] == '.csv':
                file_name = request.form["csv_file"][:-4]
            pete_final_amount, jess_final_amount, pete_adjustment, jess_adjustment = adjustments(file_name)
            return render_template('totals.html',pete_amount=str(pete_final_amount),jess_amount=str(jess_final_amount),
                table_made="No table created", csv_file=file_name, do_not_display=123, 
                jess_adjustment= jess_adjustment, pete_adjustment= pete_adjustment)
        else:
            if request.form["csv_file"][-4:] == '.csv':
                file_name = request.form["csv_file"][:-4]
            else:
                file_name = request.form["csv_file"]
            file_name = "Sheets/"+file_name
            pete_final_amount, jess_final_amount, pete_adjustment, jess_adjustment = adjustments(file_name)
            #make new table in SQLite database
            table_name = request.form["table_name"]
            table_name = table_name.replace(" ", "") #get rid of spaces
            table_name = ''.join(e for e in table_name if e.isalnum()) #get rid of special characters
            if table_name != '':
                try:
                    table_made = create_new_table(file_name,table_name)
                except sqlite3.OperationalError:
                    table_made = ("Table with that name already exists")
            if table_name != '':
                return render_template('totals.html',pete_amount=str(pete_final_amount),jess_amount=str(jess_final_amount),
                    table_made=table_made, csv_file=file_name, do_not_display=123, 
                    jess_adjustment= jess_adjustment, pete_adjustment= pete_adjustment)
            else:
                return render_template('totals.html',pete_amount=str(pete_final_amount),jess_amount=str(jess_final_amount),
                    table_made="No table created", csv_file=file_name, do_not_display=123, 
                    jess_adjustment= jess_adjustment, pete_adjustment= pete_adjustment)
    except ValueError:
        flash('No spreadsheet found', 'error')
        return redirect('/')

@app.route("/table-data", methods=["POST", "GET"])
def table_data():
    file_name = request.form["csv_file"]
    jess_adjustment = request.form["jess_adjustment"]
    pete_adjustment = request.form["pete_adjustment"]
    table_data = pd.read_csv (file_name+'.csv') 
    table_data2 = table_data[['Posted Date','Card No.','Description','Category','Debit','Credit']]
    table_data1 = table_data[['Card No.','Category','Debit']]
    groupby_sum1 = table_data1.groupby(['Card No.','Category']).sum() 
    return render_template("table_data.html", data=(groupby_sum1.to_html(classes='table')),
    data_raw=(table_data2.to_html(classes='table')), do_not_display=123, csv_file=file_name, 
    jess_adjustment= jess_adjustment, pete_adjustment= pete_adjustment)

@app.route("/past-data", methods=["POST", "GET"])
def past_data():
    file_name = request.form["csv_file"]
    jess_adjustment = request.form["jess_adjustment"]
    pete_adjustment = request.form["pete_adjustment"]
    con = connect_to_db()
    raw_data = list_of_tables()
    table_list =[]
    for name in raw_data:
        if name[0] != "user":
            table_list.append(name[0])
    if request.method == "POST" and request.form['table_list'] != '':
        jess_adjustment = request.form["jess_adjustment"]
        pete_adjustment = request.form["pete_adjustment"]
        table_name = request.form['table_list']
        data = pd.read_sql_query(f"select * from {table_name};", con)
        return render_template("past_data.html", list=table_list, data=(data.to_html(classes='table')), 
        table_name=table_name, do_not_display=123,csv_file=file_name, jess_adjustment= jess_adjustment, pete_adjustment= pete_adjustment)
    return render_template("past_data.html", list=table_list, do_not_display=123,csv_file= file_name, 
    jess_adjustment= jess_adjustment, pete_adjustment= pete_adjustment)

@app.route("/graphs", methods=['POST', 'GET'])
def graphs():
    file_name = request.form["csv_file"]
    jess_adjustment = request.form["jess_adjustment"]
    pete_adjustment = request.form["pete_adjustment"]
    return render_template('underconstruction.html', do_not_display=123, csv_file= file_name, 
    jess_adjustment= jess_adjustment, pete_adjustment= pete_adjustment) #page under construction
    file_name = request.form["csv_file"]
    jess_adjustment = request.form["jess_adjustment"]
    pete_adjustment = request.form["pete_adjustment"]
    con = connect_to_db()
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
    return render_template('graphs.html', do_not_display=123, csv_file= file_name, 
    jess_adjustment= jess_adjustment, pete_adjustment= pete_adjustment)

@app.route("/login", methods=['POST', 'GET'])
def login():
    session['user'] = ''
    if request.method == "POST":
        email = request.form['email']
        user = User.query.filter_by(email=email).first()
        password = request.form['password']
        if check_pw_hash(password, user.pw_hash):
            session['user'] = user.email
            return redirect("/")
        else:
            flash('username or password not found', 'error')
            return redirect('/login')
    return render_template("login.html",login=1)

@app.route("/register", methods=['POST', 'GET'])
def register():
    session['user'] = ''
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        verify = request.form['verify']
        if not is_email(email):
            flash('zoiks! "' + email + '" does not seem like an email address')
            return redirect('/register')
        if not password == verify:
            flash('zoiks! password does not match')
            return redirect('/register')
        existing_user = User.query.filter_by(email=email).first()
        if not existing_user:
            create_new_user(email,password)
            session['user'] = user.email
            return redirect("/")
        else:
            flash("This is a duplicate email", 'error')
            return redirect("/register", login=1)
    else:
        return render_template('register.html', login=1)

@app.before_request
def require_login():
    if not ('user' in session or request.endpoint == 'register' or request.endpoint == 'login'):
        return redirect("/login")

if __name__ == "__main__":
    app.run()