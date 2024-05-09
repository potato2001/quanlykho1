from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional,List


class ProductSchema(BaseModel):
    ProductID :str
    ProductName :str
    ProductCategory :str
    ProductBrand :str
    ProductSerial :str
    ProductDescription: Optional[str] = None  
    UnitPrice :int
    Status:str
    HasBeenDeleted:str
    Category_CategoryID:int
    Provider_ProviderID:int

class CategorySchema(BaseModel):
    CategoryName :Optional[str] = None  
    HasBeenDeleted:Optional[str] = None 

class CategoryUpdateSchema(BaseModel):
    CategoryID: int
    CategoryName: str
    HasBeenDeleted: str

class CustomerSchema(BaseModel):
    # CustomerID :int
    CustomerName: str
    CustomerAddress: str
    CustomerPhone: str
    CustomerEmail: str

class InvoiceSchema(BaseModel):
    InvoiceID :int
    UserID :int
    TotalCost: int
    # OrderDetail_OrderDetailID:int

class ProviderSchema(BaseModel):
    # ProviderID: str
    ProviderName: str
    ProviderAddress: str
    ProviderPhone: str
    ProviderEmail: str
    HasBeenDeleted: str

class InventorySchema(BaseModel):
    InventoryID: int
    QuantityAvailable: int
    Product_ProductID: int
    Invoice_InvoiceID: int  

class MultipleCategoriesSchema(BaseModel):
    categories: List[CategorySchema]

class OrderDetailSchema(BaseModel):
    OrderDetailID: int
    OrderQuantity: int
    ReceivedDate: str
    Status: int
    Oder_OderID: int
    Product_ProductID: str
    Customer_CustomerID: int