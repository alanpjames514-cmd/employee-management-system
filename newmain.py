import sqlite3
import time
import re

conn = sqlite3.connect("Employeemanagementsystem1.db", timeout=60)
cursor = conn.cursor()

# ==========================
# PASSWORD ANALYZER
# ==========================

def validate_password(password, role):

    digits = re.findall(r'\d', password)
    special = re.findall(r'[@#$%^&*!]', password)

    if len(digits) < 3:
        return False, "Password must contain at least 3 numbers"

    if len(special) < 1:
        return False, "Password must contain at least 1 special character"

    if role == "manager" and not password.endswith("mngr"):
        return False, "Manager password must end with 'mngr'"

    if role == "employee" and not password.endswith("emp"):
        return False, "Employee password must end with 'emp'"

    return True, "Valid password"

# ==========================
# LOADING (UPDATED ONLY)
# ==========================

def loading(msg):

    print("\n" + msg)

    spinner = ['|', '/', '-', '\\']

    for i in range(12):
        print(f"\r{spinner[i % 4]} Loading...", end="")
        time.sleep(0.5)

    print("\rDone!           ")

# ==========================
# INPUT
# ==========================

def get_input(msg):
    val = input(msg).strip()
    if val.lower() == "q":
        logout()
    return val

def get_choice(msg, options):
    val = input(msg).strip()
    if val.lower() == "q":
        logout()
    if val not in options:
        print("Invalid choice. Select from given options only.")
        return None
    return val

# ==========================
# LOGOUT
# ==========================

def logout():
    print("\nThank you for using system")
    conn.close()
    exit()

# ==========================
# LOGIN
# ==========================

def login():

    print("\n========== LOGIN ==========")

    username = get_input("Username: ")
    password = get_input("Password: ")

    cursor.execute(
        "SELECT user_id, role, name, password FROM Users WHERE username=?",
        (username,)
    )

    user = cursor.fetchone()

    if user:
        db_password = user[3]
        role = user[1]

        if role == "admin":
            if password == db_password:
                print(f"\nWelcome {user[2]}")
                return user
            else:
                print("Incorrect password")
                return None
        else:
            valid, msg = validate_password(password, role)

            if password == db_password and valid:
                print(f"\nWelcome {user[2]}")
                return user
            else:
                print("Password validation failed:", msg)
                return None
    else:
        print("Invalid username")
        return None

# ==========================
# CREATE USER (ADMIN ONLY)
# ==========================

def create_user():

    print("\n1. Manager\n2. Employee")
    choice = get_choice("Select Role: ", ["1","2"])
    if not choice:
        return

    role = "manager" if choice == "1" else "employee"

    cursor.execute("SELECT MAX(user_id) FROM Users")
    last_id = cursor.fetchone()[0]
    next_id = 1 if last_id is None else last_id + 1

    expected_username = f"mngr_{str(next_id).zfill(3)}" if role=="manager" else f"emp_{str(next_id).zfill(3)}"

    username = get_input(f"Username ({expected_username}): ")

    if username != expected_username:
        print("Enter correct username format")
        return

    name = get_input("Name: ")
    password = get_input("Password: ")

    valid, msg = validate_password(password, role)
    if not valid:
        print(msg)
        return

    cursor.execute("INSERT INTO Users(username,password,role,name) VALUES(?,?,?,?)",
                   (username,password,role,name))
    conn.commit()

    user_id = cursor.lastrowid

    if role == "manager":
        dept = get_input("Department name: ")
        loc = get_input("Location: ")

        cursor.execute("INSERT INTO Departments(department_name,location) VALUES(?,?)",(dept,loc))
        conn.commit()

        dept_id = cursor.lastrowid

        cursor.execute("INSERT INTO Managers(manager_name,department_id,user_id) VALUES(?,?,?)",
                       (name,dept_id,user_id))
        conn.commit()

    print("User created successfully")

# ==========================
# CREATE EMPLOYEE ONLY (MANAGER)
# ==========================

def create_employee_only():

    role = "employee"

    cursor.execute("SELECT MAX(user_id) FROM Users")
    last_id = cursor.fetchone()[0]
    next_id = 1 if last_id is None else last_id + 1

    expected_username = f"emp_{str(next_id).zfill(3)}"

    username = get_input(f"Username ({expected_username}): ")

    if username != expected_username:
        print("Enter correct username format")
        return

    name = get_input("Name: ")
    password = get_input("Password: ")

    valid, msg = validate_password(password, role)
    if not valid:
        print(msg)
        return

    cursor.execute(
        "INSERT INTO Users(username,password,role,name) VALUES(?,?,?,?)",
        (username, password, role, name)
    )

    conn.commit()

    print("Employee created successfully")

# ==========================
# UPDATE USER
# ==========================

