from pydantic import BaseModel, Field
from typing import Optional
from datetime import date
from typing import List


class Telefono(BaseModel):
    codigo_area: int
    nro_telefono: int
    tipo: str

class ProveedorCreate(BaseModel):
    id_proveedor: int
    CUIT_proveedor: str
    razon_social: str
    tipo_sociedad: str
    direccion: str
    activo: int = Field(ge=0, le=1)  # 0 o 1
    habilitado: int = Field(ge=0, le=1)  # 0 o 1
    telefonos: List[Telefono]


class ProveedorUpdate(BaseModel):
    CUIT_proveedor: Optional[str] = None
    razon_social: Optional[str] = None
    tipo_sociedad: Optional[str] = None
    direccion: Optional[str] = None
    activo: Optional[int] = None
    habilitado: Optional[int] = None

class ProductoCreate(BaseModel):
    id_producto: int
    descripcion: str
    marca: str
    categoria: str
    precio: float
    stock_actual: int
    stock_futuro: int


class ProductoUpdate(BaseModel):
    descripcion: Optional[str] = None
    marca: Optional[str] = None
    categoria: Optional[str] = None
    precio: Optional[float] = None
    stock_actual: Optional[int] = None
    stock_futuro: Optional[int] = None

class DetalleOrden(BaseModel):
    id_producto: int
    nro_item: int
    cantidad: float

class OrdenCreate(BaseModel):
    id_pedido: int
    id_proveedor: int
    fecha: date
    total_sin_iva: float
    iva: float
    items: List[DetalleOrden]
