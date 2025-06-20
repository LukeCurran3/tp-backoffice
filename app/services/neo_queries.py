from ..database.neo4j_client import driver
from ..models import ProveedorCreate


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
        ordenes_json = [dict(record) for record in res]
        return ordenes_json

def get_productos_sin_orden():
    with driver.session() as sess:
        res = sess.run("""
                MATCH (p:Producto)
                WHERE NOT (p)<-[:REALIZA_PEDIDO]-(:Orden)
                RETURN p.codigo, p.nombre, p.marca, p.precio
        """)
        productos_json = [dict(record) for record in res]
        return productos_json