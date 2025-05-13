from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from datetime import datetime

class TokenUsage(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    calls_count: int

class ProfileItem(BaseModel):
    value: str
    count: int
    summary: Optional[str] = None

class TopicStats(BaseModel):
    好评: int
    差评: int
    中评: int
    总数: int
    好评占比: float
    中差评占比: float
    提及率: float
    好评摘要: Optional[str] = None
    中差评摘要: Optional[str] = None
    quadrant: Optional[str] = None
    avg_mention_rate: Optional[float] = None
    avg_satisfaction_rate: Optional[float] = None

class TotalStats(BaseModel):
    topic_count: int
    good_count: int
    neutral_count: int
    bad_count: int
    total_count: int
    good_rate: float
    neutral_bad_rate: float

class DataResultModel(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    project_code: str
    solution: str
    model: str
    top_topics_count: int
    process_time: str
    data_id: str
    token_usage: TokenUsage
    total_review: int
    user_profile: Dict[str, Any]
    product_topics: Dict[str, Any]
    user_profile_insight: str
    topic_insight: str
    quadrant_insight: str
    overall_insight: str
    first_stage_tokens: int
    all_stages_total_tokens: int

    class Config:
        populate_by_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class DataResultResponse(BaseModel):
    total: int
    data: List[DataResultModel]

class ErrorResponse(BaseModel):
    detail: str
