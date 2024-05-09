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
from model import OrderDetailModel,ProductModel,OrderDetail
from schema import OrderDetailSchema
from typing import List
router = APIRouter()  
model.Base.metadata.create_all(bind=engine)


def get_database_session():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

#Tạo đơn hàng
@router.post("/create_product", summary="Tạo sản phẩm")
async def create_product(
    productSchema: ProductSchema,
    db: Session = Depends(get_database_session),
):
    product_exists = db.query(exists().where(ProductModel.ProductID == productSchema.ProductID)).scalar()
    if product_exists:
        return {"data": "Sản phẩm đã tồn tại!"}

    # Create a new ProductSchema instance and add it to the database
    new_product = ProductModel(
        ProductID=productSchema.ProductID,
        ProductName=productSchema.ProductName,
        ProductBrand=productSchema.ProductBrand,
        ProductSerial=productSchema.ProductSerial,
        ProductDescription=productSchema.ProductDescription,
        UnitPrice=productSchema.UnitPrice,
        Status=productSchema.Status,
        HasBeenDeleted=0,
        Category_CategoryID=productSchema.Category_CategoryID

    )
    # new_invetory=InventoryModel()

    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return productSchema
#Sửa thông tin sản phẩm
@router.put("/update_product/{product_id}", summary="Cập nhật thông tin sản phẩm")
async def update_product(
    product_id: str,
    product_update: ProductSchema,
    db: Session = Depends(get_database_session),
):
    # Check if the product with the given ProductID exists
    existing_product = db.query(ProductModel).filter(ProductModel.ProductID == product_id).first()
    if not existing_product:
        raise HTTPException(status_code=404, detail="Sản phẩm không tồn tại!")

    # Update the product fields with the new values
    existing_product.ProductID = product_update.ProductID
    existing_product.ProductName = product_update.ProductName
    existing_product.ProductBrand = product_update.ProductBrand
    existing_product.ProductSerial = product_update.ProductSerial
    existing_product.ProductDescription = product_update.ProductDescription
    existing_product.UnitPrice = product_update.UnitPrice
    existing_product.Status = product_update.Status
    existing_product.Category_CategoryID = product_update.Category_CategoryID

    # Commit the changes to the database
    db.commit()
    db.refresh(existing_product)

    return {"data": "Thông tin sản phẩm đã được cập nhật thành công!"}

@router.post("/create_products", summary="Tạo nhiều sản phẩm")
async def create_products(
    products: List[ProductSchema],
    db: Session = Depends(get_database_session),
):
    # List to store any duplicate product IDs
    duplicates = []

    for productSchema in products:
        product_exists = db.query(exists().where(ProductModel.ProductSerial == productSchema.ProductSerial)).scalar()
        if product_exists:
            duplicates.append(productSchema.ProductID)
        else:
            # Create a new ProductSchema instance and add it to the database
            new_product = ProductModel(
                ProductID=productSchema.ProductID,
                ProductName=productSchema.ProductName,
                ProductBrand=productSchema.ProductBrand,
                ProductSerial=productSchema.ProductSerial,
                ProductDescription=productSchema.ProductDescription,
                UnitPrice=productSchema.UnitPrice,
                Status=productSchema.Status,
                HasBeenDeleted=0,
                Category_CategoryID=productSchema.Category_CategoryID
            )
            db.add(new_product)

    db.commit()

    if duplicates:
        return {"data": f"Sản phẩm đã tồn tại: {', '.join(duplicates)}"}

    return {"data": "Tạo sản phẩm thành công"}
@router.put("/update_products", summary="Cập nhật nhiều sản phẩm")
async def update_products(
    products_update: List[ProductSchema],
    db: Session = Depends(get_database_session),
):
    duplicates = []

    for product_update in products_update:
        # Check if the product with the given ProductID exists
        existing_product = db.query(ProductModel).filter(ProductModel.ProductID == product_update.ProductID).first()
        if not existing_product:
            raise HTTPException(status_code=404, detail=f"Sản phẩm có ID {product_update.ProductID} không tồn tại!")

        # Check for duplicate ProductID
        if product_update.ProductID != existing_product.ProductID:
            product_exists = db.query(exists().where(ProductModel.ProductID == product_update.ProductID)).scalar()
            if product_exists:
                duplicates.append(product_update.ProductID)

        # Update the product fields with the new values
        existing_product.ProductCode = product_update.ProductCode
        existing_product.ProviderID = product_update.ProviderID
        existing_product.ProductName = product_update.ProductName
        existing_product.ProductBrand = product_update.ProductBrand
        existing_product.ProductSerial = product_update.ProductSerial
        existing_product.ProductDescription = product_update.ProductDescription
        existing_product.ReorderQuantity = product_update.ReorderQuantity
        existing_product.UnitPrice = product_update.UnitPrice
        existing_product.Status = product_update.Status
        existing_product.Category_CategoryID = product_update.Category_CategoryID

    if duplicates:
        return {"data": f"Sản phẩm đã tồn tại: {', '.join(duplicates)}"}

    # Commit the changes to the database
    db.commit()

    return {"data": "Thông tin các sản phẩm đã được cập nhật thành công!"}

