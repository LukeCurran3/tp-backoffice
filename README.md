# tp-backoffice
Base de Datos II: TP Backoffice



## Integrantes
- Ian Dalton
- Nicolas Tordomar
- Luke Curran

---

## Lenguajes Usados y Justificación

Se eligieron MongoDB y Neo4j como bases de datos NoSQL para implementar la capa de persistencia del sistema.

MongoDB fue utilizada para las consultas sobre datos estructurados y aquellas que requieren agregaciones simples (totales, conteos), sin necesidad de joins complejos. Su capacidad de escalar horizontalmente y su rendimiento en operaciones CRUD la convierten en una opción eficiente para manejar grandes volúmenes de información. Además, permite ordenar órdenes por fecha y generar vistas simuladas de manera flexible.

Neo4j, por su parte, fue seleccionada para resolver consultas que implican múltiples relaciones o saltos entre entidades, que en Mongo por ejemplo implicarían múltiples joins o subconsultas anidadas. En Neo4j, estas operaciones se expresan de forma sencilla mediante patrones MATCH, optimizando el rendimiento. Es ideal para modelar y consultar relaciones como proveedores ↔ órdenes ↔ productos, facilitando la navegación del grafo con gran eficiencia.



---

## Pasos para Ejecutar el Proyecto

### Codespace
1. En Github, abrí el proyecto directamente en Codespaces con clic en "Code" y seleccionando "Open with Codespaces".

2. Leventar los contenedores con
   ```js
   docker-compose up -d
   ```
Esto va a leventar los contenedores de MongoDB y Neo4j y cargar la app desarollada con FastAPI automáticamente.
   
3. Te va a avisar que puerto 8000 esta corriendo, pero los datos todavia tienen que cargar. Se generará un enlace al servidor, que puede demorar unos segundos en estar disponible. Cuando te cuente que no hay attributos, sumá "/docs" al final de la URL y recargá la pantalla.


4. Ahí tendrás acceso a todas las 15 consultas que corresponden a las 15 consultas en el TP para probar y testear.
   



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
db.ordenes.aggregate([
  // Convertimos la fecha a formato ordenable
  {
    $addFields: {
      fecha_iso: {
        $dateFromString: {
          dateString: "$fecha",
          format: "%d/%m/%Y"
        }
      }
    }
  },
  // Traemos datos del proveedor
  {
    $lookup: {
      from: "proveedores",
      localField: "id_proveedor",
      foreignField: "id_proveedor",
      as: "proveedor"
    }
  },
  { $unwind: "$proveedor" },
  // Descomponemos items para buscar productos
  { $unwind: "$items" },
  // Traemos datos del producto por cada item
  {
    $lookup: {
      from: "productos",
      localField: "items.id_producto",
      foreignField: "id_producto",
      as: "producto"
    }
  },
  { $unwind: "$producto" },
  // Reestructuramos el item con el producto embebido
  {
    $addFields: {
      item: {
        cantidad: "$items.cantidad",
        producto: "$producto"
      }
    }
  },
  {
    $addFields: {
      subtotal_item: { $multiply: ["$producto.precio", "$items.cantidad"] },
    }
  },
  // Agrupamos por orden nuevamente, reconstruyendo items
  {
    $group: {
      _id: "$_id",
      id_pedido: { $first: "$_id" },
      fecha_pedido: { $first: "$fecha" },
      fecha_iso: { $first: "$fecha_iso" },
      total_sin_iva: { $sum: "$subtotal_item" },
      iva: { $first: "$iva" },
      proveedor: { $first: "$proveedor" },
      items: { $push: "$item" }
    }
  },
  // Calculamos total con IVA
  {
    $addFields: {
      total_con_iva: {
        $round: [
          { $multiply: ["$total_sin_iva", { $add: [1, { $divide: ["$iva", 100] }] }] },
          2
        ]
      }
    }
  },
  // Formato final del documento
  {
    $project: {
      _id: 0,
      proveedor: "$proveedor",
      total_sin_iva: 1,
      total_con_iva: 1,
      fecha_pedido: 1,
      id_pedido: 1,
      items: 1
    }
  },
  // Ordenamos por fecha
  {
    $sort: { fecha_iso: 1 }
  }
])


```
11. Crear una vista que devuelva todos los productos que aún NO han sido pedidos. -> NEO

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

### RELACIONES
- Orden tiene proveedor
- Orden tiene (3 de este) producto

## AMBOS

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

```js

db.productos.insertOne({
  id_producto: 101,
  descripcion: "Galletitas de avena",
  marca: "Bagley",
  categoria: "alimentos",
  precio: 350.00,
  stock_actual: 100,
  stock_futuro: 0
})


db.productos.updateOne(
  { id_producto: 101 }, // Filtro
  {
    $set: {
      precio: 399.99,
      stock_actual: 120
    }
  }
)
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


