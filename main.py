import sqlite3

conn = sqlite3.connect("Employeemanagementsystem1.db")
cursor = conn.cursor()

print("Database connected")

# Departments
cursor.execute("""
CREATE TABLE IF NOT EXISTS Departments(
    department_id INTEGER PRIMARY KEY AUTOINCREMENT,
    department_name TEXT NOT NULL,
    location TEXT
)
""")

# Users
cursor.execute("""
CREATE TABLE IF NOT EXISTS Users(
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT,
    role TEXT,
    name TEXT
)
""")

# Managers
cursor.execute("""
CREATE TABLE IF NOT EXISTS Managers(
    manager_id INTEGER PRIMARY KEY AUTOINCREMENT,
    manager_name TEXT,
    department_id INTEGER,
    user_id INTEGER,
    FOREIGN KEY(department_id) REFERENCES Departments(department_id),
    FOREIGN KEY(user_id) REFERENCES Users(user_id)
)
""")

print("Tables created")

# Default admin
cursor.execute("""
INSERT OR IGNORE INTO Users(username,password,role,name)
VALUES('admin','admin123','admin','Ganesh')
""")

conn.commit()
conn.close()

print("Admin created")