"""
Modelo User para TechShop
Gestiona la informació de l'usuari que fa la compra
"""

from datetime import datetime
from typing import Optional


class User:
    """Model per gestionar la informació de l'usuari que fa la compra"""
    
    def __init__(self, id: Optional[int] = None, username: str = "", 
                 password_hash: str = "", email: str = "", 
                 address: str = "",
                 role: str = "common",
                 account_type: str = "user",
                 dni: str = "",
                 nif: str = "",
                 created_at: Optional[datetime] = None):
        self.id = id
        self.username = username
        self.password_hash = password_hash
        self.email = email
        self.address = address
        self.role = role  # 'common' o 'admin'
        self.account_type = account_type  # 'user' o 'company'
        self.dni = dni  # DNI per usuaris individuals
        self.nif = nif  # NIF per empreses
        self.created_at = created_at or datetime.now()
    
    def is_admin(self) -> bool:
        """Verificar si l'usuari és administrador."""
        return self.role == "admin"
    
    def __repr__(self):
        return f"User(id={self.id}, username='{self.username}', email='{self.email}', role='{self.role}', account_type='{self.account_type}')"

