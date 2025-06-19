# tp-backoffice
Base de Datos II: TP Backoffice por Luke Curran,

---

## Lenguajes Usados

### MongoDB
Usamos Mongo para las querys de datos esctructurados incluyendo proveedores, productos, órdenes y teléfonos. Tambien el TP pide que hagamos VIEWS y MongoDB permite agregaciones para satisfacer ese requisito.

### Redis
Elejimos Redis para guardar y rastrear las actualizationes y information del stock. Redis guarda todos los datos en memoria (RAM) asi que no hace falta buscar por toda la base de datos para encontrar una unidad especifica. Este va a ser mas eficiente para nuestras necisidades.


