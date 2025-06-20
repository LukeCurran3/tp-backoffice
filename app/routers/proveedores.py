from fastapi import APIRouter

from ..models import ProveedorCreate
from ..services.mongo_queries import *

router = APIRouter()


# Obtener los datos de los proveedores activos y habilitados junto con sus teléfonos.
@router.get("/activos-habilitados")
def proveedores_activos():
    return get_proveedores_activos_habilitados()

#Obtener el/los teléfono/s y el código del/los proveedor/es que contengan la palabra
#“Tecnología” en su razón social.
@router.get("/telefonos-tecnologia")
def telefonos_tecnologia():
    return get_telefonos_tecnologia()

#Mostrar cada teléfono junto con los datos del proveedor.
@router.get("/telefonos")
def telefonos():
    return get_telefonos()

# Obtener todos los proveedores que tengan registrada al menos una orden de pedido.
@router.get("/proveedores-con-orden") #usa neo
def proveedores_con_orden():
    return get_proveedores_con_orden()

# Identificar todos los proveedores que NO tengan registrada ninguna orden de pedido.
@router.get("/proveedores-sin-orden")
def proveedores_con_orden():
    return get_proveedores_sin_orden()

#Devolver todos los proveedores, con la cantidad de ordenes que tienen registradas y el
#monto total pedido, con y sin IVA incluido (si no tienen órdenes registradas considerar
#cantidad y monto en 0).
@router.get("/proveedores-cantidad-ordenes")
def proveedores_cantidad_ordenes():
    return get_proveedores_cantidad_ordenes()

@router.post("/proveedores")
def crear_proveedor(proveedor: ProveedorCreate):
    post_proveedor(proveedor)
    return {"msg": "Proveedor creado con éxito"}

