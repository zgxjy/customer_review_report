import logging
import os
from prompts import *

# 日志配置
LOG_CONFIG = {
    "log_file": "logs/3_single_part_data_processor.log",
    "log_level": logging.INFO
}

# Token统计配置
TOKEN_CONFIG = {
    "report_file": "logs/3_single_part_token_usage_report.json"
}

# 设置日志系统
def setup_logger(log_file=None, log_level=logging.INFO):
    """设置日志系统
    
    Args:
        log_file: 日志文件路径
        log_level: 日志级别
        
    Returns:
        logger: 日志记录器
    """
    log_format = '%(asctime)s [%(levelname)s] %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'
    
    # 创建日志器
    logger = logging.getLogger("data_processor")
    logger.setLevel(log_level)
    
    # 清除已有的处理器
    if logger.handlers:
        logger.handlers.clear()
    
    # 添加控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(log_format, date_format))
    logger.addHandler(console_handler)
    
    # 添加文件处理器
    if log_file:
        # 确保日志目录存在
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)
            
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(logging.Formatter(log_format, date_format))
        logger.addHandler(file_handler)
    
    return logger

# 初始化全局日志器
logger = setup_logger(LOG_CONFIG["log_file"], LOG_CONFIG["log_level"])

# 1. 配置管理模块
def get_config():
    """集中管理所有配置"""
    config = {
        # MongoDB配置
        "mongodb": {
            "connection_string": "mongodb://localhost:27017/",
            "database_name": "kinyo_db",
            "collections": {
                "reviews": "kinyo_new_reviews",
                "llm_results": "kinyo_llm_results",
                "data_result": "kinyo_data_result"
            }
        },
        # OpenAI配置
        "openai": {
            "models": {
                "completion": "gpt-3.5-turbo",
                "embedding": "BAAI/bge-base-zh"
            },
            "proxy": {
                "url": "http://127.0.0.1",
                "port": 6465  # 注意：请替换为你自己的端口
            }
        },
        # 当前实验配置
        "experiment": {
            "project_code": "1",
            "solution": "AI自打标：不限定"
        },
        # 评论采样配置
        "sampling": {
            "max_reviews": 30,  # 最大评论采样数量
            "top_topics_count": 5  # 话题排名前几的数量，默认为5
        }
    }
    return config

# 2. 数据库访问模块
class MongoDBClient:
    """MongoDB数据库访问封装"""
    
    def __init__(self, config=None):
        """初始化MongoDB客户端和集合"""
        if config is None:
            config = get_config()
        
        self.config = config
        self.mongo_config = config["mongodb"]
        self.max_reviews = config["sampling"]["max_reviews"]
        
        # 连接MongoDB
        self.client = pymongo.MongoClient(self.mongo_config["connection_string"])
        self.db = self.client[self.mongo_config["database_name"]]
        
        # 获取集合引用
        self.reviews_collection = self.db[self.mongo_config["collections"]["reviews"]]
        self.llm_results_collection = self.db[self.mongo_config["collections"]["llm_results"]]
        self.data_result_collection = self.db[self.mongo_config["collections"]["data_result"]]
    
    def get_total_documents(self, collection_name, query):
        """获取符合条件的文档总数"""
        collection = self._get_collection_by_name(collection_name)
        return len(list(collection.find(query)))
    
    def find_documents(self, collection_name, query, projection=None):
        """查询符合条件的文档"""
        collection = self._get_collection_by_name(collection_name)
        return collection.find(query, projection)
    
    def insert_document(self, collection_name, document):
        """插入单个文档到指定集合"""
        collection = self._get_collection_by_name(collection_name)
        return collection.insert_one(document)
    
    def _get_collection_by_name(self, collection_name):
        """根据集合名称获取集合引用"""
        collection_mapping = {
            "reviews": self.reviews_collection,
            "llm_results": self.llm_results_collection,
            "data_result": self.data_result_collection
        }
        return collection_mapping.get(collection_name)
    
    def get_comments_by_criteria(self, collection_name, criteria_type, criteria_value, criteria_field=None, polarity=None):
        """通用评论检索函数
        
        Args:
            collection_name: 集合名称
            criteria_type: 'user_profile' 或 'topic'
            criteria_value: 检索的值
            criteria_field: 当criteria_type为'user_profile'时的字段名
            polarity: 当criteria_type为'topic'时的极性值
        
        Returns:
            评论列表 (随机最多max_reviews条)
        """
        collection = self._get_collection_by_name(collection_name)
        
        if criteria_type == 'user_profile':
            query = {f"user_profile.{criteria_field}": criteria_value}
            projection = {"comment": 1, "_id": 0}
            all_comments = [doc["comment"] for doc in collection.find(query, projection)]
            
            # 随机采样最多max_reviews条评论
            return self._sample_comments(all_comments)
        
        elif criteria_type == 'topic':
            cursor = collection.find(
                {"product_topic_result": {"$exists": True, "$ne": []}},
                {"comment": 1, "product_topic_result": 1, "_id": 0}
            )
            matched_comments = []
            for doc in cursor:
                for topic_item in doc.get("product_topic_result", []):
                    if (
                        topic_item.get("topic") == criteria_value
                        and topic_item.get("polarity") == polarity
                    ):
                        matched_comments.append(doc["comment"])
                        break  # 一个评论只保留一次
            
            # 随机采样最多max_reviews条评论
            return self._sample_comments(matched_comments)
        
        return []
    
    def _sample_comments(self, comments):
        """从评论列表中随机采样最多max_reviews条评论"""
        if not comments:
            return []
            
        import random
        
        # 如果评论数量超过max_reviews，随机选择max_reviews条
        if len(comments) > self.max_reviews:
            print(f"评论总数: {len(comments)}, 随机采样 {self.max_reviews} 条进行处理")
            return random.sample(comments, self.max_reviews)
        
        return comments

