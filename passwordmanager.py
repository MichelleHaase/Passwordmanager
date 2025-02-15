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
    read_In__Create_Database()


def insert_Data() -> None:
    ...


def hashing(input) -> str:
    ...


def retrieve_Data() -> None:
    ...

def read_In__Create_Database(database="test.db", schema="./schema/schema.sql") -> None:

    connection = sqlite3.connect(database)
    cursor = connection.cursor()

    schema_path = Path(schema)
    if not schema_path.is_file():
        print(f"Schema file not found: {schema_path}")
        return

    with open(schema_path, 'r') as schema_file:
        schema = schema_file.read()

    cursor.executescript(schema)

    connection.commit()
    connection.close()


if __name__ == "__main__":
    main()