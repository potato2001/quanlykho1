from fastapi import Depends, FastAPI, Request, Form,status,Header,APIRouter,HTTPException,File, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy import exists
import base64
from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder
from datetime import date
from auth.auth_bearer import JWTBearer
from auth.auth_handler import signJWT,decodeJWT,refresh_access_token
from model import CategoryModel
from database import SessionLocal, engine
from schema import CategorySchema,MultipleCategoriesSchema,CategoryUpdateSchema
import model
from typing import List

import csv

router = APIRouter()  
model.Base.metadata.create_all(bind=engine)


def get_database_session():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

#Thêm loại sản phẩm
@router.post("/create_category", summary="Tạo loại sản phẩm")
async def create_category(
    categorySchema: CategorySchema,
    db: Session = Depends(get_database_session),
):
    category_exists = db.query(exists().where(CategoryModel.CategoryName == categorySchema.CategoryName)).scalar()
    if category_exists:
        return {"data": "Sản phẩm đã tồn tại!"}

    # Create a new ProductSchema instance and add it to the database
    new_category = CategoryModel(
        CategoryName=categorySchema.CategoryName,
        HasBeenDeleted=categorySchema.HasBeenDeleted,
    )

    db.add(new_category)
    db.commit()
    db.refresh(new_category)
    return categorySchema

# Sủa loại sản phẩm
@router.put("/update_category/{category_id}", summary="Cập nhật loại sản phẩm")
async def update_product(
    category_id: str,
    category_update: CategorySchema,
    db: Session = Depends(get_database_session),
):
    existing_category = db.query(CategoryModel).filter(CategoryModel.CategoryID == category_id).first()
    if not existing_category:
        raise HTTPException(status_code=404, detail="Loại sản phẩm không tồn tại!")

    existing_category.CategoryName = category_update.CategoryName
    existing_category.HasBeenDeleted = category_update.HasBeenDeleted
  
    db.commit()
    db.refresh(existing_category)

    return {"data": "Thông tin loại sản phẩm đã được cập nhật thành công!"}
@router.post("/create_categories", summary="Tạo nhiều loại sản phẩm")
async def create_categories(
    categories_schema: MultipleCategoriesSchema,
    db: Session = Depends(get_database_session),
):
    duplicates = []

    for category in categories_schema.categories:
        category_exists = db.query(exists().where(CategoryModel.CategoryName == category.CategoryName)).scalar()
        if category_exists:
            duplicates.append(category.CategoryName)
        else:
            new_category = CategoryModel(
                CategoryName=category.CategoryName,
                HasBeenDeleted=category.HasBeenDeleted,
            )
            db.add(new_category)

    db.commit()

    if duplicates:
        return {"data": f"Sản phẩm đã tồn tại: {', '.join(duplicates)}"}

    return {"data": "Tạo loại sản phẩm thành công"}

#Cập nhật nhiều loại sản phẩm
@router.put("/update_categories", summary="Cập nhật nhiều loại sản phẩm")
async def update_categories(
    categories_update: List[CategoryUpdateSchema],
    db: Session = Depends(get_database_session),
):
    duplicates = []

    for category_update in categories_update:
        existing_category = db.query(CategoryModel).filter(CategoryModel.CategoryID == category_update.CategoryID).first()
        if not existing_category:
            raise HTTPException(status_code=404, detail=f"Loại sản phẩm có ID {category_update.CategoryID} không tồn tại!")

        if category_update.CategoryName != existing_category.CategoryName:
            category_exists = db.query(exists().where(CategoryModel.CategoryName == category_update.CategoryName)).scalar()
            if category_exists:
                duplicates.append(category_update.CategoryName)

        existing_category.CategoryName = category_update.CategoryName
        existing_category.HasBeenDeleted = category_update.HasBeenDeleted

    if duplicates:
        return {"data": f"Loại sản phẩm đã tồn tại: {', '.join(duplicates)}"}

    db.commit()

    return {"data": "Thông tin các loại sản phẩm đã được cập nhật thành công!"}

#Xóa loại sản phẩm
@router.delete("/delete_category/{category_id}", summary="Xóa loại sản phẩm")
async def delete_category(category_id: str, db: Session = Depends(get_database_session)):
    existing_category = db.query(CategoryModel).filter(CategoryModel.CategoryID == category_id).first()
    if not existing_category:
        raise HTTPException(status_code=404, detail=f"Loại sản phẩm có ID {category_id} không tồn tại!")

    existing_category.HasBeenDeleted = "Đã xoá"

    db.commit()

    return {"data": "Loại sản phẩm đã được xóa thành công!"}

#Nhập loại sản phẩm theo file csv
@router.post("/create_categories_from_csv", summary="Create categories from CSV")
async def create_categories_from_csv(
    csv_file: UploadFile = File(...),  # Accept CSV file uploads
    db: Session = Depends(get_database_session),
):
    if not csv_file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only .csv files are allowed")

    try:
        contents = await csv_file.read()  # Read the contents of the uploaded file
        decoded_contents = contents.decode("utf-8")  # Decode bytes to string
        lines = decoded_contents.split("\n")  # Split contents into lines
        reader = csv.reader(lines, delimiter=";")  # Create CSV reader with ';' delimiter
    except Exception as e:
        raise HTTPException(status_code=400, detail="Failed to read CSV file")
    next(reader)
    for row in reader:
        if len(row) < 1:  
            continue
        
        category_name = row[0].strip()  
        category_hasBeenDelete = row[1].strip()  

        
        category_exists = db.query(exists().where(CategoryModel.CategoryName == category_name)).scalar()
        if category_exists:
            continue
        
        new_category = CategoryModel(
            CategoryName=category_name,
            HasBeenDeleted=category_hasBeenDelete,  
        )
        db.add(new_category)

    db.commit()
    return {"message": "Categories created from CSV"}

#Lấy tất cả loại sản phẩm
@router.get("/category", summary="Lấy tất cả loại sản phẩm")
def get_category(
    db: Session = Depends(get_database_session),
):
    categories = (
    db.query(CategoryModel)
    .all()
    )
    print(categories)
    result = []
    for category in categories:
        result.append(
            {   
              category
            }
        )
    return {"data": result}