# FILE: main.py

import uvicorn
from fastapi import FastAPI, HTTPException
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
import models 
from models import Base

# --- DATABASE SETUP ---
DATABASE_URL = "sqlite:///./mining_knowledge.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# --- FASTAPI APP ---
app = FastAPI()

# --- HELPER FUNCTION ---
def object_as_dict(obj):
    return {c.key: getattr(obj, c.key) for c in inspect(obj).mapper.column_attrs}

# --- API ENDPOINTS ---

@app.get("/api/tables")
def get_table_names():
    inspector = inspect(engine)
    table_names = inspector.get_table_names()
    return table_names

@app.get("/api/table/{table_name}")
def get_table_data(table_name: str):
    db = SessionLocal()
    try:
        ModelClass = None
        for mapper in Base.registry.mappers:
            if mapper.local_table.name == table_name:
                ModelClass = mapper.class_
                break
        
        if not ModelClass:
            raise HTTPException(status_code=404, detail="Table not found")

        records = db.query(ModelClass).all()
        result = [object_as_dict(rec) for rec in records]
        return result
    finally:
        db.close()

# The app.mount line has been REMOVED. Vercel will handle serving the index.html.