from ..database.mongo_client import db
from ..models import ProveedorCreate, ProveedorUpdate, OrdenCreate, ProductoCreate, ProductoUpdate
import math


def clean_nans(obj):
    if isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            return None
        return obj
    elif isinstance(obj, dict):
        return {k: clean_nans(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [clean_nans(x) for x in obj]
    else:
        return obj


def get_proveedores_activos_habilitados():
    result = list(db.proveedores.find({
        "activo": 1,
        "habilitado": 1
    }, {"_id": 0}))
    return clean_nans(result)


def post_proveedor(proveedor: ProveedorCreate):
    result = db.proveedores.insert_one(proveedor.model_dump())
    return 1 if result.acknowledged else 0


def create_orden(orden: OrdenCreate):
    result = db.orden.insert_one(orden.model_dump())
    return 1 if result.acknowledged else 0


def create_producto(producto: ProductoCreate):
    result = db.producto.insert_one(producto.model_dump())
    return 1 if result.acknowledged else 0


def put_producto(id_producto: int, producto: ProductoUpdate):
    result = db.producto.update_one(
        {"id_producto": id_producto},  # criterio de búsqueda
        {"$set": producto.model_dump(exclude_unset=True)}
    )
    return result.modified_count


def put_proveedor(id_proveedor: int, proveedor: ProveedorUpdate):
    result = db.proveedores.update_one(
        {"id_proveedor": id_proveedor},  # criterio de búsqueda
        {"$set": proveedor.model_dump(exclude_unset=True)}
    )
    return result.modified_count


def delete_proveedor(id_proveedor: int):
    result = db.proveedores.delete_one({"id_proveedor": id_proveedor})
    return result.deleted_count


def get_telefonos_tecnologia():
    return list(db.proveedores.find({
        "razon_social": {"$regex": "Tecnología"}
    }, {"_id": 0, "id_proveedor": 1, "razon_social": 1, "telefonos": 1}))


def get_telefonos():
    return list(db.proveedores.find({
    },
        {"_id": 0, "id_proveedor": 1, "razon_social": 1, "telefonos": 1}))


def get_proveedores_cantidad_ordenes():
    return list(db.proveedores.aggregate([
        {
            "$lookup": {
                "from": "ordenes",
                "localField": "id_proveedor",
                "foreignField": "id_proveedor",
                "as": "ordenes"
            }
        },
        {
            "$unwind": {
                "path": "$ordenes",
                "preserveNullAndEmptyArrays": True
            }
        },
        {
            "$unwind": {
                "path": "$ordenes.items",
                "preserveNullAndEmptyArrays": True
            }
        },
        {
            "$lookup": {
                "from": "productos",
                "localField": "ordenes.items.id_producto",
                "foreignField": "id_producto",
                "as": "producto_info"
            }
        },
        {
            "$unwind": {
                "path": "$producto_info",
                "preserveNullAndEmptyArrays": True
            }
        },
        {
            "$addFields": {
                "subtotal_item": {
                    "$cond": [
                        {"$and": [
                            {"$ifNull": ["$producto_info.precio", False]},
                            {"$ifNull": ["$ordenes.items.cantidad", False]}
                        ]},
                        {"$multiply": ["$producto_info.precio", "$ordenes.items.cantidad"]},
                        0
                    ]
                },
                "iva": {"$ifNull": ["$ordenes.iva", 0]}
            }
        },
        {
            "$group": {
                "_id": {
                    "id_proveedor": "$id_proveedor",
                    "id_orden": "$ordenes._id"
                },
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
                "cantidad_ordenes": {
                    "$sum": {
                        "$cond": [
                            {"$gt": ["$total_sin_iva", 0]},
                            1,
                            0
                        ]
                    }
                },
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
        },
        {"$sort": {"id_proveedor": 1}}
    ]))


def crear_indices():
    db.proveedores.create_index({"CUIT_proveedor": 1})
    db.ordenes.create_index({"id_proveedor": 1})


def buscar_proveedor_por_cuit():
    return list(db.proveedores.find(
        {"CUIT_proveedor": "30660608175"},
        {"_id": 0}))


def buscar_ordenes_por_proveedor(cuit):
    return list(db.ordenes.find(
        {"id_proveedor": str(cuit)},
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
                "id_pedido": {"$first": {"$toString": "$_id"}},
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
                "proveedor": 1,
                "total_sin_iva": 1,
                "total_con_iva": 1,
                "fecha_pedido": 1,
                "id_pedido": 1,
                "items": 1
            }
        },
        {
            "$sort": {"fecha_iso": 1}
        }
    ]))


def get_proveedores_activos_inhabilitados():
    return list(db.proveedores.find({
        "activo": 1,
        "habilitado": 0
    }, {"_id": 0}))
