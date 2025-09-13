from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
from rag_system import RAGSystem

app = FastAPI(title="RAG系统API", description="基于检索增强生成的问答系统", version="1.0.0")

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化RAG系统
rag_system = RAGSystem()

# 请求模型
class QueryRequest(BaseModel):
    question: str
    k: int = 5
    template_type: str = "qa"

class SummaryRequest(BaseModel):
    query: str = "请总结主要内容"

class AnalysisRequest(BaseModel):
    query: str

class DocumentUploadRequest(BaseModel):
    file_paths: List[str]

# 根路径
@app.get("/")
async def root():
    return {
        "message": "RAG系统API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "query": "/query - 查询文档",
            "upload": "/upload - 上传文档",
            "summary": "/summary - 总结文档",
            "analysis": "/analysis - 分析文档",
            "info": "/info - 系统信息",
            "save": "/save - 保存系统",
            "load": "/load - 加载系统",
            "clear": "/clear - 清空系统"
        }
    }

# 查询接口
@app.post("/query")
async def query_documents(request: QueryRequest):
    """查询文档"""
    try:
        result = rag_system.query(
            question=request.question,
            k=request.k,
            template_type=request.template_type
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 上传文档接口
@app.post("/upload")
async def upload_documents(request: DocumentUploadRequest):
    """上传文档到RAG系统"""
    try:
        # 检查文件是否存在
        for file_path in request.file_paths:
            if not os.path.exists(file_path):
                raise HTTPException(status_code=404, detail=f"文件不存在: {file_path}")
        
        result = rag_system.add_documents(request.file_paths)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 总结接口
@app.post("/summary")
async def summarize_documents(request: SummaryRequest):
    """总结文档"""
    try:
        result = rag_system.summarize_documents(request.query)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 分析接口
@app.post("/analysis")
async def analyze_documents(request: AnalysisRequest):
    """分析文档"""
    try:
        result = rag_system.analyze_documents(request.query)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 系统信息接口
@app.get("/info")
async def get_system_info():
    """获取系统信息"""
    try:
        result = rag_system.get_system_info()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 保存系统接口
@app.post("/save")
async def save_system():
    """保存系统状态"""
    try:
        result = rag_system.save_system()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 加载系统接口
@app.post("/load")
async def load_system():
    """加载系统状态"""
    try:
        result = rag_system.load_system()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 清空系统接口
@app.post("/clear")
async def clear_system():
    """清空系统"""
    try:
        result = rag_system.clear_system()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 健康检查接口
@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "system_initialized": rag_system.is_initialized,
        "document_count": rag_system.document_count
    }
