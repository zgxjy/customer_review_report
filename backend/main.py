from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import json
from bson import ObjectId

from database import Database, MongoJSONEncoder
from routers import data_result

app = FastAPI(
    title="电商点评分析API",
    description="电商点评分析数据看板后端API",
    version="1.0.0"
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源，生产环境中应该限制
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 自定义JSON响应处理器，处理ObjectId
@app.middleware("http")
async def custom_json_middleware(request: Request, call_next):
    response = await call_next(request)
    
    if response.headers.get("content-type") == "application/json":
        response_body = [chunk async for chunk in response.body_iterator]
        response_body = b"".join(response_body)
        
        # 使用自定义JSON编码器重新编码响应
        try:
            data = json.loads(response_body.decode())
            new_response_body = json.dumps(data, cls=MongoJSONEncoder).encode()
            return JSONResponse(
                content=json.loads(new_response_body),
                status_code=response.status_code,
                headers=dict(response.headers),
            )
        except:
            pass
    
    return response

# 包含路由
app.include_router(data_result.router)

# 启动和关闭事件
@app.on_event("startup")
def startup_db_client():
    Database.connect_to_database()

@app.on_event("shutdown")
def shutdown_db_client():
    Database.close_database_connection()

@app.get("/")
def root():
    return {"message": "欢迎使用电商点评分析API"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