def update_user():

    user_id = get_input("Enter User ID: ")

    cursor.execute("SELECT role FROM Users WHERE user_id=?", (user_id,))
    data = cursor.fetchone()

    if not data:
        print("User not found")
        return

    role = data[0]

    print("\n1 Name\n2 Password\n3 Username")
    choice = get_choice("Select field to update: ", ["1","2","3"])
    if not choice:
        return

    if choice == "1":
        val = get_input("Enter new name: ")
        cursor.execute("UPDATE Users SET name=? WHERE user_id=?", (val,user_id))

        if role=="manager":
            cursor.execute("UPDATE Managers SET manager_name=? WHERE user_id=?", (val,user_id))

    elif choice=="2":
        val = get_input("Enter new password: ")
        valid,msg = validate_password(val,role)
        if not valid:
            print(msg)
            return
        cursor.execute("UPDATE Users SET password=? WHERE user_id=?", (val,user_id))

    elif choice=="3":
        val = get_input("Enter new username: ")
        cursor.execute("UPDATE Users SET username=? WHERE user_id=?", (val,user_id))

    conn.commit()
    print("Updated successfully")

# ==========================
# DELETE USER
# ==========================

def delete_user():
    user_id = get_input("Enter User ID to delete: ")
    confirm = get_input("Type 'confirm delete' to proceed: ")

    if confirm != "confirm delete":
        print("Cancelled")
        return

    cursor.execute("DELETE FROM Managers WHERE user_id=?", (user_id,))
    cursor.execute("DELETE FROM Users WHERE user_id=?", (user_id,))
    conn.commit()

    print("Deleted successfully")

# ==========================
# VIEW USERS
# ==========================

def view_all_users():

    loading("Loading users...")

    cursor.execute("SELECT user_id,name,role FROM Users")
    users = cursor.fetchall()

    for i,u in enumerate(users,1):
        print(f"{i}. {u[1]} ({u[2]})")

# ==========================
# MANAGER MENU
# ==========================

def manager_menu(user_id):

    while True:
        print("\nManager Menu")
        print("1 View My Details")
        print("2 View All Employees")
        print("3 Add Employee")
        print("4 Logout")

        c = get_choice("Choice: ", ["1","2","3","4"])
        if not c:
            continue

        if c=="1":
            loading("Loading your details...")
            cursor.execute("SELECT * FROM Users WHERE user_id=?", (user_id,))
            print(cursor.fetchone())

        elif c=="2":
            cursor.execute("SELECT user_id,name FROM Users WHERE role='employee'")
            for i,u in enumerate(cursor.fetchall(),1):
                print(f"{i}. {u[1]}")

        elif c=="3":
            create_employee_only()

        elif c=="4":
            logout()

# ==========================
# ADMIN MENU
# ==========================

def admin_menu(user_id):

    while True:

        print("\nAdmin Menu")
        print("1 Add User")
        print("2 Update User")
        print("3 Delete User")
        print("4 View All Users")
        print("5 My Details")
        print("6 Logout")

        c = get_choice("Choice: ", ["1","2","3","4","5","6"])
        if not c:
            continue

        if c=="1":
            create_user()
        elif c=="2":
            update_user()
        elif c=="3":
            delete_user()
        elif c=="4":
            view_all_users()
        elif c=="5":
            loading("Loading your details...")
            cursor.execute("SELECT * FROM Users WHERE user_id=?", (user_id,))
            print(cursor.fetchone())
        elif c=="6":
            logout()

# ==========================
# EMPLOYEE MENU
# ==========================

def employee_menu(user_id):

    while True:

        print("\nEmployee Menu")
        print("1 View My Details")
        print("2 Leave Request")
        print("3 Logout")

        c = get_choice("Choice: ", ["1","2","3"])
        if not c:
            continue

        if c=="1":
            loading("Loading your details...")
            cursor.execute("SELECT * FROM Users WHERE user_id=?", (user_id,))
            print(cursor.fetchone())

        elif c=="2":
            loading("Opening Leave Request Form...")
            to_mail = get_input("To Mail ID: ")
            subject = get_input("Subject: ")
            content = get_input("Content: ")

            year = get_input("Year: ")
            month = get_input("Month: ")
            day = get_input("Day: ")

            if not (year and month and day):
                print("Date mandatory")
                continue

            print("1 Sick\n2 Paid")
            leave_type = get_choice("Select: ", ["1","2"])
            if not leave_type:
                continue

            print("Leave request submitted")

        elif c=="3":
            logout()

# ==========================
# MAIN
# ==========================

while True:

    print("\n==============================")
    print(" Employee Management System")
    print("==============================")

    print("1 Login")
    print("2 Exit")

    op = get_choice("Choice: ", ["1","2"])
    if not op:
        continue

    if op=="1":
        user = login()

        if user:
            if user[1]=="admin":
                admin_menu(user[0])
            elif user[1]=="manager":
                manager_menu(user[0])
            elif user[1]=="employee":
                employee_menu(user[0])

    elif op=="2":
        logout()