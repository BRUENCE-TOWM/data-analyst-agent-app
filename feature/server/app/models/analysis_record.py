# feature/server/app/services/llm_service.py
import os
import sys
import warnings
warnings.filterwarnings("ignore")

# 1. 添加llm目录到Python路径（解决模型路径问题）
LLM_BASE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "llm")
sys.path.append(LLM_BASE_DIR)

# 2. 模型路径配置
MODEL_PATH = os.path.join(LLM_BASE_DIR, "models")
if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f"模型文件未找到！请先执行download_model.py，路径：{MODEL_PATH}")

# 3. 延迟加载模型（避免启动服务时加载，节省内存）
_tokenizer = None
_model = None

def load_llm_model():
    """单例模式加载模型（首次调用时加载）"""
    global _tokenizer, _model
    if _tokenizer is None or _model is None:
        from transformers import AutoTokenizer, AutoModelForCausalLM
        print("开始加载Phi-3-mini模型...")
        # 加载Tokenizer
        _tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
        # 加载模型（int8量化，CPU运行）
        _model = AutoModelForCausalLM.from_pretrained(
            MODEL_PATH,
            device_map="auto",  # 自动分配设备（CPU/GPU）
            torch_dtype="auto",
            trust_remote_code=True,
            load_in_8bit=True  # 关键：int8量化，降低内存占用
        )
        print("模型加载完成！")
    return _tokenizer, _model

def generate_analysis_code(requirement: str, tool_type: str = "Python") -> str:
    """
    生成数据分析代码
    :param requirement: 用户输入的分析需求（如"统计1-10的平均值"）
    :param tool_type: 生成代码的工具类型（默认Python）
    :return: 可运行的分析代码字符串
    """
    # 1. 加载模型
    tokenizer, model = load_llm_model()
    
    # 2. 构建Prompt（精准引导模型生成代码）
    prompt = f"""
你是专业的数据分析工程师，请严格按照以下要求生成{tool_type}代码：
1. 需求：{requirement}
2. 要求：
   - 仅返回可直接运行的代码，无任何解释、注释以外的文字；
   - 优先使用Python内置库（如math、statistics），避免小众依赖；
   - 代码逻辑完整，包含输入、计算、输出步骤；
   - 输出结果清晰，使用print()打印最终结果。
3. 禁止返回任何多余内容（如"以下是代码"、"解释："等）。
    """.strip()

    # 3. 调用模型生成代码
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    outputs = model.generate(
        **inputs,
        max_new_tokens=500,  # 最大生成500个token
        temperature=0.1,     # 低随机性，保证代码稳定性
        top_p=0.9,
        do_sample=False,     # 确定性生成
        pad_token_id=tokenizer.eos_token_id
    )

    # 4. 提取并清理代码
    raw_code = tokenizer.decode(outputs[0], skip_special_tokens=True)
    # 过滤Prompt部分，仅保留生成的代码
    code = raw_code.replace(prompt, "").strip()
    
    # 5. 代码合法性校验（基础）
    if not code:
        code = f"""
# 未生成有效代码，默认示例（需求：{requirement}）
import statistics
data = [1,2,3,4,5]
print(f"平均值：{{statistics.mean(data)}}")
""".strip()
    
    return code

# 测试函数（本地运行验证）
if __name__ == "__main__":
    # 测试生成代码
    test_requirement = "统计列表[10,20,30,40,50]的平均值和中位数"
    code = generate_analysis_code(test_requirement)
    print("生成的代码：\n", code)