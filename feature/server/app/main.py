import sys
import os
# 强制将app目录加入系统路径，解决导入问题
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
# 导入所有接口路由
from api.code_api import router as code_gen_router
from api.code_exec_api import router as code_exec_router
from api.task_api import router as task_router
from api.user import router as user_router

# 初始化FastAPI
app = FastAPI(title="代码生成助手API", version="1.0")

# 添加跨域支持（对接前端必备）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境替换为前端域名（如http://localhost:8080）
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册所有路由
app.include_router(code_gen_router)
app.include_router(code_exec_router)
app.include_router(task_router)
app.include_router(user_router)

# 根路径健康检查
@app.get("/")
async def root():
    return {
        "msg": "代码生成API服务运行中",
        "docs_url": "http://localhost:8000/docs",
        "tips": "请通过/docs接口文档测试所有功能"
    }