"""
检索模块 - 负责相似性搜索和文档检索
"""
import numpy as np
from typing import List, Dict, Any, Tuple
from langchain.schema import Document
from langchain.embeddings import HuggingFaceEmbeddings
from vector_store import VectorStore


class DocumentRetriever:
    def __init__(self, vector_store: VectorStore, embeddings_model: HuggingFaceEmbeddings):
        """
        初始化文档检索器
        
        Args:
            vector_store: 向量存储实例
            embeddings_model: 嵌入模型
        """
        self.vector_store = vector_store
        self.embeddings_model = embeddings_model
    
    def retrieve_documents(self, query: str, k: int = 5, score_threshold: float = 0.0) -> Dict[str, Any]:
        """
        检索相关文档
        
        Args:
            query: 查询文本
            k: 返回文档数量
            score_threshold: 相似度阈值
            
        Returns:
            检索结果字典
        """
        # 将查询文本转换为嵌入向量
        query_embedding = self.embeddings_model.embed_query(query)
        query_embedding = np.array(query_embedding)
        
        # 从向量存储中搜索相似文档
        retrieved_docs, scores, metadata = self.vector_store.search(
            query_embedding, k=k
        )
        
        # 过滤低分文档
        filtered_results = []
        for doc, score, meta in zip(retrieved_docs, scores, metadata):
            if score >= score_threshold:
                filtered_results.append({
                    'document': doc,
                    'score': float(score),
                    'metadata': meta
                })
        
        return {
            'query': query,
            'retrieved_documents': filtered_results,
            'total_found': len(filtered_results),
            'query_embedding': query_embedding.tolist()
        }
    
    def retrieve_with_context(self, query: str, k: int = 5, context_window: int = 2) -> Dict[str, Any]:
        """
        检索文档并包含上下文信息
        
        Args:
            query: 查询文本
            k: 返回文档数量
            context_window: 上下文窗口大小
            
        Returns:
            包含上下文的检索结果
        """
        # 基本检索
        basic_results = self.retrieve_documents(query, k=k)
        
        # 为每个检索到的文档添加上下文
        enhanced_results = []
        for result in basic_results['retrieved_documents']:
            doc = result['document']
            meta = result['metadata']
            
            # 获取上下文文档（同一来源的相邻文档）
            context_docs = self._get_context_documents(doc, meta, context_window)
            
            enhanced_result = {
                'document': doc,
                'score': result['score'],
                'metadata': meta,
                'context_documents': context_docs
            }
            enhanced_results.append(enhanced_result)
        
        return {
            'query': query,
            'retrieved_documents': enhanced_results,
            'total_found': len(enhanced_results),
            'query_embedding': basic_results['query_embedding']
        }
    
    def _get_context_documents(self, target_doc: Document, target_meta: Dict, window_size: int) -> List[Document]:
        """
        获取目标文档的上下文文档
        
        Args:
            target_doc: 目标文档
            target_meta: 目标文档元数据
            window_size: 上下文窗口大小
            
        Returns:
            上下文文档列表
        """
        context_docs = []
        source = target_meta.get('source', '')
        page = target_meta.get('page', 0)
        
        # 查找同一来源的文档
        for i, doc in enumerate(self.vector_store.documents):
            doc_meta = self.vector_store.metadata[i]
            if (doc_meta.get('source') == source and 
                abs(doc_meta.get('page', 0) - page) <= window_size and
                doc != target_doc):
                context_docs.append(doc)
        
        return context_docs[:window_size * 2]  # 限制上下文文档数量
    
    def hybrid_search(self, query: str, k: int = 5, alpha: float = 0.7) -> Dict[str, Any]:
        """
        混合搜索：结合向量相似度和关键词匹配
        
        Args:
            query: 查询文本
            k: 返回文档数量
            alpha: 向量搜索权重 (0-1)
            
        Returns:
            混合搜索结果
        """
        # 向量搜索
        vector_results = self.retrieve_documents(query, k=k*2)  # 获取更多候选文档
        
        # 关键词搜索（简单实现）
        keyword_results = self._keyword_search(query, k=k*2)
        
        # 合并和重新排序结果
        combined_scores = {}
        query_words = set(query.lower().split())
        
        for result in vector_results['retrieved_documents']:
            doc_id = id(result['document'])
            vector_score = result['score']
            
            # 计算关键词匹配分数
            doc_text = result['document'].page_content.lower()
            keyword_matches = sum(1 for word in query_words if word in doc_text)
            keyword_score = keyword_matches / len(query_words) if query_words else 0
            
            # 混合分数
            combined_score = alpha * (1 - vector_score) + (1 - alpha) * keyword_score
            combined_scores[doc_id] = {
                'document': result['document'],
                'vector_score': vector_score,
                'keyword_score': keyword_score,
                'combined_score': combined_score,
                'metadata': result['metadata']
            }
        
        # 按混合分数排序
        sorted_results = sorted(
            combined_scores.values(),
            key=lambda x: x['combined_score'],
            reverse=True
        )[:k]
        
        return {
            'query': query,
            'retrieved_documents': sorted_results,
            'total_found': len(sorted_results),
            'search_type': 'hybrid'
        }
    
    def _keyword_search(self, query: str, k: int) -> List[Dict]:
        """
        简单的关键词搜索
        
        Args:
            query: 查询文本
            k: 返回文档数量
            
        Returns:
            关键词搜索结果
        """
        query_words = set(query.lower().split())
        results = []
        
        for i, doc in enumerate(self.vector_store.documents):
            doc_text = doc.text.lower()
            matches = sum(1 for word in query_words if word in doc_text)
            
            if matches > 0:
                score = matches / len(query_words)
                results.append({
                    'document': doc,
                    'score': score,
                    'metadata': self.vector_store.metadata[i]
                })
        
        # 按匹配分数排序
        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:k]
    
    def get_retrieval_stats(self) -> Dict[str, Any]:
        """
        获取检索统计信息
        
        Returns:
            统计信息字典
        """
        vector_stats = self.vector_store.get_stats()
        
        return {
            'vector_store_stats': vector_stats,
            'embedding_model': 'sentence-transformers/all-MiniLM-L6-v2',
            'retrieval_methods': ['vector_similarity', 'keyword_matching', 'hybrid']
        }
