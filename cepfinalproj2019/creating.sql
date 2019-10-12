CREATE TABLE users (
  username VARCHAR UNIQUE,
  password VARCHAR NOT NULL,
  email VARCHAR NOT NULL,
  rating INTEGER
);
