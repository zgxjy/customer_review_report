"""
测试topics结构的脚本
"""
import json
import sys
from pprint import pprint

def test_topic_insight_prompt_fix(topics):
    """测试修复后的代码逻辑"""
    print("\n测试修复后的代码:")
    
    # 修复方案：检查data类型并适当处理
    sorted_topics = []
    for topic, data in topics.items():
        if isinstance(data, dict):
            # 如果是字典，使用get方法
            count = data.get("总数", 0)
        else:
            # 如果是整数，直接使用
            count = data
        sorted_topics.append((topic, count))
    
    # 按数量排序
    sorted_topics = sorted(sorted_topics, key=lambda x: x[1], reverse=True)[:5]
    print("处理后的sorted_topics:")
    pprint(sorted_topics)
    
    return sorted_topics

# 测试用例1：混合类型的topics
test_topics1 = {
    "话题A": {"总数": 10, "好评": 8, "中差评": 2},
    "话题B": 5,
    "话题C": {"总数": 15, "好评": 10, "中差评": 5},
    "话题D": 8
}

# 测试用例2：全部为整数的topics
test_topics2 = {
    "话题A": 10,
    "话题B": 5,
    "话题C": 15,
    "话题D": 8
}

# 测试用例3：全部为字典的topics
test_topics3 = {
    "话题A": {"总数": 10, "好评": 8, "中差评": 2},
    "话题B": {"总数": 5, "好评": 3, "中差评": 2},
    "话题C": {"总数": 15, "好评": 10, "中差评": 5},
    "话题D": {"总数": 8, "好评": 6, "中差评": 2}
}

print("=== 测试用例1：混合类型 ===")
print("原始topics结构:")
pprint(test_topics1)
test_topic_insight_prompt_fix(test_topics1)

print("\n=== 测试用例2：全部为整数 ===")
print("原始topics结构:")
pprint(test_topics2)
test_topic_insight_prompt_fix(test_topics2)

print("\n=== 测试用例3：全部为字典 ===")
print("原始topics结构:")
pprint(test_topics3)
test_topic_insight_prompt_fix(test_topics3)

# 尝试重现错误
print("\n=== 尝试重现错误 ===")
try:
    sorted_topics = sorted(
        [(topic, data.get("总数", 0)) for topic, data in test_topics2.items()],
        key=lambda x: x[1],
        reverse=True
    )[:5]
except AttributeError as e:
    print(f"错误复现成功: {e}")
