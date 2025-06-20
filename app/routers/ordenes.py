from fastapi import APIRouter

from ..models import ProveedorCreate, OrdenCreate
from ..services import neo_queries, mongo_queries
from ..services.mongo_queries import *
from ..services.neo_queries import *

router = APIRouter()

#Listar los datos de todas las órdenes que hayan sido pedidas al proveedor cuyo CUIT es
# 30-66060817-5.
@router.get("/ordenes-cuit")
def ordenes_cuit():
    return buscar_proveedor_por_cuit()


# Listar los datos de todas las órdenes de pedido que contengan productos de la marca
# “COTO”
@router.get("/ordenes-coto")
def ordenes_coto():
    return get_ordenes_por_marca("COTO")

# Ordenes de pedido ordenadas por fecha
@router.get("/ordenes-por-fecha")
def ordenes_por_fecha():
    return get_proveedores_por_fecha()

@router.post("/")
def crear_orden(orden: OrdenCreate):
    neo_queries.create_orden(orden)
    mongo_queries.create_orden(orden)
    return {"msg": "orden registrada con éxito"}
