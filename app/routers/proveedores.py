from fastapi import APIRouter

from ..models import ProveedorCreate, ProveedorUpdate
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



#Listar los datos de todas las órdenes que hayan sido pedidas al proveedor cuyo CUIT es
# 30-66060817-5. -> MONGO join
@router.get("/proveedor-por-cuit/{cuit}")
def get_proveedor_por_cuit(cuit: int):
    return buscar_proveedor_por_cuit(cuit)

@router.get("/ordenes-por-proveedor/{cuit}")
def get_ordenes_por_proveedor(cuit: int):
    return buscar_ordenes_por_proveedor(cuit)

#Se necesita crear una vista que devuelva los datos de las órdenes de pedido
# ordenadas por fecha (incluyendo la razón social del proveedor y el total de la orden
# sin y con IVA).
@router.get("/proveedores-por-fecha")
def proveedores_por_fecha():
    return get_proveedores_por_fecha()

# proveedores activos que están inhabilitados
@router.get("/proveedores-activos-inhabilitados")
def proveedores_activos_inhabilitados():
    return get_proveedores_activos_inhabilitados()



# 13. Implementar la funcionalidad que permita crear nuevos proveedores, eliminar y
# modificar los ya existentes.

@router.post("/")
def crear_proveedor(proveedor: ProveedorCreate):
    post_proveedor(proveedor)
    return {"msg": "Proveedor creado con éxito"}

@router.put("/{id_proveedor}")
def modificar_proveedor(id_proveedor: int, proveedor: ProveedorUpdate):
    put_proveedor(id_proveedor, proveedor)
    return {"msg": "Proveedor modificado con éxito"}
@router.delete("/{id_proveedor}")
def eliminar_proveedor(id_proveedor: int):
    delete_proveedor(id_proveedor)
    return {"msg": "Proveedor eliminado con éxito"}
