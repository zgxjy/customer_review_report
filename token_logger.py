"""
电商点评分析工具 - 日志和Token统计模块

本模块提供日志系统和Token消耗记录功能，用于跟踪API调用的token使用情况
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, Any

# 日志配置
LOG_CONFIG = {
    "log_file": "logs/data_correction.log",
    "log_level": logging.INFO
}

# Token统计配置
TOKEN_CONFIG = {
    "report_file": "logs/token_usage_report.json"
}

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

class TokenCounter:
    """Token使用统计类"""
    
    def __init__(self, test_version: str = "default"):
        """初始化Token计数器
        
        Args:
            test_version: 测试版本标识
        """
        self.total_tokens = 0
        self.call_count = 0
        self.token_by_model = {}
        self.token_by_operation = {}
        self.prompt_tokens = 0
        self.completion_tokens = 0
        self.start_time = datetime.now()
        self.test_version = test_version
        
    def add_usage(self, tokens: int, model: str, operation: str = "default", 
                 prompt_tokens: int = None, completion_tokens: int = None):
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
            "test_version": self.test_version,
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
            output_file = TOKEN_CONFIG["report_file"]
            
        # 确保输出目录存在
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(self.get_report(), f, ensure_ascii=False, indent=2)
        logger.info(f"Token使用报告已保存到 {output_file}")

# 初始化全局日志器
logger = setup_logger(LOG_CONFIG["log_file"], LOG_CONFIG["log_level"])

# 初始化全局Token计数器
token_counter = TokenCounter()

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
                    import time
                    import random
                    sleep_time = delay * (2 ** (retries - 1)) * (0.5 + random.random())
                    time.sleep(sleep_time)
            
        return wrapper
    return decorator
