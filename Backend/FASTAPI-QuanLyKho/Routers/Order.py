from fastapi import Depends, FastAPI, Request, Form,status,Header,APIRouter, Query
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy import exists
import base64
from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder
from datetime import datetime
from auth.auth_bearer import JWTBearer
from auth.auth_handler import signJWT,decodeJWT,refresh_access_token
from database import SessionLocal, engine
import model
from model import OrderSchema,ProductSchema,CustomerSchema


router = APIRouter()  
model.Base.metadata.create_all(bind=engine)


def get_database_session():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

#Tạo đơn hàng (Chưa xong và chưa có phần nối với thông tin người đặt)
@router.post("/create_order", summary="Tạo đơn hàng")
async def create_order(
    db: Session = Depends(get_database_session),
    ProductID: str = Form(...),
    ProductQuantity: str = Form(...),
    #OrderDate:str=Form(...),
    Status:str=Form(...),
):
    Product = db.query(ProductSchema).filter_by(ProductID=ProductID).first()
    if(Product.ProductQuantity==0):
        Product.Status == 0
        db.commit()
        return JSONResponse(status_code=400, content={"message": "Sản phẩm đã hết"})
    if(ProductQuantity<Product.ProductQuantity):
        return JSONResponse(status_code=400, content={"message": f"Sản phẩm tồn kho còn {Product.ProductQuantity}"})
    OrderSchema = OrderSchema(ProductID = ProductID, OrderDate = datetime.today().strftime("%H:%M ,%d-%m-%Y"), Status=0, ProductQuantity=ProductQuantity)
    Product.ProductQuantity -= ProductQuantity
    db.add(OrderSchema)
    db.commit()
    db.refresh(OrderSchema)
    return {
        "data:" "Tạo đơn hàng thành công!"
    }

#Sửa thông tin đơn hàng
@router.put("/update_order",dependencies=[Depends(JWTBearer())], summary="Sửa đơn hàng")
async def update_order(
    db: Session = Depends(get_database_session),
    ProductID: str = Form(...),
    ProductQuantity:int=Form(...)
):
    Order_exists = db.query(exists().where(OrderSchema.ProductID == ProductID)).scalar()
    Order = db.query(OrderSchema).get(ProductID)
    if Order_exists:
        print(Order)
        Order.productId = ProductID
        Order.ProductQuantity = ProductQuantity
        db.commit()
        db.refresh(Order)
        return {
            "data": "Thông tin đơn hàng đã được cập nhật!"
        }
    else:
        return JSONResponse(status_code=400, content={"message": "Không có thông tin đơn hàng!"})

#Xóa đơn hàng
@router.delete("/delete_order",dependencies=[Depends(JWTBearer())], summary="Xóa đơn hàng")
async def delete_order(
    db: Session = Depends(get_database_session),
    OrderID: int = Form(...)
):
    Order_exists = db.query(exists().where(OrderSchema.OrderID == OrderID)).scalar()
    if Order_exists:
        Order = db.query(OrderSchema).get(OrderID)
        Order.hasBeenDeleted=1
        db.commit()
        db.refresh(Order)

        return{
         "data": "Xóa sản phẩm thành công!"
        }
    else:
        return JSONResponse(status_code=400, content={"message": "Không tồn tại đơn hàng!"})

#Lấy đơn hàng theo mã đơn hàng
@router.get("/order/{OrderID}", summary="Lấy đơn hàng theo mã")
def get_order_by_OrderID(
    db: Session = Depends(get_database_session),
    OrderID = int
    
):
    Order = (
        db.query(
            OrderSchema.OrderID,
            CustomerSchema.CustomerName,
            CustomerSchema.CustomerAddress,
            CustomerSchema.CustomerPhone,
            CustomerSchema.CustomerEmail,
        )
        .join(CustomerSchema, OrderSchema.CustomerID == CustomerSchema.CustomerID)
    )

    if not Order:
        return JSONResponse(status_code=404, content={"message": "Không có Order nào!"})

    result = {
        "OrderID": Order[0],
        "CustomerName": Order[1],
        "CustomerAddress": Order[2],
        "CustomerPhone":Order[3],
        "CustomerEmail":Order[4]
    }

    return {"data": result}

