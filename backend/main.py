from fastapi import FastAPI, HTTPException, Request
from src import models
from src.database import engine, Base
import uvicorn
import logging
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

Base.metadata.create_all(bind=engine)
app = FastAPI()

if __name__ == '__main__':
    uvicorn.run('src.api.api:app', host='0.0.0.0', port=8080, reload=True)