# 3. 数据处理模块
class DataProcessor:
    """处理和分析数据的类"""
    
    def __init__(self, db_client, config=None):
        """初始化数据处理器"""
        self.db_client = db_client
        self.config = config if config else get_config()
        self.experiment = self.config["experiment"]
    
    def profile_stats(self, fields, total_reviews):
        """统计用户画像数据"""
        query = {
            "project_code": self.experiment["project_code"],
            "solution": self.experiment["solution"]
        }
        
        cursor = self.db_client.find_documents("llm_results", query)
        
        # 初始化每个字段的计数器
        field_counters = {field: Counter() for field in fields}
        
        for doc in cursor:
            user_profile = doc.get("user_profile", {})
            for field in fields:
                value = user_profile.get(field, "")
                field_counters[field][value] += 1
        
        # 组织结果
        result = {}
        for field, counter in field_counters.items():
            field_result = []
            for value, count in counter.items():
                if value !="未知" and value != "未指定" and value != "":
                    field_result.append({
                        "value": value,
                        "count": count
                    })
            result[field] = field_result
        
        return result
    
    def topic_polarity_stats(self, total_reviews):
        """统计话题极性数据"""
        query = {
            "project_code": self.experiment["project_code"],
            "solution": self.experiment["solution"],
            "product_topic_result": {"$exists": True, "$ne": []}
        }
        
        cursor = self.db_client.find_documents("llm_results", query)
        stats = {}  # {topic: {"好评": count, "差评": count，"中评": count，"总数": count}}
        
        for doc in cursor:
            for topic_item in doc.get("product_topic_result", []):
                topic = topic_item.get("topic")
                polarity = topic_item.get("polarity")
                if topic and polarity in ("好评", "差评", "中评"):
                    if topic not in stats:
                        stats[topic] = {"好评": 0, "差评": 0, "中评": 0, "总数": 0}
                    stats[topic][polarity] += 1
                    stats[topic]["总数"] += 1
                # 计算话题的好评占比和中差评占比,话题提及率
                if stats[topic]["总数"] > 0:
                    stats[topic]["好评占比"] = stats[topic]["好评"] / stats[topic]["总数"]
                    stats[topic]["中差评占比"] = (stats[topic]["差评"] + stats[topic]["中评"]) / stats[topic]["总数"]
                    stats[topic]["提及率"] = stats[topic]["总数"] / total_reviews

        return stats
    
    def get_total_reviews(self):
        """获取评论总数"""
        query = {
            "project_code": self.experiment["project_code"],
            "solution": self.experiment["solution"]
        }
        return self.db_client.get_total_documents("llm_results", query)

    # todo：加总处理的评论的token_usage

