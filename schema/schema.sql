CREATE TABLE IF NOT EXISTS Passwords (
	password_id INTEGER PRIMARY KEY AUTOINCREMENT,
	password TEXT NOT NULL UNIQUE,
	"date" TEXT -- needs to be yyyy-mm-dd or won't be properly seen by ORDER BY etc
	-- SELECT id, strftime('%d-%m-%Y', date) AS formatted_date FROM your_table; will retrieve it in dd-mm-yyyy
	);
	
	
CREATE TABLE IF NOT EXISTS Username (
	username_id INTEGER PRIMARY KEY AUTOINCREMENT,
	password_id INTEGER,
	username TEXT,
	email TEXT ,
	"date" TEXT,
	FOREIGN KEY (password_id) REFERENCES Passwords(password_id) -- not deleting on Cascade since i don't want userID in passwords
	);
	

CREATE TABLE IF NOT EXISTS Notes (
	note_id INTEGER PRIMARY KEY AUTOINCREMENT,
	note TEXT,
	"date" TEXT
	);
	
	
CREATE TABLE IF NOT EXISTS Websites (
	website_id INTEGER PRIMARY KEY AUTOINCREMENT,
	address TEXT	
	);
	
	
CREATE TABLE IF NOT EXISTS Overview (
	overview_id INTEGER PRIMARY KEY AUTOINCREMENT,
	password_id INTEGER,
	note_id INTEGER,
	website_id INTEGER,
	username_id INTEGER,
	FOREIGN KEY (password_id) REFERENCES Passwords(password_id),
	FOREIGN KEY (note_id) REFERENCES Notes(note_id),
	FOREIGN KEY (website_id) REFERENCES Websites(website_id),
	FOREIGN KEY (username_id) REFERENCES Username(username_id)
	);