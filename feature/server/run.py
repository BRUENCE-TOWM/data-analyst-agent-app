from flask import Flask, request, jsonify
from app.services.llm_service import generate_zh_analysis_code
import sys
import io
import os

# 创建Flask应用
app = Flask(__name__)

# ====================== 跨域配置（适配Flutter前端） ======================
@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'POST, GET, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    return response

# ====================== 核心API接口 ======================
@app.route('/api/v1/analysis/generate', methods=['POST'])
def generate_code_api():
    """
    接收中文分析需求，生成并执行Python代码
    请求示例：
    {
        "requirement": "计算列表[10,20,30]的平均值"
    }
    """
    try:
        # 解析请求参数
        request_data = request.get_json()
        if not request_data or 'requirement' not in request_data:
            return jsonify({
                "code": 400,
                "msg": "参数错误：缺少分析需求",
                "data": None
            })
        
        requirement = request_data['requirement'].strip()
        if not requirement:
            return jsonify({
                "code": 400,
                "msg": "分析需求不能为空",
                "data": None
            })
        
        # 生成代码
        code = generate_zh_analysis_code(requirement)
        
        # 执行代码并捕获输出
        execution_result = {
            "success": True,
            "output": "",
            "error": ""
        }
        try:
            # 重定向标准输出
            old_stdout = sys.stdout
            output_buffer = io.StringIO()
            sys.stdout = output_buffer
            
            # 安全执行代码
            exec(code)
            
            # 恢复标准输出
            sys.stdout = old_stdout
            execution_result["output"] = output_buffer.getvalue().strip()
        except Exception as e:
            sys.stdout = old_stdout
            execution_result["success"] = False
            execution_result["error"] = str(e)
        
        # 构造返回结果
        return jsonify({
            "code": 200,
            "msg": "代码生成成功",
            "data": {
                "requirement": requirement,
                "code": code,
                "execution": execution_result
            }
        })
    
    except Exception as e:
        return jsonify({
            "code": 500,
            "msg": f"服务器内部错误：{str(e)}",
            "data": None
        })

# ====================== 启动服务 ======================
if __name__ == "__main__":
    # 创建临时卸载目录（内存优化）
    if not os.path.exists("./temp_offload"):
        os.makedirs("./temp_offload")
    
    # 启动Flask服务
    app.run(
        host='0.0.0.0',
        port=5001,
        debug=True,
        threaded=True,  # 多线程支持并发
        use_reloader=False  # 禁用重载，避免模型重复加载
    )