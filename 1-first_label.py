"""
电商点评AI分析脚本 - 使用大模型进行自动化标注

本脚本用于分析电商评论数据，主要功能：
1. 使用OpenAI模型提取产品话题及情感倾向
2. 进行用户画像分析和关键短语提取
3. 支持批量并行处理评论数据
"""

import os
import json
import time
import random
import logging
import argparse
import traceback
import pandas as pd
import pymongo
from bson.objectid import ObjectId
from typing import Dict, List, Any, Tuple, Optional, Union
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
from datetime import datetime
from openai import OpenAI
from prompts import *

###################
# 配置部分
###################

# 数据库配置
DB_CONFIG = {
    "mongo_url": "mongodb://localhost:27017/",
    "db_name": "kinyo_db",
    "collections": {
        "reviews": "kinyo_new_reviews",
        "llm_results": "kinyo_llm_results"
    }
}

# 模型配置
MODEL_CONFIG = {
    "gpt_models": ["gpt-4o", "gpt-4o-mini","gpt-3.5-turbo"],
    "embedding_model": "text-embedding-3-small",
    "default_model": "gpt-3.5-turbo"
}

# 代理配置
PROXY_CONFIG = {
    "url": "http://127.0.0.1",
    "port": 6465  # 需替换为实际端口
}

# 日志配置
LOG_CONFIG = {
    "log_file": "logs/1_first_label.log",
    "log_level": logging.INFO
}

# Token统计配置
TOKEN_CONFIG = {
    "report_file": "logs/1_first_label_token_usage_report.json"
}

# 实验配置
EXPERIMENT_CONFIG = {
    "project_code": "1",
    "solution": "AI自动打标"
}

###################
# 日志系统
###################

def setup_logger(log_file: str = None, log_level: int = logging.INFO):
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
    logger = logging.getLogger("ai_analyzer")
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
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(logging.Formatter(log_format, date_format))
        logger.addHandler(file_handler)
    
    return logger

# 初始化全局日志器
logger = setup_logger(LOG_CONFIG["log_file"], LOG_CONFIG["log_level"])

###################
# Token统计
###################

class TokenCounter:
    """Token使用统计类"""
    
    def __init__(self):
        self.total_tokens = 0
        self.call_count = 0
        self.token_by_model = {}
        self.token_by_operation = {}
        self.prompt_tokens = 0
        self.completion_tokens = 0
        self.start_time = datetime.now()
        
    def add_usage(self, tokens: int, model: str, operation: str = "default", prompt_tokens: int = None, completion_tokens: int = None):
        """添加token使用记录
        
        Args:
            tokens: 使用的token数量
            model: 使用的模型名称
            operation: 操作类型
            prompt_tokens: 提示词token数量
            completion_tokens: 生成token数量
        """
        if tokens:
            self.total_tokens += tokens
            self.call_count += 1
            
            # 记录提示词和生成token
            if prompt_tokens is not None:
                self.prompt_tokens += prompt_tokens
            if completion_tokens is not None:
                self.completion_tokens += completion_tokens
            
            # 按模型统计
            if model in self.token_by_model:
                self.token_by_model[model] += tokens
            else:
                self.token_by_model[model] = tokens
            
            # 按操作类型统计
            if operation in self.token_by_operation:
                self.token_by_operation[operation] += tokens
            else:
                self.token_by_operation[operation] = tokens
            
            logger.debug(f"使用 {tokens} tokens ({model}, {operation})")
                
    def get_report(self) -> Dict[str, Any]:
        """获取使用报告"""
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()
        
        # 如果没有明确记录提示词和生成token，则估算
        if self.prompt_tokens == 0 and self.completion_tokens == 0 and self.total_tokens > 0:
            # 假设提示词占70%，生成占30%
            self.prompt_tokens = int(self.total_tokens * 0.7)
            self.completion_tokens = self.total_tokens - self.prompt_tokens
        
        # 计算成本估算（基于gpt-3.5-turbo价格）
        input_cost = round(self.prompt_tokens * 0.0000015, 6)
        output_cost = round(self.completion_tokens * 0.000002, 6)
        total_cost = round(input_cost + output_cost, 6)
        
        return {
            "total_tokens": self.total_tokens,
            "call_count": self.call_count,
            "average_tokens_per_call": round(self.total_tokens / self.call_count if self.call_count > 0 else 0, 1),
            "tokens_by_model": self.token_by_model,
            "tokens_by_operation": self.token_by_operation,
            "duration_seconds": round(duration, 6),
            "start_time": self.start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "report_time": datetime.now().isoformat(),
            "project_code": EXPERIMENT_CONFIG["project_code"],
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "cost_estimate": {
                "input_cost": input_cost,
                "output_cost": output_cost,
                "total_cost": total_cost
            }
        }
        
    def save_report(self, output_file: str = TOKEN_CONFIG["report_file"]):
        """保存报告到文件"""
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(self.get_report(), f, ensure_ascii=False, indent=2)
        logger.info(f"Token使用报告已保存到 {output_file}")

