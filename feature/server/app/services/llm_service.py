import sys
import os
import json
# 强制UTF-8编码（避免中文路径报错）
os.environ["PYTHONIOENCODING"] = "utf-8"

# ========== 1. 精准计算所有目录 ==========
# 当前文件路径：feature/server/app/services/llm_service.py
CURRENT_FILE = os.path.abspath(__file__)
# services目录：feature/server/app/services/
SERVICES_DIR = os.path.dirname(CURRENT_FILE)
# app目录：feature/server/app/
APP_DIR = os.path.dirname(SERVICES_DIR)
# server目录：feature/server/
SERVER_DIR = os.path.dirname(APP_DIR)
# feature目录：feature/（llm和server的父目录）
FEATURE_DIR = os.path.dirname(SERVER_DIR)

# 添加核心目录到系统路径
sys.path.extend([FEATURE_DIR, SERVER_DIR, APP_DIR])

from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
import ast

# ========== 2. 正确的模型路径 ==========
# llm/在feature/下，与server/同级
MODEL_DIR = os.path.normpath(os.path.join(FEATURE_DIR, "llm/models/Qwen-1_8B-Chat"))

QWEN_EOS_TOKEN_ID = 151643

# 全局缓存
_tokenizer = None
_model = None

def load_local_qwen_model():
    """加载本地千问模型（兼容4.32.0版本）"""
    global _tokenizer, _model
    if _tokenizer is None or _model is None:
        try:
            # 打印路径（调试用）
            print("="*50)
            print(f"🔍 feature目录：{FEATURE_DIR}")
            print(f"🔍 模型目录：{MODEL_DIR}")
            print("="*50)
            
            # 验证模型目录存在
            if not os.path.exists(MODEL_DIR):
                raise FileNotFoundError(
                    f"模型目录不存在！\n"
                    f"期望路径：{MODEL_DIR}\n"
                    f"请确认llm/文件夹在feature目录下"
                )
            
            # ========== 关键修复：直接加载（4.32.0版本无需手动配置） ==========
            # 加载分词器（强制本地加载）
            _tokenizer = AutoTokenizer.from_pretrained(
                MODEL_DIR,
                trust_remote_code=True,
                local_files_only=True,  # 核心：只加载本地文件
                padding_side="left",
                truncation_side="left",
                use_fast=False
            )
            _tokenizer.eos_token_id = QWEN_EOS_TOKEN_ID
            _tokenizer.pad_token_id = QWEN_EOS_TOKEN_ID

            # 加载模型（兼容千问配置）
            _model = AutoModelForCausalLM.from_pretrained(
                MODEL_DIR,
                trust_remote_code=True,
                device_map="cpu",  # 强制CPU运行
                torch_dtype=torch.float32,
                low_cpu_mem_usage=True,
                load_in_8bit=False,
                local_files_only=True,  # 核心：只加载本地文件
                use_safetensors=True
            ).eval()

            print("✅ 千问模型加载成功！")
        except Exception as e:
            raise Exception(f"模型加载失败：{str(e)}")
    return _tokenizer, _model

def fix_code_indentation(code: str) -> str:
    """修复代码缩进"""
    if not code:
        return ""
    try:
        tree = ast.parse(code)
        indent_level = 0
        indent_step = 4
        fixed_lines = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.For, ast.While, ast.FunctionDef, ast.ClassDef)):
                fixed_lines.append(" " * indent_level * indent_step + ast.unparse(node).split("\n")[0])
                indent_level += 1
            elif isinstance(node, ast.Pass):
                fixed_lines.append(" " * indent_level * indent_step + "pass")
            elif isinstance(node, ast.Expr):
                fixed_lines.append(" " * indent_level * indent_step + ast.unparse(node))
        return "\n".join(fixed_lines)
    except SyntaxError:
        return code

def generate_code_from_requirement(requirement: str) -> str:
    """生成Python代码"""
    try:
        tokenizer, model = load_local_qwen_model()

        # 构建Prompt
        prompt = f"""
生成Python代码实现以下数据分析需求：{requirement}
要求：
1. 严格遵守Python缩进规范（4个空格缩进）；
2. 仅输出可运行的Python代码，无任何解释、注释、markdown标记；
3. 优先使用内置库（math/statistics/random）；
4. 代码包含完整的输入、计算、打印输出步骤。
        """.strip()

        # 编码输入
        inputs = tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=1024,
            padding=False
        )

        # 生成代码
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=512,
                temperature=0.2,
                top_p=0.9,
                do_sample=True,
                eos_token_id=QWEN_EOS_TOKEN_ID,
                pad_token_id=QWEN_EOS_TOKEN_ID
            )

        # 解码并提取代码
        generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
        code = generated_text.replace(prompt, "").strip()
        if code.startswith("```python"):
            code = code.replace("```python", "").replace("```", "").strip()

        # 修复缩进
        return fix_code_indentation(code)
    except Exception as e:
        raise Exception(f"代码生成失败：{str(e)}")

# 测试代码（单独运行验证）
if __name__ == "__main__":
    try:
        tokenizer, model = load_local_qwen_model()
        print("\n📝 测试生成代码：")
        code = generate_code_from_requirement("计算1到100的累加和")
        print(code)
    except Exception as e:
        print(f"\n❌ 测试失败：{e}")