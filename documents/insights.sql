CREATE TABLE advisor(
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    cpf VARCHAR(14) NOT NULL,
    email VARCHAR(100) NOT NULL,
    cel VARCHAR(20) NOT NULL,
    address VARCHAR(100) NOT NULL,
    complement VARCHAR(100) NOT NULL,
    city VARCHAR(100) NOT NULL,
    state VARCHAR(100) NOT NULL,
    zip_code VARCHAR(20) NOT NULL,
    obs VARCHAR(1000) NOT NULL,
    username VARCHAR(30) NOT NULL,
    password VARCHAR(50) NOT NULL,
    birth VARCHAR(10) NOT NULL,
    salary FLOAT NOT NULL,
    work_code INT NOT NULL,
    cvm_code VARCHAR(20) NOT NULL,
    status INTEGER NOT NULL
);

CREATE TABLE client (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    cpf VARCHAR(14) NOT NULL,
    email VARCHAR(100) NOT NULL,
    cel VARCHAR(20) NOT NULL,
    username VARCHAR(30) NOT NULL,
    password VARCHAR(50) NOT NULL,
    suitability VARCHAR(20) NOT NULL,
    address VARCHAR(100) NOT NULL,
    complement VARCHAR(100) NOT NULL,
    city VARCHAR(100) NOT NULL,
    state VARCHAR(100) NOT NULL,
    zip_code VARCHAR(20) NOT NULL,
    obs VARCHAR(1000) NOT NULL,
    status INTEGER NOT NULL,
	advisor_id INTEGER NOT NULL,
	FOREIGN KEY (advisor_id) REFERENCES advisor(id)
);

CREATE TABLE portfolio(
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    amount FLOAT NOT NULL,
    status INTEGER NOT NULL,
	advisor_id INTEGER NOT NULL,
	FOREIGN KEY (advisor_id) REFERENCES advisor(id)
);

CREATE TABLE product(
    key SERIAL PRIMARY KEY,
    id VARCHAR(10),
    proportion FLOAT NOT NULL,
    amount FLOAT NOT NULL,
	portfolio_id INTEGER NOT NULL,
    FOREIGN KEY (portfolio_id) REFERENCES portfolio(id) ON DELETE CASCADE
);

CREATE TABLE portfolio_client(
  portfolio_id INT,
  client_id INT,
  FOREIGN KEY (portfolio_id) REFERENCES portfolio(id),
  FOREIGN KEY (client_id) REFERENCES client(id),
  PRIMARY KEY (portfolio_id, client_id)
);