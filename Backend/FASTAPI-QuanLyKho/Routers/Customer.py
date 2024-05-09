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
from model import CustomerModel
from schema import CustomerSchema
from typing import List
router = APIRouter()  
model.Base.metadata.create_all(bind=engine)


def get_database_session():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()
        
#Tạo khách hàng
@router.post("/create_customer", summary="Tạo khách hàng")
async def create_customer(
    customerSchema: CustomerSchema,
    db: Session = Depends(get_database_session),
):
    customer_exists = db.query(exists().where(CustomerModel.CustomerPhone == customerSchema.CustomerPhone)).scalar()
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


#Sửa thông tin khách hàng
@router.put("/update_customer/{customerID}", summary="Cập nhật thông tin khách hàng")
async def update_customer(
    customerID: str,
    customer_update: CustomerSchema,
    db: Session = Depends(get_database_session),
):
    existing_customer = db.query(CustomerModel).filter(CustomerModel.CustomerID == customerID).first()
    existing_phone = db.query(CustomerModel).filter(CustomerModel.CustomerPhone==customer_update.CustomerPhone).first()
    if existing_phone:
        raise HTTPException(status_code=404, detail="Số điện thoại tồn tại!")

    if not existing_customer:
        raise HTTPException(status_code=404, detail="Khách hàng không tồn tại!")

    existing_customer.CustomerName = customer_update.CustomerName
    existing_customer.CustomerAddress = customer_update.CustomerAddress
    existing_customer.CustomerEmail = customer_update.CustomerEmail
    existing_customer.CustomerPhone = customer_update.CustomerPhone

    db.commit()
    db.refresh(existing_customer)

    return {"data": "Thông tin khách hàng đã được cập nhật thành công!"}

#Lấy tất cả khách hàng
@router.get("/Customers", summary="Lấy tất cả thông tin khách hàng")
def get_customers(
    db: Session = Depends(get_database_session),
):
    Customer = (
    db.query(CustomerModel)
    .all()
    )
    return {"customers": Customer}

#Lấy thông tin khách hàng theo tên khách hàng
@router.get("/Customer/{customerName}", summary="Lấy thông tin khách hàng theo tên")
def get_customer_name(
    customerName: str,
    db: Session = Depends(get_database_session),
):
    query = (
        db.query(CustomerModel).filter(CustomerModel.CustomerName == customerName)
    )
    
    Customer = query.all()
    if len(Customer) == 0:
        raise HTTPException(status_code=404, detail="Khách hàng không tồn tại!")
    return {"data": Customer}