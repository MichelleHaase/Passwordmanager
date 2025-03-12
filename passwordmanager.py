'''CS50x final Project
\\password manager

Core features:
1. saving passwords (hashed)
2. retrieving clear passwords
3. master password for hashing
4. tkinter UI
    4.1 maybe categories like social media banks or similar
    4.2 search function for categories (tables?) or websites etc
5. maybe other option on saving websites, notes etc

plan:
1. create datbase
2. create

'''
import base64
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from getpass import getpass
import os
from pathlib import Path
import sqlite3



def main() -> None:
    # set salt for password hashing 
    while True:  
        database = input("Database name: ")
        if database == "":
            database = "Database"
            continue
        password = getpass("Masterpassword: ").strip() 
        salt = create_salt("salt.bin")
        hash = create_key_hash(password, salt)
        connection = database_connection(database, hash)
        if connection:
            # print("Database active")
            break
            
    while True:
        # menu
        print("1. Create new Entry")
        print("2. Retrieve Data")
        print("3. Exit")
        choice = input("Choose: ")
        print()

        if choice == "1":
            insert_Data(connection, password)
        elif choice == "2":
            retrieve_Data(connection, password)
        elif choice == "3":
            break
        else:
            print("Invalid choice")
            continue

    encrypt_Database(connection, hash)
    
def encrypting_inputs(input, password) -> str:
    """Encrypting input with Fernet"""
    salt = create_salt("salted.bin")
    hash = create_key_hash(password, salt)
    cipher = Fernet(hash)
    data = cipher.encrypt(input.encode("utf-8"))
    return data

def decrypting_inputs(input, password) -> str:
    """Decrypting input with Fernet"""
    salt = create_salt("salted.bin")
    hash = create_key_hash(password, salt)
    cipher = Fernet(hash)
    data = cipher.decrypt(input)
    return data.decode("utf-8")


def insert_Data(connection, password) -> None:
    login_title = None
    Note_title = None
    while True:
    # menu
        print("1. Login Credentials")
        print("2. Secure Note")
        print("3. Back")
        choice = input("Choose: ")
        print()

        if choice == "1":
            print("Login Credentials Title and Password required")
            login_title = input("Title: ") 
            login_Username = input("Username: ")
            login_Password = getpass("Password: ")
            login_Website = input("Website: ")
            login_Email = input("Email: ")
            if login_title == "" or login_Password == "":
                print("Title and Password required")
                continue
            break       
        elif choice == "2":
            print("Secure Note")  
            Note_title = input("Title: ")
            Note_text = input("Note: ")
            if Note_title == "" or Note_text == "":
                print("Title and Note required")
                continue
            break   
        elif choice == "3":     
            break       
        else:
            print("Invalid choice")
            
    db = connection.cursor()
    if login_title:
        login_Password = encrypting_inputs(login_Password, password)
        db.execute("INSERT OR IGNORE INTO Passwords (passwords) VALUES (?)", (login_Password,))
        password_id = db.execute("SELECT id FROM Passwords WHERE passwords = ?", (login_Password,)).fetchone()[0]
        # since many websites do not require a username only mail
        if login_Username == "":
            username_id = None
        else:
            login_Username = encrypting_inputs(login_Username, password)
            db.execute("INSERT OR IGNORE INTO Username (username) VALUES (?)", (login_Username,))
            username_id = db.execute("SELECT id FROM Username WHERE username = ?", (login_Username,)).fetchone()[0]       
        # in case a password for a local program or secure excel is saved that has neither mail nor username
        if login_Email == "":
            mail_id = None
        else:
            login_Email = encrypting_inputs(login_Email, password)
            db.execute("INSERT OR IGNORE INTO Mails (mail) VALUES (?)", (login_Email,))
            mail_id = db.execute("SELECT id FROM Mails WHERE mail = ?", (login_Email,)).fetchone()[0]
        db.execute("INSERT INTO Logins (title, username_id, password_id, website, mail_id) VALUES (?, ?, ?, ?, ?)", 
            (login_title, username_id, password_id, login_Website, mail_id))
        
    elif Note_title:
        #SQLite does not support strings longer than 1GB, unlikely but to be safe
        try:
            Note_text = encrypting_inputs(Note_text, password)
            db.execute("INSERT INTO notes (title, note) VALUES (?, ?)", (Note_title, Note_text))
        except sqlite3.DataError:
            print("Note too long to store")
            insert_Data(connection)

    connection.commit()

    while True:
        print("1. Add more Entries")
        print("2. Back")
        choice = input("Choose: ")
        print()

        if choice == "1":
            insert_Data(connection)
        elif choice == "2":
            break
        else:
            print("Invalid choice")
            continue


