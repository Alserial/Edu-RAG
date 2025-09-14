from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
from rag_system import RAGSystem
from database_manager import DatabaseManager

app = FastAPI(title="RAG系统API", description="基于检索增强生成的问答系统", version="1.0.0")

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化RAG系统和数据库管理器
rag_system = RAGSystem()
db_manager = DatabaseManager()

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

class BackupRequest(BaseModel):
    name: Optional[str] = None

class RestoreRequest(BaseModel):
    backup_name: str

class CleanupRequest(BaseModel):
    keep_count: int = 5

# 根路径
@app.get("/")
async def root():
    return {
        "message": "RAG系统API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "query": "/query - 查询文档",
            "upload": "/upload - 上传文档（文件路径）",
            "upload-files": "/upload-files - 上传文档（文件内容）",
            "summary": "/summary - 总结文档",
            "analysis": "/analysis - 分析文档",
            "info": "/info - 系统信息",
            "save": "/save - 保存系统",
            "load": "/load - 加载系统",
            "clear": "/clear - 清空系统",
            "db_backup": "/db/backup - 创建数据库备份",
            "db_restore": "/db/restore - 恢复数据库",
            "db_list": "/db/backups - 列出备份",
            "db_delete": "/db/backup/{name} - 删除备份",
            "db_stats": "/db/stats - 数据库统计",
            "db_health": "/db/health - 数据库健康检查",
            "db_cleanup": "/db/cleanup - 清理旧备份"
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

# 上传文档接口 - 支持文件路径和文件上传两种方式
@app.post("/upload")
async def upload_documents(request: DocumentUploadRequest):
    """上传文档到RAG系统（通过文件路径）"""
    try:
        # 检查文件是否存在
        for file_path in request.file_paths:
            if not os.path.exists(file_path):
                raise HTTPException(status_code=404, detail=f"文件不存在: {file_path}")
        
        result = rag_system.add_documents(request.file_paths)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 文件上传接口 - 支持直接上传文件
@app.post("/upload-files")
async def upload_files(files: List[UploadFile] = File(...)):
    """直接上传文件到RAG系统"""
    try:
        import tempfile
        import shutil
        
        temp_files = []
        file_paths = []
        
        for file in files:
            # 创建临时文件
            suffix = os.path.splitext(file.filename)[1] if file.filename else '.txt'
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
            temp_files.append(temp_file.name)
            file_paths.append(temp_file.name)
            
            # 写入文件内容
            content = await file.read()
            temp_file.write(content)
            temp_file.close()
        
        # 处理文档
        result = rag_system.add_documents(file_paths)
        
        # 清理临时文件
        for temp_file in temp_files:
            try:
                os.unlink(temp_file)
            except:
                pass
        
        return result
    except Exception as e:
        # 清理临时文件
        for temp_file in temp_files:
            try:
                os.unlink(temp_file)
            except:
                pass
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

# ==================== 数据库管理接口 ====================

# 创建数据库备份
@app.post("/db/backup")
async def create_backup(request: BackupRequest):
    """创建数据库备份"""
    try:
        result = db_manager.create_backup(request.name)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 恢复数据库
@app.post("/db/restore")
async def restore_backup(request: RestoreRequest):
    """从备份恢复数据库"""
    try:
        result = db_manager.restore_backup(request.backup_name)
        # 如果恢复成功，重新加载RAG系统
        if result["success"]:
            rag_system.load_system()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 列出所有备份
@app.get("/db/backups")
async def list_backups():
    """列出所有数据库备份"""
    try:
        result = db_manager.list_backups()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 删除备份
@app.delete("/db/backup/{backup_name}")
async def delete_backup(backup_name: str):
    """删除指定的备份"""
    try:
        result = db_manager.delete_backup(backup_name)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 获取数据库统计信息
@app.get("/db/stats")
async def get_database_stats():
    """获取数据库统计信息"""
    try:
        result = db_manager.get_database_stats()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 数据库健康检查
@app.get("/db/health")
async def database_health_check():
    """数据库健康检查"""
    try:
        result = db_manager.get_database_health()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 清理旧备份
@app.post("/db/cleanup")
async def cleanup_backups(request: CleanupRequest):
    """清理旧备份，只保留最新的几个"""
    try:
        result = db_manager.cleanup_old_backups(request.keep_count)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
