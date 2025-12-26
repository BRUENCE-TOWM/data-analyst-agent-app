import sys
import os
import time
import tempfile
import shutil
from fastapi import APIRouter, Body, UploadFile, File, Form, Query
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from services.db_service import DBService
from services.code_executor import execute_python_code
from utils.logger import get_logger

# 初始化日志
logger = get_logger(__name__)

# 创建路由
router = APIRouter(prefix="/api/code", tags=["代码执行接口"])

# 数据模型（带参数校验）
class CodeExecRequest(BaseModel):
    task_id: int = Field(gt=0, description="任务ID，必须为正整数")
    code: str = Field(None, description="可选，直接传递要执行的代码")

class CodeExecResponse(BaseModel):
    code: int
    msg: str
    data: dict

# 执行代码接口
@router.post("/execute", response_model=CodeExecResponse)
async def execute_code(request: CodeExecRequest = Body(...)):
    try:
        # 日志记录请求
        logger.info(f"执行代码请求：task_id={request.task_id}")
        
        # 初始化数据库服务
        db = DBService()
        
        # 获取要执行的代码
        code_to_execute = None
        
        # 如果请求包含code参数，直接使用该代码
        if request.code:
            code_to_execute = request.code
        else:
            # 否则从数据库查询
            task = db.get_task_by_id(request.task_id)
            if not task:
                logger.warning(f"任务不存在：task_id={request.task_id}")
                return CodeExecResponse(code=404, msg="任务不存在", data={})
            if not task.generated_code:
                logger.warning(f"任务无代码：task_id={request.task_id}")
                return CodeExecResponse(code=400, msg="无生成代码可执行", data={})
            code_to_execute = task.generated_code
        
        # 安全执行代码（调用code_executor）
        start = time.time()
        # 修改：传递task_id参数，让图表在执行过程中自动保存到数据库
        exec_result = execute_python_code(code_to_execute, task_id=request.task_id)
        duration = round(time.time() - start, 2)
        logger.info(f"执行代码完成：task_id={request.task_id}, success={exec_result['success']}, duration={duration}s")
        
        # 记录执行日志
        db.create_execution_log(
            task_id=request.task_id,
            output=exec_result["output"],
            error_msg=exec_result["error"],
            execute_duration=duration
        )
        
        # 返回响应
        if exec_result["success"]:
            return CodeExecResponse(
                code=200,
                msg="执行成功",
                data={
                    "task_id": request.task_id,
                    "output": exec_result["output"],
                    "error_msg": exec_result["error"],
                    "duration": duration,
                    "charts": exec_result.get("charts", []),
                    "data_files": exec_result.get("data_files", [])
                }
            )
        else:
            return CodeExecResponse(
                code=500,
                msg=exec_result["error"],
                data={
                    "task_id": request.task_id,
                    "output": "",
                    "error_msg": exec_result["error"],
                    "duration": duration,
                    "charts": exec_result.get("charts", []),
                    "data_files": exec_result.get("data_files", [])
                }
            )
    
    except Exception as e:
        logger.error(f"执行代码异常：{str(e)}", exc_info=True)
        return CodeExecResponse(
            code=500,
            msg=f"执行失败：{str(e)}",
            data={"task_id": request.task_id if "request" in locals() else {}}
        )

# 带文件的执行代码接口
@router.post("/execute_with_file", response_model=CodeExecResponse)
async def execute_code_with_file(
    task_id: int = Form(..., description="任务ID"),
    code: str = Form(..., description="要执行的代码"),
    file: UploadFile = File(None, description="上传的数据文件")
):
    try:
        logger.info(f"带文件执行代码请求：task_id={task_id}, filename={file.filename if file else '无'}")
        
        # 初始化数据库服务
        db = DBService()
        
        # 验证任务存在
        task = db.get_task_by_id(task_id)
        if not task:
            logger.warning(f"任务不存在：task_id={task_id}")
            return CodeExecResponse(code=404, msg="任务不存在", data={})
        
        # 处理上传文件
        file_path = None
        if file:
            # 创建临时目录保存上传文件
            temp_dir = tempfile.mkdtemp()
            file_path = os.path.join(temp_dir, file.filename)
            
            # 保存文件
            with open(file_path, "wb") as f:
                content = await file.read()
                f.write(content)
        
        try:
            # 安全执行代码
            start = time.time()
            # 修改：传递task_id参数，让图表在执行过程中自动保存到数据库
            exec_result = execute_python_code(code, task_id=task_id)
            duration = round(time.time() - start, 2)
            logger.info(f"带文件执行代码完成：task_id={task_id}, success={exec_result['success']}, duration={duration}s")
            
            # 记录执行日志
            db.create_execution_log(
                task_id=task_id,
                output=exec_result["output"],
                error_msg=exec_result["error"],
                execute_duration=duration
            )
            
            # 返回响应
            if exec_result["success"]:
                return CodeExecResponse(
                    code=200,
                    msg="执行成功",
                    data={
                        "task_id": task_id,
                        "output": exec_result["output"],
                        "error_msg": exec_result["error"],
                        "duration": duration,
                        "charts": exec_result.get("charts", []),
                        "data_files": exec_result.get("data_files", [])
                    }
                )
            else:
                return CodeExecResponse(
                    code=500,
                    msg=exec_result["error"],
                    data={
                        "task_id": task_id,
                        "output": "",
                        "error_msg": exec_result["error"],
                        "duration": duration,
                        "charts": exec_result.get("charts", []),
                        "data_files": exec_result.get("data_files", [])
                    }
                )
                
        finally:
            # 清理临时文件
            if file_path and os.path.exists(os.path.dirname(file_path)):
                shutil.rmtree(os.path.dirname(file_path))
                
    except Exception as e:
        logger.error(f"带文件执行代码异常：{str(e)}", exc_info=True)
        return CodeExecResponse(
            code=500,
            msg=f"执行失败：{str(e)}",
            data={"task_id": task_id}
        )

# 图表下载接口
@router.get("/charts/{filename}")
async def get_chart(filename: str, task_id: int = Query(None, description="任务ID")):
    """获取生成的图表文件"""
    # 先从数据库查询图表
    if task_id:
        try:
            db = DBService()
            chart = db.get_chart_by_filename(task_id, filename)
            if chart:
                # 创建临时文件保存图表数据
                with tempfile.NamedTemporaryFile(mode='wb', suffix='.png', delete=False) as f:
                    f.write(chart.chart_data)
                    temp_file_path = f.name
                
                # 返回临时文件
                return FileResponse(temp_file_path, media_type="image/png", filename=filename)
        except Exception as e:
            logger.error(f"从数据库获取图表失败：{str(e)}")
    
    # 如果数据库中没有，检查本地文件系统
    app_chart_path = f"./app/{filename}"
    current_chart_path = f"./{filename}"
    
    if os.path.exists(app_chart_path):
        return FileResponse(app_chart_path, media_type="image/png")
    elif os.path.exists(current_chart_path):
        return FileResponse(current_chart_path, media_type="image/png")
    else:
        return {"code": 404, "msg": "图表文件不存在", "data": None}