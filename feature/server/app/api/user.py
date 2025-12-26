# app/api/user.py
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import APIRouter, Body
from pydantic import BaseModel, Field
from services.db_service import DBService
from utils.logger import get_logger
import hashlib

logger = get_logger(__name__)
router = APIRouter(prefix="/api/user", tags=["用户接口"])

# 密码加密函数
def encrypt_password(password: str) -> str:
    return hashlib.md5(password.encode("utf-8")).hexdigest()  # 生产环境建议用bcrypt

# 数据模型
class UserRegisterRequest(BaseModel):
    username: str = Field(min_length=3, max_length=20, description="用户名")
    password: str = Field(min_length=6, max_length=20, description="密码")
    email: str = Field(default="", description="邮箱")

class UserLoginRequest(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    code: int
    msg: str
    data: dict

# 注册接口
@router.post("/register", response_model=UserResponse)
async def register(request: UserRegisterRequest = Body(...)):
    try:
        db = DBService()
        # 校验用户名是否已存在
        if db.get_user_by_username(request.username):
            return UserResponse(code=400, msg="用户名已存在", data={})
        # 创建用户（密码加密）
        user = db.create_user(
            username=request.username,
            password=encrypt_password(request.password),
            email=request.email
        )
        logger.info(f"用户注册成功：username={request.username}, user_id={user.id}")
        return UserResponse(
            code=200,
            msg="注册成功",
            data={"user_id": user.id, "username": user.username}
        )
    except Exception as e:
        logger.error(f"用户注册失败：{str(e)}")
        return UserResponse(code=500, msg=f"注册失败：{str(e)}", data={})

# 登录接口
@router.post("/login", response_model=UserResponse)
async def login(request: UserLoginRequest = Body(...)):
    try:
        db = DBService()
        user = db.get_user_by_username(request.username)
        if not user:
            return UserResponse(code=404, msg="用户名不存在", data={})
        # 校验密码
        if user.password != encrypt_password(request.password):
            return UserResponse(code=400, msg="密码错误", data={})
        logger.info(f"用户登录成功：user_id={user.id}, username={user.username}")
        return UserResponse(
            code=200,
            msg="登录成功",
            data={"user_id": user.id, "username": user.username}
        )
    except Exception as e:
        logger.error(f"用户登录失败：{str(e)}")
        return UserResponse(code=500, msg=f"登录失败：{str(e)}", data={})