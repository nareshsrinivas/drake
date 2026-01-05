from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
import os

from fastapi import Request
from fastapi.responses import JSONResponse
import traceback
from fastapi.staticfiles import StaticFiles
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent


# =====================
# CREATE APP
# =====================
app = FastAPI(
    title="LockTrust API",
    version="1.0.0",
    openapi_url="/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc"
)

# =====================
# CORS
# =====================
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5174",
    "https://locktrust.xyz"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "error": str(exc),
            "trace": traceback.format_exc()
        }
    )


# =====================
# ROOT
# =====================
@app.get("/")
def root():
    return {"status": "FastAPI OK"}

# =====================
# STATIC FILES
# =====================
UPLOAD_DIR = "uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)


# =====================
# ROUTERS (IMPORT AFTER APP)
# =====================
from auth.routes import router as auth_router
from admin.routes import router as admin_router
from admin.routes_slider import router as slider_router
from admin.routes_work import router as work_router
from admin.routes_skill import router as skill_router
from admin.routes_contact_banner import router as contact_router
from public.routes_public import router as public_router
from model.model_routes_master import router as model_router
from agency.agency_profile_routes import router as agency_router
from job_applications.routes import router as job_application_router

app.include_router(public_router)
app.include_router(auth_router)
app.include_router(model_router)
app.include_router(agency_router)
app.include_router(job_application_router)
app.include_router(admin_router)
app.include_router(slider_router)
app.include_router(work_router)
app.include_router(skill_router)
app.include_router(contact_router)

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")



# =====================
# CUSTOM SWAGGER AUTH
# =====================
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="LockTrust API",
        version="1.0.0",
        routes=app.routes,
    )

    # 🔥 THIS IS THE KEY LINE
    openapi_schema["servers"] = [
        {"url": "/drakeapi"}
    ]

    openapi_schema.setdefault("components", {})
    openapi_schema["components"].setdefault("securitySchemes", {})

    openapi_schema["components"]["securitySchemes"]["BearerAuth"] = {
        "type": "http",
        "scheme": "bearer",
        "bearerFormat": "JWT",
    }

    for path, methods in openapi_schema["paths"].items():
        for method, details in methods.items():
            if method in ["get", "post", "put", "delete", "patch"]:
                if not path.startswith(("/auth/login", "/auth/register")):
                    details["security"] = [{"BearerAuth": []}]

    app.openapi_schema = openapi_schema
    return app.openapi_schema

