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

from argon2 import PasswordHasher
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import os
from pathlib import Path
import sqlite3

import graphics



def main() -> None:
    # set salt for password hashing   
    password = input("Masterpassword: ").strip() 
    salt = create_salt()
    hash = create_key_hash(password, salt)
    connection = database_connection(hash)

    print("Database connection established")
    
    encrypt_Database(connection, hash)
    # close connection
    

def menu():
    # menu for choosing what to do, no clue how to do that oop
    ...


def insert_Data() -> None:
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
    print("Database saved")
    if connection:
            connection.close()
            print("Database connection closed")
    os.remove("Database.db")
    print("Database deleted")

def retrieve_Data() -> None:
    ...

def verify_Masterpassword() -> bool:
    ...

def read_In_Database(key) -> None | sqlite3.Connection:
    """decrypt Database and return connection"""
    ## Assunming that Masterpassword is already verfied? maybe saving the Hash somewhere? TODO

    with open("Database.enc", "rb") as f:
        encrypted_database = f.read()
    cipher = Fernet(key)

    decrypted_database = cipher.decrypt(encrypted_database)

    with open("Database.db", "wb") as f:
        f.write(decrypted_database)
    print("Database decrypted")

    connection = sqlite3.connect(database="Database.db")
    cursor = connection.cursor()

    connection.commit()
    print("Database loaded")

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
        sys.exit("Unknown Error, no Database loaded or created")

    return connection





if __name__ == "__main__":
    main()