# 初始化全局Token计数器
token_counter = TokenCounter()

###################
# 工具函数
###################

def mongo_doc_to_json_dict(doc):
    """将MongoDB文档转换为可JSON序列化的字典
    
    Args:
        doc: MongoDB文档
        
    Returns:
        转换后的字典
    """
    if doc is None:
        return None
    result = {}
    for key, value in doc.items():
        if isinstance(value, ObjectId):
            result[key] = str(value)
        elif isinstance(value, dict):  # 递归处理嵌套的字典
            result[key] = mongo_doc_to_json_dict(value)
        elif isinstance(value, list):  # 处理列表
            result[key] = [mongo_doc_to_json_dict(item) if isinstance(item, dict) else 
                          str(item) if isinstance(item, ObjectId) else item 
                          for item in value]
        elif isinstance(value, datetime):  # 处理日期时间
            result[key] = value.isoformat()
        else:
            result[key] = value
    return result

def timer_decorator(func):
    """函数执行时间计时装饰器"""
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        logger.debug(f"{func.__name__} 执行时间: {execution_time:.2f}秒")
        return result
    return wrapper

def api_call_with_retry(max_retries=3, initial_delay=1):
    """带重试机制的API调用装饰器"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            retries = 0
            while retries <= max_retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    retries += 1
                    if retries > max_retries:
                        logger.error(f"API调用 {func.__name__} 失败，已达到最大重试次数: {str(e)}")
                        raise
                    
                    # 使用指数退避算法
                    delay = initial_delay * (2 ** (retries - 1)) * (0.5 + random.random())
                    logger.warning(f"API调用 {func.__name__} 失败，{retries}/{max_retries}次重试，将在{delay:.2f}秒后重试: {str(e)}")
                    time.sleep(delay)
            return None
        return wrapper
    return decorator

###################
# 数据库连接管理
###################

class MongoDBManager:
    """MongoDB数据库管理类"""
    
    def __init__(self, mongo_url: str = None, db_name: str = None):
        """初始化MongoDB连接
        
        Args:
            mongo_url: MongoDB连接URL
            db_name: 数据库名称
        """
        self.mongo_url = mongo_url or DB_CONFIG["mongo_url"]
        self.db_name = db_name or DB_CONFIG["db_name"]
        self.client = pymongo.MongoClient(self.mongo_url)
        self.db = self.client[self.db_name]
        logger.info(f"MongoDB连接已初始化: {self.mongo_url} / {self.db_name}")
        
    @timer_decorator
    def get_collection(self, collection_name: str):
        """获取集合对象
        
        Args:
            collection_name: 集合名称
            
        Returns:
            pymongo.collection.Collection: 集合对象
        """
        return self.db[collection_name]
    
    @timer_decorator
    def find_one(self, collection_name: str, query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """查询单个文档
        
        Args:
            collection_name: 集合名称
            query: 查询条件
            
        Returns:
            查询结果文档，如果没有则返回None
        """
        collection = self.get_collection(collection_name)
        return collection.find_one(query)
    
    @timer_decorator
    def find_many(self, collection_name: str, query: Dict[str, Any], 
                 limit: int = 0, projection: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """查询多个文档
        
        Args:
            collection_name: 集合名称
            query: 查询条件
            limit: 限制返回文档数量，默认0表示不限制
            projection: 指定返回的字段，默认None表示返回所有字段
            
        Returns:
            查询结果文档列表
        """
        collection = self.get_collection(collection_name)
        cursor = collection.find(query, projection)
        if limit > 0:
            cursor = cursor.limit(limit)
        return list(cursor)
    
    @timer_decorator
    def get_random_document(self, collection_name: str, size: int = 1) -> List[Dict[str, Any]]:
        """随机获取文档
        
        Args:
            collection_name: 集合名称
            size: 获取文档数量
            
        Returns:
            随机文档列表
        """
        collection = self.get_collection(collection_name)
        pipeline = [{"$sample": {"size": size}}]
        return list(collection.aggregate(pipeline))
    
    @timer_decorator
    def insert_one(self, collection_name: str, document: Dict[str, Any]) -> str:
        """插入单个文档
        
        Args:
            collection_name: 集合名称
            document: 要插入的文档
            
        Returns:
            插入文档的ID
        """
        collection = self.get_collection(collection_name)
        result = collection.insert_one(document)
        return str(result.inserted_id)
    
    @timer_decorator
    def insert_many(self, collection_name: str, documents: List[Dict[str, Any]]) -> List[str]:
        """插入多个文档
        
        Args:
            collection_name: 集合名称
            documents: 要插入的文档列表
            
        Returns:
            插入文档的ID列表
        """
        collection = self.get_collection(collection_name)
        result = collection.insert_many(documents)
        return [str(id) for id in result.inserted_ids]
    
    def close(self):
        """关闭数据库连接"""
        if self.client:
            self.client.close()
            logger.info("MongoDB连接已关闭")


###################
# 模型服务
###################

class ModelService:
    """OpenAI模型服务类"""
    
    def __init__(self, api_key: str = None):
        """初始化模型服务
        
        Args:
            api_key: OpenAI API密钥，默认从环境变量获取
        """
        # 设置代理
        self._setup_proxy()
        
        # 初始化客户端
        self.api_key = api_key or os.getenv('OPEN_AI_KEY')
        self.client = OpenAI(api_key=self.api_key)
        logger.info("OpenAI客户端已初始化")
        
    def _setup_proxy(self):
        """设置HTTP代理"""
        proxy_url = PROXY_CONFIG["url"]
        proxy_port = PROXY_CONFIG["port"]
        os.environ['http_proxy'] = f'{proxy_url}:{proxy_port}'
        os.environ['https_proxy'] = f'{proxy_url}:{proxy_port}'
        logger.debug(f"HTTP代理已设置: {proxy_url}:{proxy_port}")
    
    @api_call_with_retry(max_retries=3, initial_delay=2)
    @timer_decorator
    def analyze_review(self, review: Dict[str, Any], model: str = MODEL_CONFIG["default_model"]) -> Dict[str, Any]:
        """分析评论
        
        Args:
            review: 评论数据
            model: 使用的模型
            
        Returns:
            分析结果
        """
        review_str = review['评论']
        product_name = review['商品名称']
        review_id = review['review_id']
        
        logger.debug(f"开始分析评论 ID: {review_id}")
        
        try:
            # 调用API
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": first_label_system_prompt()},
                    {"role": "user", "content": first_label_user_prompt(review_str, product_name)}
                ],
                stream=False,
                response_format={'type': 'json_object'}
            )

            # 获取token消耗量
            token_usage = response.usage.total_tokens if hasattr(response, 'usage') else 0
            prompt_tokens = response.usage.prompt_tokens if hasattr(response, 'usage') else 0
            completion_tokens = response.usage.completion_tokens if hasattr(response, 'usage') else 0
            
            # 添加到token统计
            token_counter.add_usage(
                tokens=token_usage,
                model=model,
                operation=f"analyze_review",
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens
            )
            
            # 解析内容
            content = response.choices[0].message.content
            parsed_content = json.loads(content)
            
            # 补充元数据
            parsed_content['token_usage'] = token_usage
            parsed_content['review_id'] = review_id
            parsed_content['analysis_time'] = datetime.now().isoformat()
            
            logger.info(f"成功分析评论 ID: {review_id}, 使用模型: {model}, 消耗tokens: {token_usage}")
            return parsed_content
            
        except Exception as e:
            logger.error(f"分析评论失败 ID: {review_id}, 错误: {str(e)}")
            raise

###################
# 分析服务
###################

class AnalyzerService:
    """评论分析服务类"""
    
    def __init__(self, db_manager: MongoDBManager, model_service: ModelService):
        """初始化分析服务
        
        Args:
            db_manager: 数据库管理器
            model_service: 模型服务
        """
        self.db_manager = db_manager
        self.model_service = model_service
        logger.info("评论分析服务已初始化")
    
    @timer_decorator
    def analyze_single_review(self, review_id: str = None, model: str = MODEL_CONFIG["default_model"]) -> Dict[str, Any]:
        """分析单条评论
        
        Args:
            review_id: 评论ID，如果为None则随机选择一条
            model: 使用的模型
            
        Returns:
            分析结果
        """
        if review_id:
            review = self.db_manager.find_one(
                DB_CONFIG["collections"]["reviews"], 
                {"review_id": review_id}
            )
        else:
            # 随机选择一条评论
            random_reviews = self.db_manager.get_random_document(
                DB_CONFIG["collections"]["reviews"], 1
            )
            review = random_reviews[0] if random_reviews else None
            
        if not review:
            logger.warning(f"未找到评论: ID={review_id}")
            return None
            
        logger.info(f"正在分析单条评论: {review.get('review_id')}")
        result = self.model_service.analyze_review(review, model)
        return result
    
    @timer_decorator
    def analyze_reviews_batch(
        self,
        reviews: List[Dict[str, Any]],
        max_workers: int = 4,
        show_progress: bool = True,
        model: str = MODEL_CONFIG["default_model"],
        solution: str = EXPERIMENT_CONFIG["solution"],
        project_code: str = EXPERIMENT_CONFIG["project_code"],
        test_mode: bool = True
    ) -> List[Dict[str, Any]]:
        """批量分析评论
        
        Args:
            reviews: 评论数据列表
            max_workers: 最大线程数
            show_progress: 是否显示进度条
            model: 使用的模型
            solution: 解决方案
            project_code: 项目编号
            test_mode: 测试模式(True不存储结果/False存储结果)
            
        Returns:
            分析结果列表
        """
        logger.info(f"开始批量分析 {len(reviews)} 条评论 (线程数: {max_workers}, 模型: {model})")
        
        # 初始化结果列表
        results = []
        
        # 创建线程池
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # 提交任务
            futures = [executor.submit(self.model_service.analyze_review, review, model) for review in reviews]
            
            # 获取结果
            for future in tqdm(as_completed(futures), total=len(futures), disable=not show_progress):
                try:
                    result = future.result()
                    if result:
                        # 添加元数据
                        result["project_code"] = project_code
                        result["solution"] = solution
                        result["first_label_model"] = model
                        
                        # 添加到结果列表
                        results.append(result)
                        
                        # 存储到数据库
                        if not test_mode:
                            self.db_manager.insert_one(DB_CONFIG["collections"]["llm_results"], result)
                except Exception as e:
                    logger.error(f"处理评论任务失败: {str(e)}")
        
        logger.info(f"批量分析完成，成功处理 {len(results)}/{len(reviews)} 条评论")
        
        # 保存token使用报告
        token_counter.save_report()
        
        return results
    
    def get_processed_review_ids(self, project_code: str, solution: str) -> List[str]:
        """获取已处理的评论ID
        
        Args:
            project_code: 项目编号
            solution: 解决方案
            
        Returns:
            已处理的评论ID列表
        """
        collection_name = DB_CONFIG["collections"]["llm_results"]
        results = self.db_manager.find_many(
            collection_name=collection_name,
            query={"project_code": project_code, "solution": solution},
            projection={"review_id": 1}
        )
        processed_ids = [doc.get("review_id") for doc in results if doc.get("review_id")]
        logger.info(f"已处理评论数量: {len(processed_ids)}")
        return processed_ids
    
    def get_unprocessed_reviews(self, project_code: str, solution: str, limit: int = 0) -> List[Dict[str, Any]]:
        """获取未处理的评论
        
        Args:
            project_code: 项目编号，用于限定数据范围
            solution: 解决方案
            limit: 限制返回数量，0表示不限制
            
        Returns:
            未处理的评论列表
        """
        # 获取已处理的评论ID
        processed_ids = self.get_processed_review_ids(project_code, solution)
        
        # 查询未处理的评论
        collection_name = DB_CONFIG["collections"]["reviews"]
        
        # 构建查询条件：使用project_code作为数据范围筛选条件
        query = {
            "project_code": project_code,  # 添加项目编号作为筛选条件
        }
        
        # 添加未处理条件
        if processed_ids:
            query["review_id"] = {"$nin": processed_ids}
        
        unprocessed = self.db_manager.find_many(
            collection_name=collection_name,
            query=query,
            limit=limit
        )
        
        logger.info(f"获取到 {len(unprocessed)} 条未处理评论，项目编号: {project_code}")
        return unprocessed
    
    def get_analysis_results(self, project_code: str, solution: str, limit: int = 0) -> List[Dict[str, Any]]:
        """获取分析结果
        
        Args:
            project_code: 项目编号
            solution: 解决方案
            limit: 限制返回数量，0表示不限制
            
        Returns:
            分析结果列表
        """
        collection_name = DB_CONFIG["collections"]["llm_results"]
        results = self.db_manager.find_many(
            collection_name=collection_name,
            query={"project_code": project_code, "solution": solution},
            limit=limit
        )
        logger.info(f"获取到 {len(results)} 条分析结果")
        return results
    
    def process_analysis_results(self, results: List[Dict[str, Any]]) -> pd.DataFrame:
        """处理分析结果为DataFrame
        
        Args:
            results: 分析结果列表
            
        Returns:
            处理后的DataFrame
        """
        # 检查结果是否为空
        if not results:
            logger.warning("没有分析结果可处理")
            return pd.DataFrame()
            
        logger.info(f"开始处理 {len(results)} 条分析结果")
        
        # 转换为DataFrame
        df = pd.DataFrame(results)
        
        # 分析产品话题结果
        topic_results = []
        
        for index, row in df.iterrows():
            for topic_result in row.get('product_topic_result', []):
                topic_results.append({
                    '_id': row.get('_id'),
                    'comment': row.get('comment'),
                    'topic': topic_result.get('topic'),
                    'polarity': topic_result.get('polarity'),
                    'confidence': topic_result.get('confidence'),
                    'related_text': topic_result.get('related_text'),
                    'review_id': row.get('review_id')
                })
        
        # 创建包含话题的展开DataFrame
        topic_df = pd.DataFrame(topic_results)
        logger.info(f"处理完成，生成了包含 {len(topic_results)} 条话题记录的DataFrame")
        
        return topic_df

###################
# 主程序
###################

@timer_decorator
def main():
    """主程序入口"""
    # 记录开始时间
    start_time = datetime.now()
    logger.info(f"===== 开始执行AI分析程序 - {start_time.strftime('%Y-%m-%d %H:%M:%S')} =====")
    
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='电商点评AI分析工具')
    parser.add_argument('--model', type=str, default=MODEL_CONFIG["default_model"], 
                        help=f'使用的模型，默认: {MODEL_CONFIG["default_model"]}')
    parser.add_argument('--project-code', type=str, default=EXPERIMENT_CONFIG["project_code"], 
                        help=f'项目编号，默认: {EXPERIMENT_CONFIG["project_code"]}')
    parser.add_argument('--solution', type=str, default=EXPERIMENT_CONFIG["solution"], 
                        help=f'解决方案，默认: {EXPERIMENT_CONFIG["solution"]}')
    parser.add_argument('--limit', type=int, default=10, 
                        help='处理评论数量限制，默认10，0表示不限制')
    parser.add_argument('--workers', type=int, default=4, 
                        help='并行处理的线程数，默认: 4')
    parser.add_argument('--test-mode', action='store_true', 
                        help='测试模式，不存储结果到数据库')
    parser.add_argument('--single', action='store_true',
                        help='单评论模式，只处理一条随机评论')
    args = parser.parse_args()
    
    try:
        # 初始化数据库管理器
        db_manager = MongoDBManager()
        
        # 初始化模型服务
        model_service = ModelService()
        
        # 初始化分析服务
        analyzer_service = AnalyzerService(db_manager, model_service)
        
        if args.single:
            # 单评论模式 - 随机选择一条评论进行分析
            result = analyzer_service.analyze_single_review(model=args.model)
            logger.info(f"单评论分析结果: {json.dumps(mongo_doc_to_json_dict(result), ensure_ascii=False, indent=2)}")
        else:
            # 获取未处理的评论
            unprocessed_reviews = analyzer_service.get_unprocessed_reviews(
                project_code=args.project_code,
                solution=args.solution,
                limit=args.limit
            )
            
            if not unprocessed_reviews:
                logger.warning(f"没有找到未处理的评论，项目编号: {args.project_code}, 解决方案: {args.solution}")
                return
            
            logger.info(f"找到 {len(unprocessed_reviews)} 条未处理的评论")
            
            # 批量处理评论
            results = analyzer_service.analyze_reviews_batch(
                reviews=unprocessed_reviews,
                max_workers=args.workers,
                model=args.model,
                solution=args.solution,
                project_code=args.project_code,
                test_mode=args.test_mode
            )
            
            # 处理结果
            if results:
                # 转换为DataFrame
                topic_df = analyzer_service.process_analysis_results(results)
                
                # 输出统计信息
                logger.info(f"话题分布情况:\n{topic_df['topic'].value_counts()}")
                logger.info(f"情感分布情况:\n{topic_df['polarity'].value_counts()}")
                
                # 确保输出目录存在
                os.makedirs("outputs", exist_ok=True)
                
                # 保存结果到CSV
                output_csv = f"outputs/1_初打标_v{args.project_code}_{args.model}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                topic_df.to_csv(output_csv, index=False, encoding='utf-8-sig')
                logger.info(f"结果已保存到: {output_csv}")
    except Exception as e:
        logger.error(f"程序执行过程中发生错误: {str(e)}")
        logger.error(traceback.format_exc())
    finally:
        # 保存token使用报告
        token_counter.save_report()
        
        # 关闭数据库连接
        if 'db_manager' in locals():
            db_manager.close()
        
        # 记录结束时间
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()
        logger.info(f"===== AI分析程序执行完成 - 耗时: {execution_time:.2f}秒 - {end_time.strftime('%Y-%m-%d %H:%M:%S')} =====\n")


# 当作为脚本直接运行时执行main函数
if __name__ == "__main__":
    main()