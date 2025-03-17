'''CS50x final Project
password manager

Core features:
1. saving passwords (hashed)
2. retrieving clear passwords
3. master password for encryption
4. saving secure notes
5. maybe other option on saving websites, deleting stuff etc
'''

  
import base64
import os
from getpass import getpass
from pathlib import Path
import sqlite3
import sys
import subprocess
import stat

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


def main() -> None:
    """Main function"""
    while True:
        database = input("Database Name: ")
        # if no name is given the default name is Database
        if database == "":
            database = "Database"
            continue
        password = getpass("Masterpassword: ").strip()
        print()

        # creating salt and hash for encryption
        salt = create_salt(database+".bin")
        hash = create_key_hash(password, salt)

        # creating Database or loading existing Database and connecting
        connection = database_connection(database, hash)
        # if the Database link is established the program continues
        if connection:
            break

    while True: # since the menu should be displayed after each action, logic in loop
        # menu
        print("Password Manager")
        print("1. Create New Entry")
        print("2. Retrieve Data")
        print("3. Delete Entry")
        print("4. Change Masterpassword")
        print("5. Exit")
        choice = input("Choose: ")
        print()

        if choice == "1":
            insert_Data(connection, password, database)
        elif choice == "2":
            retrieve_Data(connection, password, database)
        elif choice == "3":
            delete_entry(connection)
        elif choice == "4":
            new_pass = change_master(password)
            if new_pass:
                password = new_pass
                salt = create_salt(database+".bin")
                hash = create_key_hash(password, salt)
                print("Masterpassword Active Once the Application is Restarted")
                continue
            else:
                print("Masterpassword Not Changed")
                continue
        elif choice == "5":
            break
        else:
            print("Invalid Choice")
            continue

    # encrypt database and close connection
    encrypt_Database(connection, hash, database)

def delete_entry(connection) -> None:
    """Delete entry from Database"""
    # Delete Menu
    while True:
        print("Delete Entry")
        print("1. Delete Login Credentials")
        print("2. Delete Secure Note")
        print("3. Back")
        choice = input("Choose: ")
        print()

        if choice == "1":  # delete login credentials
            delete_login(connection)
            return
        elif choice == "2":  # delete secure note
            delete_note(connection)
            return
        elif choice == "3":
            return
    

def delete_login(connection) -> None:
    """Delete Login Credentials"""
    # Delete Login Menu
    connection.row_factory = sqlite3.Row
    db = connection.cursor()
    while True:
        print("Delete Login Credentials")
        print("1. Delete by Title")
        print("2. List Titles")
        print("3. Back")
        choice = input("Choose: ")  
        print()
        if choice in ["1", "2", "3"]:   
            break
        else:
            print("Invalid Choice")
            continue

    if choice == "1":  # delete by title
        title = input("Title: ")
        print()
        if title == "":
            print("Title Required")
            return delete_login(connection)
        else:
            db.execute(
                """DELETE FROM Logins 
                WHERE title = ?""",
                (title,),
            )
            connection.commit()
            print("If They Existed the Login Credentials are Deleted")
            print()
            return
    elif choice == "2": # list all titles
        rows = db.execute(
            """SELECT title 
            FROM Logins"""
        ).fetchall()
        pretty_print(rows)
        return delete_login(connection)
    elif choice == "3": # back
        return
    else:
        print("Invalid Choice")


def delete_note(connection) -> None:
    """Delete Secure Note"""
    # Delete Note Menu
    connection.row_factory = sqlite3.Row
    db = connection.cursor()
    while True:
        print("Delete Secure Note")
        print("1. Delete by Title")
        print("2. List Titles")
        print("3. Back")
        choice = input("Choose: ")
        print()
        if choice == "1":  # delete by title
            title = input("Title: ")
            print()
            if title == "":
                print("Title Required")
                return delete_note(connection)
            else:
                
                db.execute(
                    """DELETE FROM Notes 
                    WHERE title = ?""",
                    (title,),
                )
                connection.commit()
                print("If They Existed the Secure Note is Deleted")
                print()
                return
        
        elif choice == "2": # list all titles
            rows = db.execute(
                """SELECT title 
                FROM Notes"""
            ).fetchall()
            pretty_print(rows)
            return delete_note(connection)
        elif choice == "3": # back
            return
        

