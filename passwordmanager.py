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
import sys
from tkinter import E, N

from argon2 import PasswordHasher
import base64
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from getpass import getpass
import os
from pathlib import Path
import sqlite3

import graphics



def main() -> None:
    # set salt for password hashing 
    while True:  
        password = getpass("Masterpassword: ").strip() 
        salt = create_salt()
        hash = create_key_hash(password, salt)
        connection = database_connection(hash)
        if connection:
            print("Database active")
            break
            
    while True:
        # menu
        print("1. Create new Entry")
        print("2. Retrieve Data")
        print("3. Exit")
        choice = input("Choose: ")

        if choice == "1":
            insert_Data(connection)
        elif choice == "2":
            retrieve_Data(connection)
        elif choice == "3":
            break
        else:
            print("Invalid choice")
            continue

    encrypt_Database(connection, hash)
    


def insert_Data(connection) -> None:
    while True:
    # menu
        print("1. Login Credentials")
        print("2. Secure Note")
        print("3. Back")
        choice = input("Choose: ")

        if choice == "1":
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
            print("Secure Note")  # insert secure note
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
        db.execute("INSERT OR IGNORE INTO Passwords (passwords) VALUES (?)", (login_Password,))
        password_id = db.execute("SELECT id FROM Passwords WHERE passwords = ?", (login_Password,)).fetchone()[0]
        db.execute("INSERT OR IGNORE INTO Username (username) VALUES (?)", (login_Username,))
        username_id = db.execute("SELECT id FROM Username WHERE username = ?", (login_Username,)).fetchone()[0]       
        db.execute("INSERT OR IGNORE INTO Mails (mail) VALUES (?)", (login_Email,))
        mail_id = db.execute("SELECT id FROM Mails WHERE mail = ?", (login_Email,)).fetchone()[0]
        db.execute("INSERT INTO Logins (title, username_id, password_id, website, mail_id) VALUES (?, ?, ?, ?, ?)", 
            (login_title, username_id, password_id, login_Website, mail_id))
        
    elif Note_title:
        db.execute("INSERT INTO notes (title, note) VALUES (?, ?)", (Note_title, Note_text))
    connection.commit()

    while True:
        print("1. Add more Entries")
        print("2. Back")
        choice = input("Choose: ")

        if choice == "1":
            insert_Data(connection)
        elif choice == "2":
            break
        else:
            print("Invalid choice")
            continue


def retrieve_Data() -> None:
    ...

def create_salt() -> bytes:
    """ salt for password hashing saved in salt.bin"""

    if Path("salt.bin").is_file():
        with open("salt.bin", "rb") as salt_file:
            salt = salt_file.read()
            return salt
    
    salt = os.urandom(16)
    with open("salt.bin", "wb") as f:
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



def read_In_Database(key) -> None | sqlite3.Connection:
    """decrypt Database and return connection"""

    try:
        with open("Database.enc", "rb") as f:
            encrypted_database = f.read()
        cipher = Fernet(key)

        decrypted_database = cipher.decrypt(encrypted_database)

    except InvalidToken:
        print("Masterpassword incorrect")
        return

    with open("Database.db", "wb") as f:
        f.write(decrypted_database)
    # print("Database decrypted")

    connection = sqlite3.connect(database="Database.db")
    cursor = connection.cursor()

    connection.commit()
    # print("Database loaded")

    return connection



def create_Database(schema="./schema/schema.sql") -> None | sqlite3.Connection:
    """Create Database and return connection according to schema"""

    connection = sqlite3.connect(database="Database.db")
    cursor = connection.cursor()
    schema_path = Path(schema)
    if not schema_path.is_file():
        print(f"Schema file not found: {schema_path}")
        return

    with open(schema_path, 'r') as schema_file:
        schema = schema_file.read()

    cursor.executescript(schema)
    connection.commit()
    print("Database created")

    return connection


def database_connection(hash) -> sqlite3.Connection:
    """Create Database connection"""
    # opening/ creating Database
    connection = None
    if Path("./Database.enc").is_file():
        connection = read_In_Database(hash)
    else:
        connection = create_Database()

    # abort when no Database is found or created
    if connection == None:
        return None

    return connection





if __name__ == "__main__":
    main()