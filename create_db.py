import mysql.connector

mydb = mysql.connector.connect(

    host="localhost",
    user="root",
    passwd="password",
    database="medical_record"
)

mycursor = mydb.cursor()

# # Create table
# mycursor.execute("CREATE TABLE patient (id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR (20), age INT)")

# # Insert data
# sql = "INSERT INTO patient (id, name, age) VALUES (%s, %s, %s)"
# val = [(1, "John", 25),
#        (2, "Peter", 30),
#        (3, "Amy", 20),
#        (4, "Hannah", 25),
#        (5, "Michael", 30)]
# mycursor.executemany(sql, val)

# mydb.commit()

# mycursor.execute("SELECT * FROM patient")

# myresult = mycursor.fetchall()

# for x in myresult:
#     print(x)