# 4. AI摘要生成模块
class SummaryGenerator:
    """生成文本摘要的类"""
    
    def __init__(self, config=None):
        """初始化摘要生成器"""
        self.config = config if config else get_config()
        
        # 设置代理
        proxy_config = self.config["openai"]["proxy"]
        os.environ['http_proxy'] = f'{proxy_config["url"]}:{proxy_config["port"]}'
        os.environ['https_proxy'] = f'{proxy_config["url"]}:{proxy_config["port"]}'
        
        # 初始化OpenAI客户端
        self.client = OpenAI(api_key=os.getenv('OPEN_AI_KEY'))
        self.model = self.config["openai"]["models"]["completion"]
        
        # 初始化token计数器
        self.token_usage = {
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0,
            "calls_count": 0
        }
    
    def generate_summary(self, reviews, summary_direction, direction_focus):
        """
        根据评论列表和总结方向，调用大模型生成50字以内总结。
        
        Args:
            reviews: 评论文本列表
            summary_direction: 总结方向
            direction_focus: 总结方向焦点
            
        Returns:
            总结内容（字符串），如出错返回None
        """
        if not reviews:
            print(f"警告: 没有找到关于 {direction_focus} 的评论")
            return None
            
        from prompts import summary_prompt
        prompt = summary_prompt(reviews, summary_direction, direction_focus)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一个专业的评论总结专家"},
                    {"role": "user", "content": prompt}
                ],
                stream=False,
            )
            
            # 记录token使用情况
            usage = response.usage
            self.token_usage["prompt_tokens"] += usage.prompt_tokens
            self.token_usage["completion_tokens"] += usage.completion_tokens
            self.token_usage["total_tokens"] += usage.total_tokens
            self.token_usage["calls_count"] += 1
            
            # 打印当前调用的token使用情况
            print(f"本次调用token使用: 提示词={usage.prompt_tokens}, 生成={usage.completion_tokens}, 总计={usage.total_tokens}")
            
            return response.choices[0].message.content
        except Exception as e:
            print(f"调用大模型总结出错: {e}")
            return None
            
    def get_token_usage(self):
        """返回token使用情况统计"""
        return self.token_usage
        
    def generate_user_profile_insight(self, user_profile_data):
        """
        基于用户画像数据生成简短的洞察总结
        
        Args:
            user_profile_data: 用户画像数据
            
        Returns:
            用户画像洞察总结（最多两句话），如出错返回None
        """
        # 提取关键数据
        top_profile = user_profile_data.get("top_profile", {})
        
        prompt = user_profile_insight_prompt(top_profile)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一个专业的电商数据分析师，擅长精简总结"},
                    {"role": "user", "content": prompt}
                ],
                stream=False,
            )
            
            # 记录token使用情况
            usage = response.usage
            self.token_usage["prompt_tokens"] += usage.prompt_tokens
            self.token_usage["completion_tokens"] += usage.completion_tokens
            self.token_usage["total_tokens"] += usage.total_tokens
            self.token_usage["calls_count"] += 1
            
            # 打印当前调用的token使用情况
            print(f"用户画像洞察生成token使用: 提示词={usage.prompt_tokens}, 生成={usage.completion_tokens}, 总计={usage.total_tokens}")
            
            return response.choices[0].message.content
        except Exception as e:
            print(f"调用大模型生成用户画像洞察出错: {e}")
            return None
    
    def generate_quadrant_insight(self, topic_data):
        """
        基于四象限数据生成简短的四象限分析总结
        
        Args:
            topic_data: 话题数据，包含四象限信息
            
        Returns:
            四象限分析总结（最多四句话），如出错返回None
        """
        # 提取关键数据
        topics = topic_data.get("topics", {})
        avg_mention_rate = topic_data.get("total_stats", {}).get("avg_mention_rate", 0)
        avg_satisfaction_rate = topic_data.get("total_stats", {}).get("avg_satisfaction_rate", 0)
        
        # 按象限分类话题
        quadrant_topics = {
            1: [],  # 右上：高提及率，高满意度（优势话题）
            2: [],  # 右下：高提及率，低满意度（需改进话题）
            3: [],  # 左上：低提及率，高满意度（潜力话题）
            4: []   # 左下：低提及率，低满意度（次要话题）
        }
        
        # 过滤出有象限信息的话题
        for topic, stats in topics.items():
            quadrant = stats.get("quadrant")
            if quadrant and 1 <= quadrant <= 4:
                quadrant_topics[quadrant].append({
                    "name": topic,
                    "count": stats.get("总数", 0),
                    "satisfaction": stats.get("好评占比", 0),
                    "mention_rate": stats.get("提及率", 0)
                })
        
        # 对每个象限内的话题按提及数排序
        for quadrant in quadrant_topics:
            quadrant_topics[quadrant] = sorted(
                quadrant_topics[quadrant],
                key=lambda x: x["count"],
                reverse=True
            )
        
        prompt = quadrant_insight_prompt(quadrant_topics, avg_mention_rate, avg_satisfaction_rate)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一个专业的电商数据分析师，擅长精简总结"},
                    {"role": "user", "content": prompt}
                ],
                stream=False,
            )
            
            # 记录token使用情况
            usage = response.usage
            self.token_usage["prompt_tokens"] += usage.prompt_tokens
            self.token_usage["completion_tokens"] += usage.completion_tokens
            self.token_usage["total_tokens"] += usage.total_tokens
            self.token_usage["calls_count"] += 1
            
            # 打印当前调用的token使用情况
            print(f"四象限分析总结生成token使用: 提示词={usage.prompt_tokens}, 生成={usage.completion_tokens}, 总计={usage.total_tokens}")
            
            return response.choices[0].message.content
        except Exception as e:
            print(f"调用大模型生成四象限分析总结出错: {e}")
            return None
            
    def generate_topic_insight(self, topic_data):
        """
        基于话题数据生成简短的洞察总结
        
        Args:
            topic_data: 话题数据
            
        Returns:
            话题洞察总结（最多两句话），如出错返回None
        """
        # 提取关键数据
        topics_stats = topic_data.get("total_stats", {})
        topics = topic_data.get("topics", {})
        
        # 按总提及数排序话题，选取前5个
        sorted_topics = sorted(
            [(topic, data.get("总数", 0)) for topic, data in topics.items()],
            key=lambda x: x[1],
            reverse=True
        )[:5]
        print("sorted_topics:", sorted_topics)
        print("topics_stats:", topics_stats)


        prompt = topic_insight_prompt(topics_stats=topics_stats, topics=topics)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一个专业的电商数据分析师，擅长精简总结"},
                    {"role": "user", "content": prompt}
                ],
                stream=False,
            )
            
            # 记录token使用情况
            usage = response.usage
            self.token_usage["prompt_tokens"] += usage.prompt_tokens
            self.token_usage["completion_tokens"] += usage.completion_tokens
            self.token_usage["total_tokens"] += usage.total_tokens
            self.token_usage["calls_count"] += 1
            
            # 打印当前调用的token使用情况
            print(f"话题洞察生成token使用: 提示词={usage.prompt_tokens}, 生成={usage.completion_tokens}, 总计={usage.total_tokens}")
            
            return response.choices[0].message.content
        except Exception as e:
            print(f"调用大模型生成话题洞察出错: {e}")
            return None
    
    def generate_overall_insight(self, user_profile_data, topic_data, user_profile_insight, topic_insight, quadrant_insight=None):
        """
        基于用户画像、话题数据及其洞察生成整体洞察总结
        
        Args:
            user_profile_data: 用户画像数据
            topic_data: 话题数据
            user_profile_insight: 用户画像洞察
            topic_insight: 话题洞察
            
        Returns:
            整体洞察总结（字符串），如出错返回None
        """
        # 提取关键数据
        top_profile = user_profile_data.get("top_profile", {})
        topics_stats = topic_data.get("total_stats", {})
        topics = topic_data.get("topics", {})
        
        prompt = overall_insight_prompt(top_profile, topics_stats, topics, user_profile_insight, topic_insight, quadrant_insight)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一个专业的电商数据分析师，擅长从数据中发现商业洞察"},
                    {"role": "user", "content": prompt}
                ],
                stream=False,
            )
            
            # 记录token使用情况
            usage = response.usage
            self.token_usage["prompt_tokens"] += usage.prompt_tokens
            self.token_usage["completion_tokens"] += usage.completion_tokens
            self.token_usage["total_tokens"] += usage.total_tokens
            self.token_usage["calls_count"] += 1
            
            # 打印当前调用的token使用情况
            print(f"整体洞察生成token使用: 提示词={usage.prompt_tokens}, 生成={usage.completion_tokens}, 总计={usage.total_tokens}")
            
            return response.choices[0].message.content
        except Exception as e:
            print(f"调用大模型生成整体洞察出错: {e}")
            return None

