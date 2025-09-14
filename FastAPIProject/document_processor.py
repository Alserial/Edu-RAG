"""
文档处理模块 - 负责文档加载、分块和向量化
支持PDF、图片OCR、文本文件等多种格式
"""
import os
import tiktoken
import logging
import io
from typing import List, Dict, Any, Optional
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.document_loaders import PyPDFLoader, UnstructuredPDFLoader
from langchain_community.document_loaders import TextLoader
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_core.documents import Document
import numpy as np

# OCR相关导入
try:
    from PIL import Image
    import pytesseract
    import fitz  # PyMuPDF
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False
    print("警告: OCR功能不可用，请安装 pytesseract, Pillow, PyMuPDF")

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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
        加载文档，支持PDF、图片OCR、文本文件
        
        Args:
            file_path: 文档路径
            
        Returns:
            Document对象列表
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")

        file_extension = os.path.splitext(file_path)[1].lower()
        logger.info(f"正在处理文件: {file_path}, 格式: {file_extension}")

        try:
            if file_extension == '.txt':
                return self._load_text_file(file_path)
            elif file_extension == '.pdf':
                return self._load_pdf_file(file_path)
            elif file_extension in ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff']:
                return self._load_image_file(file_path)
            else:
                raise ValueError(f"不支持的文件格式: {file_extension}")
        except Exception as e:
            logger.error(f"加载文档失败 {file_path}: {str(e)}")
            raise

    def _load_text_file(self, file_path: str) -> List[Document]:
        """加载文本文件"""
        try:
            loader = TextLoader(file_path, encoding='utf-8')
            return loader.load()
        except Exception as e:
            # 尝试其他编码
            try:
                loader = TextLoader(file_path, encoding='gbk')
                return loader.load()
            except:
                raise e

    def _load_pdf_file(self, file_path: str) -> List[Document]:
        """加载PDF文件，支持包含图片的PDF"""
        documents = []
        
        try:
            # 方法1: 尝试使用PyPDFLoader（快速，但可能无法处理图片）
            logger.info("尝试使用PyPDFLoader加载PDF...")
            loader = PyPDFLoader(file_path)
            documents = loader.load()
            logger.info(f"PyPDFLoader成功加载 {len(documents)} 页")
            
            # 检查是否有空内容，如果有则尝试OCR
            empty_pages = [i for i, doc in enumerate(documents) if not doc.page_content.strip()]
            if empty_pages and OCR_AVAILABLE:
                logger.info(f"发现 {len(empty_pages)} 页空内容，尝试OCR处理...")
                ocr_documents = self._extract_text_from_pdf_with_ocr(file_path, empty_pages)
                # 替换空页面
                for i, ocr_doc in zip(empty_pages, ocr_documents):
                    if i < len(documents):
                        documents[i] = ocr_doc
                        
        except Exception as e:
            logger.warning(f"PyPDFLoader失败: {str(e)}")
            
            # 方法2: 如果PyPDFLoader失败，尝试使用UnstructuredPDFLoader
            try:
                logger.info("尝试使用UnstructuredPDFLoader...")
                loader = UnstructuredPDFLoader(file_path)
                documents = loader.load()
                logger.info(f"UnstructuredPDFLoader成功加载 {len(documents)} 页")
            except Exception as e2:
                logger.warning(f"UnstructuredPDFLoader也失败: {str(e2)}")
                
                # 方法3: 如果都失败且支持OCR，尝试完全OCR处理
                if OCR_AVAILABLE:
                    logger.info("尝试完全OCR处理PDF...")
                    documents = self._extract_text_from_pdf_with_ocr(file_path)
                else:
                    raise Exception(f"所有PDF加载方法都失败: PyPDFLoader({str(e)}), UnstructuredPDFLoader({str(e2)})")

        return documents

    def _load_image_file(self, file_path: str) -> List[Document]:
        """加载图片文件并使用OCR提取文字"""
        if not OCR_AVAILABLE:
            raise ImportError("OCR功能不可用，请安装 pytesseract, Pillow, PyMuPDF")
        
        try:
            # 使用pytesseract进行OCR
            image = Image.open(file_path)
            text = pytesseract.image_to_string(image, lang='chi_sim+eng')
            
            if not text.strip():
                logger.warning(f"图片 {file_path} 中未检测到文字")
                text = f"[图片文件: {os.path.basename(file_path)} - 未检测到文字内容]"
            
            document = Document(
                page_content=text,
                metadata={
                    'source': file_path,
                    'page': 0,
                    'file_type': 'image',
                    'ocr_processed': True
                }
            )
            
            logger.info(f"OCR成功提取文字，长度: {len(text)} 字符")
            return [document]
            
        except Exception as e:
            logger.error(f"OCR处理图片失败 {file_path}: {str(e)}")
            # 返回一个包含错误信息的文档
            return [Document(
                page_content=f"[图片文件: {os.path.basename(file_path)} - OCR处理失败: {str(e)}]",
                metadata={
                    'source': file_path,
                    'page': 0,
                    'file_type': 'image',
                    'ocr_processed': False,
                    'error': str(e)
                }
            )]

    def _extract_text_from_pdf_with_ocr(self, file_path: str, page_numbers: Optional[List[int]] = None) -> List[Document]:
        """使用OCR从PDF中提取文字"""
        if not OCR_AVAILABLE:
            raise ImportError("OCR功能不可用")
        
        documents = []
        
        try:
            # 使用PyMuPDF打开PDF
            pdf_document = fitz.open(file_path)
            total_pages = pdf_document.page_count
            
            # 如果没有指定页面，处理所有页面
            if page_numbers is None:
                page_numbers = list(range(total_pages))
            
            logger.info(f"开始OCR处理PDF，总页数: {total_pages}, 处理页面: {page_numbers}")
            
            for page_num in page_numbers:
                if page_num >= total_pages:
                    continue
                    
                try:
                    page = pdf_document[page_num]
                    
                    # 首先尝试提取文本
                    text = page.get_text()
                    
                    # 如果文本为空或很少，尝试OCR
                    if not text.strip() or len(text.strip()) < 50:
                        logger.info(f"页面 {page_num} 文本内容较少，尝试OCR...")
                        
                        # 将页面转换为图片
                        mat = fitz.Matrix(2.0, 2.0)  # 放大2倍提高OCR精度
                        pix = page.get_pixmap(matrix=mat)
                        img_data = pix.tobytes("png")
                        
                        # 使用PIL打开图片
                        image = Image.open(io.BytesIO(img_data))
                        
                        # OCR处理
                        ocr_text = pytesseract.image_to_string(image, lang='chi_sim+eng')
                        
                        if ocr_text.strip():
                            text = ocr_text
                            logger.info(f"页面 {page_num} OCR成功，提取文字长度: {len(text)}")
                        else:
                            text = f"[页面 {page_num} - OCR未检测到文字内容]"
                            logger.warning(f"页面 {page_num} OCR未检测到文字")
                    else:
                        logger.info(f"页面 {page_num} 文本提取成功，长度: {len(text)}")
                    
                    # 创建文档对象
                    document = Document(
                        page_content=text,
                        metadata={
                            'source': file_path,
                            'page': page_num,
                            'file_type': 'pdf',
                            'ocr_processed': not text.strip() or len(text.strip()) < 50
                        }
                    )
                    documents.append(document)
                    
                except Exception as e:
                    logger.error(f"处理页面 {page_num} 失败: {str(e)}")
                    # 添加错误页面
                    documents.append(Document(
                        page_content=f"[页面 {page_num} - 处理失败: {str(e)}]",
                        metadata={
                            'source': file_path,
                            'page': page_num,
                            'file_type': 'pdf',
                            'error': str(e)
                        }
                    ))
            
            pdf_document.close()
            logger.info(f"PDF OCR处理完成，成功处理 {len(documents)} 页")
            
        except Exception as e:
            logger.error(f"PDF OCR处理失败: {str(e)}")
            raise
        
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
