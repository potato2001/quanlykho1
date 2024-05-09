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
from model import ProviderModel
from schema import ProviderSchema
from typing import List
router = APIRouter()  
model.Base.metadata.create_all(bind=engine)


def get_database_session():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()
#Tạo thông tin nhà cung cấp
@router.post("/create_provider", summary="Tạo nhà cung cấp")
async def create_provider(
    providerSchema: ProviderSchema,
    db: Session = Depends(get_database_session),
):
    provider_exists = db.query(exists().where(ProviderModel.ProviderPhone == providerSchema.ProviderPhone)).scalar()
    if provider_exists:
        return {"data": "Nhà cung cấp đã tồn tại!"}

    new_provider = ProviderModel(
        # ProviderID=providerSchema.ProviderID,
        ProviderName=providerSchema.ProviderName,
        ProviderAddress=providerSchema.ProviderAddress,
        ProviderPhone=providerSchema.ProviderPhone,
        ProviderEmail=providerSchema.ProviderEmail,
        HasBeenDeleted=0,
    )

    db.add(new_provider)
    db.commit()
    db.refresh(new_provider)
    return HTTPException(status_code=200, detail="Tạo nhà cung cấp thành công")


#Sửa thông tin nhà cung cấp
@router.put("/update_provider/{ProviderID}", summary="Cập nhật thông tin nhà cung cấp")
async def update_provider(
    ProviderID: str,
    provider_update: ProviderSchema,
    db: Session = Depends(get_database_session),
):
    # Check if the product with the given ProductID exists
    existing_provider = db.query(ProviderModel).filter(ProviderModel.ProviderID == ProviderID).first()
    if not existing_provider:
        raise HTTPException(status_code=404, detail="Nhà cung cấp không tồn tại!")

    # Update the product fields with the new values
    existing_provider.ProviderName = provider_update.ProviderName
    existing_provider.ProviderAddress = provider_update.ProviderAddress
    existing_provider.ProviderPhone = provider_update.ProviderPhone
    existing_provider.ProviderEmail = provider_update.ProviderEmail
    

    # Commit the changes to the database
    db.commit()
    db.refresh(existing_provider)

    return HTTPException(status_code=200, detail="Thông tin nhà cung cấp đã được cập nhật thành công!")

#Lấy tất cả nhà cung cấp
@router.get("/Providers", summary="Lấy tất cả thông tin nhà cung cấp")
def get_Providers(
    db: Session = Depends(get_database_session),
):
    Provider = (
    db.query(ProviderModel)
    .all()
    )
    return {"Providers": Provider}

#Lấy thông tin nhà cung cấp theo tên nhà cung cấp
@router.get("/Provider/{providerName}", summary="Lấy thông tin nhà cung cấp theo tên")
def get_provider_name(
    providerName: str,
    db: Session = Depends(get_database_session),
):
    query = (
        db.query(ProviderModel).filter(ProviderModel.ProviderName == providerName)
    )
    
    Provider = query.all()
    if len(Provider) == 0:
        raise HTTPException(status_code=404, detail="Nhà cung cấp không tồn tại!")
    return {"data": Provider}