# %%
from pymongo import MongoClient
import os
import pandas as pd
from neo4j import GraphDatabase

# %%
mongo = MongoClient(os.getenv("MONGO_URI", "mongodb://localhost:27017"))

# %%
mdb = mongo["backoffice"]

# %%
df_prov = pd.read_csv("data/proveedor.csv",encoding="Windows 1252",sep=";")
df_tel  = pd.read_csv("data/telefono.csv",encoding="Windows 1252",sep=";")
df_prod = pd.read_csv("data/producto.csv",encoding="Windows 1252",sep=";")
df_op   = pd.read_csv("data/op.csv",encoding="Windows 1252",sep=";")
df_det  = pd.read_csv("data/detalle_op.csv",encoding="Windows 1252",sep=";")

# %%
df_prov["CUIT_proveedor"] = df_prov["CUIT_proveedor"].astype(str)


# %%
def is_not_all_nan(phone):
    import math
    return not all(
        (isinstance(phone.get(f), float) and math.isnan(phone.get(f))) or phone.get(f) is None
        for f in ['codigo_area', 'nro_telefono', 'tipo']
    )

res = pd.merge(df_prov,df_tel, on="id_proveedor",how="left")
proveedores = res.groupby("id_proveedor").apply(lambda g: {
    'id_proveedor': int(g['id_proveedor'].iloc[0]),
    "CUIT_proveedor": g["CUIT_proveedor"].iloc[0],
    "razon_social":g["razon_social"].iloc[0],
    "tipo_sociedad":g["tipo_sociedad"].iloc[0] ,
    "direccion":g["direccion"].iloc[0]  , 
    "activo" :int(g["activo"].iloc[0]),
    "habilitado":int(g["habilitado"].iloc[0]),
    "telefonos": [t for t in g[['codigo_area', 'nro_telefono', 'tipo']].to_dict(orient='records') if is_not_all_nan(t)]
})

proveedores = proveedores.reset_index(name='document')["document"].to_list()
proveedores

# %%
res = pd.merge(df_op,df_det,on="id_pedido",how="outer")
ordenes = res.groupby('id_pedido').apply(lambda g: {
    "id_pedido": int(g['id_pedido'].iloc[0]),
    'id_proveedor': int(g['id_proveedor'].iloc[0]),
    'fecha': g['fecha'].iloc[0],
    'iva': float(g['iva'].iloc[0]),
    'items': g[['id_producto', 'nro_item', 'cantidad']].to_dict(orient='records')
}).reset_index(name='document')["document"].to_list()

# %%
import math