# @router.put("/update_product",dependencies=[Depends(JWTBearer())], summary="Sửa sản phẩm")
# async def update_product(
#     db: Session = Depends(get_database_session),
#     ProductID: str = Form(...),
#     ProviderID: str = Form(...),
#     ProductName: str = Form(...),
#     CategoryID: str = Form(...),
#     ProductBrand:str = Form(...),
#     ProductSerial:str = Form(...),
#     ProductDescription:str = Form(...),
#     ReorderQuantity: int = Form(...),
#     UnitPrice: float = Form(...),
# ):
#     product_exists = db.query(exists().where(ProductSchema.ProductID == ProductID)).scalar()
#     product = db.query(ProductSchema).get(ProductID)
#     if product_exists:
#         print(product)
#         product.ProductName = ProductName
#         product.ProviderID = ProviderID
#         product.CategoryID = CategoryID
#         product.ProductBrand = ProductBrand
#         product.ProductSerial = ProductSerial
#         product.ProductDescription = ProductDescription
#         product.ReorderQuantity = ReorderQuantity
#         product.UnitPrice = UnitPrice
#         db.commit()
#         db.refresh(product)
#         return {
#             "data": "Thông tin sản phẩm đã được cập nhật!"
#         }
#     else:
#         return JSONResponse(status_code=400, content={"message": "Không có thông tin sản phẩm!"})

# #Xóa sản phẩm
# @router.delete("/delete_product",dependencies=[Depends(JWTBearer())], summary="Xóa sản phẩm")
# async def delete_product(
#     db: Session = Depends(get_database_session),
#     ProductID: int = Form(...)
# ):
#     Product_exists = db.query(exists().where(ProductSchema.ProductID == ProductID)).scalar()
#     if Product_exists:
#         Product = db.query(ProductSchema).get(ProductID)
#         Product.hasBeenDeleted=1
#         # db.delete(product)
#         db.commit()
#         db.refresh(Product)

#         return{
#          "data": "Xóa sản phẩm thành công!"
#         }
#     else:
#         return JSONResponse(status_code=400, content={"message": "Không tồn tại sản phẩm!"})

#Lấy sản phẩm theo mã sản phẩm
@router.get("/Product/{productID}", summary="Lấy sản phẩm theo mã")
def get_courses_with_subject_info(
    db: Session = Depends(get_database_session),
    productID = int
):
    product = (
    db.query(ProductModel)  # Specify the model (ProductSchema) to query
    .filter(ProductModel.ProductID == productID)
    .first()
    )
    # print(products)
    # result = []
    # for product in products:
    #     result.append(
    #         {   
    #           product
    #         }
    #     )
    return {"product": product}

#Lấy tất cả sản phẩm
@router.get("/Products", summary="Lấy tất cả sản phẩm")
def get_products(
    db: Session = Depends(get_database_session),
):
    Product = (
    db.query(ProductModel)  # Specify the model (ProductSchema) to query
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
    return {"products": Product}

# #Lấy tất cả sản phẩm còn trong kho
# @router.get("/Product/All", summary="Lấy sản phẩm theo mã")
# def get_all_products(
#     db: Session = Depends(get_database_session),
# ):
#     Product = (
#     db.query(ProductSchema) 
#     .filter(ProductSchema.ReorderQuantity>0,ProductSchema.HasBeenDeleted == 0)
#     .all()
#     )
#     print(Product)
#     result = []
#     for Product in Product:
#         result.append(
#             {   
#               Product
#             }
#         )
#     return {"data": result}

#Lấy tất cả sản phẩm theo hãng
@router.get("/Product/All/ProductBrand", summary="Lấy sản phẩm theo hãng")
def get_all_products_with_brand(
    ProductBrand: str = Query(None),
    db: Session = Depends(get_database_session),
):
    query = (
        db.query(ProductModel)
    )

    if ProductBrand:
        query = query.filter(ProductModel.ProductBrand == ProductBrand)

    Product = query.all()
    result = []
    for Product in Product:
        result.append(
            {   
              Product
            }
        )
    return {"data": result}

# #Lấy tất cả sản phẩm theo hãng và còn hàng (chạy không lọc ra theo hãng)
# @router.get("/Product/All/ProductBrand/Instock", summary="Lấy sản phẩm theo hãng và còn hàng")
# def get_all_products_with_brand_instock(
#     ProductBrand: str = Query(None),
#     db: Session = Depends(get_database_session),
# ):
#     query = (
#         db.query(ProductSchema)
#         .filter(ProductSchema.ReorderQuantity > 0, ProductSchema.HasBeenDeleted == 0)
#     )

#     if ProductBrand:
#         query = query.filter(ProductSchema.ProductBrand == ProductBrand)

#     Product = query.all()
#     result = []
#     for Product in Product:
#         result.append(
#             {   
#               Product
#             }
#         )
#     return {"data": result}

#Lấy tất cả sản phẩm theo loại
@router.get("/Product/All/Category", summary="Lấy sản phẩm theo loại")
def get_all_products_with_category(
    CategoryID: str = Query(None),
    db: Session = Depends(get_database_session),
):
    query = (
        db.query(ProductModel)
    )

    if CategoryID:
        query = query.filter(ProductModel.Category_CategoryID == CategoryID)

    Product = query.all()
    result = []
    for Product in Product:
        result.append(
            {   
              Product
            }
        )
    return {"data": result}

# #Lấy tất cả sản phẩm thuộc loại được chọn và còn hàng
# @router.get("/Product/All/ProductCategory/Instock", summary="Lấy sản phẩm theo loại và còn hàng")
# def get_all_products_with_category(
#     CategoryID: str = Query(None),
#     db: Session = Depends(get_database_session),
# ):
#     query = (
#         db.query(ProductSchema)
#         .filter(ProductSchema.ReorderQuantity > 0, ProductSchema.HasBeenDeleted == 0)
#     )
# #dadad
#     if CategoryID:
#         query = query.filter(ProductSchema.CategoryID == CategoryID)

#     Product = query.all()
#     result = []
#     for Product in Product:
#         result.append(
#             {   
#               Product
#             }
#         )
#     return {"data": result}
