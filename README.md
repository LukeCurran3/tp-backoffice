# tp-backoffice
Base de Datos II: TP Backoffice



## Integrantes
- Ian Dalton
- Nicolas Tordomar
- Luke Curran

---

## Lenguajes Usados y Justificación

### MongoDB
Usamos Mongo para las querys de datos estructurados y para las preguntas que requieran ejecutar agregaciones de totales y conteos sin joins complejos, con capacidad de escalar horizontalmente para grandes volúmenes. También nos permitió contar órdenes y generar “vistas” ordenadas por fecha, destacándose por su alto rendimiento en operaciones CRUD para inserciones, lecturas, y actualizaciones rápidas.

### Neo4j

Lo elegimos para todas las consultas que se tratan de tareas que en una base de datos relacional requerirían múltiples joins y subconsultas. En Neo4j se reducen a patrones MATCH muy sencillos para recorrer niveles de relaciones mucho más eficientemente que Mongo o JOINS en SQL. Neo4j tiene el mejor rendimiento en ciertos casos pero también provee las mejores herramientas visuales del mercado.



---

## Pasos para Ejecutar el Proyecto

### Abrí en Codespace
1. En Github, abrí el proyecto directamente en Codespaces

2. Leventar los contenedores con
   ```js
   docker-compose up -d
   ```
   Esto va a leventar los servicios de MongoDB y Neo4j
   
4. Corré el archivo llamado "populate.ipynb" con "Run All. Este carga y importa todas las bases de datos y convierte las columnas a un formato que podemos usar para contestar las consultas. Si te pide cargar una fuente de kernel, descarga la version de python recomendada y elegí esa para ejucatar el codigo.

5. En la terminal de Codespaces, ejecutá
    ```js
    python -m uvicorn app.main:app --reload
     ```
parado en el directorio donde esta app (no adentro de el). Este va a leventar FastAPI, la api que elejimos por su velocidad y rendimiento. 

6. Ahora la app debe estar y podes chequear que todo esta cargado bien con
   ```js
   curl http://localhost:8000/proveedores/activos-habilitados
   ```

6. Probá los endpoints que corresponden a las consultas 1 a 15.



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

# Resultados
1. Obtener los datos de los proveedores activos y habilitados junto con sus teléfonos.

2. Obtener el/los teléfono/s y el código del/los proveedor/es que contengan la palabra
“Tecnología” en su razón social.

3. Mostrar cada teléfono junto con los datos del proveedor.

4. Obtener todos los proveedores que tengan registrada al menos una orden de pedido.

5. Identificar todos los proveedores que NO tengan registrada ninguna orden de pedido.
Es importante conocer su estado (¿el proveedor está activo?, ¿está habilitado?)

6. Devolver todos los proveedores, con la cantidad de ordenes que tienen registradas y el
monto total pedido, con y sin IVA incluido (si no tienen órdenes registradas considerar
cantidad y monto en 0).

7. Listar los datos de todas las órdenes que hayan sido pedidas al proveedor cuyo CUIT es
30-66060817-5.

8. Mostrar los productos que han sido pedido al menos 1 vez.

9. Listar los datos de todas las órdenes de pedido que contengan productos de la marca
“COTO”.

10. Se necesita crear una vista que devuelva los datos de las órdenes de pedido ordenadas
por fecha (incluyendo la razón social del proveedor y el total de la orden sin y con IVA).

11. Crear una vista que devuelva todos los productos que aún NO han sido pedidos.

12. Crear una vista que devuelva los datos de los proveedores activos que están
inhabilitados.

13. Implementar la funcionalidad que permita crear nuevos proveedores, eliminar y
modificar los ya existentes.

14. Implementar la funcionalidad que permita crear nuevos productos y modificar los ya
existentes.

15. Implementar la funcionalidad que permita registrar nuevas órdenes de pedido a los
proveedores si corresponde
