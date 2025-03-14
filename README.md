# Password Manager
*TKinter?
Core CS50x Concepts: File I/O, encryption, SQL, security, command-line interfaces.
Steps:

    Planning Phase:

        Define features: password storage, retrieval, encryption, master password hashing.

        Choose tools: SQLite (for database), argon2 (hashing), cryptography (AES encryption).

    Core Implementation:

        Database Setup: Create SQL tables to store encrypted passwords (similar to C$50 Finance’s structure).

        Encryption Layer: Use AES to encrypt/decrypt passwords before storing/retrieving.

        CLI Interface: Add commands like add, get, delete with argparse (Python) or getopt (C).

    Security Enhancements:

        Hash the master password with Argon2 (like CS50’s crypt function but modern).

        Implement timeout/attempt limits to prevent brute-force attacks.

    Testing:

        Validate edge cases: incorrect master passwords, corrupted databases.

        Test encryption/decryption cycles for data integrity.

Stretch Goals:

    Add a password generator (similar to CS50’s Scrabble’s randomization).

    Implement audit logging (track access times).

CLI Password Manager

Feasibility: 3–4 days (if using Python + prebuilt libraries).
MVP (Minimum Viable Product):

    Basic encryption (e.g., Fernet instead of AES).

    SQLite database with 1 table (no complex schemas).

    Simple add/get commands with a hardcoded master password (skip hashing for now).

Time-Saving Adjustments:

    Use the cryptography library’s built-in Fernet encryption instead of implementing AES from scratch.

    Skip audit logging and advanced features.

Bottlenecks:

    Debugging encryption/decryption workflows.

    Handling SQLite exceptions (e.g., locked databases).

Reverse Engineering: Python bytecode is easier to decompile than compiled C binaries.

    Mitigation: For a class project (not a commercial tool), this isn’t a priority. If it worries you, tools like pyinstaller can obfuscate code.

    Python’s garbage collector is less predictable, but you can still overwrite sensitive data manually (e.g., using ctypes to zero memory).



Security Best Practices for Your Project

Even in Python, you must:

    Avoid Hardcoding Keys: Store encryption keys in environment variables, not the code.

    Use Salted Hashing: For the master password, use argon2 with a unique salt (the library handles this by default).

    Limit File Permissions: Ensure the SQLite database is readable only by the user.

    Validate Inputs: Sanitize CLI inputs to prevent path traversal or SQL injection (even though SQLite is local).



. Tkinter (Best for Simplicity)

    Why Choose It:

        Built into Python (no installation needed).

        Simple and lightweight, perfect for small GUIs.

        Great for CS50x’s scope (no need for advanced features).

    Example Use Case:

        A window with fields for Website, Username, and Password, plus buttons like Save and Retrieve.

    Pros:

        Easy to learn (CS50x even uses it in some problem sets).

        Lightweight and fast for small projects.

    Cons:

        Limited styling options (looks outdated by default).

        Not ideal for complex layouts.

Resources:

    Tkinter Documentation

    CS50x’s Birthdays problem set (uses Tkinter).


Example Tkinter Workflow

Here’s how you could structure your password manager GUI with Tkinter:

    Main Window:

        Labels: Website, Username, Password.

        Entry fields: For user input.

        Buttons: Save, Retrieve, Clear.

    Event Handlers:

        Save: Encrypt the password and store it in SQLite.

        Retrieve: Decrypt and display the password.

        Clear: Reset the input fields.

    Styling:

        Use ttk for slightly better-looking widgets.

        Add padding and alignment for a cleaner layout.

