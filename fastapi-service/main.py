from src.database import engine, Base
import src.models  # Import models to register them with Base.metadata
import uvicorn

print("Creating tables...")
Base.metadata.create_all(bind=engine)
print("Tables created successfully")

if __name__ == '__main__':
    uvicorn.run('src.api.api:app', host='0.0.0.0', port=8000, reload=True)