
from fastapi import APIRouter
from fastapi import Response, status

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
    object_neo = neo_queries.create_producto(producto)
    object_mongo = mongo_queries.create_producto(producto)
    if object_neo is None or object_mongo == 0:
        return {"msg": "No se ha podido crear el producto"}
    return Response(
        content="Producto creado correctamente",
        status_code=status.HTTP_201_CREATED
    )
@router.put("/{id_producto}")
def modificar_producto(id_producto: int, producto: ProductoUpdate):
    object_neo = neo_queries.put_producto(id_producto, producto)
    object_mongo = mongo_queries.put_producto(id_producto,  producto)
    if object_neo is None or object_mongo == 0:
        return Response(
            content="Producto no encontrado",
            status_code=status.HTTP_404_NOT_FOUND
        )
    return {"msg": "Producto modificado con éxito"}