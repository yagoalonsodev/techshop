-- Esquema de Base de Datos para TechShop
-- SQLite Database Schema

-- Tabla Product: gestiona la llista de productes disponibles
CREATE TABLE Product (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100),
    price DECIMAL(10,2),
    stock INTEGER,
    company_id INTEGER,
    FOREIGN KEY (company_id) REFERENCES User(id)
);

-- Tabla User: conté la informació de l'usuari que fa la compra
CREATE TABLE User (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(20),
    password_hash VARCHAR(60),
    email VARCHAR(100),
    address TEXT,
    role VARCHAR(10) DEFAULT 'common' CHECK(role IN ('common', 'admin')),
    account_type VARCHAR(10) DEFAULT 'user' CHECK(account_type IN ('user', 'company')),
    dni VARCHAR(20),  -- DNI per usuaris individuals
    nif VARCHAR(20),  -- NIF per empreses
    created_at DATETIME
);

-- Tabla Order: representa cada comanda realitzada
CREATE TABLE "Order" (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    total DECIMAL(10,2),
    created_at DATETIME,
    user_id INTEGER,
    FOREIGN KEY (user_id) REFERENCES User(id)
);

-- Tabla OrderItem: especifica els productes que formen part d'una comanda
CREATE TABLE OrderItem (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER,
    product_id INTEGER,
    quantity INTEGER,
    FOREIGN KEY (order_id) REFERENCES "Order"(id),
    FOREIGN KEY (product_id) REFERENCES Product(id)
);