def replace_nans(obj):
    if isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            return None
        return obj
    elif isinstance(obj, dict):
        return {k: replace_nans(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [replace_nans(x) for x in obj]
    else:
        return obj

def import_mongo():
    mdb.proveedores.create_index([("id_proveedor", 1)], unique=True)
    mdb.proveedores.create_index([("CUIT_proveedor", 1)], unique=True)
    mdb.proveedores.delete_many({})
    mdb.proveedores.insert_many(replace_nans(proveedores))

    mdb.productos.create_index([("id_producto", 1)], unique=True)
    mdb.productos.delete_many({})
    mdb.productos.insert_many(replace_nans(df_prod.to_dict("records")))
    
    mdb.ordenes.create_index([("id_pedido", 1)], unique=True)
    mdb.ordenes.delete_many({})
    mdb.ordenes.insert_many(replace_nans(ordenes))


import_mongo()

# %%

mdb.command({
  "create": "view_productos_no_pedidos",
  "viewOn":"productos",
  "pipeline":[

    {
      "$lookup": {
        "from": "ordenes",
        "let": { "producto_id": "$id_producto" },
        "pipeline": [
          { "$unwind": "$items" },
          {
            "$match": {
              "$expr": { "$eq": ["$items.id_producto", "$$producto_id"] }
            }
          },
          { "$limit": 1 } 
        ],
        "as": "ordenes_que_lo_piden"
      }
    },

    {
      "$match": {
        "ordenes_que_lo_piden": { "$eq": [] }
      }
    },
    {
      "$project": {
        "_id": 0,
        "id_producto": 1,
        "descripcion": 1,
        "marca": 1,
        "precio": 1
      }
    }
  ]}
)


# %%
mdb.command({
  "create": "view_proveedores_por_fecha",
  "viewOn":"ordenes",
  "pipeline":[
        {
            "$addFields": {
                "fecha_iso": {
                    "$dateFromString": {
                        "dateString": "$fecha",
                        "format": "%-d/%-m/%Y"
                    }
                }
            }
        },
        {
            "$lookup": {
                "from": "proveedores",
                "localField": "id_proveedor",
                "foreignField": "id_proveedor",
                "as": "proveedor"
            }
        },
        {"$unwind": "$proveedor"},
        # Convert proveedor._id to string
        {
            "$addFields": {
                "proveedor._id": {"$toString": "$proveedor._id"}
            }
        },
        {"$unwind": "$items"},
        {
            "$lookup": {
                "from": "productos",
                "localField": "items.id_producto",
                "foreignField": "id_producto",
                "as": "producto"
            }
        },
        {"$unwind": "$producto"},
        # Convert producto._id to string
        {
            "$addFields": {
                "producto._id": {"$toString": "$producto._id"}
            }
        },
        {
            "$addFields": {
                "item": {
                    "cantidad": "$items.cantidad",
                    "producto": "$producto"
                }
            }
        },
        {
            "$addFields": {
                "subtotal_item": {
                    "$multiply": ["$producto.precio", "$items.cantidad"]
                }
            }
        },
        {
            "$group": {
                "_id": "$_id",
                "id_pedido": {"$first": {"$toString": "$id_pedido"}},
                "fecha_pedido": {"$first": "$fecha"},
                "fecha_iso": {"$first": "$fecha_iso"},
                "total_sin_iva": {"$sum": "$subtotal_item"},
                "iva": {"$first": "$iva"},
                "proveedor": {"$first": "$proveedor"},
                "items": {"$push": "$item"}
            }
        },
        {
            "$addFields": {
                "total_con_iva": {
                    "$round": [
                        {
                            "$multiply": [
                                "$total_sin_iva",
                                {"$add": [1, {"$divide": ["$iva", 100]}]}
                            ]
                        },
                        2
                    ]
                }
            }
        },
        {
            "$project": {
                "_id": 0,
                "proveedor.razon_social": 1,
                "proveedor.id_proveedor": 1,
                "total_sin_iva": 1,
                "total_con_iva": 1,
                "fecha_pedido": 1,
                "id_pedido": 1
            }
        },
        {
            "$sort": {"fecha_iso": 1}
        }
    ]})

# %%
mdb.command({
  "create": "view_proveedores_activos_inhabilitados",
  "viewOn":"proveedores",
  "pipeline":[
     {
        "$match": {
          "activo": 1,
          "habilitado": 0
        }
      },
      {
        "$project": {
          "_id": 0,
          "telefonos": 0
        }
      }
    ]
    }
    )

# %%
uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
neo = GraphDatabase.driver(uri, auth=("neo4j", os.getenv("NEO4J_PASSWORD", "epicpassword123")))

# %%
def import_neo4j():
    with neo.session() as sess:
        sess.run("MATCH (n) DETACH DELETE n")
        # proveedores
        df = pd.read_csv("data/proveedor.csv",encoding="Windows 1252",sep=";")
        df["CUIT_proveedor"] = df["CUIT_proveedor"].astype(str)
        for _,r in df.iterrows():
            sess.run("""
                CREATE (p:Proveedor {
                  id_proveedor:$id_proveedor,
                  cuit: $CUIT_proveedor,
                  razon_social: $razon_social,
                  activo: $activo,
                  habilitado: $habilitado
                })
            """, **r.to_dict())

        # RELACIÓN TELEFONO
        df = pd.read_csv("data/telefono.csv",encoding="Windows 1252",sep=";")
        for _,r in df.iterrows():
            sess.run("""
                MATCH (p:Proveedor {id_proveedor: $id_proveedor})
                CREATE (p)-[:TIENE_TELEFONO {numero:$telefono}]->(:Telefono)
            """, id_proveedor=r.id_proveedor, telefono=r.nro_telefono)

        # productos
        df = pd.read_csv("data/producto.csv",encoding="Windows 1252",sep=";")
        for _,r in df.iterrows():
            sess.run("""
                CREATE (:Producto {
                  codigo: $id_producto,
                  nombre: $descripcion,
                  marca: $marca,
                  precio: $precio
                })
            """, **r.to_dict())

        # ordenes y detalles
        df_op = pd.read_csv("data/op.csv",encoding="Windows 1252",sep=";")
        df_op["fecha"] = pd.to_datetime(df_op["fecha"], dayfirst=True).dt.strftime("%Y-%m-%d")
        df_det= pd.read_csv("data/detalle_op.csv",encoding="Windows 1252",sep=";")
        
        for _,o in df_op.iterrows():
            sess.run("""
                CREATE (o:Orden {
                     id_pedido:$id_pedido,
                     id_proveedor:$id_proveedor,
                     iva:$iva,
                     total_sin_iva: $total_sin_iva,
                  fecha: date($fecha)
                })
                WITH o
                MATCH (p:Proveedor {id_proveedor:$id_proveedor})
                CREATE (o) - [:LE_COMPRA_A] -> (p)
            """, **o.to_dict())

        #Orden tiene (3 de este) producto
        
        for _,detalle in df_det.iterrows():
            sess.run("""
                MATCH (o:Orden {id_pedido:$id_pedido})
                MATCH (p:Producto {codigo: $id_producto})
                CREATE (o)-[:REALIZA_PEDIDO {cantidad: $cantidad}] -> (p)
            """, **detalle.to_dict())


        for _,d in df_det.iterrows():
            sess.run("""
                MATCH (o:Orden {id_pedido:$id_pedido,id_producto:$id_producto}), (pr:Producto {codigo:$id_producto})
                CREATE (o)-[:CONTiene {cantidad:$cantidad}]->(pr)
            """, **d.to_dict())
import_neo4j()

# %%



