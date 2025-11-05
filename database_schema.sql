-- Esquema de Base de Datos para TechShop
-- SQLite Database Schema

-- Tabla Product: gestiona la llista de productes disponibles
CREATE TABLE Product (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100),
    price DECIMAL(10,2),
    stock INTEGER
);

-- Tabla User: conté la informació de l'usuari que fa la compra
CREATE TABLE User (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(20),
    password_hash VARCHAR(60),
    email VARCHAR(100),
    address TEXT,
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
