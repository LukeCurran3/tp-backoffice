from fastapi import FastAPI
from .routers import productos, proveedores, ordenes

app = FastAPI()

app.include_router(proveedores.router, prefix="/proveedores", tags=["Proveedores"])
app.include_router(productos.router, prefix="/productos", tags=["Productos"])
app.include_router(ordenes.router, prefix="/ordenes", tags=["Ordenes"])