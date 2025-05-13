"""
电商点评AI分析系统 - Prompt管理模块

本模块集中管理所有项目中使用的prompt模板，便于统一维护和更新。
"""

###################
# 1-first_label.py 中的prompt
###################

def first_label_system_prompt():
    """准备系统提示词 - 用于第一阶段标注"""
    system_prompt = """# 任务目标：
精确分析消费者评论并提取结构化信息，具体包括：

1. **产品话题细粒度分类**：
   - 识别评论中涉及的具体产品特性/功能点
   - 将每个话题精确匹配到预定义的细分类别（不创建新类别）
   - 提取每个话题的相关文本片段（不超过原文20%长度）
   - 为每个匹配提供置信度评分（0.0-1.0）
   - 避免过于宽泛的分类，专注于特定产品属性而非一般性描述

2. **精确情感分析**：
   - 对每个识别的话题进行独立情感判定
   - 根据文本强度和明确性区分"好评"(明显正面)/"差评"(明显负面)/"中评"(中性或模糊)
   - 考虑上下文和语气，而非仅依靠情感词汇

3. **关键词提取**：
   - 识别评论中最具信息量和区分度的产品特性词/短语
   - 每条评论提取3-5个关键词/短语，保持简洁性
   - 优先考虑产品特定词汇而非一般性描述

4. **用户画像分析**：
   - 仅基于评论中明确提及的信息进行用户特征推断
   - 不进行过度推测，无明确信息时保留字段为空

# 输出要求：
- 以json格式输出，包含以下字段：
 1. comment: 原始的评论文本（数据类型：字符串）。
 2. product_topic_result: 由匹配的评论片段、话题分类和情感倾向组成的列表，每个元素包含以下四个字段：
  - topic：分类话题（数据类型：字符串，来源于预定义的分类列表，不可改变）。
  - polarity：情感分析的结果，表示该话题的情感倾向（数据类型：字符串，值为"好评"、"差评"或"中评"）。
  - confidence：匹配置信度（数据类型：float）。
  - related_text：与话题相关的评论片段（数据类型：字符串）。
 3. keyphrases: 从评论中提取的关键词和短语（数据类型：列表）。
 4. user_profile: 从评论中提取的用户画像特征（数据类型：字典），包含性别、职业、消费频率、消费场景、消费痛点、消费兴奋点、消费痛点,没有判断出来的时候就是空:
  - gender: 用户性别（只有：男|女,数据类型：字符串）。
  - occupation: 用户职业（数据类型：字符串）。
  - consumption_frequency: 用户购买频率（数据类型：字符串）,首次|复购|高频。
  - consumption_scene: 用户具体的消费场景（数据类型：字符串）。
  - consumption_thrill_point: 产品在使用过程中带来的超出预期的即时满足或愉悦体验，请仅用简短短语描述，保留客户口语感觉（如“外观具有装饰性”、“操作流畅”）。
  - consumption_pain_point: 产品自身的设计、功能或服务等带来的新的困扰或不便（不是用户原有的痛点），请仅用简短短语描述，保留客户口语感觉（如“安装复杂”、“配件易丢失”）。
  - consumption_itch_point: 产品可优化但非必须改进的方面，优化后可提升体验，请仅用简短短语描述，保留客户口语感觉（如“支持多色选择”、“增加语音助手”）。
"""
    return system_prompt

def first_label_user_prompt(review_str: str, product_name: str) -> str:
    """准备用户提示词 - 用于第一阶段标注
    
    Args:
        review_str: 评论文本
        product_name: 产品名称
        
    Returns:
        格式化后的用户提示词
    """
    user_prompt = f"""# 客户评论：
- {review_str}
# 产品名称：
- {product_name}
- 请基于任务目标和评论及产品类型提取出任务要求输出
"""
    return user_prompt

