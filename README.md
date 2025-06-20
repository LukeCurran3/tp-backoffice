# tp-backoffice
Base de Datos II: TP Backoffice por Ian Dalton, Nicolas Tordomar, y Luke Curran

---

## Lenguajes Usados

### MongoDB
 Usamos Mongo para las querys de datos estructurados y para las preguantas que requisen ejecutar agregaciones de totales y conteos sin joins complejos, con capacidad de escalar horizontalmente para grandes volúmenes. También nos permitió contar órdenes y generar “vistas” ordenadas por fecha

### Neo4j

Lo elegimos para todas las consultas se tratan de tareas que en una base de datos relacional requerirían múltiples joins y subconsultas. En Neo4j se reducen a patrones MATCH muy sencillos y eficientes y nos permitio hacer operaciones CRUD sobre nodos y relaciones 

# Consultas
## MONGO

1. Obtener los datos de los proveedores activos y habilitados junto con sus teléfonos. -> MONGO
```js
db.proveedores.find({activos:1,habilitados:1})
```

2. Obtener el/los teléfono/s y el código del/los proveedor/es que contengan la palabra “Tecnología” en su razón social. -> MONGO
```js
db.proveedores.find({razon_social:{$regex:/Tecnología/}})
```

3. Mostrar cada teléfono junto con los datos del proveedor. -> MONGO, si pide el orden en particular, neo
```js
db.proveedores.find()
```

6. Devolver todos los proveedores, con la cantidad de ordenes que tienen registradas y el
monto total pedido, con y sin IVA incluido (si no tienen órdenes registradas considerar
cantidad y monto en 0). -> MONGO (JOIN ordenes y productos con GROUP BY proveedor con sus calculos )
```js
db.ordenes.aggregate([
  // Desenrollar items para poder juntar con productos
  { $unwind: "$items" },

  // Hacer lookup con productos para obtener precio y posible IVA
  {
    $lookup: {
      from: "productos",
      localField: "items.id_producto",
      foreignField: "id_producto",
      as: "producto_info"
    }
  },
  { $unwind: "$producto_info" },

  // Calcular subtotal por item = precio * cantidad
  {
    $addFields: {
      subtotal_item: { $multiply: ["$producto_info.precio", "$items.cantidad"] },
    }
  },

  // Agrupar por orden para sumar subtotales y calcular total
  {
    $group: {
      _id: "$_id", // id de orden
      id_proveedor: { $first: "$id_proveedor" },
      total_sin_iva: { $sum: "$subtotal_item" },
      iva: { $first: "$iva" }
    }
  },

  // Calcular total con IVA
  {
    $addFields: {
      total_con_iva: {
        $multiply: [
          "$total_sin_iva",
          { $add: [1, { $divide: ["$iva", 100] }] }
        ]
      }
    }
  },

  // Agrupar por proveedor para sumar todos los totales de sus órdenes
  {
    $group: {
      _id: "$id_proveedor",
      cantidad_ordenes: { $sum: 1 },
      monto_total_sin_iva: { $sum: "$total_sin_iva" },
      monto_total_con_iva: { $sum: "$total_con_iva" }
    }
  },

  {
    $project: {
      id_proveedor: "$_id",
      cantidad_ordenes: 1,
      monto_total_sin_iva: 1,
      monto_total_con_iva: 1,
      _id: 0
    }
  }
])

```

7. Listar los datos de todas las órdenes que hayan sido pedidas al proveedor cuyo CUIT es
30-66060817-5. -> MONGO join
```js
db.proveedores.createIndex({ CUIT_proveedor: 1 });
db.ordenes.createIndex({ id_proveedor: 1 });
db.proveedores.find({ CUIT_proveedor: NumberLong("30660608175") })
db.ordenes.find({ id_proveedor:  }) (arriba)
```

10. Se necesita crear una vista que devuelva los datos de las órdenes de pedido ordenadas
por fecha (incluyendo la razón social del proveedor y el total de la orden sin y con IVA). -> MONGO
```js
```

12. Crear una vista que devuelva los datos de los proveedores activos que están
inhabilitados. -> MONGO
```js
db.proveedores.find({activos:1,habilitados:0})
```

## NEO4J

4. Obtener todos los proveedores que tengan registrada al menos una orden de pedido. -> NEO
```cypher
MATCH (p:Proveedor)<-[:LE_COMPRA_A]-(o:Orden)
RETURN DISTINCT p
```
5. Identificar todos los proveedores que NO tengan registrada ninguna orden de pedido.
Es importante conocer su estado (¿el proveedor está activo?, ¿está habilitado?) -> NEO
```cypher
MATCH (p:Proveedor)
WHERE NOT (p)<-[:LE_COMPRA_A]-(:Orden)
RETURN p.id_proveedor, p.razon_social, p.activo, p.habilitado
```

8. Mostrar los productos que han sido pedido al menos 1 vez. -> NEO
```cypher
MATCH (p:Producto)<-[:REALIZA_PEDIDO]-(:Orden)
RETURN DISTINCT p.codigo, p.nombre, p.marca, p.precio
```
9. Listar los datos de todas las órdenes de pedido que contengan productos de la marca
“COTO”. -> NEO
```cypher
MATCH (o:Orden)-[:REALIZA_PEDIDO]->(p:Producto)
WHERE p.marca = "COTO"
RETURN DISTINCT o.id_pedido, o.fecha, o.iva, o.id_proveedor
ORDER BY o.fecha DESC

```
11. Crear una vista que devuelva todos los productos que aún NO han sido pedidos. -> NEO
```cypher
MATCH (p:Producto)
WHERE NOT (p)<-[:REALIZA_PEDIDO]-(:Orden)
RETURN p.codigo, p.nombre, p.marca, p.precio
```

### RELACIONES
- Orden tiene proveedor
- Orden tiene (3 de este) producto

## AMBOS

ACID!!!

13. Implementar la funcionalidad que permita crear nuevos proveedores, eliminar y
modificar los ya existentes. -> AMBOS ;.;
```cypher
CREATE (p:Proveedor {
  id_proveedor: $id_proveedor,
  cuit: $cuit,
  razon_social: $razon_social,
  activo: $activo,
  habilitado: $habilitado
})
RETURN p

MATCH (p:Proveedor {id_proveedor: $id_proveedor})
DETACH DELETE p

MATCH (p:Proveedor {id_proveedor: $id_proveedor})
SET p.cuit = $cuit,
    p.razon_social = $razon_social,
    p.activo = $activo,
    p.habilitado = $habilitado
RETURN p

```

14. Implementar la funcionalidad que permita crear nuevos productos y modificar los ya
existentes. -> AMBOS
```cypher
CREATE (p:Producto {
  codigo: $codigo,
  nombre: $nombre,
  marca: $marca,
  precio: $precio
})
RETURN p

MATCH (p:Producto {codigo: $codigo})
SET p.nombre = $nombre,
    p.marca = $marca,
    p.precio = $precio
RETURN p

```
15. Implementar la funcionalidad que permita registrar nuevas órdenes de pedido a los
proveedores si corresponde. -> AMBOS
```cypher
MATCH (p:Proveedor {id_proveedor: $id_proveedor})
CREATE (o:Orden {
  id_pedido: $id_pedido,
  id_proveedor: $id_proveedor,
  iva: $iva,
  fecha: date($fecha)
})
CREATE (o)-[:LE_COMPRA_A]->(p)
RETURN o, p

```

# Set-up

docker-compose up -d

Correr todos los bloques de test.ipynb
