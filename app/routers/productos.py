
from fastapi import APIRouter

from ..models import ProductoUpdate, ProductoCreate
from ..services import neo_queries, mongo_queries
from ..services.neo_queries import *

router = APIRouter()

# Mostrar los productos que han sido pedido al menos 1 vez.
@router.get("/productos-pedidos")
def productos_pedidos():
    return get_productos_con_orden()

# Crear una vista que devuelva todos los productos que aún NO han sido pedidos.
@router.get("/productos-no-pedidos")
def productos_no_pedidos():
    return get_productos_sin_orden()

@router.post("/")
def crear_producto(producto: ProductoCreate):
    neo_queries.create_producto(producto)
    mongo_queries.create_producto(producto)
    return {"msg": "Producto creado con éxito"}

@router.put("/{id_producto}")
def modificar_producto(id_producto: int, producto: ProductoUpdate):
    neo_queries.put_producto(id_producto, producto)
    mongo_queries.put_producto(id_producto,  producto)
    return {"msg": "Producto modificado con éxito"}