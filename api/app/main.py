from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .routers import demo, gestiones, metricas

settings = get_settings()

app = FastAPI(
    title="NBO Movistar · API",
    version="1.0.0",
    description=(
        "Motor de Next Best Offer para la consola del asesor.\n\n"
        "**Fase 1**: los endpoints de `/api/clientes/*` se sirven desde un JSON de demo. "
        "Las gestiones y calificaciones sí se persisten en PostgreSQL."
    ),
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(demo.router)
app.include_router(gestiones.router)
app.include_router(metricas.router)


@app.get("/health", tags=["salud"])
def health() -> dict[str, str]:
    return {"estado": "ok"}
