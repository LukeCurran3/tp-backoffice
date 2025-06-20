import os
import pandas as pd
from pymongo import MongoClient
from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv()

mongo = MongoClient(os.getenv("MONGO_URI", "mongodb://mongo:27017"))
mdb = mongo["backoffice"]

uri = os.getenv("NEO4J_URI", "bolt://neo4j:7687")
neo = GraphDatabase.driver(uri, auth=("neo4j", os.getenv("NEO4J_PASSWORD", "secret")))

def import_mongo():
    df_prov = pd.read_csv("data/proveedor.csv",encoding="utf-8")
    df_prov["CUIT_proveedor"] = df_prov["CUIT_proveedor"].astype(str)
    df_tel  = pd.read_csv("data/telefono.csv",encoding="utf-8")
    df_prod = pd.read_csv("data/producto.csv",encoding="utf-8")
    df_op   = pd.read_csv("data/op.csv",encoding="utf-8")
    df_det  = pd.read_csv("data/detalle_op.csv",encoding="utf-8")

    mdb.proveedores.delete_many({})
    mdb.proveedores.insert_many(df_prov.to_dict("records"))

    mdb.telefonos.delete_many({})
    mdb.telefonos.insert_many(df_tel.to_dict("records"))

    mdb.productos.delete_many({})
    mdb.productos.insert_many(df_prod.to_dict("records"))

    mdb.ordenes.delete_many({})
    mdb.ordenes.insert_many(df_op.to_dict("records"))

    mdb.detalles.delete_many({})
    mdb.detalles.insert_many(df_det.to_dict("records"))
def import_neo4j():
    with neo.session() as sess:
        sess.run("MATCH (n) DETACH DELETE n")
        # proveedores
        df = pd.read_csv("data/proveedor.csv",encoding="utf-8")
        for _,r in df.iterrows():
            sess.run("""
                CREATE (p:Proveedor {
                  cuit: $cuit,
                  razon_social: $razon_social,
                  activo: $activo,
                  habilitado: $habilitado
                })
            """, **r.to_dict())

        # telefonos
        df = pd.read_csv("data/telefono.csv",encoding="utf-8")
        for _,r in df.iterrows():
            sess.run("""
                MATCH (p:Proveedor {cuit: $cuit})
                CREATE (p)-[:TIENE_TELEFONO {numero:$telefono}]->(:Telefono)
            """, cuit=r.cuit, telefono=r.telefono)

        # productos
        df = pd.read_csv("data/producto.csv",encoding="utf-8")
        for _,r in df.iterrows():
            sess.run("""
                CREATE (:Producto {
                  codigo: $codigo,
                  nombre: $nombre,
                  marca: $marca,
                  precio: $precio,
                  iva: $iva
                })
            """, **r.to_dict())

        # ordenes y detalles
        df_op = pd.read_csv("data/op.csv",encoding="utf-8")
        df_det= pd.read_csv("data/detalle_op.csv",encoding="utf-8")
        for _,o in df_op.iterrows():
            sess.run("""
                CREATE (o:Orden {
                  id_op: $id_op,
                  fecha: date($fecha),
                  cuit: $cuit
                })
            """, id_op=o.id_op, fecha=o.fecha, cuit=o.cuit)
        for _,d in df_det.iterrows():
            sess.run("""
                MATCH (o:Orden {id_op:$id_op}), (pr:Producto {codigo:$codigo})
                CREATE (o)-[:CONTiene {cantidad:$cantidad}]->(pr)
            """, **d.to_dict())
if __name__ == "__main__":
    import_mongo()
    import_neo4j()
    print("Data imported into MongoDB & Neo4j.")