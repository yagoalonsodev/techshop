"""
Utilitats de validació per DNI, NIE i CIF
Implementa la lògica de validació segons les normes espanyoles
"""

import re


def validar_dni(dni: str) -> bool:
    """
    Validar DNI espanyol.
    Format: 8 números seguits d'una lletra de control.
    
    Args:
        dni (str): DNI a validar
        
    Returns:
        bool: True si el DNI és vàlid, False altrament
    """
    if not dni or len(dni.strip()) == 0:
        return False
    
    dni = dni.strip().upper()
    
    # Verificar formato
    if not re.match(r'^\d{8}[A-Z]$', dni):
        return False
    
    letras = "TRWAGMYFPDXBNJZSQVHLCKE"
    try:
        numero = int(dni[:8])
        letra = dni[8]
        letra_correcta = letras[numero % 23]
        return letra == letra_correcta
    except (ValueError, IndexError):
        return False


def validar_nie(nie: str) -> bool:
    """
    Validar NIE espanyol.
    Format: X/Y/Z + 7 números + lletra de control.
    
    Args:
        nie (str): NIE a validar
        
    Returns:
        bool: True si el NIE és vàlid, False altrament
    """
    if not nie or len(nie.strip()) == 0:
        return False
    
    nie = nie.strip().upper()
    
    # Verificar formato
    if not re.match(r'^[XYZ]\d{7}[A-Z]$', nie):
        return False
    
    letras = "TRWAGMYFPDXBNJZSQVHLCKE"
    valores = {'X': 0, 'Y': 1, 'Z': 2}
    
    try:
        inicial = nie[0]
        letra = nie[-1]
        numero_str = str(valores[inicial]) + nie[1:8]
        numero = int(numero_str)
        letra_correcta = letras[numero % 23]
        return letra == letra_correcta
    except (ValueError, KeyError, IndexError):
        return False


def validar_cif(cif: str) -> bool:
    """
    Validar CIF espanyol.
    Format: Lletra + 7 números + caràcter de control.
    
    Args:
        cif (str): CIF a validar
        
    Returns:
        bool: True si el CIF és vàlid, False altrament
    """
    if not cif or len(cif.strip()) == 0:
        return False
    
    cif = cif.strip().upper()
    
    # Verificar formato
    if not re.match(r'^[ABCDEFGHJKLMNPQRSUVW]\d{7}[0-9A-J]$', cif):
        return False
    
    letra_inicial = cif[0]
    digitos = cif[1:8]
    control_char = cif[8]
    
    suma_pares = 0
    suma_impares = 0
    
    try:
        for i in range(len(digitos)):
            n = int(digitos[i])
            if (i + 1) % 2 == 0:
                suma_pares += n
            else:
                mult = n * 2
                suma_impares += mult // 10 + (mult % 10)
        
        suma = suma_pares + suma_impares
        unidad = suma % 10
        control_num = (10 - unidad) % 10
        tabla_control = "JABCDEFGHI"
        control_letra = tabla_control[control_num]
        
        # Reglas según letra inicial
        if letra_inicial in "ABEH":
            return control_char == str(control_num)
        if letra_inicial in "KPQS":
            return control_char == control_letra
        
        # Otros casos: ambos son válidos
        return control_char == str(control_num) or control_char == control_letra
    except (ValueError, IndexError):
        return False


def validar_dni_nie(dni: str) -> bool:
    """
    Validar DNI o NIE (per usuaris individuals).
    Detecta automàticament si és DNI o NIE segons el format.
    
    Args:
        dni (str): DNI o NIE a validar
        
    Returns:
        bool: True si és vàlid, False altrament
    """
    if not dni or len(dni.strip()) == 0:
        return False
    
    dni_upper = dni.strip().upper()
    
    # Si comienza con X, Y o Z, es NIE
    if re.match(r'^[XYZ]', dni_upper):
        return validar_nie(dni_upper)
    # Si no, es DNI
    return validar_dni(dni_upper)


def validar_cif_nif(nif: str) -> bool:
    """
    Validar CIF/NIF (per empreses).
    
    Args:
        nif (str): CIF/NIF a validar
        
    Returns:
        bool: True si és vàlid, False altrament
    """
    if not nif or len(nif.strip()) == 0:
        return False
    
    return validar_cif(nif.strip().upper())

