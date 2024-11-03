
DROP TABLE IF EXISTS task;
DROP TABLE IF EXISTS apiKey;

CREATE TABLE task (
    name TEXT PRIMARY KEY,
    startDate TEXT DEFAULT NULL,
    status TEXT DEFAULT 'Created'
);

CREATE TABLE apiKey (
    key TEXT PRIMARY KEY,
    active INTEGER DEFAULT 1 NOT NULL
);

INSERT INTO apiKey 
    (key) 
    VALUES 
    ('admin');