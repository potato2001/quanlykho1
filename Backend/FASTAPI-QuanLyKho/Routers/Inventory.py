from fastapi import Depends, FastAPI, Request, Form,status,Header,APIRouter, Query,HTTPException,Response
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy import exists
import base64
from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder
from datetime import date
from auth.auth_bearer import JWTBearer
from auth.auth_handler import signJWT,decodeJWT,refresh_access_token
from database import SessionLocal, engine
import model
from model import InventoryModel
from schema import InventorySchema
from typing import List
router = APIRouter()  
model.Base.metadata.create_all(bind=engine)

router = APIRouter()  
model.Base.metadata.create_all(bind=engine)

def get_database_session():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

#Hiển thị tất cả các sản phẩm còn trong kho
@router.get("/show_all_products", summary="Lấy tất cả sản phẩm còn trong kho (chưa hoàn thành)")
def show_all_products(
    db: Session = Depends(get_database_session),
):
    Inventory = (
    db.query(InventoryModel)  # Specify the model (ProductSchema) to query
    .all()
    )
    # print(Product)
    # result = []
    # for product in Product:
    #     result.append(
    #         {   
    #           product
    #         }
    #     )
    return {"products": Inventory}