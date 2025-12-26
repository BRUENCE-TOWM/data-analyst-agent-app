import subprocess
import sys
import tempfile
import os
import re

# 导入数据库服务
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.db_service import DBService

def execute_python_code(code: str, file_path: str = None, task_id: int = None) -> dict:
    """
    安全执行Python代码，返回执行结果/错误
    :param code: 待执行的Python代码字符串
    :param file_path: 可选的文件路径，用于支持文件导入
    :param task_id: 可选的任务ID，用于存储图表到数据库
    :return: {"success": bool, "output": str, "error": str, "charts": list, "data_files": list}
    """
    # 1. 危险操作拦截（核心安全控制）
    dangerous_keywords = ["os.system", "subprocess.", "sys.exit", "shutil.", "eval(", "exec("]
    for keyword in dangerous_keywords:
        if keyword in code:
            return {
                "success": False,
                "output": "",
                "error": f"禁止执行危险操作（关键词：{keyword}）",
                "charts": [],
                "data_files": []
            }
    
    # 2. 创建临时目录用于存储生成的图表
    temp_chart_dir = tempfile.mkdtemp()
    
    try:
        # 3. 创建临时文件执行代码
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
            # 在用户代码前添加matplotlib后端设置和图像保存配置
            file_import_code = f"import os\nos.chdir('{os.path.dirname(tempfile.gettempdir())}')\n" if file_path else ""
            
            # 构建增强的代码字符串，修改图表保存路径到临时目录
            enhanced_code = '''
{}
import matplotlib
matplotlib.use('Agg')  # 使用非GUI后端

# 配置matplotlib支持中文
matplotlib.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']  # 中文字体
matplotlib.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import io
import base64

# 基础库导入（已在服务器端预先安装）
import sklearn
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score

# 联网库支持
import requests
import urllib.request

# 设置临时图表保存目录
temp_chart_dir = '{}'
import os
if not os.path.exists(temp_chart_dir):
    os.makedirs(temp_chart_dir)

# 重写plt.savefig函数，将图表保存到临时目录
original_plt_savefig = plt.savefig
def temp_savefig(filename, *args, **kwargs):
    # 如果filename是相对路径，保存到临时目录
    if not os.path.isabs(filename):
        filename = os.path.join(temp_chart_dir, filename)
    return original_plt_savefig(filename, *args, **kwargs)
plt.savefig = temp_savefig

# 重写plt.show()函数，自动保存图表
original_plt_show = plt.show
def auto_save_show(*args, **kwargs):
    import os
    # 生成唯一的图表文件名
    chart_num = 1
    while os.path.exists(os.path.join(temp_chart_dir, 'output_chart_' + str(chart_num) + '.png')):
        chart_num += 1
    # 保存图表到临时目录
    plt.savefig('output_chart_' + str(chart_num) + '.png', dpi=300, bbox_inches='tight')
    print('图表已保存: output_chart_' + str(chart_num) + '.png')
# 替换plt.show()
plt.show = auto_save_show

# 用户代码开始
{}
# 用户代码结束

# 检查是否有未保存的图表
if plt.get_fignums():
    import os  # 确保os模块可用
    chart_num = 1
    while os.path.exists(os.path.join(temp_chart_dir, 'output_chart_' + str(chart_num) + '.png')):
        chart_num += 1
    plt.savefig('output_chart_' + str(chart_num) + '.png', dpi=300, bbox_inches='tight')
    print('图表已保存: output_chart_' + str(chart_num) + '.png')
'''.format(file_import_code, temp_chart_dir.replace('\\', '\\\\'), code)
            
            f.write(enhanced_code)
            temp_file_path = f.name
        
        # 4. 执行代码（设置超时30秒）
        result = subprocess.run(
            [sys.executable, temp_file_path],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        # 5. 处理执行结果
        output = result.stdout
        error = result.stderr
        success = result.returncode == 0
        
        # 6. 解析输出中的图表和数据文件
        charts = []
        data_files = []
        
        # 查找生成的图表文件（在临时目录中）
        for file_name in os.listdir(temp_chart_dir):
            if file_name.endswith('.png'):
                chart_path = os.path.join(temp_chart_dir, file_name)
                
                # 读取图表数据
                with open(chart_path, 'rb') as f:
                    chart_data = f.read()
                
                # 如果提供了任务ID，将图表保存到数据库
                if task_id:
                    try:
                        db = DBService()
                        db.save_chart(task_id, file_name, chart_data)
                        charts.append(file_name)  # 返回文件名列表
                    except Exception as e:
                        error += f"\n保存图表到数据库失败：{str(e)}"
        
        # 处理数据文件（CSV等）
        output_dir = os.path.dirname(temp_file_path)
        for file_name in os.listdir(output_dir):
            if file_name.endswith('.csv'):
                data_file_path = os.path.join(output_dir, file_name)
                if os.path.exists(data_file_path):
                    # 读取CSV内容
                    with open(data_file_path, 'r') as f:
                        data_content = f.read()
                    # 保存到当前工作目录
                    new_data_path = os.path.join(os.getcwd(), file_name)
                    with open(new_data_path, 'w') as f:
                        f.write(data_content)
                    data_files.append(file_name)
                    # 同时保存到app目录
                    app_data_path = os.path.join('./app', file_name)
                    if not os.path.exists('./app'):
                        os.makedirs('./app')
                    with open(app_data_path, 'w') as f:
                        f.write(data_content)
        
        return {
            "success": success,
            "output": output if output else "代码执行成功，无输出",
            "error": error if error else "",
            "charts": charts,
            "data_files": data_files
        }
    except subprocess.TimeoutExpired:
        return {"success": False, "output": "", "error": "代码执行超时（>30秒）", "charts": [], "data_files": []}
    except Exception as e:
        return {"success": False, "output": "", "error": f"执行异常：{str(e)}", "charts": [], "data_files": []}
    finally:
        # 7. 清理临时文件和目录
        if 'temp_file_path' in locals() and os.path.exists(temp_file_path):
            os.unlink(temp_file_path)
        
        # 清理临时图表目录
        if os.path.exists(temp_chart_dir):
            for file_name in os.listdir(temp_chart_dir):
                file_path = os.path.join(temp_chart_dir, file_name)
                try:
                    os.unlink(file_path)
                except:
                    pass
            try:
                os.rmdir(temp_chart_dir)
            except:
                pass
        
        # 清理当前目录下可能残留的旧图表文件（可选）
        for file_name in os.listdir('.'):
            if file_name.startswith('output_chart_') and file_name.endswith('.png'):
                try:
                    os.unlink(file_name)
                except:
                    pass

# 本地测试
if __name__ == "__main__":
    test_code = "print(1+1)"
    print(execute_python_code(test_code))  # 预期：{"success":True, "output":"2", "error":""}