###################
# 2-second_data_correction.py/3-process_single_part_report_data.py 中的prompt
###################
def user_profile_classification_prompt(origin_category: str, category_type: str) -> str:
    """
    生成用户画像分类的prompt
    """
    return f"""# 任务
请你根据下列商品的原始分类信息，结合语义含义，归纳总结出一组【简明、具体、互不重复且有明显区别】的典型分类。要求如下：

- 分类名称要用普通人日常生活中常说的词语，而不是笼统或抽象的表达。
- 分类之间要有清晰的区分，不要出现含糊或重复的类别。
- 尽量避免使用行业术语或官方用语，确保每个分类都让大众一看就明白。
- 如果原始分类有相似但细微差别的，可以合并为一个大家都熟悉的类别；如果差异明显，则分别列出。
- 请确保所有原始分类都能被覆盖，不遗漏、不冗余。

# 原始分类信息：
{origin_category}
# 分类场景：
{category_type}
# 输出格式
请用如下JSON格式输出：
{{
  "categories": ["分类1", "分类2", ...]
}}
"""

def product_topic_classification_prompt(origin_category: str, category_type: str) -> str:
    """
    生成商品话题分类的prompt
    """
    return f"""# 任务
请你作为电商领域专家，根据下列商品的原始话题分类信息，结合语义含义，归纳总结出一组【具体、精准、层次分明】的商品话题分类体系。要求如下：

- 分类体系应保留电商评价中的重要细节和维度，如商品质量、外观、功能、性价比、物流、服务等。
- 分类名称要简洁明了，既要专业又要通俗易懂，便于普通消费者理解。
- 分类之间要有明确的界限，避免概念重叠，确保每个话题有其独特的关注点。
- 对于高频出现的话题（如物流、质量、价格等），可以进一步细分为更具体的子类别。
- 如果出现子类别，可以使用"/"分隔，例如："物流配送/速度"。
- 子类别最多分两级，也就是最多可以有两级分类。
- 对于低频但有特色的话题，可以适当保留其独特性，不要过度合并。
- 请确保分类体系能覆盖所有原始话题，并且具有实用性和可扩展性。
- 分类结果使用中文。

# 原始话题分类信息：
{origin_category}

# 分类场景：
电商商品{category_type}评价分析

# 输出格式
请用如下JSON格式输出：
{{
  "categories": ["分类1", "分类2", ...]，所有的分类全部在列表中
}}
"""

###################
#3-process_single_part_report_data.py 中的prompt
###################

def summary_prompt(reviews, summary_direction, direction_focus):
    """
    评论总结prompt
    """
    return (
        f"# 任务\n"
        f"- 请你根据以下所有的评论，生成一个{summary_direction}方向关于{direction_focus}的总结，简单解释在这个方向下总结消费者的理由,只从评论中提取信息并总结，不添加其他信息\n"
        f"# 评论\n"
        f"- {reviews}\n"
        f"# 输出\n"
        f"- 50字以内的总结，只有总结内容，没有其他说明"
    )

def user_profile_insight_prompt(top_profile):
    """
    用户画像洞察总结prompt
    """
    prompt = (
        "# 任务\n"
        "- 你是一个专业的电商数据分析师\n"
        "- 请基于以下用户画像数据，生成一个最多两句话的用户画像洞察总结\n"
        "- 总结应该捕捉用户群体的核心特征和消费偏好\n\n"
        "# 用户画像数据\n"
        "## 主要用户群体特征\n"
    )
    for field, data in top_profile.items():
        field_name = field.replace("new_", "")
        value = data.get("value", "")
        count = data.get("count", 0)
        summary = data.get("summary", "")
        if value and count > 0:
            prompt += f"- {field_name}: {value} (数量: {count})\n"
            if summary:
                prompt += f"  摘要: {summary}\n"
    prompt += "\n# 输出要求\n"
    prompt += "- 请生成一个最多两句话的用户画像洞察总结\n"
    prompt += "- 直接输出洞察内容，不要添加额外的说明\n"
    return prompt

