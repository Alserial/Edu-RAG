"""
RAG系统主控制器 - 整合文档处理、向量存储、检索和生成
"""
import os
from typing import List, Dict, Any, Optional
from document_processor import DocumentProcessor
from vector_store import VectorStore
from retriever import DocumentRetriever
from generator import RAGGenerator
from database_manager import DatabaseManager
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_huggingface import HuggingFaceEmbeddings
class RAGSystem:
    def __init__(self, 
                 chunk_size: int = 1000,
                 chunk_overlap: int = 200,
                 embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2",
                 llm_model: str = "deepseek-chat",
                 vector_store_path: str = "./vector_store"):
        """
        初始化RAG系统
        
        Args:
            chunk_size: 文档分块大小
            chunk_overlap: 分块重叠大小
            embedding_model: 嵌入模型名称
            llm_model: LLM模型名称
            vector_store_path: 向量存储路径
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.vector_store_path = vector_store_path

        # 初始化组件
        self.document_processor = DocumentProcessor(chunk_size, chunk_overlap)
        self.embeddings = HuggingFaceEmbeddings(
            model_name=embedding_model,
            model_kwargs={'device': 'cpu'}
        )
        self.vector_store = VectorStore(dimension=384)  # all-MiniLM-L6-v2的维度
        self.retriever = DocumentRetriever(self.vector_store, self.embeddings)
        self.generator = RAGGenerator(llm_model)
        self.db_manager = DatabaseManager(vector_store_path)

        # 系统状态
        self.is_initialized = False
        self.document_count = 0

    def add_documents(self, file_paths: List[str]) -> Dict[str, Any]:
        """
        添加文档到RAG系统
        
        Args:
            file_paths: 文档路径列表
            
        Returns:
            添加结果
        """
        try:
            # 处理文档
            processed_data = self.document_processor.process_multiple_documents(file_paths)

            # 添加到向量存储
            self.vector_store.add_documents(
                documents=processed_data['chunks'],
                embeddings=processed_data['embeddings'],
                metadata=processed_data['metadata']
            )

            # 更新状态
            self.document_count += len(processed_data['chunks'])
            self.is_initialized = True

            # 更新数据库元数据
            sources = [doc.metadata.get('source', 'unknown') for doc in processed_data['chunks']]
            self.db_manager.update_document_metadata(
                document_count=len(file_paths),
                chunk_count=len(processed_data['chunks']),
                sources=sources
            )

            return {
                "success": True,
                "documents_added": len(file_paths),
                "chunks_created": len(processed_data['chunks']),
                "total_documents": self.document_count,
                "message": f"成功添加 {len(file_paths)} 个文档，创建了 {len(processed_data['chunks'])} 个文档块"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"添加文档失败: {str(e)}"
            }

    def query(self, question: str, k: int = 5, template_type: str = "qa") -> Dict[str, Any]:
        """
        查询RAG系统
        
        Args:
            question: 问题
            k: 检索文档数量
            template_type: 生成模板类型
            
        Returns:
            查询结果
        """
        if not self.is_initialized:
            return {
                "success": False,
                "error": "RAG系统未初始化，请先添加文档",
                "answer": "请先添加文档到系统中"
            }

        try:
            # 使用检索和生成
            result = self.generator.generate_with_retrieval(
                question=question,
                retriever=self.retriever,
                k=k,
                template_type=template_type
            )

            return {
                "success": result["success"],
                "question": question,
                "answer": result["answer"],
                "retrieval_info": {
                    "documents_retrieved": len(result["retrieval_results"]["retrieved_documents"]),
                    "scores": [doc["score"] for doc in result["retrieval_results"]["retrieved_documents"]]
                },
                "generation_info": {
                    "template_type": template_type,
                    "model": result["generation_result"]["model"]
                }
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "answer": f"查询失败: {str(e)}"
            }

    def summarize_documents(self, query: str = "请总结主要内容") -> Dict[str, Any]:
        """
        总结所有文档
        
        Args:
            query: 总结查询
            
        Returns:
            总结结果
        """
        if not self.is_initialized:
            return {
                "success": False,
                "error": "RAG系统未初始化，请先添加文档"
            }

        try:
            # 获取所有文档
            all_documents = self.vector_store.documents

            # 生成总结
            result = self.generator.generate_summary(all_documents, query)

            return {
                "success": result["success"],
                "summary": result["summary"],
                "query": query,
                "document_count": result["document_count"]
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "summary": f"生成总结失败: {str(e)}"
            }

    def analyze_documents(self, query: str) -> Dict[str, Any]:
        """
        分析文档
        
        Args:
            query: 分析查询
            
        Returns:
            分析结果
        """
        if not self.is_initialized:
            return {
                "success": False,
                "error": "RAG系统未初始化，请先添加文档"
            }

        try:
            # 获取所有文档
            all_documents = self.vector_store.documents

            # 生成分析
            result = self.generator.generate_analysis(all_documents, query)

            return {
                "success": result["success"],
                "analysis": result["analysis"],
                "query": query,
                "document_count": result["document_count"]
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "analysis": f"生成分析失败: {str(e)}"
            }

    def save_system(self) -> Dict[str, Any]:
        """
        保存RAG系统状态
        
        Returns:
            保存结果
        """
        try:
            # 创建保存目录
            os.makedirs(self.vector_store_path, exist_ok=True)

            # 保存向量存储
            self.vector_store.save_index(os.path.join(self.vector_store_path, "index"))

            return {
                "success": True,
                "message": f"系统状态已保存到 {self.vector_store_path}",
                "document_count": self.document_count
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"保存系统状态失败: {str(e)}"
            }

    def load_system(self) -> Dict[str, Any]:
        """
        加载RAG系统状态
        
        Returns:
            加载结果
        """
        try:
            index_path = os.path.join(self.vector_store_path, "index")

            if not os.path.exists(f"{index_path}.faiss"):
                return {
                    "success": False,
                    "error": "未找到保存的系统状态文件"
                }

            # 加载向量存储
            self.vector_store.load_index(index_path)

            # 更新状态
            self.document_count = len(self.vector_store.documents)
            self.is_initialized = True

            return {
                "success": True,
                "message": f"系统状态已从 {self.vector_store_path} 加载",
                "document_count": self.document_count
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"加载系统状态失败: {str(e)}"
            }

    def get_system_info(self) -> Dict[str, Any]:
        """
        获取系统信息
        
        Returns:
            系统信息字典
        """
        vector_stats = self.vector_store.get_stats()
        model_info = self.generator.get_model_info()
        retrieval_stats = self.retriever.get_retrieval_stats()

        return {
            "system_status": {
                "initialized": self.is_initialized,
                "document_count": self.document_count,
                "vector_store_path": self.vector_store_path
            },
            "vector_store": vector_stats,
            "generator": model_info,
            "retriever": retrieval_stats,
            "configuration": {
                "chunk_size": self.chunk_size,
                "chunk_overlap": self.chunk_overlap,
                "embedding_model": "sentence-transformers/all-MiniLM-L6-v2"
            }
        }

    def clear_system(self) -> Dict[str, Any]:
        """
        清空系统
        
        Returns:
            清空结果
        """
        try:
            self.vector_store.clear()
            self.document_count = 0
            self.is_initialized = False

            return {
                "success": True,
                "message": "系统已清空"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"清空系统失败: {str(e)}"
            }
