from src.database import engine, Base
import uvicorn

Base.metadata.create_all(bind=engine)

if __name__ == '__main__':
    uvicorn.run('src.api.api:app', host='0.0.0.0', port=8000, reload=True)