def change_master(password) -> bool|str:
    """Change Masterpassword"""
    # changing the masterpassword
    print("Please Re-enter your Current Masterpassword")
    current_password = getpass("Current Masterpassword: ").strip()
    print()
    # checking if the current password is correct
    # salt = create_salt("salt.bin")
    # hash = create_key_hash(current_password, salt)

    if current_password != password:
        print("Masterpassword Incorrect")
        return False
    # if the current password is correct the new password is set
    new_password = getpass("New Masterpassword: ").strip()
    print()
    return new_password


def encrypting_inputs(input, password, database) -> str:
    """Encrypting input with Fernet"""
    # creating a different salt than for the db encryption
    salt = create_salt((database + "_.bin"))
    hash = create_key_hash(password, salt)
    cipher = Fernet(hash)
    # encrypting input so sensitive data is not stored in clear text
    data = cipher.encrypt(input.encode("utf-8"))

    return data


def decrypting_inputs(input, password, database) -> str:
    """Decrypting input with Fernet"""
    salt = create_salt((database + "_.bin"))
    hash = create_key_hash(password, salt)
    cipher = Fernet(hash)
    data = cipher.decrypt(input)

    # returning decrypted and decoded data
    return data.decode("utf-8")


def insert_Data(connection, password, database) -> None:
    # setting up variables to identify the menu choice
    login_title = None
    Note_title = None
    while True:
        # menu
        print("Insert Data")
        print("1. Login Credentials")
        print("2. Secure Note")
        print("3. Back")
        choice = input("Choose: ")
        print()
        if choice in ["1", "2", "3"]:
            break
        else:
            print("Invalid Choice")

    if choice == "1":  # login credentials
        # password and title are required so passwords can be stored singularly
        print("Login Credentials Title and Password Required")

        login_title = input("Title: ")
        login_Username = input("Username: ")
        login_Password = getpass("Password: ")
        login_Website = input("Website: ")
        login_Email = input("Email: ")
        print()

        # re-prompt if title or password are not entered
        if login_title == "" or login_Password == "":
            print("Title and Password Required")
            return insert_Data(connection, password, database)
        else:
            insert_login(
                connection,
                login_title,
                login_Username,
                login_Password,
                login_Website,
                login_Email,
                password,
                database
            )
            

    elif choice == "2":  # secure note
        print("Secure Note")
        Note_title = input("Title: ")
        Note_text = input("Note: ")
        print()

        # re-prompt if title or note are not entered
        if Note_title == "" or Note_text == "":
            print("Title and Note Required")
            return insert_Data(connection, password, database)
        else:
            insert_note(connection, Note_title, Note_text, password, database)

    elif choice == "3":
        return
    
    while True:
        print("Insert Data")
        print("1. Add More Entries")
        print("2. Back")
        choice = input("Choose: ")
        print()

        if choice == "1":
            insert_Data(connection, password, database)
        elif choice == "2":
            break
        else:
            print("Invalid Choice")
            continue
    return


def insert_login(
    connection,
    login_title,
    login_Username,
    login_Password,
    login_Website,
    login_Email,
    password,
    database
) -> None:
    """Inserting login credentials into Database"""
    db = connection.cursor()
    # inserting encrypted password into Passwords table
    login_Password = encrypting_inputs(login_Password, password, database)
    db.execute(
        """INSERT OR IGNORE INTO Passwords 
                (passwords) 
                VALUES (?)""",
        (login_Password,)
    )
    connection.commit()
    
    password_id = db.execute(
        """SELECT id FROM Passwords 
        WHERE passwords = ?""",
        (login_Password,)
    ).fetchone()[0]

    # since many websites do not require a username only mail
    if login_Username == "":
        username_id = None
    else:
        login_Username = encrypting_inputs(login_Username, password, database)
        db.execute(
            """INSERT OR IGNORE INTO Username 
            (username) 
            VALUES (?)""",
            (login_Username,)
        )
        connection.commit()

        username_id = db.execute(
            """SELECT id FROM Username 
            WHERE username = ?""",
            (login_Username,)
        ).fetchone()[0]

    # in case a password for a local program or secure excel is saved that has neither mail nor username
    if login_Email == "":
        mail_id = None
    else:
        login_Email = encrypting_inputs(login_Email, password, database)
        db.execute(
            """INSERT OR IGNORE INTO Mails
            (mail) 
            VALUES (?)""",
            (login_Email,)
        )
        connection.commit()

        mail_id = db.execute(
            """SELECT id FROM Mails 
            WHERE mail = ?""",
            (login_Email,)
        ).fetchone()[0]
    # insert collected data into Logins table
    db.execute(
        """INSERT INTO Logins 
        (title, username_id, password_id, website, mail_id) 
        VALUES (?, ?, ?, ?, ?)""",
        (login_title, username_id, password_id, login_Website, mail_id),
    )

    connection.commit()
    print("Login Credentials Saved")
    print()

    return