def quadrant_insight_prompt(topics, avg_mention_rate, avg_satisfaction_rate):
    """
    四象限分析总结prompt
    """
    prompt = (
        "# 任务\n"
        "- 你是一个专业的电商数据分析师\n"
        "- 请基于以下四象限分析数据，生成一个最多四句话的四象限分析总结\n"
        "- 总结应该简明扼要地概括四个象限的情况及其商业意义\n\n"
        "# 四象限分析数据\n"
        f"- 平均提及率: {avg_mention_rate:.4f}\n"
        f"- 平均满意度: {avg_satisfaction_rate:.4f}\n\n"
    )
    quadrant_names = {
        1: "右上象限（优势话题）：高提及率，高满意度",
        2: "右下象限（需改进话题）：高提及率，低满意度",
        3: "左上象限（潜力话题）：低提及率，高满意度",
        4: "左下象限（次要话题）：低提及率，低满意度"
    }
    for quadrant, name in quadrant_names.items():
        topics_list = topics.get(quadrant, [])
        prompt += f"## {name}\n"
        if topics_list:
            for i, topic in enumerate(topics_list[:3]):
                prompt += f"- {topic['name']} (提及数: {topic['count']}, "
                prompt += f"提及率: {topic['mention_rate']:.2%}, "
                prompt += f"满意度: {topic['satisfaction']:.2%})\n"
            if len(topics_list) > 3:
                prompt += f"- 还有 {len(topics_list) - 3} 个其他话题\n"
        else:
            prompt += "- 无话题\n"
        prompt += "\n"
    prompt += "# 输出要求\n"
    prompt += "- 请生成一个最多四句话的四象限分析总结\n"
    prompt += "- 总结应包含对四个象限的整体评价和商业建议\n"
    prompt += "- 直接输出总结内容，不要添加额外的说明\n"
    return prompt

def topic_insight_prompt(topics_stats, topics):
    """
    话题洞察总结prompt
    """
    # 添加类型检查，兼容整数和字典类型
    temp_topics = []
    for topic, data in topics.items():
        if isinstance(data, dict):
            # 如果是字典，使用get方法
            count = data.get("总数", 0)
        else:
            # 如果是整数，直接使用
            count = data
        temp_topics.append((topic, count))
    
    # 按数量排序取前5
    sorted_topics = sorted(temp_topics, key=lambda x: x[1], reverse=True)[:5]
    prompt = (
        "# 任务\n"
        "- 你是一个专业的电商数据分析师\n"
        "- 请基于以下产品话题数据，生成一个最多两句话的话题洞察总结\n"
        "- 总结应该捕捉产品评价的核心话题和用户关注点\n\n"
        "# 产品话题数据\n"
        "## 话题总体情况\n"
    )
    prompt += f"- 话题总数: {topics_stats.get('topic_count', 0)}\n"
    prompt += f"- 好评总数: {topics_stats.get('good_count', 0)}\n"
    prompt += f"- 中评总数: {topics_stats.get('neutral_count', 0)}\n"
    prompt += f"- 差评总数: {topics_stats.get('bad_count', 0)}\n"
    prompt += f"- 好评率: {topics_stats.get('good_rate', 0):.2%}\n"
    prompt += f"- 中差评率: {topics_stats.get('neutral_bad_rate', 0):.2%}\n\n"
    prompt += "## 主要话题\n"
    for topic, count in sorted_topics:
        topic_data = topics.get(topic, {})
        good_count = topic_data.get("好评", 0)
        neutral_bad_count = topic_data.get("中评", 0) + topic_data.get("差评", 0)
        good_summary = topic_data.get("好评摘要", "")
        neutral_bad_summary = topic_data.get("中差评摘要", "")
        prompt += f"### 话题: {topic} (总提及数: {count})\n"
        if good_count > 0:
            prompt += f"- 好评数: {good_count} ({good_count/count:.2%})\n"
        if neutral_bad_count > 0:
            prompt += f"- 中差评数: {neutral_bad_count} ({neutral_bad_count/count:.2%})\n"
        if good_summary:
            prompt += f"- 好评摘要: {good_summary}\n"
        if neutral_bad_summary:
            prompt += f"- 中差评摘要: {neutral_bad_summary}\n"
    prompt += "\n# 输出要求\n"
    prompt += "- 请生成一个最多两句话的话题洞察总结\n"
    prompt += "- 直接输出洞察内容，不要添加额外的说明\n"
    return prompt

