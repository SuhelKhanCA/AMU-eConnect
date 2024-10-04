-- CREATING THE AMU eCONNECT DATABASE

CREATE DATABASE econnect;

-- USE IT

USE econnect;

-- ADMIN TABLE
CREATE TABLE econnect_admin(
    id INT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL
);

-- INSERT Admin Record
INSERT INTO econnect_admin (id, name, email, password)
VALUES (1, 'suhel', 'suhelkhanca@gmail.com', 'password');

SELECT * FROM econnect_admin;
-- USER TABLE

CREATE TABLE user(
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    enrollment_no VARCHAR(10),
    faculty_no VARCHAR(10),
    id_proof BLOB NOT NULL
);

-- Detailed description of user -> TABLE

CREATE TABLE user_desc(
    id INT PRIMARY KEY,
    short_desc VARCHAR(250),
    detail_desc TEXT,
    passing_year DECIMAL(4),
    user_image BLOB NOT NULL,
    department VARCHAR(20),
    course VARCHAR(20),
    social1 VARCHAR(150),
    social2 VARCHAR(150),
    social3 VARCHAR(150),
    social4 VARCHAR(150),
    FOREIGN KEY (id) REFERENCES user(id)
);