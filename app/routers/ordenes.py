from fastapi import APIRouter

from ..models import ProveedorCreate, OrdenCreate
from ..services import neo_queries, mongo_queries


from fastapi import Response, status

router = APIRouter()

#Listar los datos de todas las órdenes que hayan sido pedidas al proveedor cuyo CUIT es
# 30-66060817-5.
@router.get("/ordenes-cuit")
def ordenes_cuit():
    return mongo_queries.buscar_proveedor_por_cuit()


# Listar los datos de todas las órdenes de pedido que contengan productos de la marca
# “COTO”
@router.get("/ordenes-coto")
def ordenes_coto():
    return neo_queries.get_ordenes_por_marca("COTO")

# Ordenes de pedido ordenadas por fecha
@router.get("/ordenes-por-fecha")
def ordenes_por_fecha():
    return mongo_queries.get_proveedores_por_fecha()

@router.post("/")
def crear_orden(orden: OrdenCreate):
    object_neo = neo_queries.create_orden(orden)
    object_mongo = mongo_queries.create_orden(orden)
    if object_neo is None or object_mongo == 0:
        return {"msg": "No se ha podido crear la orden"}
    return Response(
        content="Orden creada correctamente",
        status_code=status.HTTP_201_CREATED
    )