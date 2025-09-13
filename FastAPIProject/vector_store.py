"""
向量存储模块 - 使用FAISS进行向量存储和检索
"""
import os
import pickle
import numpy as np
import faiss
from typing import List, Dict, Any, Tuple
from langchain.schema import Document


class VectorStore:
    def __init__(self, dimension: int = 384, index_type: str = "flat"):
        """
        初始化向量存储
        
        Args:
            dimension: 向量维度
            index_type: 索引类型 ("flat" 或 "ivf")
        """
        self.dimension = dimension
        self.index_type = index_type
        self.index = None
        self.documents = []
        self.metadata = []
        self.is_trained = False
        
    def create_index(self, embeddings: np.ndarray) -> None:
        """
        创建FAISS索引
        
        Args:
            embeddings: 嵌入向量数组
        """
        if self.index_type == "flat":
            # 使用L2距离的平面索引
            self.index = faiss.IndexFlatL2(self.dimension)
        elif self.index_type == "ivf":
            # 使用倒排文件索引
            nlist = min(100, len(embeddings) // 10)  # 聚类数量
            quantizer = faiss.IndexFlatL2(self.dimension)
            self.index = faiss.IndexIVFFlat(quantizer, self.dimension, nlist)
            self.index.train(embeddings.astype('float32'))
            self.is_trained = True
        else:
            raise ValueError(f"不支持的索引类型: {self.index_type}")
        
        # 添加向量到索引
        self.index.add(embeddings.astype('float32'))
    
    def add_documents(self, documents: List[Document], embeddings: np.ndarray, metadata: List[Dict] = None) -> None:
        """
        添加文档到向量存储
        
        Args:
            documents: 文档列表
            embeddings: 对应的嵌入向量
            metadata: 元数据列表
        """
        if self.index is None:
            self.create_index(embeddings)
        else:
            # 如果索引已存在，添加新向量
            self.index.add(embeddings.astype('float32'))
        
        # 存储文档和元数据
        self.documents.extend(documents)
        if metadata:
            self.metadata.extend(metadata)
        else:
            # 如果没有提供元数据，创建默认元数据
            for i, doc in enumerate(documents):
                self.metadata.append({
                    'chunk_id': len(self.metadata) + i,
                    'source': doc.metadata.get('source', 'unknown'),
                    'page': doc.metadata.get('page', 0)
                })
    
    def search(self, query_embedding: np.ndarray, k: int = 5) -> Tuple[List[Document], List[float], List[Dict]]:
        """
        搜索相似文档
        
        Args:
            query_embedding: 查询向量
            k: 返回的文档数量
            
        Returns:
            (文档列表, 相似度分数列表, 元数据列表)
        """
        if self.index is None:
            raise ValueError("索引未初始化，请先添加文档")
        
        # 确保查询向量是正确的形状
        if query_embedding.ndim == 1:
            query_embedding = query_embedding.reshape(1, -1)
        
        # 搜索最相似的向量
        scores, indices = self.index.search(query_embedding.astype('float32'), k)
        
        # 获取对应的文档和元数据
        retrieved_docs = [self.documents[i] for i in indices[0] if i < len(self.documents)]
        retrieved_scores = scores[0].tolist()
        retrieved_metadata = [self.metadata[i] for i in indices[0] if i < len(self.metadata)]
        
        return retrieved_docs, retrieved_scores, retrieved_metadata
    
    def save_index(self, filepath: str) -> None:
        """
        保存索引到文件
        
        Args:
            filepath: 保存路径
        """
        if self.index is None:
            raise ValueError("没有索引可保存")
        
        # 创建保存目录
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # 保存FAISS索引
        faiss.write_index(self.index, f"{filepath}.faiss")
        
        # 保存文档和元数据
        with open(f"{filepath}.pkl", "wb") as f:
            pickle.dump({
                'documents': self.documents,
                'metadata': self.metadata,
                'dimension': self.dimension,
                'index_type': self.index_type,
                'is_trained': self.is_trained
            }, f)
    
    def load_index(self, filepath: str) -> None:
        """
        从文件加载索引
        
        Args:
            filepath: 文件路径
        """
        # 加载FAISS索引
        self.index = faiss.read_index(f"{filepath}.faiss")
        
        # 加载文档和元数据
        with open(f"{filepath}.pkl", "rb") as f:
            data = pickle.load(f)
            self.documents = data['documents']
            self.metadata = data['metadata']
            self.dimension = data['dimension']
            self.index_type = data['index_type']
            self.is_trained = data['is_trained']
    
    def get_stats(self) -> Dict[str, Any]:
        """
        获取向量存储统计信息
        
        Returns:
            统计信息字典
        """
        if self.index is None:
            return {
                'total_documents': 0,
                'index_type': self.index_type,
                'dimension': self.dimension,
                'is_trained': False
            }
        
        return {
            'total_documents': len(self.documents),
            'index_type': self.index_type,
            'dimension': self.dimension,
            'is_trained': self.is_trained,
            'index_size': self.index.ntotal if hasattr(self.index, 'ntotal') else 0
        }
    
    def clear(self) -> None:
        """
        清空向量存储
        """
        self.index = None
        self.documents = []
        self.metadata = []
        self.is_trained = False