def retrieve_Data(connection, password) -> None:
    title = None
    website = None
    connection.row_factory = sqlite3.Row
    db = connection.cursor()
    while True:
        # menu
        print("1. Login Credentials")
        print("2. Secure Note") 
        print("3. Back")
        choice = input("Choose: ")
        print()
        if choice == "1":
            while True:
                print("1. Search by Title")
                print("2. Search by Website")
                print("3. list Titles")
                print("4. Back")
                choice_search = input("Choose: ")
                print()
                if choice_search == "1":
                    title = input("Title: ")
                    print()
                    break
                elif choice_search == "2":
                    website = input("Website: ")
                    break
                elif choice_search == "3":
                    rows = db.execute("SELECT title FROM Logins").fetchall()
                    result = [dict(row) for row in rows]
                    [(print(*[f"{k}: {v}" for k, v in row.items()], sep="\n")) for row in result]
                    input("Press Enter to continue...")
                    continue
                elif choice_search == "4":
                    retrieve_Data(connection)
                else:
                    print("Invalid choice")
                    continue
            if title:
                rows = db.execute("SELECT title, username, passwords, website, mail FROM Logins JOIN Username ON Logins.username_id = Username.id JOIN Passwords ON Logins.password_id = Passwords.id JOIN Mails ON Logins.mail_id = Mails.id WHERE title = ?", (title,))
            elif website:
                rows = db.execute("SELECT title, username, passwords, website, mail FROM Logins JOIN Username ON Logins.username_id = Username.id JOIN Passwords ON Logins.password_id = Passwords.id JOIN Mails ON Logins.mail_id = Mails.id WHERE website = ?", (website,))
            result = [dict(row) for row in rows]
            for row in result:
                row["passwords"] = decrypting_inputs(row["passwords"], password)
                row["username"] = decrypting_inputs(row["username"], password)
                row["mail"] = decrypting_inputs(row["mail"], password)
            [(print(*[f"{k}: {v}" for k, v in row.items()], sep="\n")) for row in result]
            input("Press Enter to continue...")
            break
        if choice == "2":
            while True:
                print("1. Search by Title")
                print("2. list Titles")
                print("3. Back")
                choice_search = input("Choose: ")
                print()
                if choice_search == "1":
                    title = input("Title: ")
                    print()
                    break
                elif choice_search == "2":
                    rows = db.execute("SELECT title FROM notes").fetchall()
                    result = [dict(row) for row in rows]
                    [(print(*[f"{k}: {v}" for k, v in row.items()], sep="\n")) for row in result]
                    input("Press Enter to continue...")
                    continue
                elif choice_search == "3":
                    break
                else:
                    print("Invalid choice")
                    continue
            if title:
                rows = db.execute("SELECT title, note FROM notes").fetchall()
                result = [dict(row) for row in rows]
                [(print(*[f"{k}: {v}" for k, v in row.items()], sep="\n")) for row in result]
                input("Press Enter to continue...")
                break
            else:
                print("Title required")
                continue
        if choice == "3":
            return False
    return

def create_salt(saltname) -> bytes:
    """ salt for password hashing saved in salt.bin"""

    if Path(saltname).is_file():
        with open(saltname, "rb") as salt_file:
            salt = salt_file.read()
            return salt
    
    salt = os.urandom(16)
    with open(saltname, "wb") as f:
            f.write(salt)
    return salt


def create_key_hash(password, salt) -> str:
    kdf = PBKDF2HMAC(algorithm=hashes.SHA3_256(), length=32, 
                 salt=salt, iterations=100000, backend=default_backend())
    kdf_key = kdf.derive(password.encode("utf-8"))

    return base64.urlsafe_b64encode(kdf_key)

def encrypt_Database(connection, key) -> None:
    """encrypt Database and save it as Database.enc"""

    with open("Database.db", "rb") as f:
        database = f.read()

    cipher = Fernet(key)
    encrypted_database = cipher.encrypt(database)

    with open("Database.enc", "wb") as f:
        f.write(encrypted_database)

    print("Database encrypted")

    connection.commit()
    # print("Database saved")
    if connection:
            connection.close()
            print("Database connection closed")
    os.remove("Database.db")
    # print("Database deleted")


def read_In_Database(db, key) -> None | sqlite3.Connection:
    """decrypt Database and return connection"""

    try:
        with open((db +".enc"), "rb") as f:
            encrypted_database = f.read()
        cipher = Fernet(key)

        decrypted_database = cipher.decrypt(encrypted_database)

    except InvalidToken:
        print("Masterpassword incorrect")
        return

    with open((db + ".db"), "wb") as f:
        f.write(decrypted_database)
    # print("Database decrypted")

    connection = sqlite3.connect(database=(db+ ".db"))
    cursor = connection.cursor()

    connection.commit()
    # print("Database loaded")

    return connection


def create_Database(db, schema="./schema/schema.sql") -> None | sqlite3.Connection:
    """Create Database and return connection according to schema"""

    connection = sqlite3.connect(database=(db +".db"))
    cursor = connection.cursor()
    schema_path = Path(schema)
    if not schema_path.is_file():
        print(f"Schema file not found: {schema_path}")
        return

    with open(schema_path, 'r') as schema_file:
        schema = schema_file.read()

    cursor.executescript(schema)
    connection.commit()
    print("\n", "New Database created", "\n")

    return connection


def database_connection(db, hash) -> sqlite3.Connection:
    """Create Database connection"""
    # opening/ creating Database
    if db.endswith(".db"):
        db = db[:-3]
    elif db.endswith(".enc"):
        db = db[:-4]
    connection = None
    if Path(db + ".enc").is_file():
        connection = read_In_Database(db, hash)
    else:
        connection = create_Database(db)

    # abort when no Database is found or created
    if connection == None:
        return None

    return connection





if __name__ == "__main__":
    main()