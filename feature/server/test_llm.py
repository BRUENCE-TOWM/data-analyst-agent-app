import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.llm_service import generate_analysis_code

# 覆盖常见分析场景的测试用例
test_cases = [
    "统计列表[10,20,30,40,50]的平均值、中位数和标准差",
    "计算1到100的累加和",
    "筛选出列表[5,8,12,15,20]中大于10的元素并排序",
    "计算字典{'A':85, 'B':92, 'C':78}中值的平均分",
    "生成一个随机数列表（长度10，范围1-100）并计算最大值"
]

def test_code_generation():
    print("===== 开始批量验证代码生成效果 =====\n")
    success_count = 0
    for i, req in enumerate(test_cases):
        print(f"测试用例{i+1}：{req}")
        try:
            code = generate_analysis_code(req)
            print("生成的代码：\n", code)
            # 执行代码验证语法正确性
            exec(code, {}, {})
            print("✅ 验证通过\n")
            success_count += 1
        except Exception as e:
            print(f"❌ 验证失败：{str(e)}\n")
    
    print(f"===== 验证完成：{success_count}/{len(test_cases)} 用例通过 =====")

if __name__ == "__main__":
    test_code_generation()