# 5. 主控制流程
class DataPipelineManager:
    """管理整个数据处理和生成流程"""
    
    def __init__(self):
        """初始化管理器"""
        self.config = get_config()
        self.db_client = MongoDBClient(self.config)
        self.data_processor = DataProcessor(self.db_client, self.config)
        self.summary_generator = SummaryGenerator(self.config)
        
        # 获取话题排名前几的数量
        self.top_topics_count = self.config["sampling"]["top_topics_count"]
        
        # 用户画像字段
        self.profile_fields = [
            "new_gender", "new_occupation", "new_consumption_scene", 
            "new_consumption_frequency", "new_consumption_thrill_point", 
            "new_consumption_pain_point","new_consumption_itch_point"
        ]
        
        # 字段展示名称映射
        self.fields_dict = {
            'new_consumption_thrill_point': '产品在使用过程中带来的超出预期的即时满足或愉悦体验，请仅用简短短语描述，保留客户口语感觉',
            'new_consumption_pain_point': '产品自身的设计、功能或服务等带来的新的困扰或不便（不是用户原有的痛点），请仅用简短短语描述',
            'new_consumption_itch_point': '产品可优化但非必须改进的方面，优化后可提升体验，请仅用简短短语描述，保留客户口语感觉'
        }
        
        # 话题极性描述
        self.topic_polarity_dict = {
            '好评': '该主题下的好评总结',
            '中差评': '该主题下的中差评总结'
        }
        
        # 初始化结果字典
        self.result_data = {
            "project_code": self.config["experiment"]["project_code"],
            "solution": self.config["experiment"]["solution"],
            "model": self.config["openai"]["models"]["completion"],
            "top_topics_count": self.config["sampling"]["top_topics_count"],
            "process_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "data_id": str(uuid.uuid4()),
            "token_usage": {  # 添加token使用统计
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_tokens": 0,
                "calls_count": 0
            }
        }
    
    def process_user_profiles(self):
        """处理用户画像数据"""
        print("开始处理用户画像数据...")

        # 获取评论总数
        self.result_data["total_review"] = self.data_processor.get_total_reviews()
        
        # 获取用户画像统计
        profile_stats = self.data_processor.profile_stats(self.profile_fields, self.result_data["total_review"])
        
        # 为需要摘要的字段生成摘要
        summary_fields = [
            'new_consumption_thrill_point',
            'new_consumption_pain_point',
            'new_consumption_itch_point'
        ]
        
        for field in summary_fields:
            print("#"*50)
            print(f"现在正在处理：{field}方向下的用户评论总结")
            
            # 对各个字段中的值按数量排序，选取前 N 个
            sorted_focus_points = sorted(
                [(item['value'], item['count']) for item in profile_stats[field]],
                key=lambda x: x[1],
                reverse=True
            )[:self.top_topics_count]
            
            print(f"{field}方向下排名前{self.top_topics_count}的值：{[value for value, _ in sorted_focus_points]}")
            
            for focus_point, count in sorted_focus_points:
                print(f"\n正在处理 {field} 中的 {focus_point}（数量：{count}）")
                
                # 获取评论
                reviews_list = self.db_client.get_comments_by_criteria(
                    "llm_results", 
                    'user_profile', 
                    focus_point, 
                    field
                )
                
                # 生成摘要
                summary = self.summary_generator.generate_summary(
                    reviews=reviews_list,
                    summary_direction=self.fields_dict[field],
                    direction_focus=focus_point
                )
                
                if summary:
                    print("#"*25, focus_point, "#"*25)
                    print(f"{field}方向下的{focus_point}总结：{summary}")
                    
                    # 更新数据
                    for item in profile_stats[field]:
                        if item['value'] == focus_point:
                            item['summary'] = summary
                            break
        
        # 统计top1的用户画像：性别、职业、消费场景、消费频率、消费兴奋点、消费痛点、消费痒点
        top_profile = {}
        for field in self.profile_fields:
            # 按数量排序，选取数量最多的一个
            sorted_items = sorted(
                profile_stats.get(field, []),
                key=lambda x: x.get('count', 0),
                reverse=True
            )
            
            if sorted_items and len(sorted_items) > 0:
                top_profile[field] = {
                    'value': sorted_items[0].get('value', ''),
                    'count': sorted_items[0].get('count', 0)
                }
                # 如果有摘要，也添加到top_profile中
                if 'summary' in sorted_items[0]:
                    top_profile[field]['summary'] = sorted_items[0]['summary']
        
        # 将结果添加到最终数据中
        self.result_data["user_profile"] = {
            "profiles": profile_stats,
            "top_profile": top_profile
        }
        
        print("用户画像数据处理完成")
    
    def process_topics(self):
        """处理话题数据"""
        print("开始处理话题数据...")
        
        # 获取评论总数
        total_reviews = self.data_processor.get_total_reviews()
        
        # 获取话题统计
        topic_stats = self.data_processor.topic_polarity_stats(total_reviews)
        
        # 统计整体话题数据
        total_topic_stats = {
            "topic_count": len(topic_stats),  # 话题总数
            "good_count": 0,  # 好评总数
            "neutral_count": 0,  # 中评总数
            "bad_count": 0,  # 差评总数
            "total_count": 0,  # 总评论数
            "good_rate": 0,  # 好评率
            "neutral_bad_rate": 0  # 中差评率
        }
        
        # 计算各项统计数据
        for topic, stats in topic_stats.items():
            total_topic_stats["good_count"] += stats.get("好评", 0)
            total_topic_stats["neutral_count"] += stats.get("中评", 0)
            total_topic_stats["bad_count"] += stats.get("差评", 0)
            total_topic_stats["total_count"] += stats.get("总数", 0)
        
        # 计算比率
        if total_topic_stats["total_count"] > 0:
            total_topic_stats["good_rate"] = total_topic_stats["good_count"] / total_topic_stats["total_count"]
            total_topic_stats["neutral_bad_rate"] = (total_topic_stats["neutral_count"] + total_topic_stats["bad_count"]) / total_topic_stats["total_count"]
        
        print("开始生成话题摘要...")
        
        # 极性定义
        good_polarity = '好评'
        bad_polarities = ['中评', '差评']
        
        # 对话题按好评数量排序，选取前 N 个
        top_good_topics = sorted(
            [(topic, stats["好评"]) for topic, stats in topic_stats.items()],
            key=lambda x: x[1],
            reverse=True
        )[:self.top_topics_count]
        
        # 对话题按中差评数量排序，选取前 N 个（中评和差评数量之和）
        top_bad_topics = sorted(
            [(topic, stats["中评"] + stats["差评"]) for topic, stats in topic_stats.items()],
            key=lambda x: x[1],
            reverse=True
        )[:self.top_topics_count]
        
        print(f"好评话题数排名前{self.top_topics_count}的话题：{[topic for topic, _ in top_good_topics]}")
        print(f"中差评话题数排名前{self.top_topics_count}的话题：{[topic for topic, _ in top_bad_topics]}")
        
        # 创建新的话题结构，首先复制所有原始话题数据
        topics_data = {}
        for topic, stats in topic_stats.items():
            topics_data[topic] = stats.copy()
        
        # 处理好评排名前 N 的话题
        print(f"\n正在处理好评排名前{self.top_topics_count}的话题...")
        for topic, count in top_good_topics:
            print("#" * 50)
            print(f"现在正在处理 topic：{topic}（好评数：{count}）")
            
            # 确保 topic 存在于结果字典中
            if topic not in topics_data:
                topics_data[topic] = topic_stats.get(topic, {})
            
            # 好评摘要
            reviews_good = self.db_client.get_comments_by_criteria(
                "llm_results", 
                'topic', 
                topic, 
                polarity=good_polarity
            )
            
            summary_good = self.summary_generator.generate_summary(
                reviews=reviews_good,
                summary_direction=self.topic_polarity_dict['好评'],
                direction_focus=f"{topic}"
            )
            
            if summary_good:
                print("#" * 25, f"{topic} - 好评", "#" * 25)
                print(f"{topic}下好评的总结：{summary_good}")
                topics_data[topic]['好评摘要'] = summary_good
        
        # 处理中差评排名前 N 的话题
        print(f"\n正在处理中差评排名前{self.top_topics_count}的话题...")
        for topic, count in top_bad_topics:
            print("#" * 50)
            print(f"现在正在处理 topic：{topic}（中差评数：{count}）")
            
            # 确保 topic 存在于结果字典中
            if topic not in topics_data:
                topics_data[topic] = topic_stats.get(topic, {})
            
            # 中差评合并摘要
            reviews_bad = []
            for polarity in bad_polarities:
                reviews_bad.extend(self.db_client.get_comments_by_criteria(
                    "llm_results", 
                    'topic', 
                    topic, 
                    polarity=polarity
                ))
            
            summary_bad = self.summary_generator.generate_summary(
                reviews=reviews_bad,
                summary_direction=self.topic_polarity_dict['中差评'],
                direction_focus=f"{topic}下的中差评的原因"
            )
            
            if summary_bad:
                print("#" * 25, f"{topic} - 中差评", "#" * 25)
                print(f"{topic}下中差评的总结：{summary_bad}")
                topics_data[topic]['中差评摘要'] = summary_bad
        
        # 计算四象限数据
        print("\n计算四象限数据...")
        # 过滤出总数大于30的话题
        filtered_topics = {
            topic: stats for topic, stats in topics_data.items() 
            if stats.get("总数", 0) > 30
        }
        
        # 计算平均提及率和满意度
        avg_mention_rate = 0
        avg_satisfaction_rate = 0
        total_topics = len(filtered_topics)
        
        if total_topics > 0:
            for stats in filtered_topics.values():
                avg_mention_rate += stats.get("提及率", 0)
                avg_satisfaction_rate += stats.get("好评占比", 0)
            
            avg_mention_rate /= total_topics
            avg_satisfaction_rate /= total_topics
        
        print(f"平均提及率: {avg_mention_rate:.4f}, 平均满意度: {avg_satisfaction_rate:.4f}")
        
        # 确定每个话题的象限
        for topic, stats in filtered_topics.items():
            mention_rate = stats.get("提及率", 0)
            satisfaction_rate = stats.get("好评占比", 0)
            
            # 确定象限: 1=右上(优势), 2=右下(改进), 3=左上(潜力), 4=左下(次要)
            if mention_rate >= avg_mention_rate and satisfaction_rate >= avg_satisfaction_rate:
                quadrant = 1  # 右上：高提及率，高满意度（优势话题）
            elif mention_rate >= avg_mention_rate and satisfaction_rate < avg_satisfaction_rate:
                quadrant = 2  # 右下：高提及率，低满意度（需改进话题）
            elif mention_rate < avg_mention_rate and satisfaction_rate >= avg_satisfaction_rate:
                quadrant = 3  # 左上：低提及率，高满意度（潜力话题）
            else:
                quadrant = 4  # 左下：低提及率，低满意度（次要话题）
                
            # 保存象限信息到话题数据中
            topics_data[topic]["quadrant"] = quadrant
            topics_data[topic]["avg_mention_rate"] = avg_mention_rate
            topics_data[topic]["avg_satisfaction_rate"] = avg_satisfaction_rate
        
        # 添加四象限信息到总体统计中
        total_topic_stats["avg_mention_rate"] = avg_mention_rate
        total_topic_stats["avg_satisfaction_rate"] = avg_satisfaction_rate
        
        # 将结果添加到最终数据中
        self.result_data["product_topics"] = {
            "total_stats": total_topic_stats,
            "topics": topics_data
        }
        
        # 打印话题总数统计
        print(f"\n话题统计信息:")
        print(f"话题总数: {total_topic_stats['topic_count']}")
        print(f"好评总数: {total_topic_stats['good_count']}")
        print(f"中评总数: {total_topic_stats['neutral_count']}")
        print(f"差评总数: {total_topic_stats['bad_count']}")
        print(f"好评率: {total_topic_stats['good_rate']:.2%}")
        print(f"中差评率: {total_topic_stats['neutral_bad_rate']:.2%}")
        
        print("话题数据处理完成")
    
    def calculate_first_stage_token_usage(self):
        """计算第一阶段token使用总量"""
        # 构建查询条件
        query = {
            "project_code": self.config["experiment"]["project_code"],
            "solution": self.config["experiment"]["solution"],
            "token_usage": {"$exists": True}
        }
        
        # 查询所有带有token_usage的文档
        cursor = self.db_client.find_documents("llm_results", query)
        
        # 累计token使用量
        total_tokens = 0
        reviews_count = 0
        
        for doc in cursor:
            if "token_usage" in doc:
                total_tokens += doc["token_usage"]
                reviews_count += 1
        
        print(f"第一阶段共处理了 {reviews_count} 条评论，总计使用 {total_tokens} tokens")
        return total_tokens
    
    def save_results(self):
        """保存处理结果到数据库和文件"""
        print("保存结果到数据库和文件...")
        
        # 更新token使用情况
        token_usage = self.summary_generator.get_token_usage()
        self.result_data["token_usage"] = token_usage
        
        # 计算第一阶段token使用总量
        first_stage_tokens = self.calculate_first_stage_token_usage()
        
        # 将第一阶段token使用量和所有阶段总token使用量添加到结果数据中
        total_all_stages = token_usage['total_tokens'] + first_stage_tokens
        self.result_data["first_stage_tokens"] = first_stage_tokens
        self.result_data["all_stages_total_tokens"] = total_all_stages
        
        # 保存到数据库
        result = self.db_client.insert_document("data_result", self.result_data)
        
        # 确保输出目录存在
        os.makedirs("outputs", exist_ok=True)
        
        # 确保日志目录存在
        os.makedirs("logs", exist_ok=True)
        
        # 创建一个可以处理MongoDB ObjectId的JSON编码器
        class MongoJSONEncoder(json.JSONEncoder):
            def default(self, obj):
                if isinstance(obj, ObjectId):
                    return str(obj)
                return super().default(obj)
        
        # 保存到JSON文件
        output_file = f"outputs/3_分析报告_v{self.result_data['project_code']}_{self.result_data['model']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(self.result_data, f, ensure_ascii=False, indent=2, cls=MongoJSONEncoder)
        
        # 保存token使用情况到报告文件
        now = datetime.now()
        start_time = now - timedelta(seconds=30)  # 估算开始时间，实际应该在运行前记录
        
        # 计算总token使用量（第一阶段+第二阶段）
        total_all_stages = token_usage['total_tokens'] + first_stage_tokens
        
        token_report = {
            "total_tokens": token_usage['total_tokens'],
            "call_count": token_usage['calls_count'],
            "average_tokens_per_call": round(token_usage['total_tokens'] / token_usage['calls_count'] if token_usage['calls_count'] > 0 else 0, 1),
            "tokens_by_model": {
                self.result_data['model']: token_usage['total_tokens']
            },
            "tokens_by_operation": {
                "generate_summary": token_usage['total_tokens']
            },
            "duration_seconds": round((now - start_time).total_seconds(), 6),
            "start_time": start_time.isoformat(),
            "end_time": now.isoformat(),
            "report_time": now.isoformat(),
            "project_code": self.result_data['project_code'],
            "prompt_tokens": token_usage['prompt_tokens'],
            "completion_tokens": token_usage['completion_tokens'],
            "first_stage_tokens": first_stage_tokens,
            "all_stages_total_tokens": total_all_stages,
            "cost_estimate": {
                "input_cost": round(token_usage['prompt_tokens'] * 0.0000015, 6),  # 估算输入成本，按照gpt-3.5-turbo价格
                "output_cost": round(token_usage['completion_tokens'] * 0.000002, 6),  # 估算输出成本
                "total_cost": round(token_usage['prompt_tokens'] * 0.0000015 + token_usage['completion_tokens'] * 0.000002, 6),  # 总成本
                "first_stage_cost": round(first_stage_tokens * 0.000003, 6),  # 估算第一阶段成本
                "all_stages_total_cost": round(token_usage['prompt_tokens'] * 0.0000015 + token_usage['completion_tokens'] * 0.000002 + first_stage_tokens * 0.000003, 6)  # 所有阶段总成本
            }
        }
        
        token_report_file = TOKEN_CONFIG["report_file"]
        with open(token_report_file, "w", encoding="utf-8") as f:
            json.dump(token_report, f, ensure_ascii=False, indent=2)
        
        logger.info(f"结果已保存到文件: {output_file}")
        logger.info(f"Token使用情况已保存到文件: {token_report_file}")
        print(f"数据已保存到数据库和文件: {output_file}")
        print(f"Token使用情况已保存到文件: {token_report_file}")
    
    def process_insights(self):
        """生成用户画像洞察、话题洞察、四象限分析总结和整体洞察总结"""
        print("\n开始生成洞察总结...")
        print("#" * 50)
        
        # 确保用户画像和话题数据已经处理完成
        if "user_profile" not in self.result_data or "product_topics" not in self.result_data:
            print("错误: 用户画像或话题数据尚未处理，无法生成洞察")
            return
        
        # 1. 生成用户画像洞察
        print("\n生成用户画像洞察...")
        user_profile_insight = self.summary_generator.generate_user_profile_insight(
            self.result_data["user_profile"]
        )
        
        if user_profile_insight:
            print("#" * 25, "用户画像洞察", "#" * 25)
            print(user_profile_insight)
            self.result_data["user_profile_insight"] = user_profile_insight
            print("用户画像洞察生成完成")
        else:
            print("用户画像洞察生成失败")
            user_profile_insight = "无法生成用户画像洞察"
            self.result_data["user_profile_insight"] = user_profile_insight
        
        # 2. 生成话题洞察
        print("\n生成话题洞察...")
        topic_insight = self.summary_generator.generate_topic_insight(
            self.result_data["product_topics"]
        )
        
        if topic_insight:
            print("#" * 25, "话题洞察", "#" * 25)
            print(topic_insight)
            self.result_data["topic_insight"] = topic_insight
            print("话题洞察生成完成")
        else:
            print("话题洞察生成失败")
            topic_insight = "无法生成话题洞察"
            self.result_data["topic_insight"] = topic_insight
            
        # 3. 生成四象限分析总结
        print("\n生成四象限分析总结...")
        quadrant_insight = self.summary_generator.generate_quadrant_insight(
            self.result_data["product_topics"]
        )
        
        if quadrant_insight:
            print("#" * 25, "四象限分析总结", "#" * 25)
            print(quadrant_insight)
            self.result_data["quadrant_insight"] = quadrant_insight
            print("四象限分析总结生成完成")
        else:
            print("四象限分析总结生成失败")
            quadrant_insight = "无法生成四象限分析总结"
            self.result_data["quadrant_insight"] = quadrant_insight
        
        # 4. 生成整体洞察
        print("\n生成整体洞察总结...")
        overall_insight = self.summary_generator.generate_overall_insight(
            self.result_data["user_profile"],
            self.result_data["product_topics"],
            self.result_data["user_profile_insight"],
            self.result_data["topic_insight"],
            self.result_data["quadrant_insight"]
        )
        
        if overall_insight:
            print("#" * 25, "整体洞察总结", "#" * 25)
            print(overall_insight)
            self.result_data["overall_insight"] = overall_insight
            print("整体洞察总结生成完成")
        else:
            print("整体洞察总结生成失败")
            self.result_data["overall_insight"] = "无法生成整体洞察总结"
        
        print("\n所有洞察总结生成完成")
    
    def run(self):
        """运行完整的数据处理流程"""
        print("开始数据处理流程...")
        self.process_user_profiles()
        self.process_topics()
        self.process_insights()  # 添加洞察生成步骤
        self.save_results()
        
        # 输出token使用情况统计
        token_usage = self.result_data["token_usage"]
        print("\nToken使用情况统计:")
        print(f"提示词tokens: {token_usage['prompt_tokens']}")
        print(f"生成tokens: {token_usage['completion_tokens']}")
        print(f"总计tokens: {token_usage['total_tokens']}")
        print(f"API调用次数: {token_usage['calls_count']}")
        
        # 计算第一阶段token使用总量
        first_stage_tokens = self.calculate_first_stage_token_usage()
        total_all_stages = token_usage['total_tokens'] + first_stage_tokens
        print(f"\n第一阶段总计tokens: {first_stage_tokens}")
        print(f"所有阶段总计tokens: {total_all_stages}")
        
        print("数据处理流程完成")
        return self.result_data

