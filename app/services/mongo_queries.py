from ..database.mongo_client import db
from ..models import ProveedorCreate


def get_proveedores_activos_habilitados():
    return list(db.proveedores.find({
        "activo": 1,
        "habilitado": 1
    }, {"_id": 0, "activo": 1}))

def post_proveedor(proveedor:ProveedorCreate):
    db.proveedores.insert_one(proveedor.dict())



def get_telefonos_tecnologia():
    return list(db.proveedores.find({
         "razon_social": {"$regex": "Tecnología"}
     }, {"_id": 0, "id_proveedor": 1, "telefono": 1}))

def get_telefonos()():
    return list(db.proveedores.find({
    },
    {"_id": 0}))

def get_proveedores_cantidad_ordenes()():
    return list(db.ordenes.aggregate([
        {"$unwind": "$items"},
        {
            "$lookup": {
                "from": "productos",
                "localField": "items.id_producto",
                "foreignField": "id_producto",
                "as": "producto_info"
            }
        },
        {"$unwind": "$producto_info"},
        {
            "$addFields": {
                "subtotal_item": {
                    "$multiply": ["$producto_info.precio", "$items.cantidad"]
                }
            }
        },
        {
            "$group": {
                "_id": "$_id",
                "id_proveedor": {"$first": "$id_proveedor"},
                "total_sin_iva": {"$sum": "$subtotal_item"},
                "iva": {"$first": "$iva"}
            }
        },
        {
            "$addFields": {
                "total_con_iva": {
                    "$multiply": [
                        "$total_sin_iva",
                        {"$add": [1, {"$divide": ["$iva", 100]}]}
                    ]
                }
            }
        },
        {
            "$group": {
                "_id": "$id_proveedor",
                "cantidad_ordenes": {"$sum": 1},
                "monto_total_sin_iva": {"$sum": "$total_sin_iva"},
                "monto_total_con_iva": {"$sum": "$total_con_iva"}
            }
        },
        {
            "$project": {
                "id_proveedor": "$_id",
                "cantidad_ordenes": 1,
                "monto_total_sin_iva": 1,
                "monto_total_con_iva": 1,
                "_id": 0
            }
        }
    ]))
def crear_indices():
    db.proveedores.create_index({"CUIT_proveedor": 1})
    db.ordenes.create_index({"id_proveedor": 1})
def buscar_proveedor_por_cuit():
    return list(db.proveedores.find(
        {"CUIT_proveedor": 30660608175}, 
        {"_id": 0}))
def buscar_ordenes_por_proveedor():
    return list(db.ordenes.find(
        {"id_proveedor": 30660608175},
        {"_id": 0}))

def get_proveedores_por_fecha():
    return list(db.ordenes.aggregate([
        {
            "$addFields": {
                "fecha_iso": {
                    "$dateFromString": {
                        "dateString": "$fecha",
                        "format": "%d/%m/%Y"
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
        { "$unwind": "$proveedor" },
        { "$unwind": "$items" },
        {
            "$lookup": {
                "from": "productos",
                "localField": "items.id_producto",
                "foreignField": "id_producto",
                "as": "producto"
            }
        },
        { "$unwind": "$producto" },
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
                "id_pedido": { "$first": "$_id" },
                "fecha_pedido": { "$first": "$fecha" },
                "fecha_iso": { "$first": "$fecha_iso" },
                "total_sin_iva": { "$sum": "$subtotal_item" },
                "iva": { "$first": "$iva" },
                "proveedor": { "$first": "$proveedor" },
                "items": { "$push": "$item" }
            }
        },
        {
            "$addFields": {
                "total_con_iva": {
                    "$round": [
                        {
                            "$multiply": [
                                "$total_sin_iva",
                                { "$add": [1, { "$divide": ["$iva", 100] }] }
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
                "proveedor": 1,
                "total_sin_iva": 1,
                "total_con_iva": 1,
                "fecha_pedido": 1,
                "id_pedido": 1,
                "items": 1
            }
        },
        {
            "$sort": { "fecha_iso": 1 }
        }
    ]))
def get_proveedores_activos_inhabilitados():
    return list(db.proveedores.find({
        "activo": 1,
        "habilitado": 0
    }, {"_id": 0, "activo": 1}))