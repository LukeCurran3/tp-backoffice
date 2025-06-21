import datetime

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
    doc = orden.model_dump()
    if isinstance(doc.get('fecha'), datetime.date) and not isinstance(doc.get('fecha'), datetime.datetime):
        doc['fecha'] = datetime.datetime.combine(doc['fecha'], datetime.time.min)

    result = db.ordenes.insert_one(doc)

    return 1 if result.acknowledged else 0


def create_producto(producto: ProductoCreate):
    result = db.productos.insert_one(producto.model_dump())
    return 1 if result.acknowledged else 0


def put_producto(id_producto: int, producto: ProductoUpdate):
    result = db.productos.update_one(
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


def delete_producto(id_producto: int):
    result = db.productos.delete_one({"id_producto": id_producto})
    return result.deleted_count


def delete_order(id_pedido: int):
    result = db.ordenes.delete_one({"id_pedido": id_pedido})
    return result.deleted_count


def get_telefonos_tecnologia():
    return list(db.proveedores.find({
        "razon_social": {"$regex": "Tecnología"}
    }, {"_id": 0, "id_proveedor": 1, "telefonos": 1}))


def get_telefonos():
    return list(db.proveedores.aggregate([
        {"$unwind": "$telefonos"},
        {"$project": {
            "_id": 0,
            "id_proveedor": 1,
            "razon_social": 1,
            "codigo_area": "$telefonos.codigo_area",
            "nro_telefono": "$telefonos.nro_telefono",
            "tipo": "$telefonos.tipo"
        }}
    ]))


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



def buscar_proveedor_por_cuit():
    provider_info = db.proveedores.find(
        {"CUIT_proveedor": "30660608175"},
        {"_id": 0}).to_list()[0]

    order_info = db.ordenes.find({ "id_proveedor": provider_info["id_proveedor"] },{"_id":0}).to_list()
    
    return order_info


def buscar_ordenes_por_proveedor(cuit):
    return list(db.ordenes.find(
        {"id_proveedor": str(cuit)},
        {"_id": 0}))


def get_proveedores_por_fecha():
    return db["view_proveedores_por_fecha"].find().to_list()


def get_proveedores_activos_inhabilitados():
    return db["view_proveedores_activos_inhabilitados"].find().to_list()

def get_productos_sin_orden():
    return db["view_productos_no_pedidos"].find().to_list()