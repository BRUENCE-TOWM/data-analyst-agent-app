import sys
import os
import re
import time
import tempfile
import shutil
from openai import OpenAI  # 使用OpenAI客户端
from fastapi import APIRouter, Body, UploadFile, File, Form
from pydantic import BaseModel, Field
from services.db_service import DBService
from utils.logger import get_logger

# 通义千问API配置（兼容OpenAI接口）
THIRD_PARTY_API_KEY = "sk-cc7bad738ed94cd786890583b6f7b495"  # 已配置的千问API密钥
BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"

# 初始化OpenAI客户端（与用户提供的示例一致）
client = OpenAI(
    api_key=THIRD_PARTY_API_KEY,
    base_url=BASE_URL,
)

# 初始化
logger = get_logger(__name__)
router = APIRouter(prefix="/api/code", tags=["代码生成接口"])
db = DBService()

# 数据模型
class CodeGenerateRequest(BaseModel):
    user_id: int = Field(gt=0, description="用户ID")
    requirement: str = Field(min_length=1, description="数据分析需求")
    model_name: str = Field(default="qwen-turbo", description="通义千问模型名称")

class CodeGenerateResponse(BaseModel):
    code: int
    msg: str
    data: dict

# 核心：解析纯Python代码
def parse_pure_code(full_content: str) -> str:
    """从AI返回内容中提取```python包裹的纯代码"""
    match = re.search(r'```python([\s\S]*?)```', full_content)
    if match:
        pure_code = match.group(1).strip()
        # 清理多余注释（可选）
        pure_code = re.sub(r'#.*?(?=\n)', '', pure_code)
        return pure_code
    return ""

# 调用第三方API生成代码（使用OpenAI客户端）
def call_ai_generate_code(requirement: str, model_name: str = "qwen-turbo", file_info: str = "") -> str:
    """
    调用通义千问API生成代码
    :param requirement: 数据分析需求
    :param model_name: 通义千问模型名称（默认qwen-turbo）
    :param file_info: 文件信息，包含文件名和格式
    """
    # 提示词（强化数据分析+纯代码输出）
    file_context = f"并且已上传数据文件：{file_info}。代码中请使用该文件名进行数据读取，不要修改文件名。" if file_info else ""
    
    prompt = f"""
    你是数据分析师智能体，仅生成纯Python代码（无需文字说明），代码需满足：
    1. 基于Pandas/Numpy/Matplotlib等数据分析库；
    2. 严格匹配需求：{requirement}{file_context}；
    3. 代码可直接执行，无语法错误；
    4. 输出格式：仅```python包裹代码，无其他文字。
    """
    
    try:
        # 使用OpenAI客户端调用通义千问API（兼容模式）
        completion = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.1
        )
        
        # 获取AI响应内容
        full_content = completion.choices[0].message.content.strip()
        logger.info(f"AI返回内容：{full_content[:100]}...")  # 只记录前100个字符
        return full_content
        
    except Exception as e:
        logger.error(f"AI调用异常：{str(e)}", exc_info=True)
        return ""

# 生成代码接口
@router.post("/generate", response_model=CodeGenerateResponse)
async def generate_code(request: CodeGenerateRequest = Body(...)):
    try:
        logger.info(f"生成代码请求：user_id={request.user_id}, requirement={request.requirement}, model_name={request.model_name}")
        
        # 1. 调用通义千问API生成代码
        full_content = call_ai_generate_code(request.requirement, request.model_name)
        if not full_content:
            return CodeGenerateResponse(
                code=500,
                msg="AI生成代码失败",
                data={}
            )
        
        # 2. 解析纯代码
        pure_code = parse_pure_code(full_content)
        if not pure_code:
            return CodeGenerateResponse(
                code=400,
                msg="未生成有效Python代码",
                data={"full_content": full_content}
            )
        
        # 3. 存入数据库
        task = db.create_task(
            user_id=request.user_id,
            requirement=request.requirement,
            priority="normal"
        )
        
        # 更新任务代码
        db.update_task_code(task.id, pure_code, status="success")
        
        # 4. 返回响应
        return CodeGenerateResponse(
            code=200,
            msg="代码生成成功",
            data={
                "task_id": task.id,
                "generated_code": pure_code,
                "full_content": full_content
            }
        )
    except Exception as e:
        logger.error(f"生成代码异常：{str(e)}", exc_info=True)
        return CodeGenerateResponse(
            code=500,
            msg=f"生成失败：{str(e)}",
            data={}
        )

