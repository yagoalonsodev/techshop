"""
Script per inicialitzar la base de dades TechShop
Crea les taules i insereix dades de prova
"""

import sqlite3
import os


def init_database():
    """
    Inicialitza la base de dades techshop.db
    Crea les taules segons l'esquema i insereix productes de prova
    """
    
    # Esborrar base de dades anterior si existeix
    if os.path.exists('techshop.db'):
        os.remove('techshop.db')
        print("🗑️  Base de dades anterior eliminada")
    
    # Connectar a la base de dades (es crea automàticament)
    conn = sqlite3.connect('techshop.db')
    cursor = conn.cursor()
    
    print("📦 Creant base de dades techshop.db...")
    
    # Crear taula Product
    cursor.execute("""
        CREATE TABLE Product (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(100),
            price DECIMAL(10,2),
            stock INTEGER
        )
    """)
    print("✅ Taula Product creada")
    
    # Crear taula User
    cursor.execute("""
        CREATE TABLE User (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username VARCHAR(20),
            password_hash VARCHAR(60),
            email VARCHAR(100),
            address TEXT,
            created_at DATETIME
        )
    """)
    print("✅ Taula User creada")
    
    # Crear taula Order
    cursor.execute("""
        CREATE TABLE "Order" (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            total DECIMAL(10,2),
            created_at DATETIME,
            user_id INTEGER,
            FOREIGN KEY (user_id) REFERENCES User(id)
        )
    """)
    print("✅ Taula Order creada")
    
    # Crear taula OrderItem
    cursor.execute("""
        CREATE TABLE OrderItem (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER,
            product_id INTEGER,
            quantity INTEGER,
            FOREIGN KEY (order_id) REFERENCES "Order"(id),
            FOREIGN KEY (product_id) REFERENCES Product(id)
        )
    """)
    print("✅ Taula OrderItem creada")
    
    # Inserir productes de prova
    products = [
        ("MacBook Pro 14\"", 1999.00, 15),
        ("iPhone 15 Pro", 1199.00, 25),
        ("iPad Air", 649.00, 30),
        ("Apple Watch Series 9", 429.00, 40),
        ("AirPods Pro", 279.00, 50),
        ("Magic Keyboard", 349.00, 20),
        ("Sony WH-1000XM5", 399.00, 18),
        ("Samsung Galaxy S24", 899.00, 22),
        ("Dell XPS 13", 1299.00, 12),
        ("Logitech MX Master 3", 99.00, 35)
    ]
    
    cursor.executemany(
        "INSERT INTO Product (name, price, stock) VALUES (?, ?, ?)",
        products
    )
    print(f"✅ {len(products)} productes insertats")
    
    # Confirmar els canvis
    conn.commit()
    print("\n🎉 Base de dades inicialitzada correctament!")
    print(f"📊 Productes disponibles: {len(products)}")
    
    # Mostrar productes
    print("\n📋 Llista de productes:")
    print("-" * 60)
    cursor.execute("SELECT id, name, price, stock FROM Product")
    for row in cursor.fetchall():
        print(f"  ID {row[0]}: {row[1]} - {row[2]:.2f} € (Stock: {row[3]})")
    print("-" * 60)
    
    # Tancar connexió 
    conn.close()
    print("\n✅ Tot llest! Pots executar l'aplicació amb: python3 app.py")


if __name__ == '__main__':
    init_database()

