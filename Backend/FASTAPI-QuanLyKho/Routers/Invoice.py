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
from model import InvoiceModel
from schema import InvoiceSchema
from typing import List
router = APIRouter()  
model.Base.metadata.create_all(bind=engine)


def get_database_session():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()
#Tạo hoá đơn
@router.post("/create_invoice", summary="Tạo hoá đơn")
async def create_invoice(
    invoiceSchema: InvoiceSchema,
    db: Session = Depends(get_database_session),
):
    invoice_exists = db.query(exists().where(CustomerModel.CustomerPhone == customerSchema.CustomerPhone)).scalar()
    if customer_exists:
        return {"data": "Khách hàng đã tồn tại!"}

    new_customer = CustomerModel(
        CustomerName=customerSchema.CustomerName,
        CustomerAddress=customerSchema.CustomerAddress,
        CustomerPhone=customerSchema.CustomerPhone,
        CustomerEmail=customerSchema.CustomerEmail,
    )
    db.add(new_customer)
    db.commit()
    db.refresh(new_customer)
    return  HTTPException(status_code=200, detail="Tạo khách hàng thành công")