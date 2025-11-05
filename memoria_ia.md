# Memoria del Uso de Inteligencia Artificial - TechShop

## Sección 5: Uso de la Inteligencia Artificial y Requisitos Adicionales

### Reglas Establecidas para la IA

Durante el desarrollo de esta práctica, se establecieron las siguientes reglas para el uso de la IA:

1. **No barrejar el codi HTML amb consultes SQL o lògica de negoci**
2. **Tots els accessos a la base de dades s'han de fer a través de funcions o mètodes específics en la capa de dades**
3. **No superar les 5 unitats per producte al carretó**
4. **Validar sempre les dades rebudes des del client abans de processar-les**
5. **Utilitzar noms de funcions en anglès seguint snake_case**
6. **Separar responsabilitats entre vista, lògica de negoci i accés a dades**
7. **Cada funció ha de tenir docstrings explicant paràmetres, validacions i excepcions**

### Transcripciones de Peticiones y Respuestas Útiles

#### Petición 1: Generación del Esquema de Base de Datos
**Petición**: "Crear esquema de base de datos SQLite con las 4 tablas: Product, User, Order, OrderItem siguiendo las reglas del apartado 2"

**Respuesta de la IA**: La IA generó el esquema SQLite con las tablas exactamente como se especificaba, incluyendo:
- Tipos de datos correctos (INTEGER, VARCHAR, DECIMAL, DATETIME)
- Claves primarias autoincrementales
- Claves foráneas con relaciones correctas
- Manejo de la palabra reservada "Order" en SQLite

**Reflexión**: La IA siguió correctamente las especificaciones técnicas, pero requirió corrección manual para el manejo de palabras reservadas en SQLite.

#### Petición 2: Implementación de la Lógica de Negocio
**Petición**: "Implementar cart_service.py con add_to_cart, remove_from_cart, validate_stock siguiendo las reglas del apartado 3"

**Respuesta de la IA**: La IA generó el servicio con:
- Separación clara de responsabilidades
- Validaciones de cantidad positiva y límite de 5 unitats
- Validación de stock disponible
- Docstrings completos
- Manejo de errores apropiado

**Reflexión**: La IA aplicó correctamente los principios MVC y las validaciones requeridas. El código generado fue funcional y siguió las mejores prácticas.

#### Petición 3: Validaciones del Frontend
**Petición**: "Implementar validaciones HTML5 en formularios siguiendo las reglas del apartado 4"

**Respuesta de la IA**: La IA generó:
- Atributos HTML5 (required, minlength, maxlength, pattern)
- Campos numéricos con rangos adecuados (1-5)
- JavaScript para validaciones adicionales
- Mensajes de error claros sin revelar información interna

**Reflexión**: La IA comprendió bien los requisitos de validación y generó código que cumple con los estándares de seguridad.

### Cómo la IA Ha Ayudado

1. **Generación de Código Estructurado**: La IA ayudó a generar código bien estructurado que sigue los patrones MVC y las mejores prácticas de Flask.

2. **Implementación de Validaciones**: Generó validaciones tanto del lado del cliente como del servidor de manera consistente.

3. **Separación de Responsabilidades**: La IA respetó la arquitectura de tres capas y no mezcló lógica de negocio con presentación.

4. **Documentación**: Generó docstrings completos y comentarios apropiados.

### Límites de la IA Identificados

1. **Conocimiento Específico de SQLite**: La IA no consideró inicialmente que "Order" es una palabra reservada en SQLite, requiriendo corrección manual.

2. **Contexto de la Práctica**: A veces generó código más complejo del necesario para los requisitos específicos de la práctica.

3. **Validaciones Específicas**: Requirió iteraciones para ajustar las validaciones exactas según las reglas del profesor.

### Criterio Crítico Aplicado

1. **Revisión Manual**: Todo el código generado por la IA fue revisado manualmente para asegurar que cumple con los requisitos específicos.

2. **Pruebas de Funcionalidad**: Se verificó que cada función implementada funciona correctamente con los datos de prueba.

3. **Ajustes Específicos**: Se realizaron modificaciones cuando el código generado no se ajustaba exactamente a las especificaciones.

4. **Validación de Arquitectura**: Se confirmó que la separación de responsabilidades se mantiene en todo el código.

### Conclusión

El uso de la IA fue muy útil para acelerar el desarrollo y generar código bien estructurado. Sin embargo, fue esencial aplicar criterio crítico y realizar revisiones manuales para asegurar que el código cumple exactamente con los requisitos específicos de la práctica. La IA sirvió como una herramienta de asistencia, no como un reemplazo del pensamiento crítico y la comprensión de los requisitos.