# 带文件的生成代码接口
@router.post("/generate_with_file", response_model=CodeGenerateResponse)
async def generate_code_with_file(
    user_id: int = Form(..., description="用户ID"),
    requirement: str = Form(..., description="数据分析需求"),
    model_name: str = Form(default="qwen-turbo", description="通义千问模型名称"),
    file: UploadFile = File(None, description="上传的数据文件")
):
    try:
        logger.info(f"带文件生成代码请求：user_id={user_id}, requirement={requirement}, model_name={model_name}, filename={file.filename if file else '无'}")
        
        # 处理上传文件
        file_path = None
        file_info = ""
        temp_dir = None
        
        if file:
            # 创建临时目录保存上传文件
            temp_dir = tempfile.mkdtemp()
            file_path = os.path.join(temp_dir, file.filename)
            
            # 保存文件
            with open(file_path, "wb") as f:
                content = await file.read()
                f.write(content)
            
            file_info = f"{file.filename}（格式：{file.content_type}）"
        
        try:
            # 1. 调用通义千问API生成代码
            full_content = call_ai_generate_code(requirement, model_name, file_info)
            if not full_content:
                return CodeGenerateResponse(
                    code=500,
                    msg="AI生成代码失败",
                    data={}
                )
            
            # 2. 解析纯代码
            pure_code = parse_pure_code(full_content)
            if not pure_code:
                return CodeGenerateResponse(
                    code=400,
                    msg="未生成有效Python代码",
                    data={"full_content": full_content}
                )
            
            # 3. 存入数据库
            task = db.create_task(
                user_id=user_id,
                requirement=requirement,
                priority="normal"
            )
            
            # 更新任务代码
            db.update_task_code(task.id, pure_code, status="success")
            
            # 4. 返回响应
            return CodeGenerateResponse(
                code=200,
                msg="代码生成成功",
                data={
                    "task_id": task.id,
                    "generated_code": pure_code,
                    "full_content": full_content
                }
            )
        finally:
            # 清理临时文件
            if temp_dir and os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
                
    except Exception as e:
        logger.error(f"带文件生成代码异常：{str(e)}", exc_info=True)
        return CodeGenerateResponse(
            code=500,
            msg=f"生成失败：{str(e)}",
            data={}
        )

# 测试网络连接接口
class NetworkTestRequest(BaseModel):
    test_url: str = Field(default="https://www.baidu.com", description="测试网络连接的URL")

class NetworkTestResponse(BaseModel):
    code: int
    msg: str
    data: dict

@router.post("/test_network", response_model=NetworkTestResponse)
async def test_network_connection(request: NetworkTestRequest = Body(...)):
    """测试大模型网络连接功能"""
    try:
        logger.info(f"测试网络连接请求：url={request.test_url}")
        
        # 生成测试代码
        test_code = f"""
import requests
import json

try:
    # 测试网络连接
    response = requests.get('{request.test_url}', timeout=5)
    print(f"网络连接成功！")
    print(f"状态码：{response.status_code}")
    print(f"响应内容长度：{len(response.text)} 字符")
    
    # 保存测试结果到文件
    result = {{
        'status': 'success',
        'url': '{request.test_url}',
        'status_code': response.status_code,
        'content_length': len(response.text)
    }}
    
    import pandas as pd
    df = pd.DataFrame([result])
    df.to_csv('output_data_network_test.csv', index=False)
    print("测试结果已保存到 output_data_network_test.csv")
    
except Exception as e:
    print(f"网络连接失败：{{str(e)}}")
    
    # 保存失败结果
    result = {{
        'status': 'failed',
        'url': '{request.test_url}',
        'error': str(e)
    }}
    
    import pandas as pd
    df = pd.DataFrame([result])
    df.to_csv('output_data_network_test.csv', index=False)
"""
        
        # 执行测试代码
        import subprocess
        import sys
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
            f.write(test_code)
            temp_file_path = f.name
        
        try:
            result = subprocess.run(
                [sys.executable, temp_file_path],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            success = result.returncode == 0
            output = result.stdout + ("\n错误：" + result.stderr if result.stderr else "")
            
            return NetworkTestResponse(
                code=200 if success else 500,
                msg="网络测试完成" if success else "网络测试失败",
                data={
                    "success": success,
                    "output": output,
                    "test_url": request.test_url
                }
            )
        finally:
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
    except Exception as e:
        logger.error(f"网络测试异常：{str(e)}", exc_info=True)
        return NetworkTestResponse(
            code=500,
            msg=f"网络测试异常：{str(e)}",
            data={
                "success": False,
                "output": str(e)
            }
        )