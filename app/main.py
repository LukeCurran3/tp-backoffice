from fastapi import FastAPI
from .routers import proveedores

app = FastAPI()

app.include_router(proveedores.router, prefix="/proveedores", tags=["Proveedores"])