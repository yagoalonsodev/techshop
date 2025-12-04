"""
Servei de gestió de productes per empreses
Implementa la lògica de negoci per a les operacions de gestió de productes de les empreses
"""

import sqlite3
import os
import io
from pathlib import Path
from decimal import Decimal
from typing import Dict, List, Tuple, Optional
from werkzeug.utils import secure_filename
from PIL import Image
from models import Product

ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
MAX_IMAGES = 4


class CompanyService:
    """Servei per gestionar productes de les empreses"""
    
    def __init__(self, db_path: str = "techshop.db", static_folder: str = "static"):
        self.db_path = db_path
        self.static_folder = static_folder
    
    def get_company_products(self, company_id: int) -> List[Product]:
        """
        Obtenir tots els productes d'una empresa.
        
        Args:
            company_id (int): ID de l'empresa
            
        Returns:
            List[Product]: Llista de productes de l'empresa
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT id, name, price, stock FROM Product WHERE company_id = ? ORDER BY id",
                    (company_id,)
                )
                results = cursor.fetchall()
                
                products = []
                for row in results:
                    products.append(Product(
                        id=row[0],
                        name=row[1],
                        price=Decimal(str(row[2])),
                        stock=row[3]
                    ))
                return products
        except sqlite3.Error:
            return []
    
    def get_product_by_id(self, product_id: int, company_id: int) -> Optional[Product]:
        """
        Obtenir un producte per ID, verificant que pertany a l'empresa.
        
        Args:
            product_id (int): ID del producte
            company_id (int): ID de l'empresa
            
        Returns:
            Optional[Product]: Producte si existeix i pertany a l'empresa, None altrament
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT id, name, price, stock FROM Product WHERE id = ? AND company_id = ?",
                    (product_id, company_id)
                )
                row = cursor.fetchone()
                
                if row:
                    return Product(
                        id=row[0],
                        name=row[1],
                        price=Decimal(str(row[2])),
                        stock=row[3]
                    )
        except sqlite3.Error:
            pass
        
        return None
    
    def create_product(self, company_id: int, name: str, price: Decimal, stock: int) -> Tuple[bool, str, Optional[int]]:
        """
        Crear un nou producte per una empresa.
        
        Args:
            company_id (int): ID de l'empresa
            name (str): Nom del producte
            price (Decimal): Preu del producte
            stock (int): Stock inicial
            
        Returns:
            Tuple[bool, str, Optional[int]]: (èxit, missatge, product_id)
        """
        if not name or len(name.strip()) == 0:
            return False, "El nom del producte és obligatori", None
        
        if price < 0:
            return False, "El preu no pot ser negatiu", None
        
        if stock < 0:
            return False, "El stock no pot ser negatiu", None
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO Product (name, price, stock, company_id) VALUES (?, ?, ?, ?)",
                    (name.strip(), float(price), stock, company_id)
                )
                product_id = cursor.lastrowid
                conn.commit()
                return True, f"Producte creat correctament", product_id
        except sqlite3.Error as e:
            return False, f"Error creant el producte: {str(e)}", None
    
    def update_product(self, product_id: int, company_id: int, name: str, price: Decimal, stock: int) -> Tuple[bool, str]:
        """
        Actualitzar un producte existent.
        
        Args:
            product_id (int): ID del producte
            company_id (int): ID de l'empresa
            name (str): Nou nom del producte
            price (Decimal): Nou preu
            stock (int): Nou stock
            
        Returns:
            Tuple[bool, str]: (èxit, missatge)
        """
        # Verificar que el producte pertany a l'empresa
        product = self.get_product_by_id(product_id, company_id)
        if not product:
            return False, "Producte no trobat o no tens permís per editar-lo"
        
        if not name or len(name.strip()) == 0:
            return False, "El nom del producte és obligatori"
        
        if price < 0:
            return False, "El preu no pot ser negatiu"
        
        if stock < 0:
            return False, "El stock no pot ser negatiu"
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE Product SET name = ?, price = ?, stock = ? WHERE id = ? AND company_id = ?",
                    (name.strip(), float(price), stock, product_id, company_id)
                )
                conn.commit()
                return True, "Producte actualitzat correctament"
        except sqlite3.Error as e:
            return False, f"Error actualitzant el producte: {str(e)}"
    
    def can_delete_product(self, product_id: int, company_id: int) -> Tuple[bool, str]:
        """
        Verificar si un producte pot ser eliminat (no té vendes).
        
        Args:
            product_id (int): ID del producte
            company_id (int): ID de l'empresa
            
        Returns:
            Tuple[bool, str]: (pot eliminar, missatge)
        """
        # Verificar que el producte pertany a l'empresa
        product = self.get_product_by_id(product_id, company_id)
        if not product:
            return False, "Producte no trobat o no tens permís per eliminar-lo"
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                # Verificar si hi ha ordres amb aquest producte
                cursor.execute(
                    "SELECT COUNT(*) FROM OrderItem WHERE product_id = ?",
                    (product_id,)
                )
                order_count = cursor.fetchone()[0]
                
                if order_count > 0:
                    return False, f"No es pot eliminar el producte perquè té {order_count} venda(s) associada(s)"
                
                return True, "Producte pot ser eliminat"
        except sqlite3.Error as e:
            return False, f"Error verificant vendes: {str(e)}"
    
    def delete_product(self, product_id: int, company_id: int) -> Tuple[bool, str]:
        """
        Eliminar un producte (només si no té vendes).
        
        Args:
            product_id (int): ID del producte
            company_id (int): ID de l'empresa
            
        Returns:
            Tuple[bool, str]: (èxit, missatge)
        """
        can_delete, message = self.can_delete_product(product_id, company_id)
        if not can_delete:
            return False, message
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "DELETE FROM Product WHERE id = ? AND company_id = ?",
                    (product_id, company_id)
                )
                conn.commit()
                
                # Eliminar imatges del producte
                self._delete_product_images(product_id)
                
                return True, "Producte eliminat correctament"
        except sqlite3.Error as e:
            return False, f"Error eliminant el producte: {str(e)}"
    
    def save_product_images(self, product_id: int, files: List) -> Tuple[bool, str]:
        """
        Guardar imatges per a un producte (màxim 4 en total).
        
        Args:
            product_id (int): ID del producte
            files: Llista de fitxers d'imatge
            
        Returns:
            Tuple[bool, str]: (èxit, missatge)
        """
        if not files or len(files) == 0:
            return True, "No hi ha imatges per guardar"
        
        # Filtrar fitxers vàlids
        valid_files = []
        for file in files:
            if file and file.filename:
                filename = secure_filename(file.filename)
                file_ext = Path(filename).suffix.lower()
                if file_ext in ALLOWED_EXTENSIONS:
                    valid_files.append((file, file_ext))
        
        if len(valid_files) == 0:
            return True, "No hi ha imatges vàlides per guardar"
        
        # Crear directori per al producte
        images_dir = Path(self.static_folder) / 'img' / 'products' / str(product_id)
        images_dir.mkdir(parents=True, exist_ok=True)
        
        # Comptar imatges existents
        existing_images = []
        if images_dir.exists():
            for img_file in sorted(images_dir.iterdir()):
                if img_file.is_file() and img_file.suffix.lower() in ALLOWED_EXTENSIONS:
                    existing_images.append(img_file)
        
        # Calcular quantes imatges podem afegir
        available_slots = MAX_IMAGES - len(existing_images)
        if available_slots <= 0:
            return False, f"Ja tens {MAX_IMAGES} imatges. Elimina algunes abans d'afegir-ne de noves."
        
        if len(valid_files) > available_slots:
            return False, f"Només pots afegir {available_slots} imatge(s) més (màxim {MAX_IMAGES} en total)"
        
        # Trobar el següent número disponible
        next_number = len(existing_images) + 1
        
        # Guardar imatges comprimides
        saved_count = 0
        for file, file_ext in valid_files:
            if next_number > MAX_IMAGES:
                break
            try:
                # Generar nom únic per a la imatge (format: {idfoto}.{ext})
                # Per millor compressió, sempre usem .jpg
                image_filename = f"{next_number}.jpg"
                image_path = images_dir / image_filename
                
                # Comprimir imatge per reduir el tamany en un 80%
                self._compress_image(file, image_path, file_ext)
                
                saved_count += 1
                next_number += 1
            except Exception as e:
                return False, f"Error guardant imatge: {str(e)}"
        
        return True, f"{saved_count} imatge(s) guardada(s) correctament"
    
    def _compress_image(self, file, output_path: Path, file_ext: str):
        """
        Comprimir una imatge per reduir el seu tamany en un 80% (deixar només el 20%).
        Utilitza tècniques similars a Squoosh per optimitzar les imatges.
        Format de nom: {idfoto}.jpg (sempre JPEG per millor compressió)
        
        Args:
            file: Fitxer d'imatge de Flask
            output_path (Path): Ruta on guardar la imatge comprimida (ja amb .jpg)
            file_ext (str): Extensió del fitxer original (per informació)
        """
        # Carregar imatge
        file.seek(0)
        img = Image.open(io.BytesIO(file.read()))
        
        # Redimensionar si és massa gran (màxim 1920px) - ajuda a reduir tamany significativament
        max_size = 1920
        if img.width > max_size or img.height > max_size:
            img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
        
        # Convertir a RGB (necessari per JPEG)
        if img.mode in ('RGBA', 'LA', 'P'):
            # Crear fons blanc per imatges amb transparència
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            if img.mode in ('RGBA', 'LA'):
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            img = background
        elif img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Guardar com JPEG amb qualitat baixa per reduir 80% del tamany
        # Qualitat 20 = aproximadament 20% del tamany original (reducció del 80%)
        img.save(
            str(output_path),
            'JPEG',
            quality=20,  # Qualitat baixa per reduir tamany en ~80%
            optimize=True,
            progressive=True
        )
    
    def _delete_product_images(self, product_id: int):
        """
        Eliminar totes les imatges d'un producte.
        
        Args:
            product_id (int): ID del producte
        """
        images_dir = Path(self.static_folder) / 'img' / 'products' / str(product_id)
        if images_dir.exists():
            try:
                for image_file in images_dir.iterdir():
                    if image_file.is_file():
                        image_file.unlink()
                images_dir.rmdir()
            except Exception:
                pass  # Ignorar errors en l'eliminació

