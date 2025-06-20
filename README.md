# tp-backoffice
Base de Datos II: TP Backoffice por Luke Curran,

---

## Lenguajes Usados

### MongoDB
 

### Neo4j




# Consultas
## MONGO

1. Obtener los datos de los proveedores activos y habilitados junto con sus teléfonos. -> MONGO

2. Obtener el/los teléfono/s y el código del/los proveedor/es que contengan la palabra “Tecnología” en su razón social. -> MONGO

3. Mostrar cada teléfono junto con los datos del proveedor. -> MONGO, si pide el orden en particular, neo

6. Devolver todos los proveedores, con la cantidad de ordenes que tienen registradas y el
monto total pedido, con y sin IVA incluido (si no tienen órdenes registradas considerar
cantidad y monto en 0). -> MONGO (JOIN ordenes y productos con GROUP BY proveedor con sus calculos )

7. Listar los datos de todas las órdenes que hayan sido pedidas al proveedor cuyo CUIT es
30-66060817-5. -> MONGO join

10. Se necesita crear una vista que devuelva los datos de las órdenes de pedido ordenadas
por fecha (incluyendo la razón social del proveedor y el total de la orden sin y con IVA). -> MONGO

12. Crear una vista que devuelva los datos de los proveedores activos que están
inhabilitados. -> MONGO

## NEO4J

4. Obtener todos los proveedores que tengan registrada al menos una orden de pedido. -> NEO

5. Identificar todos los proveedores que NO tengan registrada ninguna orden de pedido.
Es importante conocer su estado (¿el proveedor está activo?, ¿está habilitado?) -> NEO

8. Mostrar los productos que han sido pedido al menos 1 vez. -> NEO

9. Listar los datos de todas las órdenes de pedido que contengan productos de la marca
“COTO”. -> NEO

11. Crear una vista que devuelva todos los productos que aún NO han sido pedidos. -> NEO

### RELACIONES
- Orden tiene proveedor
- Orden tiene (3 de este) producto

## AMBOS

ACID!!!

13. Implementar la funcionalidad que permita crear nuevos proveedores, eliminar y
modificar los ya existentes. -> AMBOS ;.;

14. Implementar la funcionalidad que permita crear nuevos productos y modificar los ya
existentes. -> AMBOS

15. Implementar la funcionalidad que permita registrar nuevas órdenes de pedido a los
proveedores si corresponde. -> AMBOS


# Set-up

docker-compose up -d

Correr todos los bloques de test.ipynb
