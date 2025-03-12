CREATE TABLE IF NOT EXISTS Passwords (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	passwords TEXT NOT NULL UNIQUE,
	"date" DATE DEFAULT CURRENT_TIMESTAMP -- needs to be yyyy-mm-dd or won't be properly seen by ORDER BY etc
	-- SELECT id, strftime('%d-%m-%Y', date) AS formatted_date FROM your_table; will retrieve it in dd-mm-yyyy
	);

CREATE TABLE IF NOT EXISTS Username (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	username TEXT NOT NULL UNIQUE,
	"date" DATE DEFAULT CURRENT_TIMESTAMP
	);
	
CREATE TABLE IF NOT EXISTS Mails (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	mail TEXT NOT NULL UNIQUE
	);


CREATE TABLE IF NOT EXISTS Logins (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	username_id INTEGER,
	password_id INTEGER,
	mail_id INTEGER,	
	website TEXT,
	title TEXT,
	"date" DATE DEFAULT CURRENT_TIMESTAMP,
	FOREIGN KEY (username_id) REFERENCES Username(id) ON DELETE RESTRICT,
	FOREIGN KEY (password_id) REFERENCES Passwords(id) ON DELETE RESTRICT,
	FOREIGN KEY (mail_id) REFERENCES Mails(id) ON DELETE RESTRICT
	);
	

CREATE TABLE IF NOT EXISTS Notes (
	note_id INTEGER PRIMARY KEY AUTOINCREMENT,
	title TEXT,
	note TEXT NOT NULL,
	"date" DATE DEFAULT CURRENT_TIMESTAMP
	);
	
	
-- CREATE TABLE IF NOT EXISTS Overview (
-- 	overview_id INTEGER PRIMARY KEY AUTOINCREMENT,
-- 	password_id INTEGER,
-- 	note_id INTEGER,
-- 	website_id INTEGER,
-- 	username_id INTEGER,
-- 	FOREIGN KEY (password_id) REFERENCES Passwords(password_id),
-- 	FOREIGN KEY (note_id) REFERENCES Notes(note_id),
-- 	FOREIGN KEY (website_id) REFERENCES Websites(website_id),
-- 	FOREIGN KEY (username_id) REFERENCES Username(username_id)
-- 	);