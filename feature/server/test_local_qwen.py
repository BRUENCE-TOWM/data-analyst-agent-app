import sys
sys.path.append('.')

from app.services.llm_service import generate_zh_analysis_code

# ====================== 批量测试用例 ======================
TEST_CASES = [
    "计算1到100的累加和",
    "统计字典{'A班':85, 'B班':92, 'C班':78}中各班平均分，找出最高分班级",
    "生成一个长度为10的随机数列表（1-100），计算最大值、最小值和平均值",
    "筛选出列表[1,2,3,4,5,6,7,8,9,10]中的偶数并排序",
    "计算列表[12,45,78,9,23,56,89,34,77,8]的标准差和方差"
]

# ====================== 执行测试 ======================
if __name__ == "__main__":
    print("===== 千问模型本地部署批量测试 =====\\n")
    pass_count = 0
    total_count = len(TEST_CASES)
    
    for idx, req in enumerate(TEST_CASES):
        print(f"=== 测试用例 {idx+1}/{total_count} ===")
        print(f"需求：{req}")
        
        # 生成代码
        code = generate_zh_analysis_code(req)
        print(f"生成代码：\\n{code}")
        
        # 执行代码
        print("执行结果：")
        try:
            exec(code)
            pass_count += 1
            print("✅ 测试通过\\n")
        except Exception as e:
            print(f"❌ 测试失败：{str(e)}\\n")
    
    # 测试总结
    print(f"===== 测试完成 ======")