from datetime import date

from ..database.neo4j_client import driver
from ..models import ProveedorCreate, ProveedorUpdate, ProductoCreate, ProductoUpdate, OrdenCreate


def get_proveedores_con_orden():
    with driver.session() as sess:
        res = sess.run("""
            MATCH (p:Proveedor)<-[:LE_COMPRA_A]-(o:Orden)
            RETURN DISTINCT p
        """)
        # Convert Neo4j records to a list of dicts
        proveedores = [record["p"] for record in res]
        # If you want plain dicts (not Node objects), use .items() or ._properties
        proveedores_json = [dict(node._properties) for node in proveedores]
        return proveedores_json

def get_proveedores_sin_orden():
    with driver.session() as sess:
        res = sess.run("""
            MATCH (p:Proveedor)
            WHERE NOT (p)<-[:LE_COMPRA_A]-(:Orden)
            RETURN p.id_proveedor AS id_proveedor, p.razon_social AS razon_social, p.activo AS activo, p.habilitado AS habilitado
        """)
        proveedores_json = [dict(record) for record in res]
        return proveedores_json

def get_productos_con_orden():
    with driver.session() as sess:
        res = sess.run("""
            MATCH (p:Producto)<-[:REALIZA_PEDIDO]-(:Orden)
            RETURN DISTINCT p.codigo, p.nombre, p.marca, p.precio
        """)
        productos_json = [dict(record) for record in res]
        return productos_json

def get_ordenes_por_marca(brand):
    with driver.session() as sess:
        res = sess.run(
            """
                MATCH (o:Orden)-[:REALIZA_PEDIDO]->(p:Producto)
                WHERE p.marca = $brand
                RETURN DISTINCT o.id_pedido, o.fecha, o.iva, o.id_proveedor
                ORDER BY o.fecha DESC
            """,
            brand=brand
        )
        ordenes_json = [
            {k.split('.')[-1]: v.strftime("%d/%m/%Y") if k.endswith("fecha") and hasattr(v, "year") else v for k, v in
             r.items()}
            for r in res
        ]
        return ordenes_json


def create_proveedor(proveedor: ProveedorCreate):
    with driver.session() as sess:
        res = sess.run(
            """
            CREATE (p:Proveedor {
              id_proveedor: $id_proveedor,
              cuit: $CUIT_proveedor,
              razon_social: $razon_social,
              tipo_sociedad: $tipo_sociedad,
              direccion: $direccion,
              activo: $activo,
              habilitado: $habilitado
            })
            RETURN p
            """,
            **proveedor.model_dump()
        )
        record = res.single()
        return dict(record["p"]._properties) if record else None

def delete_proveedor(id_proveedor: int):
    with driver.session() as sess:
        res = sess.run(
            """
            MATCH (p:Proveedor {id_proveedor: $id_proveedor})
            DETACH DELETE p
            RETURN count(p) AS eliminados
            """,
            id_proveedor=id_proveedor
        )
        record = res.single()
        return record["eliminados"] if record else 0

def put_proveedor(id_proveedor: int, proveedor: ProveedorUpdate):
    update_fields = {k: v for k, v in proveedor.dict().items() if v is not None}
    set_clause = ", ".join([f"p.{k} = ${k}" for k in update_fields.keys()])
    if not set_clause:
        return None
    cypher = f"""
        MATCH (p:Proveedor {{id_proveedor: $id_proveedor}})
        SET {set_clause}
        RETURN p
    """
    params = {"id_proveedor": id_proveedor, **update_fields}
    with driver.session() as sess:
        res = sess.run(cypher, **params)
        record = res.single()
        return dict(record["p"]._properties) if record else None

def create_producto(producto: ProductoCreate):
    with driver.session() as sess:
        res = sess.run(
            """
            CREATE (p:Producto {
              codigo: $id_producto,
              nombre: $descripcion,
              marca: $marca,
              categoria: $categoria,
              precio: $precio,
              stock_actual: $stock_actual,
              stock_futuro: $stock_futuro
            })
            RETURN p
            """,
            **producto.model_dump()
        )
        record = res.single()
        return dict(record["p"]._properties) if record else None

def put_producto(id_producto: int, producto: ProductoUpdate):
    update_fields = {k: v for k, v in producto.model_dump().items() if v is not None}
    set_clause = ", ".join([f"p.{k} = ${k}" for k in update_fields.keys()])
    if not set_clause:
        return None
    cypher = f"""
        MATCH (p:Producto {{codigo: $id_producto}})
        SET {set_clause}
        RETURN p
    """
    params = {"id_producto": id_producto, **update_fields}
    with driver.session() as sess:
        res = sess.run(cypher, **params)
        record = res.single()
        return dict(record["p"]._properties) if record else None

def create_orden(orden: OrdenCreate):
    with driver.session() as sess:
        res = sess.run(
            """
            MATCH (p:Proveedor {id_proveedor: $id_proveedor})
            CREATE (o:Orden {
              id_pedido: $id_pedido,
              id_proveedor: $id_proveedor,
              iva: $iva,
              fecha: date($fecha),
              total_sin_iva: $total_sin_iva
            })
            CREATE (o)-[:LE_COMPRA_A]->(p)
            RETURN o, p
            """,
            id_pedido=orden.id_pedido,
            id_proveedor=orden.id_proveedor,
            iva=orden.iva,
            fecha=orden.fecha.isoformat(),
            total_sin_iva=orden.total_sin_iva
        )
        record = res.single()
        if record:
            return {
                "orden": dict(record["o"]._properties),
                "proveedor": dict(record["p"]._properties)
            }
        return None