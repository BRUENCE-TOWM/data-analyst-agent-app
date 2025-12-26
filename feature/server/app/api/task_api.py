import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.logger import get_logger
logger = get_logger(__name__)

from fastapi import APIRouter, Body, HTTPException
from pydantic import BaseModel, Field  # 新增：用于参数校验
from services.db_service import DBService

router = APIRouter(prefix="/api/task", tags=["任务查询接口"])

# 数据模型（新增参数校验，避免非法输入）
class TaskListRequest(BaseModel):
    user_id: int = Field(gt=0, description="用户ID，必须为正整数")  # 新增校验
    page: int = Field(ge=1, default=1, description="页码，最小为1")    # 新增校验
    page_size: int = Field(ge=1, le=100, default=10, description="每页条数，1-100")  # 新增校验

class TaskListResponse(BaseModel):
    code: int
    msg: str
    data: dict

# 任务列表查询接口
@router.post("/list", response_model=TaskListResponse)
async def get_task_list(request: TaskListRequest = Body(...)):
    try:
        db = DBService()
        
        # 新增：校验用户是否存在（避免查询不存在的用户）
        user = db.get_user_by_id(request.user_id)
        if not user:
            return TaskListResponse(
                code=404,
                msg=f"用户ID {request.user_id} 不存在",
                data={}
            )
        
        total, tasks = db.get_user_tasks(request.user_id, request.page, request.page_size)
        
        # 格式化返回数据（兼容空数据场景）
        task_list = []
        for task in tasks:
            log = db.get_log_by_task_id(task.id) if task else None
            task_list.append({
                "id": task.id if task else "",  # 修改：与前端一致的字段名
                "requirement": task.requirement if task else "",
                "generated_code": task.generated_code if task else "",  # 修改：与前端一致的字段名
                "created_at": task.create_time.strftime("%Y-%m-%d %H:%M:%S") if task else "",  # 修改：与前端一致的字段名
                "exec_output": log.output if log else "",
                "exec_error": log.error_msg if log else "",
                "exec_duration": round(log.execute_duration, 2) if (log and log.execute_duration) else 0.0  # 优化：保留2位小数
            })
        
        return TaskListResponse(
            code=200,
            msg="查询成功",
            data={
                "total": total,
                "page": request.page,
                "page_size": request.page_size,
                "tasks": task_list,
                "total_pages": (total + request.page_size - 1) // request.page_size  # 新增：总页数，便于前端分页
            }
        )
    except Exception as e:
        # 新增：打印异常栈，便于调试
        import traceback
        traceback.print_exc()
        return TaskListResponse(
            code=500,
            msg=f"查询失败：{str(e)}",
            data={}
        )

# 新增：单任务查询接口（补充能力，便于前端查看单个任务详情）
@router.post("/detail", response_model=TaskListResponse)
async def get_task_detail(request: dict = Body(...)):
    try:
        task_id = request.get("task_id")
        if not task_id or not isinstance(task_id, int):
            return TaskListResponse(code=400, msg="task_id必须为正整数", data={})
        
        db = DBService()
        task = db.get_task_by_id(task_id)
        if not task:
            return TaskListResponse(code=404, msg=f"任务ID {task_id} 不存在", data={})
        
        log = db.get_log_by_task_id(task.id)
        task_detail = {
            "id": task.id,  # 修改：与前端一致的字段名
            "user_id": task.user_id,
            "requirement": task.requirement,
            "generated_code": task.generated_code,  # 修改：与前端一致的字段名
            "status": task.status,
            "created_at": task.create_time.strftime("%Y-%m-%d %H:%M:%S"),  # 修改：与前端一致的字段名
            "exec_output": log.output if log else "",
            "exec_error": log.error_msg if log else "",
            "exec_duration": round(log.execute_duration, 2) if (log and log.execute_duration) else 0.0,
            "exec_time": log.execute_time.strftime("%Y-%m-%d %H:%M:%S") if (log and log.execute_time) else ""
        }
        
        return TaskListResponse(
            code=200,
            msg="查询成功",
            data={"task_detail": task_detail}
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        return TaskListResponse(code=500, msg=f"查询失败：{str(e)}", data={})