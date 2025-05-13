from fastapi import APIRouter, HTTPException, Query
from bson import ObjectId
from typing import List, Optional
from database import Database
from models import DataResultModel, DataResultResponse

router = APIRouter(
    prefix="/api/data_result",
    tags=["data_result"],
    responses={404: {"description": "Not found"}},
)

# 先定义具体路由
@router.get("/project_codes", response_model=List[str])
def get_project_codes():
    """获取所有项目代码列表"""
    try:
        collection = Database.get_collection("data_result")
        if collection is None:
            raise HTTPException(status_code=500, detail="数据库集合不存在")
        
        # 获取唯一的project_code列表
        project_codes = collection.distinct("project_code")
        return project_codes
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器错误: {str(e)}")

@router.get("/solutions", response_model=List[str])
def get_solutions():
    """获取所有解决方案列表"""
    try:
        collection = Database.get_collection("data_result")
        if collection is None:
            raise HTTPException(status_code=500, detail="数据库集合不存在")
        
        # 获取唯一的solution列表
        solutions = collection.distinct("solution")
        return solutions
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器错误: {str(e)}")

@router.get("/models", response_model=List[str])
def get_models():
    """获取所有模型列表"""
    try:
        collection = Database.get_collection("data_result")
        if collection is None:
            raise HTTPException(status_code=500, detail="数据库集合不存在")
        
        # 获取唯一的model列表
        models = collection.distinct("model")
        return models
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器错误: {str(e)}")

@router.get("/", response_model=DataResultResponse)
def get_data_results(
    project_code: Optional[str] = None,
    solution: Optional[str] = None,
    model: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100)
):
    """获取数据结果列表，支持分页和筛选"""
    try:
        collection = Database.get_collection("data_result")
        if collection is None:
            raise HTTPException(status_code=500, detail="数据库集合不存在")
        
        # 构建查询条件
        query = {}
        if project_code:
            query["project_code"] = project_code
        if solution:
            query["solution"] = solution
        if model:
            query["model"] = model
        
        # 获取总数
        total = collection.count_documents(query)
        
        # 获取数据
        cursor = collection.find(query).skip(skip).limit(limit).sort("process_time", -1)
        results = []
        for doc in cursor:
            doc["_id"] = str(doc["_id"])
            
            # 为缺少的字段提供默认值
            if "first_stage_tokens" not in doc:
                doc["first_stage_tokens"] = 0
            if "all_stages_total_tokens" not in doc:
                # 如果存在token_usage，则使用其total_tokens作为默认值
                if "token_usage" in doc and "total_tokens" in doc["token_usage"]:
                    doc["all_stages_total_tokens"] = doc["token_usage"]["total_tokens"]
                else:
                    doc["all_stages_total_tokens"] = 0
            # 为缺少的quadrant_insight字段提供默认值
            if "quadrant_insight" not in doc:
                doc["quadrant_insight"] = "四象限分析显示产品话题分布情况，帮助识别关键优势和改进点。"
            
            results.append(doc)
        
        return {"total": total, "data": results}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器错误: {str(e)}")

# 最后定义通用路由
@router.get("/{data_id}", response_model=DataResultModel)
def get_data_result_by_id(data_id: str):
    """获取单个数据结果详情"""
    try:
        collection = Database.get_collection("data_result")
        if collection is None:
            raise HTTPException(status_code=500, detail="数据库集合不存在")
        
        # 尝试将data_id作为ObjectId查询
        try:
            if ObjectId.is_valid(data_id):
                result = collection.find_one({"_id": ObjectId(data_id)})
            else:
                # 如果不是有效的ObjectId，则尝试按data_id字段查询
                result = collection.find_one({"data_id": data_id})
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"数据库查询错误: {str(e)}")
        
        if not result:
            raise HTTPException(status_code=404, detail=f"未找到ID为 {data_id} 的数据")
        
        # 转换_id为字符串
        result["_id"] = str(result["_id"])
        
        # 为缺少的字段提供默认值
        if "first_stage_tokens" not in result:
            result["first_stage_tokens"] = 0
        if "all_stages_total_tokens" not in result:
            # 如果存在token_usage，则使用其total_tokens作为默认值
            if "token_usage" in result and "total_tokens" in result["token_usage"]:
                result["all_stages_total_tokens"] = result["token_usage"]["total_tokens"]
            else:
                result["all_stages_total_tokens"] = 0
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器错误: {str(e)}")