def insert_note(connection, Note_title, Note_text, password, database) -> None:
    db = connection.cursor()
    # SQLite does not support strings longer than 1GB, unlikely but to be safe
    try:
        Note_text = encrypting_inputs(Note_text, password, database)
        db.execute(
            """INSERT INTO notes 
            (title, note) 
            VALUES (?, ?)""",
            (Note_title, Note_text),
        )

    except sqlite3.DataError:
        print("Note too Long to Store")
        insert_Data(connection, password, database)

    connection.commit()
    print("Secure Note Saved")
    print()

    return


def retrieve_Data(connection, password, database) -> None:

    # allows to address sql output by column name
    connection.row_factory = sqlite3.Row
    db = connection.cursor()

    while True:
        # menu
        print("Retrieve Data")
        print("1. Login Credentials")
        print("2. Secure Note")
        print("3. Back")
        choice = input("Choose: ")
        print()
        if choice == "1":  # login credentials
            return retrieve_login(connection, password, database)
        if choice == "2":  # secure note
            return retrieve_note(connection, password, database)
        if choice == "3":
            break
        return


def retrieve_login(connection, password, database) -> None:
    connection.row_factory = sqlite3.Row
    db = connection.cursor()
    # setting up variables to identify the menu choice
    title = None
    website = None
    while True:
        print("Search Login Credentials")
        print("1. Search by Title")
        print("2. Search by Website")
        print("3. List Titles")
        print("4. Back")
        choice_search = input("Choose: ")
        print()
        if choice_search in ["1","2","3","4"]:
            break
        else:
            print("Invalid Choice")
            continue

    if choice_search == "1":  # search by title
        title = input("Title: ")
        print()
        if title == "":
            print("Title Required")
            return retrieve_login(connection, password, database)

    elif choice_search == "2":  # search by website
        website = input("Website: ")
        print()
        if website == "":
            print("Website Required")
            return retrieve_login(connection, password, database)

    elif choice_search == "3":  # list all titles
        rows = db.execute(
            """SELECT title 
            FROM Logins"""
        ).fetchall()
        pretty_print(rows)

        return retrieve_login(connection, password, database)

    elif choice_search == "4":  # back
        return

    # if title or website is no longer None the according search is executed
    if title:
        rows = db.execute(
            """SELECT title, username, passwords, website, mail 
            FROM Logins 
            JOIN Username 
            ON Logins.username_id = Username.id 
            JOIN Passwords 
            ON Logins.password_id = Passwords.id 
            JOIN Mails 
            ON Logins.mail_id = Mails.id 
            WHERE title = ?""",
            (title,)
        )

    elif website:
        rows = db.execute(
            """SELECT title, username, passwords, website, mail 
            FROM Logins 
            JOIN Username 
            ON Logins.username_id = Username.id 
            JOIN Passwords 
            ON Logins.password_id = Passwords.id 
            JOIN Mails 
            ON Logins.mail_id = Mails.id 
            WHERE website = ?""",
            (website,)
        )

    # transforming the output into a list of dicts for easier printing
    result = [dict(row) for row in rows]
    # decrypting the sensitive data
    for row in result:
        row["passwords"] = decrypting_inputs(row["passwords"], password, database)
        row["username"] = decrypting_inputs(row["username"], password, database)
        row["mail"] = decrypting_inputs(row["mail"], password, database)
    # prints one key/value pair per line with an \n between list items
    
    [(print(*[f"{k}: {v}" for k, v in row.items()], sep="\n")) for row in result]
    # wait till user is ready to continue
    input("Press Enter to Continue...")
    print()
    return


def retrieve_note(connection, password, database) -> None:
    title = None
    connection.row_factory = sqlite3.Row
    db = connection.cursor()
    # search menu
    while True:
        print("Search Secure Notes")
        print("1. Search by Title")
        print("2. List Titles")
        print("3. Back")

        choice_search = input("Choose: ")
        print()

        if choice_search in ["1","2","3"]:
            break
        else:
            continue
        
    if choice_search == "1":  # search by title
        title = input("Title: ")
        print()
        

    elif choice_search == "2":  # list all titles
        rows = db.execute(
            """SELECT title 
            FROM Notes"""
        ).fetchall()

        pretty_print(rows)
        return retrieve_note(connection, password, database)

    elif choice_search == "3":  # back
        return


    # if title is no longer None the according search is executed
    if title:
        rows = db.execute(
            """SELECT title, note 
            FROM notes
            WHERE title = ?""",
            (title,)
        ).fetchall()

        result = [dict(row) for row in rows]
        for row in result:
            row["note"] = decrypting_inputs(row["note"], password, database)

        [(print(*[f"{k}: {v}" for k, v in row.items()], sep="\n")) for row in result]

        input("Press Enter to Continue...")
        print()
        return

    else:
        print("Title Required")
        return retrieve_note(connection, password, database)



