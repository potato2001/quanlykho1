from fastapi import Depends, FastAPI, Request, Form,status,Header,UploadFile,File
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy import exists
import base64
from starlette.responses import RedirectResponse
from sqlalchemy.orm import Session
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.encoders import jsonable_encoder
from datetime import date
from auth.auth_bearer import JWTBearer
from auth.auth_handler import signJWT,decodeJWT
from database import SessionLocal, engine
from Routers import login,user,Category,Product,Customer,Provider,Inventory

import uuid
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
origins = [
    "http://localhost",
    "http://localhost:8080",  # Adjust this based on your frontend URL
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#Người dùng
app.include_router(login.router, tags=['Login Controller'], prefix='')
app.include_router(user.router, tags=['User Controller'], prefix='')

#Sản phẩm
app.include_router(Product.router, tags=['Products Controller'], prefix='')
app.include_router(Category.router, tags=['Category Controller'], prefix='')

#Nhà cung cấp
app.include_router(Provider.router, tags=['Provider Controller'], prefix='')
# app.include_router(courseClass.router, tags=['Class Controller'], prefix='')
# app.include_router(exam.router, tags=['Exam Controller'], prefix='')
# app.include_router(studentExam.router, tags=['Student Exam Controller'], prefix='')
# app.include_router(grade.router, tags=['Grade Controller'], prefix='')
# app.include_router(bill.router, tags=['Bill Controller'], prefix='')

# Kho hàng 
app.include_router(Inventory.router, tags=['Inventory Controller'], prefix='')

# Đơn hàng
# app.include_router(Order.router, tags=['Orders Controller'], prefix='')

#Khách hàng
app.include_router(Customer.router, tags=['Customers Controller'], prefix='') 