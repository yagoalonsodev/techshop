"""
Generador de factures en format PDF
Utilitza ReportLab per generar factures PDF
"""

import sqlite3
from io import BytesIO
from decimal import Decimal
from datetime import datetime
from typing import Optional

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False


def generate_invoice_pdf(order_id: int, user_id: int) -> Optional[bytes]:
    """
    Generar una factura en format PDF per una comanda.
    
    Args:
        order_id (int): ID de la comanda
        user_id (int): ID de l'usuari (per verificar permisos)
        
    Returns:
        bytes o None: Dades del PDF o None si hi ha error
    """
    if not REPORTLAB_AVAILABLE:
        print("❌ ReportLab no está disponible")
        return None
    
    print(f"🔍 Iniciando generación de factura para orden {order_id}, usuario {user_id}")
    
    try:
        with sqlite3.connect('techshop.db') as conn:
            cursor = conn.cursor()
            
            # Obtenir dades de la comanda
            print(f"📋 Buscando orden {order_id} para usuario {user_id}...")
            cursor.execute(
                'SELECT id, total, created_at, user_id FROM "Order" WHERE id = ? AND user_id = ?',
                (order_id, user_id)
            )
            order_result = cursor.fetchone()
            if not order_result:
                print(f"❌ No se encontró la orden {order_id} para el usuario {user_id}")
                return None
            
            print(f"✅ Orden encontrada: total={order_result[1]}, fecha={order_result[2]}")
            
            order_id_db, total, created_at, user_id_db = order_result
            
            # Parsear fecha de forma más robusta
            try:
                if created_at:
                    if isinstance(created_at, str):
                        # Intentar diferentes formatos de fecha
                        try:
                            order_date = datetime.fromisoformat(created_at)
                        except ValueError:
                            try:
                                # Formato alternativo: "YYYY-MM-DD HH:MM:SS"
                                order_date = datetime.strptime(created_at, "%Y-%m-%d %H:%M:%S")
                            except ValueError:
                                try:
                                    # Formato alternativo: "YYYY-MM-DD"
                                    order_date = datetime.strptime(created_at, "%Y-%m-%d")
                                except ValueError:
                                    order_date = datetime.now()
                    else:
                        order_date = datetime.now()
                else:
                    order_date = datetime.now()
            except Exception as e:
                print(f"⚠️  Error parseando fecha: {e}, usando fecha actual")
                order_date = datetime.now()
            
            # Obtenir dades de l'usuari (con manejo de columnas opcionales)
            print(f"👤 Buscando datos del usuario {user_id}...")
            try:
                cursor.execute(
                    "SELECT username, email, address, account_type, dni, nif FROM User WHERE id = ?",
                    (user_id,)
                )
                user_result = cursor.fetchone()
                if not user_result:
                    print(f"❌ No se encontró el usuario {user_id}")
                    return None
                
                print(f"✅ Usuario encontrado, columnas: {len(user_result)}")
                
                if len(user_result) >= 6:
                    username, email, address, account_type, dni, nif = user_result
                    # Asegurar que dni y nif no sean None
                    dni = dni or ""
                    nif = nif or ""
                    account_type = account_type or "user"
                else:
                    # Compatibilidad con esquema antiguo
                    username = user_result[0] if len(user_result) > 0 else ""
                    email = user_result[1] if len(user_result) > 1 else ""
                    address = user_result[2] if len(user_result) > 2 else ""
                    account_type = user_result[3] if len(user_result) > 3 else "user"
                    dni = user_result[4] if len(user_result) > 4 else ""
                    nif = user_result[5] if len(user_result) > 5 else ""
                
                print(f"📋 Datos usuario: username={username}, email={email}, account_type={account_type}, dni={dni}, nif={nif}")
            except sqlite3.OperationalError:
                # Si las columnas no existen
                cursor.execute(
                    "SELECT username, email, address FROM User WHERE id = ?",
                    (user_id,)
                )
                user_result = cursor.fetchone()
                if not user_result:
                    return None
                username, email, address = user_result
                account_type = "user"
                dni = ""
                nif = ""
            
            # Obtenir items de la comanda
            cursor.execute("""
                SELECT oi.quantity, p.name, p.price
                FROM OrderItem oi
                JOIN Product p ON oi.product_id = p.id
                WHERE oi.order_id = ?
                ORDER BY p.name
            """, (order_id,))
            items = cursor.fetchall()
            
            if not items:
                print(f"⚠️  No se encontraron items para la orden {order_id}")
                return None
            
            print(f"📦 Items encontrados: {len(items)}")
            
            # Crear PDF en memòria
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4, 
                                    rightMargin=20*mm, leftMargin=20*mm,
                                    topMargin=20*mm, bottomMargin=20*mm)
            
            # Estils
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                textColor=colors.HexColor('#111111'),
                spaceAfter=30,
                alignment=TA_CENTER
            )
            
            # Estilo para texto en negrita en tablas (mismo tamaño que items_table)
            bold_style = ParagraphStyle(
                'BoldStyle',
                parent=styles['Normal'],
                fontName='Helvetica-Bold',
                fontSize=12
            )
            
            # Contingut del PDF
            story = []
            
            # Títol
            story.append(Paragraph("FACTURA", title_style))
            story.append(Spacer(1, 10*mm))
            
            # Informació de l'empresa (TechShop)
            company_info = [
                ["<b>TechShop</b>", ""],
                ["Carrer de l'Exemple, 123", ""],
                ["08001 Barcelona, Espanya", ""],
                ["NIF: B12345678", ""],
            ]
            
            # Informació del client
            client_label = "NIF:" if account_type == 'company' else "DNI:"
            client_id = nif if account_type == 'company' else dni
            
            # Construir líneas de información del cliente (solo mostrar si existen)
            client_info_lines = [
                ["Carrer de l'Exemple, 123", f"Nom: {username}", f"Número: #{order_id:06d}"],
            ]
            
            # Añadir email solo si existe
            if email:
                client_info_lines.append(["08001 Barcelona, Espanya", f"Email: {email}", f"Data: {order_date.strftime('%d/%m/%Y')}"])
            else:
                client_info_lines.append(["08001 Barcelona, Espanya", "", f"Data: {order_date.strftime('%d/%m/%Y')}"])
            
            # Añadir dirección solo si existe
            if address:
                client_info_lines.append(["NIF: B12345678", f"Adreça: {address}", ""])
            else:
                client_info_lines.append(["NIF: B12345678", "", ""])
            
            # Añadir línea de DNI/NIF solo si existe
            if client_id:
                client_info_lines.append(["", f"{client_label} {client_id}", ""])
            
            # Taula d'informació - usar texto plano en encabezados para que coincida con items_table
            info_data = [
                ["TechShop", "Dades del Client", "Dades de la Factura"]
            ] + client_info_lines
            
            info_table = Table(info_data, colWidths=[60*mm, 60*mm, 60*mm])
            info_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#111111')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('TOPPADDING', (0, 0), (-1, 0), 12),
                ('LEFTPADDING', (0, 0), (-1, -1), 8),
                ('RIGHTPADDING', (0, 0), (-1, -1), 8),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f5f5')]),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('TOPPADDING', (0, 1), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
            ]))
            story.append(info_table)
            story.append(Spacer(1, 15*mm))
            
            # Taula d'items
            items_data = [["Producte", "Quantitat", "Preu Unitari", "Total"]]
            
            for quantity, product_name, price in items:
                unit_price = Decimal(str(price))
                item_total = unit_price * quantity
                items_data.append([
                    product_name,
                    str(quantity),
                    f"{unit_price:.2f} €",
                    f"{item_total:.2f} €"
                ])
            
            items_table = Table(items_data, colWidths=[80*mm, 30*mm, 35*mm, 35*mm])
            items_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#111111')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
                ('ALIGN', (2, 1), (-1, -1), 'RIGHT'),
                ('ALIGN', (3, 1), (-1, -1), 'RIGHT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('TOPPADDING', (0, 0), (-1, 0), 12),
                ('LEFTPADDING', (0, 0), (-1, -1), 8),
                ('RIGHTPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f5f5')]),
                ('TOPPADDING', (0, 1), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
            ]))
            story.append(items_table)
            story.append(Spacer(1, 10*mm))
            
            # Total (usando Paragraph para HTML)
            total_bold_style = ParagraphStyle(
                'TotalBoldStyle',
                parent=styles['Normal'],
                fontName='Helvetica-Bold',
                fontSize=16
            )
            total_data = [
                ["", "", 
                 Paragraph("<b>TOTAL:</b>", total_bold_style), 
                 Paragraph(f"<b>{Decimal(str(total)):.2f} €</b>", total_bold_style)]
            ]
            total_table = Table(total_data, colWidths=[80*mm, 30*mm, 35*mm, 35*mm])
            total_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
                ('FONTNAME', (2, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (2, 0), (-1, 0), 16),
                ('TEXTCOLOR', (2, 0), (-1, 0), colors.HexColor('#111111')),
                ('TOPPADDING', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
                ('LEFTPADDING', (0, 0), (-1, -1), 8),
                ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ]))
            story.append(total_table)
            
            # Generar PDF
            print(f"📄 Generando PDF para orden {order_id}...")
            doc.build(story)
            buffer.seek(0)
            pdf_bytes = buffer.getvalue()
            print(f"✅ PDF generado correctamente, tamaño: {len(pdf_bytes)} bytes")
            return pdf_bytes
            
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"❌ Error generant PDF: {e}")
        print(f"📋 Detalles del error:\n{error_details}")
        return None

