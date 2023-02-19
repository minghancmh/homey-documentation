import json
from flask import Flask, Response, render_template, request
from flask_sqlalchemy import SQLAlchemy
import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, query
from sqlalchemy import JSON, Column, String, Integer, create_engine, Insert, select
from sqlalchemy.sql.expression import update
import mysql.connector
from enum import Enum
from sqlalchemy.orm import sessionmaker
from sqlalchemy import MetaData
import os
from dotenv import load_dotenv
load_dotenv() #load environment variables



app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://'+os.getenv("MYSQL_USERNAME")+ ':' + os.getenv("MYSQL_PASSWORD") + '@localhost/homey_db'

db = SQLAlchemy(app)
engine = create_engine('mysql+mysqlconnector://root:mysqlmurong@localhost/homey_db', echo = True)
Session = sessionmaker(bind = engine)
session = Session()



class Accounts(db.Model): 
    __tablename__ = 'UserAccounts'
    UserID = Column('UserID', Integer, primary_key=True, unique=True)
    Username = Column('Username', String(100), unique=True)
    Password = Column('Password', String(100))
    Email = Column('Email', String(100))
    SavedListings = Column('SavedListings', Integer)
    Address = Column('Address', String(100))

    def __init__ (self, UserID, Username, Password, Email, SavedListings, Address):
        self.UserID = UserID
        self.Username = Username
        self.Password = Password
        self.Email = Email
        self.SavedListings = SavedListings
        self.Address = Address
    
    def __repr__(self):
        return f"{self.UserID} , {self.Username}"
    
    def as_dict(self):
        attr = ["UserID", "Username", "Password", "Email",]
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
    




@app.route("/createUser", methods=["POST", "GET"])
def create():
    # data = json.loads('{"UserID": 12, "Username": "hello", "Password": "1234", "Email": "hello@gmail.com", "SavedListings": 9, "Address": "clementi"}')
    data = request.get_json() #get json payload from the post req
    new_row = Accounts(UserID=data['UserID'], Username=data['Username'], Password=data['Password'], Email=data['Email'], SavedListings=data['SavedListings'], Address=data['Address'])
    db.session.add(new_row)
    db.session.commit()

    return "user created"

@app.route("/view/<int:user_id>", methods=["GET"])
def view(user_id):
    if request.method == 'GET':
        account = db.session.query(Accounts).filter_by(UserID = user_id)
        if account is None:
            return f"Account with UserID {user_id} does not exist"
        
        else:
            acc = account[0]
       
            accout = acc.as_dict()
            return json.dumps(accout)

            # return json.dumps("UserID: {acc.UserID}, Username: {acc.Username}, Password: {acc.Password}, Email: {acc.Email}, SavedListings: {acc.SavedListings}, Address: {acc.Address}}")



@app.route("/delete/<int:UserID>", methods=["POST", "GET"])
def delete(UserID):
    if request.method == 'GET':
        account = Accounts.query.filter_by(UserID=UserID).first()
        if account is None:
            return f"Account with UserID {UserID} does not exist"
        
        else:
            db.session.delete(account)
            db.session.commit()

            return f"Account with UserID {UserID} has been deleted"
        
    else: 
        return "method not allowed"
    
@app.route("/update/<int:user_id>", methods=["POST"])
def updateUser(user_id): 
    if request.method =="POST":
        account = db.session.query(Accounts).filter_by(UserID = user_id)
        acc = account[0]
        data = request.get_json()

        acc.UserID = data['UserID']
        acc.Username = data['Username']
        acc.Password = data['Password']
        acc.Email = data['Email']
        acc.SavedListings = data['SavedListings']
        acc.Address = data['Address']

        db.session.commit()

        if account is None:
            return "Account no exist"
        else:
            return "Account successfully updated!"
    else: 
        return "update failed"

if __name__ == "__main__":
    app.app_context().push()
    db.create_all()
    app.run(host='0.0.0.0', debug=True)