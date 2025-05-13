#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
电商点评分析工具 - 数据矫正模块

本模块用于对电商点评数据进行分类矫正，主要包括两部分功能：
1. 用户画像数据矫正：对用户性别、职业、消费场景等字段进行标准化处理
2. 商品标签数据矫正：对商品话题分类进行标准化处理

实现思路：
1. 收集所有原始分类短语
2. 使用大语言模型进行自动识别分类，生成标准分类体系
3. 使用向量相似度进行自动化分类映射
"""

import os
import json
import time
import logging
import traceback
import numpy as np
import pandas as pd
import pymongo
from typing import Dict, Any, List, Set, Tuple
from collections import Counter
from datetime import datetime
from openai import OpenAI
from sentence_transformers import SentenceTransformer
from prompts import *

# 默认配置
DEFAULT_CONFIG = {
    "mongodb": {
        "host": "localhost",
        "port": 27017,
        "db_name": "kinyo_db",
        "reviews_collection": "kinyo_new_reviews",
        "llm_results_collection": "kinyo_llm_results",
        "data_result_collection": "kinyo_data_result"
    },
    "openai": {
        "api_key_env": "OPEN_AI_KEY",
        "proxy": {
            "url": "http://127.0.0.1",
            "port": 6465
        }
    },
    "models": {
        "llm_models": ["gpt-4o", "gpt-4o-mini","gpt-3.5-turbo"],
        "default_llm_model": "gpt-3.5-turbo",
        "embedding_model": "BAAI/bge-base-zh"
    },
    "project_code": "kinyo-data-10",
    "solution": "AI自动打标",
    "logging": {
        "log_file": "logs/2_second_data_correction.log",
        "log_level": logging.INFO
    },
    "token": {
        "report_file": "logs/2_second_data_correction_token_usage.json"
    },
    "product_type": "扩音器"
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
    logger = logging.getLogger("data_correction")
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
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(logging.Formatter(log_format, date_format))
        logger.addHandler(file_handler)
    
    return logger

# 初始化全局日志器
logger = setup_logger(DEFAULT_CONFIG["logging"]["log_file"], DEFAULT_CONFIG["logging"]["log_level"])

###################
# Token统计
###################

class TokenCounter:
    """Token使用统计类"""
    
    def __init__(self, project_code: str = DEFAULT_CONFIG["project_code"]):
        self.total_tokens = 0
        self.call_count = 0
        self.token_by_model = {}
        self.token_by_operation = {}
        self.prompt_tokens = 0
        self.completion_tokens = 0
        self.start_time = datetime.now()
        self.project_code = project_code
        
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
            "project_code": self.project_code,
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "cost_estimate": {
                "input_cost": input_cost,
                "output_cost": output_cost,
                "total_cost": total_cost
            }
        }
        
    def save_report(self, output_file: str = None):
        """保存报告到文件
        
        Args:
            output_file: 输出文件路径，如果为None则使用默认路径
        """
        if output_file is None:
            output_file = DEFAULT_CONFIG["token"]["report_file"]
            
        # 确保输出目录存在
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(self.get_report(), f, ensure_ascii=False, indent=2)
        logger.info(f"Token使用报告已保存到 {output_file}")

# 初始化全局Token计数器
token_counter = TokenCounter()

###################
# 工具函数
###################

def timer_decorator(func):
    """函数执行时间计时装饰器"""
    def wrapper(*args, **kwargs):
        start_time = datetime.now()
        logger.debug(f"开始执行 {func.__name__}")
        result = func(*args, **kwargs)
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        logger.debug(f"执行完成 {func.__name__}, 耗时: {duration:.4f}秒")
        return result
    return wrapper

def api_call_with_retry(max_retries=3, initial_delay=1):
    """带重试机制的API调用装饰器"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            retries = 0
            delay = initial_delay
            
            while retries <= max_retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    retries += 1
                    if retries > max_retries:
                        logger.error(f"API调用失败，已达到最大重试次数: {func.__name__}, 错误: {str(e)}")
                        raise
                    
                    logger.warning(f"API调用失败，准备第{retries}次重试: {func.__name__}, 错误: {str(e)}")
                    # 指数退避策略
                    sleep_time = delay * (2 ** (retries - 1)) * (0.5 + random.random())
                    time.sleep(sleep_time)
            
        return wrapper
    return decorator