# 6. 主程序入口
def main():
    """主程序入口"""
    # 设置matplotlib中文显示
    plt.rcParams['font.sans-serif'] = ['SimHei']  # 设置中文字体为黑体
    plt.rcParams['axes.unicode_minus'] = False    # 正常显示负号
    
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='电商点评分析报告生成工具')
    parser.add_argument('--project-code', type=str, default=get_config()["experiment"]["project_code"], 
                        help=f'项目编号，默认: {get_config()["experiment"]["project_code"]}')
    parser.add_argument('--model', type=str, default=get_config()["openai"]["models"]["completion"], 
                        help=f'使用的模型，默认: {get_config()["openai"]["models"]["completion"]}')
    parser.add_argument('--solution', type=str, default=get_config()["experiment"]["solution"], 
                        help=f'解决方案，默认: {get_config()["experiment"]["solution"]}')
    parser.add_argument('--top_n', type=int, default=get_config()["sampling"]["top_topics_count"], 
                        help=f'话题排名前几的数量，默认: {get_config()["sampling"]["top_topics_count"]}')
    args = parser.parse_args()
    
    # 更新配置
    config = get_config()
    config["experiment"]["project_code"] = args.project_code
    config["experiment"]["solution"] = args.solution
    config["openai"]["models"]["completion"] = args.model
    config["sampling"]["top_topics_count"] = args.top_n
    
    logger.info(f"===== 开始执行分析报告生成程序 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} =====")
    logger.info(f"project_code: {args.project_code}")
    logger.info(f"solution: {args.solution}")
    logger.info(f"model: {args.model}")
    logger.info(f"top_n: {args.top_n}")
    
    # 创建并运行数据管道
    pipeline = DataPipelineManager()
    # 手动更新 pipeline 的配置
    pipeline.config = config
    pipeline.db_client.config = config
    pipeline.data_processor.config = config
    pipeline.data_processor.experiment = config["experiment"]
    pipeline.summary_generator.config = config
    pipeline.summary_generator.model = config["openai"]["models"]["completion"]
    # 手动更新 top_topics_count 属性
    pipeline.top_topics_count = config["sampling"]["top_topics_count"]
    logger.info(f"pipeline.top_topics_count: {pipeline.top_topics_count}")
    
    # 更新结果数据中的配置相关字段
    pipeline.result_data["project_code"] = config["experiment"]["project_code"]
    pipeline.result_data["solution"] = config["experiment"]["solution"]
    pipeline.result_data["model"] = config["openai"]["models"]["completion"]
    pipeline.result_data["top_topics_count"] = config["sampling"]["top_topics_count"]
    result = pipeline.run()
    
    # 输出结果摘要
    print("\n数据生成完成，结果摘要:")
    print(f"共处理评论数量: {result['total_review']}")
    print(f"用户画像维度数量: {len(result['user_profile']['profiles'])}")
    print(f"话题数量: {result['product_topics']['total_stats']['topic_count']}")
    print(f"只生成前 {result['top_topics_count']} 个排名的摘要总结")
    return result

# 如果直接运行此脚本，则执行main函数
if __name__ == "__main__":
    # 导入所需的库
    import pymongo
    import pandas as pd
    from collections import Counter
    import json
    import argparse
    from datetime import datetime, timedelta
    import uuid
    import matplotlib.pyplot as plt
    import os
    from openai import OpenAI
    from typing import List, Optional
    from bson import ObjectId
    from prompts import *

    
    main() 