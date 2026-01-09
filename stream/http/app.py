from fastapi import FastAPI

from oracle.service import OracleService
from stream.http.routes import router


def create_app() -> FastAPI:
    oracle_service = OracleService()

    app = FastAPI(title="Nexus")
    app.state.oracle = oracle_service
    app.include_router(router)

    return app


app = create_app()