def overall_insight_prompt(top_profile, topics_stats, topics, user_profile_insight, topic_insight, quadrant_insight=None):
    """
    整体洞察总结prompt
    """
    sorted_topics = sorted(
        [(topic, data.get("总数", 0)) for topic, data in topics.items()],
        key=lambda x: x[1],
        reverse=True
    )[:5]
    prompt = (
        "# 任务\n"
        "- 你是一个高级电商数据分析师和商业战略顾问\n"
        "- 请基于以下用户画像和产品话题数据，生成一份深入的整体洞察总结\n"
        "- 这个洞察应该超越已有的用户画像洞察和话题洞察，提供更深层次的分析\n"
        "- 必须发现用户画像与话题评价之间的关联模式和潜在相关性\n"
        "- 必须提出具有商业执行价值的洞察和具体可行的改进建议\n"
        "- 必须包含产品定位、市场竞争、用户群体分析、产品优势和劣势分析\n"
        "- 必须提出至少一个非常具体的商业机会或产品创新方向\n\n"
        "# 已有的洞察\n"
        f"## 用户画像洞察\n{user_profile_insight}\n\n"
        f"## 话题洞察\n{topic_insight}\n\n"
        f"## 四象限分析总结\n{quadrant_insight if quadrant_insight else '无四象限分析总结'}\n\n"
        "# 用户画像数据\n"
        "## 主要用户群体特征\n"
    )
    for field, data in top_profile.items():
        field_name = field.replace("new_", "")
        value = data.get("value", "")
        count = data.get("count", 0)
        summary = data.get("summary", "")
        if value and count > 0:
            prompt += f"- {field_name}: {value} (数量: {count})\n"
            if summary:
                prompt += f"  摘要: {summary}\n"
    prompt += "\n# 产品话题数据\n"
    prompt += f"## 话题总体情况\n"
    prompt += f"- 话题总数: {topics_stats.get('topic_count', 0)}\n"
    prompt += f"- 好评总数: {topics_stats.get('good_count', 0)}\n"
    prompt += f"- 中评总数: {topics_stats.get('neutral_count', 0)}\n"
    prompt += f"- 差评总数: {topics_stats.get('bad_count', 0)}\n"
    prompt += f"- 好评率: {topics_stats.get('good_rate', 0):.2%}\n"
    prompt += f"- 中差评率: {topics_stats.get('neutral_bad_rate', 0):.2%}\n\n"
    prompt += "## 主要话题\n"
    for topic, count in sorted_topics:
        topic_data = topics.get(topic, {})
        good_count = topic_data.get("好评", 0)
        neutral_bad_count = topic_data.get("中评", 0) + topic_data.get("差评", 0)
        good_summary = topic_data.get("好评摘要", "")
        neutral_bad_summary = topic_data.get("中差评摘要", "")
        prompt += f"### 话题: {topic} (总提及数: {count})\n"
        if good_count > 0:
            prompt += f"- 好评数: {good_count} ({good_count/count:.2%})\n"
        if neutral_bad_count > 0:
            prompt += f"- 中差评数: {neutral_bad_count} ({neutral_bad_count/count:.2%})\n"
        if good_summary:
            prompt += f"- 好评摘要: {good_summary}\n"
        if neutral_bad_summary:
            prompt += f"- 中差评摘要: {neutral_bad_summary}\n"
    prompt += "\n# 分析框架\n"
    prompt += "1. 市场定位分析: 基于用户画像和评价数据，分析产品在市场中的定位\n"
    prompt += "2. 用户需求与产品匹配分析: 用户群体特征与产品评价之间的关联模式\n"
    prompt += "3. 产品优势与劣势分析: 基于话题数据的好评和中差评分析\n"
    prompt += "4. 竞争对比分析: 与竞争产品的比较和差异化优势\n"
    prompt += "5. 商业机会与创新方向: 基于数据发现的商业机会和产品创新方向\n"
    prompt += "\n# 输出要求\n"
    prompt += "- 请生成一份300-400字的深度整体洞察总结\n"
    prompt += "- 必须超越简单的用户画像和话题摘要，提供更深层次的分析\n"
    prompt += "- 必须包含具体的商业洞察和可执行的改进建议\n"
    prompt += "- 必须提出至少一个创新的产品方向或市场机会\n"
    prompt += "- 直接输出洞察内容，不要添加额外的说明\n"
    return prompt