class DataCorrectionTool:
    """数据矫正工具类，用于对电商点评数据进行分类矫正"""
    
    def __init__(self, config=None):
        """
        初始化数据矫正工具
        
        参数:
        config: 配置信息，如果为None则使用默认配置
        """
        self.config = config or DEFAULT_CONFIG
        self._setup_environment()
        self._connect_mongodb()
        self._init_openai_client()
        
    def _setup_environment(self):
        """设置环境变量，如代理等"""
        proxy_config = self.config["openai"]["proxy"]
        os.environ['http_proxy'] = f'{proxy_config["url"]}:{proxy_config["port"]}'
        os.environ['https_proxy'] = f'{proxy_config["url"]}:{proxy_config["port"]}'
        
    def _connect_mongodb(self):
        """连接MongoDB数据库"""
        mongodb_config = self.config["mongodb"]
        self.mongo_client = pymongo.MongoClient(f"mongodb://{mongodb_config['host']}:{mongodb_config['port']}/")
        self.db = self.mongo_client[mongodb_config["db_name"]]
        self.reviews_collection = self.db[mongodb_config["reviews_collection"]]
        self.llm_results_collection = self.db[mongodb_config["llm_results_collection"]]
        self.data_result_collection = self.db[mongodb_config["data_result_collection"]]
        
    def _init_openai_client(self):
        """初始化OpenAI客户端"""
        self.client = OpenAI(api_key=os.getenv(self.config["openai"]["api_key_env"]))
        
    def _cosine_sim(self, a, b):
        """计算两个向量的余弦相似度"""
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


    
    @timer_decorator
    @api_call_with_retry(max_retries=3, initial_delay=2)
    def get_category_from_llm(self, origin_category: str, category_type: str, 
                             is_product_topic: bool = False, model: str = None) -> Dict[str, Any]:
        """
        调用LLM获取标准分类
        
        参数:
        origin_category: 原始分类信息，逗号分隔的字符串
        category_type: 分类类型
        is_product_topic: 是否为商品话题分类，默认为False
        model: 使用的模型，默认为配置中的默认模型
        
        返回:
        Dict: 包含categories和token_usage的字典
        """
        if model is None:
            model = self.config["models"]["default_llm_model"]
        
        operation_type = "product_topic_classification" if is_product_topic else "user_profile_classification"
        logger.info(f"开始获取{category_type}标准分类，使用模型: {model}")
            
        if is_product_topic:
            prompt = product_topic_classification_prompt(origin_category, category_type)
        else:
            prompt = user_profile_classification_prompt(origin_category, category_type)
        
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "你是一个专业的分类专家"},
                    {"role": "user", "content": prompt}
                ],
                stream=False,
                response_format={'type': 'json_object'}
            )

            # 获取token消耗数量
            token_usage = response.usage.total_tokens if hasattr(response, 'usage') else 0
            prompt_tokens = response.usage.prompt_tokens if hasattr(response, 'usage') else 0
            completion_tokens = response.usage.completion_tokens if hasattr(response, 'usage') else 0
            
            # 添加到token统计
            token_counter.add_usage(
                tokens=token_usage,
                model=model,
                operation=operation_type,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens
            )
            
            # 解析内容
            content = response.choices[0].message.content
            parsed_content = json.loads(content)
            parsed_content['token_usage'] = token_usage
            parsed_content['prompt_tokens'] = prompt_tokens
            parsed_content['completion_tokens'] = completion_tokens
            
            logger.info(f"成功获取{category_type}标准分类，使用模型: {model}, 消耗tokens: {token_usage}")
            return parsed_content
        except Exception as e:
            logger.error(f"调用LLM获取{category_type}标准分类失败: {str(e)}")
            logger.debug(traceback.format_exc())
            return None
    
    def get_profile_stats(self, fields: List[str], project_code: str = None, solution: str = None) -> Dict[str, List[Dict]]:
        """
        获取用户画像字段的统计信息
        
        参数:
        fields: 需要统计的字段列表
        project_code: 项目编号，默认使用配置中的版本
        solution: 解决方案，默认使用配置中的方案
        
        返回:
        Dict: 包含每个字段统计信息的字典
        """
        if project_code is None:
            project_code = self.config["project_code"]
        if solution is None:
            solution = self.config["solution"]
            
        cursor = self.llm_results_collection.find({
            "project_code": project_code,
            "solution": solution
        })

        # 初始化每个字段的计数器
        field_counters = {field: Counter() for field in fields}
        total = 0

        for doc in cursor:
            user_profile = doc.get("user_profile", {})
            for field in fields:
                value = user_profile.get(field, "")
                field_counters[field][value] += 1
            total += 1

        # 组织结果
        result = {}
        for field, counter in field_counters.items():
            field_result = []
            for value, count in counter.items():
                percent = round(count / total, 4) if total > 0 else 0
                field_result.append({
                    field: value,
                    "count": count,
                    "percent": percent
                })
            result[field] = field_result

        return result
    
    @timer_decorator
    def normalize_user_profile_field(self, field_name: str, category_type: str, 
                                    profile_stats: Dict, project_code: str = None, 
                                    solution: str = None, model_name: str = None,
                                    embedding_model: str = None) -> pd.DataFrame:
        """
        对用户画像字段进行归一化处理并更新到MongoDB
        
        参数:
        field_name: 需要处理的字段名称，如"occupation"
        category_type: 分类类型，如"职业"
        profile_stats: 包含统计信息的字典
        project_code: 项目编号，默认使用配置中的版本
        solution: 解决方案，默认使用配置中的方案
        model_name: 使用的LLM模型，默认使用配置中的模型
        embedding_model: 使用的嵌入模型，默认使用配置中的模型
        
        返回:
        DataFrame: 包含原始类别和归属类别的数据框
        """
        if project_code is None:
            project_code = self.config["project_code"]
        if solution is None:
            solution = self.config["solution"]
        if model_name is None:
            model_name = self.config["models"]["default_llm_model"]
        if embedding_model is None:
            embedding_model = self.config["models"]["embedding_model"]
        
        logger.info(f"开始处理用户画像字段: {field_name} ({category_type})")
            
        # 1. 获取原始数据列表并过滤掉None值和非字符串值
        original_list = [
            str(item[field_name])
            for item in profile_stats[field_name]
            if item[field_name] is not None and str(item[field_name]).strip() != ''
        ]
        
        logger.info(f"已获取 {len(original_list)} 个原始{category_type}类别")
        
        # 2. 获取标准分类
        logger.info(f"开始获取{category_type}标准分类")
        category_result = self.get_category_from_llm(
            origin_category=",".join(original_list),
            category_type=category_type,
            model=model_name
        )
        
        if not category_result or "categories" not in category_result:
            logger.error(f"获取{category_type}标准分类失败")
            print(f"获取{category_type}标准分类失败")
            return pd.DataFrame()
            
        category_names = category_result["categories"]
        logger.info(f"获取到 {len(category_names)} 个标准{category_type}分类: {', '.join(category_names)}")
        print(f"重新的{category_type}分类：", category_names)
        
        # 3. 向量化
        logger.info(f"开始使用模型 {embedding_model} 进行向量化")
        model = SentenceTransformer(embedding_model)
        category_vecs = model.encode(category_names)
        original_vecs = model.encode(original_list)
        logger.info("向量化完成")
        
        # 4. 相似度归类
        logger.info("开始进行相似度归类")
        results = []
        update_count = 0
        empty_count = 0
        
        for orig, orig_vec in zip(original_list, original_vecs):
            if orig.strip() != '':
                # 非空值，计算相似度
                sims = [self._cosine_sim(orig_vec, cat_vec) for cat_vec in category_vecs]
                idx = np.argmax(sims)
                assigned_category = category_names[idx]
                results.append({"原始类别": orig, "归属类别": assigned_category})
                
                # 更新MongoDB
                new_field_name = f"user_profile.new_{field_name}"
                update_result = self.llm_results_collection.update_many(
                    {
                        "project_code": project_code,
                        "solution": solution,
                        f"user_profile.{field_name}": orig
                    },
                    {"$set": {new_field_name: assigned_category}}
                )
                update_count += update_result.modified_count
            else:
                # 空值处理为"未知"
                new_field_name = f"user_profile.new_{field_name}"
                update_result = self.llm_results_collection.update_many(
                    {
                        "project_code": project_code,
                        "solution": solution,
                        f"user_profile.{field_name}": orig
                    },
                    {"$set": {new_field_name: "未知", "second_correction_model": model_name}}
                )
                update_count += update_result.modified_count
                empty_count += 1
        
        logger.info(f"相似度归类完成，共处理 {len(results)} 个非空类别和 {empty_count} 个空类别")
        logger.info(f"MongoDB更新完成，共更新 {update_count} 条文档")
        
        # 5. 生成DataFrame
        df = pd.DataFrame(results)
        logger.info(f"{category_type}字段处理完成")
        return df
    
    @timer_decorator
    def normalize_product_topics(self, product_type: str = DEFAULT_CONFIG["product_type"], project_code: str = None, 
                                solution: str = None, model_name: str = None,
                                embedding_model: str = None) -> pd.DataFrame:
        """
        对商品话题进行归一化处理并更新到MongoDB
        
        参数:
        product_type: 产品类型，如"扩音器"
        project_code: 项目编号，默认使用配置中的版本
        solution: 解决方案，默认使用配置中的方案
        model_name: 使用的LLM模型，默认使用配置中的模型
        embedding_model: 使用的嵌入模型，默认使用配置中的模型
        
        返回:
        DataFrame: 包含原始话题和归属类别的数据框
        """
        if project_code is None:
            project_code = self.config["project_code"]
        if solution is None:
            solution = self.config["solution"]
        if model_name is None:
            model_name = self.config["models"]["default_llm_model"]
        if embedding_model is None:
            embedding_model = self.config["models"]["embedding_model"]
        
        logger.info(f"开始处理商品话题，产品类型: {product_type}")
            
        # 1. 收集所有不同的topic
        logger.info(f"开始从 MongoDB 收集原始话题分类，项目编号: {project_code}, 解决方案: {solution}")
        pipeline = [
            {"$match": {"project_code": project_code, "solution": solution}},
            {"$unwind": "$product_topic_result"},
            {"$group": {"_id": "$product_topic_result.topic"}}
        ]
        
        topic_results = list(self.llm_results_collection.aggregate(pipeline))
        original_topics = [str(doc["_id"]) for doc in topic_results if doc["_id"] is not None and str(doc["_id"]).strip() != '']
        
        logger.info(f"已收集 {len(original_topics)} 个原始话题分类")
        
        # 2. 获取标准分类
        logger.info(f"开始获取{product_type}标准话题分类")
        category_result = self.get_category_from_llm(
            origin_category=",".join(original_topics),
            category_type=product_type,
            is_product_topic=True,
            model=model_name
        )
        
        if not category_result or "categories" not in category_result:
            logger.error(f"获取商品话题标准分类失败")
            print(f"获取商品话题标准分类失败")
            return pd.DataFrame()
            
        category_names = category_result["categories"]
        logger.info(f"获取到 {len(category_names)} 个标准话题分类: {', '.join(category_names)}")
        print(f"重新的商品话题分类：", category_names)
        
        # 3. 向量化
        logger.info(f"开始使用模型 {embedding_model} 进行向量化")
        model = SentenceTransformer(embedding_model)
        category_vecs = model.encode(category_names)
        topic_vecs = model.encode(original_topics)
        logger.info("向量化完成")
        
        # 4. 相似度归类
        logger.info("开始进行相似度归类")
        results = []
        topic_mapping = {}  # 用于存储映射关系
        
        for topic, topic_vec in zip(original_topics, topic_vecs):
            if topic.strip() != '':
                # 非空值，计算相似度
                sims = [self._cosine_sim(topic_vec, cat_vec) for cat_vec in category_vecs]
                idx = np.argmax(sims)
                assigned_category = category_names[idx]
                results.append({"原始话题": topic, "归属类别": assigned_category})
                topic_mapping[topic] = assigned_category
        
        logger.info(f"相似度归类完成，共处理 {len(results)} 个话题")
        
        # 5. 更新MongoDB
        logger.info("开始更新MongoDB文档")
        update_count = 0
        doc_count = 0
        
        # 由于product_topic_result是数组，我们需要遍历每个文档并更新
        for doc in self.llm_results_collection.find({"project_code": project_code, "solution": solution}):
            doc_count += 1
            if "product_topic_result" in doc and isinstance(doc["product_topic_result"], list):
                updated_topics = []
                for topic_item in doc["product_topic_result"]:
                    # 复制原始项
                    updated_item = topic_item.copy()
                    
                    # 添加new_topic字段
                    original_topic = topic_item.get("topic", "")
                    if original_topic.strip() != '':
                        updated_item["new_topic"] = topic_mapping.get(original_topic, "未知")
                    else:
                        updated_item["new_topic"] = "未知"
                    
                    updated_topics.append(updated_item)
                
                # 更新文档
                update_result = self.llm_results_collection.update_one(
                    {"_id": doc["_id"]},
                    {"$set": {"product_topic_result": updated_topics, "second_correction_model": model_name}}
                )
                if update_result.modified_count > 0:
                    update_count += 1
        
        logger.info(f"MongoDB更新完成，共检查 {doc_count} 条文档，更新 {update_count} 条文档")
        
        # 6. 生成DataFrame
        df = pd.DataFrame(results)
        logger.info(f"商品话题处理完成，共生成 {len(df)} 条归类结果")
        return df
    
    def process_all_user_profile_fields(self, fields_config: Dict[str, str] = None, model_name: str = None) -> Dict[str, pd.DataFrame]:
        """
        处理所有用户画像字段
        
        参数:
        fields_config: 字段配置，键为字段名，值为分类类型，如果为None则使用默认配置
        
        返回:
        Dict: 包含每个字段处理结果的字典
        """
        if fields_config is None:
            fields_config = {
                "gender": "性别",
                "occupation": "职业",
                "consumption_scene": "用户消费场景",
                "consumption_frequency": "用户购买情况：首次|二次|多次",
                "consumption_thrill_point": "产品给用户带来的超出预期的即时满足的特点",
                "consumption_pain_point": "产品给用户带来的不得不解决的问题",
                "consumption_itch_point": "产品给用户带来的不解决也行，但解决更爽的欲望"
            }
            
        # 获取用户画像统计信息
        fields = list(fields_config.keys())
        profile_stats = self.get_profile_stats(fields)
        
        # 处理每个字段
        results = {}
        for field_name, category_type in fields_config.items():
            print(f"\n开始处理{category_type}字段...")
            df = self.normalize_user_profile_field(
                field_name=field_name,
                category_type=category_type,
                profile_stats=profile_stats,
                model_name=model_name
            )
            results[field_name] = df
            print(f"{category_type}归类结果:")
            print(df)
            
        return results
    
    def run_full_correction(self, product_type: str = "扩音器", model_name: str = None) -> Dict[str, Any]:
        """
        运行完整的数据矫正流程
        
        参数:
        product_type: 产品类型，默认为"扩音器"
        
        返回:
        Dict: 包含处理结果的字典
        """
        # 1. 处理用户画像字段
        user_profile_results = self.process_all_user_profile_fields(model_name=model_name)
        
        # 2. 处理商品话题
        print("\n开始处理商品话题...")
        topic_df = self.normalize_product_topics(product_type=product_type, model_name=model_name)
        print("商品话题归类结果:")
        print(topic_df)
        
        # 3. 返回结果
        return {
            "user_profile_results": user_profile_results,
            "topic_results": topic_df
        }