# #Lấy tất cả đơn hàng
# @router.get("/orders/all", summary="Lấy tất cả đơn hàng")
# def get_all_order(
#     db: Session = Depends(get_database_session),
# ):
#     orders = (
#         db.query(
#             ProductSchema.productName,
#             ProductSchema.serial,
#             ProductSchema.unitPrice*OrdersSchema.quantityProduct,
#             OrdersSchema
#         )
#         .join(ProductSchema, ProductSchema.productId == OrdersSchema.productId)
#         .all()
#     )

#     if not orders:
#         return JSONResponse(status_code=404, content={"message": "Không có Order nào!"})

#     result = []
#     for order in orders:
#         result.append(
#             {   
#             "productName":order[0],
#             "serial":order[1],
#             "price":order[2],
#             "orderInfo":order[3]
#             }
#         )
#     return {"data": result}

# #Lấy đơn hàng theo tên khách hàng (chưa xong)
# @router.get("/order/{customerName}", summary="Lấy đơn hàng theo tên khách hàng")
# def get_order_by_customer_name(
#     db: Session = Depends(get_database_session),
#     customerName= str
# ):
#     orders = (
#         db.query(
#             ProductSchema.productName,
#             ProductSchema.serial,
#             ProductSchema.unitPrice*OrdersSchema.quantityProduct,
#             OrdersSchema
#         )
#         .join(ProductSchema, ProductSchema.productId == OrdersSchema.productId)
#         .filter(OrdersSchema.customerName == customerName)
#         .first()
#     )

#     if not orders:
#         return JSONResponse(status_code=404, content={"message": "Không có đơn hàng nào của mã khách hàng này!"})

#     result = {
#         "productName": orders[0],
#         "serial": orders[1],
#         "price": orders[2],
#         "orderInfo":orders[3]
#     }


# # #Lấy tất cả sản phẩm theo hãng và còn hàng (chạy không lọc ra theo hãng)
# # @router.get("/products/all/brand/instock", summary="Lấy sản phẩm theo hãng và còn hàng")
# # def get_all_products_with_category(
# #     brand: str = Query(None, description="Filter products by brand"),
# #     db: Session = Depends(get_database_session),
# # ):
# #     query = (
# #         db.query(ProductSchema)
# #         .filter(ProductSchema.quantity > 0, ProductSchema.hasBeenDeleted == 0)
# #     )

# #     if brand:
# #         query = query.filter(ProductSchema.brand == brand)

# #     products = query.all()
# #     result = []
# #     for product in products:
# #         result.append(
# #             {   
# #               product
# #             }
# #         )
# #     return {"data": result}

# # #Lấy tất cả sản phẩm theo loại
# # @router.get("/products/all/category", summary="Lấy sản phẩm theo loại")
# # def get_all_products_with_category(
# #     categoryId: str = Query(None, description="Lọc sản phẩm theo loại"),
# #     db: Session = Depends(get_database_session),
# # ):
# #     query = (
# #         db.query(ProductSchema)
# #     )

# #     if categoryId:
# #         query = query.filter(ProductSchema.categoryId == categoryId)

# #     products = query.all()
# #     result = []
# #     for product in products:
# #         result.append(
# #             {   
# #               product
# #             }
# #         )
# #     return {"data": result}

# # #Lấy tất cả sản phẩm thuộc loại được chọn và còn hàng
# # @router.get("/products/all/category/instock", summary="Lấy sản phẩm theo loại và còn hàng")
# # def get_all_products_with_category(
# #     categoryId: str = Query(None, description="Lọc sản phẩm theo loại và còn hàng"),
# #     db: Session = Depends(get_database_session),
# # ):
# #     query = (
# #         db.query(ProductSchema)
# #         .filter(ProductSchema.quantity > 0, ProductSchema.hasBeenDeleted == 0)
# #     )

# #     if categoryId:
# #         query = query.filter(ProductSchema.categoryId == categoryId)

# #     products = query.all()
# #     result = []
# #     for product in products:
# #         result.append(
# #             {   
# #               product
# #             }
# #         )
# #     return {"data": result}
