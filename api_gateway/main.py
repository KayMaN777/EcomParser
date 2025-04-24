import os
import asyncio
import uvicorn
from fastapi import FastAPI
from api import router
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.gzip import GZipMiddleware
from dotenv import load_dotenv

load_dotenv()

async def main() -> None:
    app = FastAPI(
    title="EcomParser api gateway"
    )
    app.include_router(router=router, prefix="/api/v1")
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    port = os.getenv("API_GATEWAY_PORT")
    host = os.getenv("API_GATEWAY_HOST")
    config = uvicorn.Config(
        app,
        host=host,  
        port=int(port),  
    )
    server = uvicorn.Server(config)
    await server.serve()

if __name__ == "__main__":
    asyncio.run(main())