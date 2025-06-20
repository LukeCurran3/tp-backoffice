from pydantic import BaseModel, Field
from typing import Optional


class ProveedorCreate(BaseModel):
    id_proveedor: int
    CUIT_proveedor: str
    razon_social: str
    tipo_sociedad: str
    direccion: str
    activo: int = Field(ge=0, le=1)  # 0 o 1
    habilitado: int = Field(ge=0, le=1)  # 0 o 1


class ProveedorUpdate(BaseModel):
    CUIT_proveedor: Optional[str] = None
    razon_social: Optional[str] = None
    tipo_sociedad: Optional[str] = None
    direccion: Optional[str] = None
    activo: Optional[int] = None
    habilitado: Optional[int] = None
