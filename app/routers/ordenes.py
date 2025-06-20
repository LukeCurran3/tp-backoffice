from fastapi import APIRouter

from ..models import ProveedorCreate, OrdenCreate
from ..services.mongo_queries import *

router = APIRouter()

#Listar los datos de todas las órdenes que hayan sido pedidas al proveedor cuyo CUIT es
# 30-66060817-5.
@router.get("/ordenes-cuit")
def ordenes_cuit():
    return get_ordenes_cuit()


# Listar los datos de todas las órdenes de pedido que contengan productos de la marca
# “COTO”
@router.get("/ordenes-coto")
def ordenes_coto():
    return get_ordenes_coto()

# Ordenes de pedido ordenadas por fecha
@router.get("/ordenes-por-fecha")
def ordenes_por_fecha():
    return get_ordenes_por_fecha()

@router.post("/")
def crear_orden(orden: OrdenCreate):
    post_orden(orden)
    return {"msg": "orden registrada con éxito"}