def pretty_print(rows) -> None:
    """cleans up SQL outputs"""
    # transforming the output into a list of dicts for easier printing
    result = [dict(row) for row in rows]
    # prints one key/value pair per line with an \n between list items
    # no decryption since titoles are saved in clear text
    [
        (print(*[f"{k}: {v}" for k, v in row.items()], sep="\n"))
        for row in result
    ]
    input("Press Enter to Continue...")
    print()
    return
    

def create_salt(saltname) -> bytes:
    """salt for password hashing saved in salt.bin"""
    # if there is a stored salt it is used
    if Path(saltname).is_file():
        with open(saltname, "rb") as salt_file:
            salt = salt_file.read()
            
    # if not a new salt is created
    else:
        salt = os.urandom(16)
        with open(saltname, "wb") as f:
            f.write(salt)

    # Set restrictive file permissions should work for windows apple and linux
    if sys.platform.startswith("win"):
        subprocess.run(f'icacls "{saltname}" /inheritance:r /grant %USERNAME%:R', shell=True, check=True)
    else:
        os.chmod(saltname, stat.S_IRUSR | stat.S_IWUSR) 

    return salt


def create_key_hash(password, salt) -> str:
    """hashing the password with salt"""
    # set algorithm SHA3_256 and parameters
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA3_256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend(),
    )
    # derive binary key from password
    kdf_key = kdf.derive(password.encode("utf-8"))
    # return key as base64 encoded string (urlsafe and printable)
    return base64.urlsafe_b64encode(kdf_key)


def encrypt_Database(connection, key, db) -> None:
    """encrypt Database and save it as Database.enc"""
    # read in db
    with open((db + ".db"), "rb") as f:
        database = f.read()

    # derive cipher from key
    cipher = Fernet(key)
    # encrypt contents
    encrypted_database = cipher.encrypt(database)

    # write encrypted db
    with open((db + ".enc"), "wb") as f:
        f.write(encrypted_database)

    print("Database Encrypted")

    connection.commit()
    # close connection
    if connection:
        connection.close()
        print("Database Connection Closed")
    # delete decrypted db
    os.remove((db + ".db"))


def database_connection(db, hash) -> sqlite3.Connection:
    """Create Database connection"""
    # deleting file extension if present
    if db.endswith(".db"):
        db = db[:-3]
    elif db.endswith(".enc"):
        db = db[:-4]
    connection = None
    # check if encrypted Database exists
    if Path(db + ".enc").is_file() | Path(db + ".db").is_file():
        connection = read_In_Database(db, hash)
    else:
        connection = create_Database(db)

    # abort when no Database is found or created
    if connection == None:
        return None

    return connection


def read_In_Database(db, key) -> None | sqlite3.Connection:
    """decrypt Database and return connection"""
    # read in encrypted db
    if Path(db + ".enc").is_file():
        try:
            with open((db + ".enc"), "rb") as f:
                encrypted_database = f.read()
            cipher = Fernet(key)

            decrypted_database = cipher.decrypt(encrypted_database)

        except InvalidToken:
            print("Masterpassword Incorrect")
            return
        # write decrypted db
        with open((db + ".db"), "wb") as f:
            f.write(decrypted_database)

    # connect to decrypted db
    connection = sqlite3.connect(database=(db + ".db"))
    connection.commit()

    return connection


def create_Database(db, schema="./schema/schema.sql") -> None | sqlite3.Connection:
    """Create Database and return connection according to schema"""
    # create Database according to default schema
    connection = sqlite3.connect(database=(db + ".db"))
    cursor = connection.cursor()
    schema_path = Path(schema)
    
    if not schema_path.is_file():
        print(f"Schema File Not Found: {schema_path}")
        return

    # read in schema
    with open(schema_path, "r") as schema_file:
        schema = schema_file.read()

    # execute schema
    cursor.executescript(schema)
    connection.commit()
   

    return connection


if __name__ == "__main__":
    main()
