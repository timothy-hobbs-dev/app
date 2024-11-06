# main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

app = FastAPI()
#test container

engine = create_engine("postgresql://root:pass1234@database-1.cf00csegghpu.us-east-1.rds.amazonaws.com:5432/postgres")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Model
class Item(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)

# Schema
class ItemCreate(BaseModel):
    name: str
    description: str

class ItemResponse(BaseModel):
    id: int
    name: str
    description: str

    class Config:
        from_attributes = True

# Create tables
Base.metadata.create_all(bind=engine)

# CRUD operations
@app.post("/items/", response_model=ItemResponse)
def create_item(item: ItemCreate):
    db = SessionLocal()
    db_item = Item(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    db.close()
    return db_item

@app.get("/items/{item_id}", response_model=ItemResponse)
def read_item(item_id: int):
    db = SessionLocal()
    item = db.query(Item).filter(Item.id == item_id).first()
    db.close()
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

@app.get("/items/", response_model=list[ItemResponse])
def read_items():
    db = SessionLocal()
    items = db.query(Item).all()
    db.close()
    return items

@app.put("/items/{item_id}", response_model=ItemResponse)
def update_item(item_id: int, item: ItemCreate):
    db = SessionLocal()
    db_item = db.query(Item).filter(Item.id == item_id).first()
    if db_item is None:
        db.close()
        raise HTTPException(status_code=404, detail="Item not found")
    
    for key, value in item.dict().items():
        setattr(db_item, key, value)
    
    db.commit()
    db.refresh(db_item)
    db.close()
    return db_item

@app.delete("/items/{item_id}")
def delete_item(item_id: int):
    db = SessionLocal()
    item = db.query(Item).filter(Item.id == item_id).first()
    if item is None:
        db.close()
        raise HTTPException(status_code=404, detail="Item not found")
    
    db.delete(item)
    db.commit()
    db.close()
    return {"message": "Item deleted"}
