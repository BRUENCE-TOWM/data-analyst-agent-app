from flask import Blueprint, request, jsonify
from app.services.llm_service import generate_analysis_code
from app.services.code_executor import execute_python_code
import traceback

analysis_bp = Blueprint('analysis', __name__, url_prefix='/api/v1/data')

# 健康检查接口
@analysis_bp.get('/health')
def health_check():
    return jsonify({
        "code": 200,
        "msg": "后端服务正常",
        "data": {"service": "data-analysis", "status": "running", "port": 5001}
    })

# 核心接口：生成+执行代码
@analysis_bp.post('/analyze')
def analyze_data():
    try:
        # 1. 参数接收与校验
        req_data = request.json
        if not req_data or not req_data.get("requirement"):
            return jsonify({
                "code": 400,
                "msg": "缺少分析需求（requirement）",
                "data": {}
            }), 400
        
        requirement = req_data.get("requirement")
        tool_type = req_data.get("tool_type", "Python")
        user_id = req_data.get("user_id", "test_user_001")
        execute_code = req_data.get("execute_code", True)
        
        # 2. 生成代码
        code = generate_analysis_code(requirement, tool_type)
        
        # 3. 执行代码（仅Python）
        exec_result = None
        if execute_code and tool_type == "Python":
            exec_result = execute_python_code(code)
        
        # 4. 返回结果
        return jsonify({
            "code": 200,
            "msg": "代码生成成功" + ("并执行完成" if exec_result else ""),
            "data": {
                "user_id": user_id,
                "requirement": requirement,
                "tool_type": tool_type,
                "code": code,
                "execution": exec_result if exec_result else {"msg": "未执行代码"}
            }
        })
    
    except FileNotFoundError as e:
        return jsonify({"code": 404, "msg": f"模型文件缺失：{str(e)}", "data": {}}), 404
    except Exception as e:
        error_detail = traceback.format_exc()[:200]
        return jsonify({"code": 500, "msg": f"服务异常：{str(e)}", "data": {"error_detail": error_detail}}), 500