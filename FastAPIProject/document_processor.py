"""
文档处理模块 - 负责文档加载、分块和向量化
"""
import os
import tiktoken
from typing import List, Dict, Any
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.document_loaders import PyPDFLoader

from langchain_community.document_loaders import TextLoader
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_core.documents import Document
import numpy as np


class DocumentProcessor:
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        """
        初始化文档处理器
        
        Args:
            chunk_size: 文档分块大小
            chunk_overlap: 分块重叠大小
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

        # 初始化文本分割器
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )

        # 初始化嵌入模型
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'}
        )

        # 初始化tokenizer用于计算token数量
        self.tokenizer = tiktoken.get_encoding("cl100k_base")

    def load_document(self, file_path: str) -> List[Document]:
        """
        加载文档
        
        Args:
            file_path: 文档路径
            
        Returns:
            Document对象列表
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")

        file_extension = os.path.splitext(file_path)[1].lower()

        if file_extension == '.txt':
            loader = TextLoader(file_path, encoding='utf-8')
        elif file_extension == '.pdf':
            loader = PyPDFLoader(file_path)
        else:
            raise ValueError(f"不支持的文件格式: {file_extension}")

        documents = loader.load()
        return documents

    def split_documents(self, documents: List[Document]) -> List[Document]:
        """
        分割文档为小块
        
        Args:
            documents: 原始文档列表
            
        Returns:
            分割后的文档块列表
        """
        chunks = self.text_splitter.split_documents(documents)
        return chunks

    def create_embeddings(self, texts: List[str]) -> np.ndarray:
        """
        为文本创建嵌入向量
        
        Args:
            texts: 文本列表
            
        Returns:
            嵌入向量数组
        """
        embeddings = self.embeddings.embed_documents(texts)
        return np.array(embeddings)

    def process_document(self, file_path: str) -> Dict[str, Any]:
        """
        处理单个文档的完整流程
        
        Args:
            file_path: 文档路径
            
        Returns:
            包含文档块和嵌入向量的字典
        """
        # 加载文档
        documents = self.load_document(file_path)

        # 分割文档
        chunks = self.split_documents(documents)

        # 提取文本内容
        texts = [chunk.page_content for chunk in chunks]

        # 创建嵌入向量
        embeddings = self.create_embeddings(texts)

        # 准备元数据
        metadata = []
        for i, chunk in enumerate(chunks):
            metadata.append({
                'chunk_id': i,
                'source': chunk.metadata.get('source', file_path),
                'page': chunk.metadata.get('page', 0),
                'text_length': len(chunk.page_content),
                'token_count': len(self.tokenizer.encode(chunk.page_content))
            })

        return {
            'chunks': chunks,
            'texts': texts,
            'embeddings': embeddings,
            'metadata': metadata
        }

    def process_multiple_documents(self, file_paths: List[str]) -> Dict[str, Any]:
        """
        处理多个文档
        
        Args:
            file_paths: 文档路径列表
            
        Returns:
            合并后的文档处理结果
        """
        all_chunks = []
        all_texts = []
        all_embeddings = []
        all_metadata = []

        for file_path in file_paths:
            result = self.process_document(file_path)
            all_chunks.extend(result['chunks'])
            all_texts.extend(result['texts'])
            all_embeddings.append(result['embeddings'])
            all_metadata.extend(result['metadata'])

        # 合并所有嵌入向量
        if all_embeddings:
            combined_embeddings = np.vstack(all_embeddings)
        else:
            combined_embeddings = np.array([])

        return {
            'chunks': all_chunks,
            'texts': all_texts,
            'embeddings': combined_embeddings,
            'metadata': all_metadata
        }
