BEGIN TRANSACTION;

CREATE TEMPORARY TABLE users_backup(id,user_name,first_name,last_name);

INSERT INTO users_backup SELECT id,user_name,first_name,last_name FROM users;

DROP TABLE users;

CREATE TABLE IF NOT EXISTS users (
          id TEXT PRIMARY KEY,
          user_name TEXT,
          first_name TEXT,
          last_name TEXT
);

INSERT INTO users SELECT id,user_name,first_name,last_name FROM users_backup;

DROP TABLE users_backup;

COMMIT;