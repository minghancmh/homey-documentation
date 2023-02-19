import mysql.connector
from mysql.connector import Error
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv() #load environment variables



try:
    connection = mysql.connector.connect(host='localhost',
                                         database='homey_db',
                                         user=os.getenv("MYSQL_USERNAME"),
                                         password=os.getenv("MYSQL_PASSWORD"))


    ###### ENTER THE SQL QUERY HERE #######
    my_sql_query = """
        SELECT * FROM ACCOUNTS;

                    """

    #######################################
    if connection.is_connected():
        db_Info = connection.get_server_info()
        print("Connected to MySQL Server version ", db_Info)
        cursor = connection.cursor()
        #write sql commands below
        cursor.execute(my_sql_query)


        #sample view all functionality
        #SELECT * FROM Accounts;
        #sample create functionality (must do connection.commit to commit the change to the db)
        # INSERT INTO Accounts(UserID, Username, Password, Email, SavedListings)
        # VALUES(2,'murong', 'murong', 'murong@mgila.com', 10);

        myresult = cursor.fetchall()
        for x in myresult:
            print(x)

        connection.commit()


except Error as e:
    print("Error while connecting to MySQL", e)
finally:
    if connection.is_connected():
        cursor.close()
        connection.close()
        print("MySQL connection is closed")