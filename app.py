import json
from flask import Flask, Response, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import sqlalchemy.schema
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, query
from sqlalchemy.schema import PrimaryKeyConstraint
from sqlalchemy import JSON, Column, String, Integer, create_engine, Insert, select
import mysql.connector
from sqlalchemy.types import Enum, PickleType
import enum
from sqlalchemy.orm import sessionmaker
from sqlalchemy import MetaData
import os
import pickle
from dotenv import load_dotenv



load_dotenv() #load environment variables



app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://'+os.getenv("MYSQL_USERNAME")+ ':' + os.getenv("MYSQL_PASSWORD") + '@localhost/homey_db'

db = SQLAlchemy(app)
engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'], echo = True)
Session = sessionmaker(bind = engine)
session = Session()

# enums

class PropertyType(str, enum.Enum):
    RENT = "RENT"
    SALE = "SALE"

# models in the database are init here. make sure database parameters do not change!
# if changing any of the models, drop the table on sqlworkbench first, then reinitialise them.
# models
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

    
    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class Property(db.Model):
    __tablename__ = 'Property'
    PropertyID = Column('PropertyID', String(100), primary_key=True)
    ClusterID = Column('ClusterID', String(100))
    PropType = Column('PropType', Enum(PropertyType))
    # UserSaved = Column('UserSaved', )

    def __init__(self, PropertyID, ClusterID, PropType):
        self.PropertyID = PropertyID
        self.ClusterID = ClusterID
        self.PropType = PropType
    
    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class UserSavedProperty(db.Model):
    __tablename__ = 'SavedListings'
    UserID = Column('UserID', String(100))
    PropertyID = Column('PropertyID', String(100))
    Property = Column('Property', PickleType) 
    __table_args__ = (
        PrimaryKeyConstraint(UserID, PropertyID),
        {},
    )

    def __init__(self, UserID, PropertyID, Property):
        self.UserID = UserID
        self.PropertyID = PropertyID
        self.Property = Property

    def as_dict(self):
        dicout = {}
        for col in self.__table__.columns:

            if col.name=="UserID":
                dicout["UserID"] = getattr(self, col.name)
            if col.name=="PropertyID":
                dicout["PropertyID"] = getattr(self, col.name)
            if col.name=="Property":
                dicout["Property"] = pickle.loads(getattr(self,col.name))

        return dicout


# routes
@app.route("/createUser", methods=["POST"])
def createUser():
    # data = json.loads('{"UserID": 12, "Username": "hello", "Password": "1234", "Email": "hello@gmail.com", "SavedListings": 9, "Address": "clementi"}')
    data = request.get_json() #get json payload from the post req
    new_row = Accounts(UserID=data['UserID'], Username=data['Username'], Password=data['Password'], Email=data['Email'], SavedListings=data['SavedListings'], Address=data['Address'])
    db.session.add(new_row)
    db.session.commit()

    return "user created"

@app.route("/view/<int:user_id>", methods=["GET"])
def viewUser(user_id):
    if request.method == 'GET':
        account = db.session.query(Accounts).filter_by(UserID = user_id)

        if account.first() is None:
            return f"Account with UserID {user_id} does not exist"
        
        else:

            acc = account[0]

            accout = acc.as_dict()
            return json.dumps(accout)

            # return json.dumps("UserID: {acc.UserID}, Username: {acc.Username}, Password: {acc.Password}, Email: {acc.Email}, SavedListings: {acc.SavedListings}, Address: {acc.Address}}")



@app.route("/delete/<int:UserID>", methods=["GET"])
def deleteUser(UserID):
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

        if account.first() is None:
            return "Account no exist"
        else:
            return "Account successfully updated!"
    else: 
        return "update failed"
    

@app.route("/createProperty", methods=["POST"])
def createProperty():
    # data = json.loads('{"PropertyID": 1, "ClusterID": "1", "PropType": "RENT"}')
    data = request.get_json() #get json payload from the post req
    print(data)
    if "PropType" not in data:
        new_row = Property(PropertyID=data['PropertyID'], ClusterID=data['ClusterID'], PropType=PropertyType.RENT)
    else:
        new_row = Property(PropertyID=data['PropertyID'], ClusterID=data['ClusterID'], PropType=data["PropType"])
    db.session.add(new_row)
    db.session.commit()

    return "property created"

@app.route("/viewProperty/<int:prop_id>", methods=["GET"])
def viewProp(prop_id):
    if request.method == 'GET':
        property = db.session.query(Property).filter_by(PropertyID = prop_id)

        if property.first() is None:
            return f"Property with PropID {prop_id} does not exist"
        
        else:

            prop = property[0]
            propout = prop.as_dict()
            print(propout)
            return json.dumps(propout)

@app.route("/deleteProperty/<int:prop_id>", methods=["GET"])
def deleteProperty(prop_id):
    if request.method == 'GET':
        property = Property.query.filter_by(PropertyID=prop_id).first()
        if property is None:
            return f"Property with Property_ID {prop_id} does not exist"
        
        else:
            db.session.delete(property)
            db.session.commit()

            return f"Property with PropertyID {prop_id} has been deleted"
        
    else: 
        return "method not allowed"

@app.route("/updateProperty/<int:prop_id>", methods=["POST"])
def updateProperty(prop_id): 
    if request.method =="POST":
        property = db.session.query(Property).filter_by(PropertyID = prop_id)
        prop = property[0]
        data = request.get_json()

        prop.PropertyID = data['PropertyID']
        prop.ClusterID = data['ClusterID']
        prop.PropType = data['PropType']

        db.session.commit()

        if property.first() is None:
            return "Account no exist"
        else:
            return "Account successfully updated!"
    else: 
        return "update failed"




@app.route("/createUserSavedProperty", methods=["POST"])
def createUserSavedProperty():
    # data = json.loads({"UserID" : "1","PropertyID" : "1", "Property": {"UserID": 12, "ClusterID": "1", "PropType": "RENT"}})
    data = request.get_json()
    pickledProperty = pickle.dumps(data["Property"])
    new_row = UserSavedProperty(UserID=data["UserID"], PropertyID=data["PropertyID"], Property=pickledProperty)
    db.session.add(new_row)
    db.session.commit()

    return "usp created"

@app.route("/viewUSP/<int:user_id>", methods=["GET"])
def viewUSP(user_id):
    if request.method == 'GET':
        usp = db.session.query(UserSavedProperty).filter_by(UserID = user_id).all()
        if len(usp)==0:
            return f"User with UserID {user_id} has no saved listings"
        
        else:
            listout = []
            for savedListing in usp:
                listout.append(savedListing.as_dict())
            return json.dumps({"result": listout})

@app.route("/deleteUSP/<int:user_id>/<int:prop_id>", methods=["GET"])
def deleteUSP(user_id,prop_id):
    if request.method == 'GET':
        usp = UserSavedProperty.query.filter_by(UserID = user_id, PropertyID=prop_id).first()
        if usp is None:
            return f"USP does not exist"
        
        else:
            db.session.delete(usp)
            db.session.commit()

            return f"USP has been deleted"
        
    else: 
        return "method not allowed"
    

if __name__ == "__main__":
    app.app_context().push()
    db.create_all()
    app.run(host='0.0.0.0', debug=True)



#1) Check if user and property exists
#1.1) If user doesn't exists, exit (NOT_FOUND)
#1.2) if property doesn't exists, create new Property 
#2) if both property and user exists, create a new UserSavedProperty
#3) return all UserSavedProperty with matching userId