@timer_decorator
def main():
    """主函数，用于命令行调用"""
    # 记录开始时间
    start_time = datetime.now()
    logger.info(f"===== 开始执行数据矫正程序 - {start_time.strftime('%Y-%m-%d %H:%M:%S')} =====")
    
    import argparse
    import random
    
    parser = argparse.ArgumentParser(description='电商点评数据矫正工具')
    parser.add_argument('--project-code', type=str, default=DEFAULT_CONFIG["project_code"],
                        help=f'项目编号，默认: {DEFAULT_CONFIG["project_code"]}')
    parser.add_argument('--solution', type=str, default=DEFAULT_CONFIG["solution"],
                        help=f'解决方案，默认: {DEFAULT_CONFIG["solution"]}')
    parser.add_argument('--product_type', type=str, default="扩音器",
                        help='产品类型，默认: 扩音器')
    parser.add_argument('--mode', type=str, choices=['all', 'user_profile', 'product_topic'], 
                        default='all', help='处理模式，默认: all')
    parser.add_argument('--field', type=str, default=None,
                        help='要处理的用户画像字段，仅在mode=user_profile时有效')
    parser.add_argument('--token_report', type=str, default=None,
                        help='指定token使用报告输出文件路径')
    parser.add_argument('--model', type=str, default=DEFAULT_CONFIG["models"]["default_llm_model"],
                        help=f'LLM模型，默认: {DEFAULT_CONFIG["models"]["default_llm_model"]}')
    
    args = parser.parse_args()
    
    try:
        # 创建配置
        config = DEFAULT_CONFIG.copy()
        config["project_code"] = args.project_code
        config["solution"] = args.solution
        config["product_type"] = args.product_type
        config["models"]["default_llm_model"] = args.model
        
        # 更新token计数器的项目编号
        token_counter.project_code = args.project_code
        
        logger.info(f"项目编号: {args.project_code}, 解决方案: {args.solution}")
        logger.info(f"处理模式: {args.mode}, 产品类型: {args.product_type}")
        logger.info(f"LLM模型: {args.model}")
        
        # 初始化工具
        tool = DataCorrectionTool(config)
        
        # 根据模式执行不同的处理
        if args.mode == 'all':
            logger.info("开始执行完整矫正流程")
            results = tool.run_full_correction(
                product_type=args.product_type,
                model_name=args.model
            )
            logger.info("完整矫正流程执行完成")
        elif args.mode == 'user_profile':
            if args.field:
                # 处理单个字段
                fields_config = {
                    "gender": "性别",
                    "occupation": "职业",
                    "consumption_scene": "用户消费场景",
                    "consumption_frequency": "用户消费频率",
                    "consumption_thrill_point": "用户消费兴奋点",
                    "consumption_pain_point": "用户消费痛点",
                    "consumption_itch_point": "用户消费痒点"
                }
                if args.field in fields_config:
                    logger.info(f"开始处理用户画像字段: {args.field} ({fields_config[args.field]})")
                    fields = [args.field]
                    profile_stats = tool.get_profile_stats(fields)
                    df = tool.normalize_user_profile_field(
                        field_name=args.field,
                        category_type=fields_config[args.field],
                        profile_stats=profile_stats,
                        model_name=args.model
                    )
                    print(f"{fields_config[args.field]}归类结果:")
                    print(df)
                    logger.info(f"用户画像字段 {args.field} 处理完成")
                else:
                    logger.error(f"错误: 未知的字段 '{args.field}'")
                    print(f"错误: 未知的字段 '{args.field}'")
            else:
                # 处理所有字段
                logger.info("开始处理所有用户画像字段")
                results = tool.process_all_user_profile_fields()
                logger.info("所有用户画像字段处理完成")
        elif args.mode == 'product_topic':
            # 处理商品话题
            logger.info(f"开始处理商品话题，产品类型: {args.product_type}")
            topic_df = tool.normalize_product_topics(product_type=args.product_type, model_name=args.model)
            print("商品话题归类结果:")
            print(topic_df)
            logger.info("商品话题处理完成")
    except Exception as e:
        logger.error(f"程序执行过程中发生错误: {str(e)}")
        logger.error(traceback.format_exc())
    finally:
        # 保存token使用报告
        token_counter.save_report(args.token_report)
        
        # 记录结束时间
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()
        logger.info(f"===== 数据矫正程序执行完成 - 耗时: {execution_time:.2f}秒 - {end_time.strftime('%Y-%m-%d %H:%M:%S')} =====\n")


if __name__ == "__main__":
    main()
