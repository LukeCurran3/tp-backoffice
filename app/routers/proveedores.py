from fastapi import APIRouter
from fastapi import Response, status

from ..models import ProveedorCreate, ProveedorUpdate
from ..services import neo_queries, mongo_queries



router = APIRouter()


# Obtener los datos de los proveedores activos y habilitados junto con sus teléfonos.
@router.get("/activos-habilitados")
def proveedores_activos():
    return mongo_queries.get_proveedores_activos_habilitados()


# Obtener el/los teléfono/s y el código del/los proveedor/es que contengan la palabra
# “Tecnología” en su razón social.
@router.get("/telefonos-tecnologia")
def telefonos_tecnologia():
    return mongo_queries.get_telefonos_tecnologia()


# Mostrar cada teléfono junto con los datos del proveedor.
@router.get("/telefonos")
def telefonos():
    return mongo_queries.get_telefonos()


# Obtener todos los proveedores que tengan registrada al menos una orden de pedido.
@router.get("/proveedores-con-orden")  # usa neo
def proveedores_con_orden():
    return neo_queries.get_proveedores_con_orden()


# Identificar todos los proveedores que NO tengan registrada ninguna orden de pedido.
@router.get("/proveedores-sin-orden")
def proveedores_con_orden():
    return neo_queries.get_proveedores_sin_orden()


# Devolver todos los proveedores, con la cantidad de ordenes que tienen registradas y el
# monto total pedido, con y sin IVA incluido (si no tienen órdenes registradas considerar
# cantidad y monto en 0).
@router.get("/proveedores-cantidad-ordenes")
def proveedores_cantidad_ordenes():
    return mongo_queries.get_proveedores_cantidad_ordenes()


# Se necesita crear una vista que devuelva los datos de las órdenes de pedido
# ordenadas por fecha (incluyendo la razón social del proveedor y el total de la orden
# sin y con IVA).
@router.get("/proveedores-por-fecha")
def proveedores_por_fecha():
    res = mongo_queries.get_proveedores_por_fecha()
    print(res)
    return res


# proveedores activos que están inhabilitados
@router.get("/proveedores-activos-inhabilitados")
def proveedores_activos_inhabilitados():
    return mongo_queries.get_proveedores_activos_inhabilitados()


# 13. Implementar la funcionalidad que permita crear nuevos proveedores, eliminar y
# modificar los ya existentes.

@router.post("/")
def crear_proveedor(proveedor: ProveedorCreate):
    object_mongo = mongo_queries.post_proveedor(proveedor)
    object_neo = neo_queries.create_proveedor(proveedor)
    if object_neo is None or object_mongo == 0:
        return {"msg": "No se ha podido crear el proveedor"}
    return Response(
        content="Proveedor creado correctamente",
        status_code=status.HTTP_201_CREATED
    )


@router.put("/{id_proveedor}")
def modificar_proveedor(id_proveedor: int, proveedor: ProveedorUpdate):
    object_mongo = mongo_queries.put_proveedor(id_proveedor, proveedor)
    object_neo = neo_queries.put_proveedor(id_proveedor, proveedor)
    if object_neo is None or object_mongo == 0:
        return Response(
            content="Proveedor no encontrado",
            status_code=status.HTTP_404_NOT_FOUND
        )
    return {"msg": "Proveedor modificado con éxito"}


@router.delete("/{id_proveedor}")
def eliminar_proveedor(id_proveedor: int):
    deleted_mongo = mongo_queries.delete_proveedor(id_proveedor)
    deleted_neo = neo_queries.delete_proveedor(id_proveedor)
    if deleted_neo == 0 or deleted_mongo == 0:
        return Response(
            content="Proveedor no encontrado",
            status_code=status.HTTP_404_NOT_FOUND
        )
    return {"msg": "Proveedor eliminado con éxito"}
