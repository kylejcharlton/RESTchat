from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse

from backend.auth import ExpiredToken, InvalidToken, auth_router
from backend.entities import InvalidStateException, NoPermissionException
from backend.routers.chats import chats_router
from backend.routers.users import users_router
from backend.database import create_db_and_tables, EntityNotFoundException


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(
    title="RESTchat API",
    description="An API for the RESTchat application",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(auth_router)
app.include_router(chats_router)
app.include_router(users_router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(EntityNotFoundException)
def handle_entity_not_found(
    _request: Request,
    exception: EntityNotFoundException,
) -> JSONResponse:
    return JSONResponse(
        status_code=404,
        content={
            "detail": {
                "type": "entity_not_found",
                "entity_name": exception.entity_name,
                "entity_id": exception.entity_id,
            },
        },
    )


@app.exception_handler(NoPermissionException)
def handle_invalid_client(
    _request: Request,
    exception: NoPermissionException,
) -> JSONResponse:
    return JSONResponse(
        status_code=403,
        content={
            "detail": {
                "error": "no_permission",
                "error_description": exception.error_description
            },
        },
    )


@app.exception_handler(InvalidStateException)
def handle_invalid_client(
    _request: Request,
    exception: InvalidStateException,
) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content={
            "detail": {
                "error": "invalid_state",
                "error_description": exception.error_description
            },
        },
    )


@app.exception_handler(InvalidToken)
def handle_invalid_client(
    _request: Request,
    exception: InvalidToken,
) -> JSONResponse:
    return JSONResponse(
        status_code=401,
        content={
            "detail": {
                **exception.detail
            },
        },
    )


@app.get("/", include_in_schema=False)
def default() -> str:
    return HTMLResponse(
        content=f"""
        <html>
            <body>
                <h1>{app.title}</h1>
                <p>{app.description}</p>
                <h2>API docs</h2>
                <ul>
                    <li><a href="/docs">Swagger</a></li>
                    <li><a href="/redoc">ReDoc</a></li>
                </ul>
            </body>
        </html>
        """,
    )