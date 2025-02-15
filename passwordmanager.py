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

import graphics
import sqlite3
from pathlib import Path


def main() -> None:
    key = input("Masterpassword: ").strip()
    connection = None
    if Path("./Database.db").is_file():
        # decript file
        connection = read_In_Database()
    else:
        connection = create_Database()
    if connection == None:
        print("Unknown Error, no Database loaded or created")
    # Master password already set?
    
    if connection:
            connection.close()
            # encrypt
            print("Database connection closed")


def insert_Data() -> None:
    ...


def hashing(input) -> str:
    ...


def retrieve_Data() -> None:
    ...


def read_In_Database() -> None | sqlite3.Connection:
    connection = sqlite3.connect(database="Database.db")
    cursor = connection.cursor()

    connection.commit()
    print("Database loaded")

    return connection



def create_Database(schema="./schema/schema.sql") -> None | sqlite3.Connection:

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





if __name__ == "__main__":
    main()