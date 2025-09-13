"""
生成模块 - 负责LLM集成和文本生成
"""
import os
from typing import List, Dict, Any, Optional
from langchain_core.documents import Document
from langchain_openai import OpenAI
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain.chains import LLMChain


from langchain_core.messages import HumanMessage

from langchain_core.messages import SystemMessage
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


class RAGGenerator:
    def __init__(self, model_name: str = "deepseek-chat", temperature: float = 0.7):
        """
        初始化RAG生成器
        
        Args:
            model_name: 模型名称
            temperature: 生成温度
        """
        self.model_name = model_name
        self.temperature = temperature

        # 初始化LLM
        self.llm = self._initialize_llm()

        # 定义提示模板
        self.prompt_templates = self._create_prompt_templates()

    def _initialize_llm(self):
        """初始化LLM模型"""
        api_key = os.environ.get("DEEPSEEK_API_KEY")
        if not api_key:
            raise ValueError("请设置DEEPSEEK_API_KEY环境变量")

        if "deepseek" in self.model_name.lower():
            return ChatOpenAI(
                model=self.model_name,
                temperature=self.temperature,
                openai_api_key=api_key,
                openai_api_base="https://api.deepseek.com"
            )
        else:
            return ChatOpenAI(
                model=self.model_name,
                temperature=self.temperature,
                openai_api_key=api_key
            )

    def _create_prompt_templates(self) -> Dict[str, PromptTemplate]:
        """创建提示模板"""
        templates = {
            "qa": PromptTemplate(
                input_variables=["context", "question"],
                template="""基于以下上下文信息回答问题。如果上下文中没有相关信息，请说明无法找到答案。

上下文信息：
{context}

问题：{question}

答案："""
            ),

            "summarize": PromptTemplate(
                input_variables=["context", "query"],
                template="""请基于以下上下文信息，针对查询"{query}"进行总结：

上下文信息：
{context}

总结："""
            ),

            "conversation": PromptTemplate(
                input_variables=["context", "question", "chat_history"],
                template="""你是一个智能助手，请基于提供的上下文信息回答问题。保持对话的自然流畅。

上下文信息：
{context}

对话历史：
{chat_history}

用户问题：{question}

助手回答："""
            ),

            "analysis": PromptTemplate(
                input_variables=["context", "query"],
                template="""请分析以下上下文信息，并针对查询"{query}"提供详细分析：

上下文信息：
{context}

分析结果："""
            )
        }
        return templates

    def generate_answer(self, question: str, context_documents: List[Document], 
                       template_type: str = "qa", max_context_length: int = 4000) -> Dict[str, Any]:
        """
        生成答案
        
        Args:
            question: 问题
            context_documents: 上下文文档
            template_type: 提示模板类型
            max_context_length: 最大上下文长度
            
        Returns:
            生成结果字典
        """
        # 准备上下文
        context = self._prepare_context(context_documents, max_context_length)

        # 选择提示模板
        if template_type not in self.prompt_templates:
            template_type = "qa"

        prompt_template = self.prompt_templates[template_type]

        # 创建LLM链
        llm_chain = LLMChain(llm=self.llm, prompt=prompt_template)

        # 生成答案
        try:
            if template_type == "conversation":
                # 对话模式需要特殊处理
                response = llm_chain.run(
                    context=context,
                    question=question,
                    chat_history=""  # 可以扩展为真正的对话历史
                )
            else:
                response = llm_chain.run(
                    context=context,
                    question=question
                )

            return {
                "answer": response,
                "question": question,
                "context_used": context,
                "template_type": template_type,
                "model": self.model_name,
                "success": True
            }
        except Exception as e:
            return {
                "answer": f"生成答案时出错: {str(e)}",
                "question": question,
                "context_used": context,
                "template_type": template_type,
                "model": self.model_name,
                "success": False,
                "error": str(e)
            }

    def generate_with_retrieval(self, question: str, retriever, k: int = 5, 
                               template_type: str = "qa") -> Dict[str, Any]:
        """
        结合检索生成答案
        
        Args:
            question: 问题
            retriever: 检索器实例
            k: 检索文档数量
            template_type: 提示模板类型
            
        Returns:
            完整的RAG结果
        """
        # 检索相关文档
        retrieval_results = retriever.retrieve_documents(question, k=k)

        # 提取文档
        context_documents = [result['document'] for result in retrieval_results['retrieved_documents']]

        # 生成答案
        generation_result = self.generate_answer(
            question, context_documents, template_type
        )

        # 合并结果
        return {
            "question": question,
            "answer": generation_result["answer"],
            "retrieval_results": retrieval_results,
            "generation_result": generation_result,
            "success": generation_result["success"]
        }

    def _prepare_context(self, documents: List[Document], max_length: int) -> str:
        """
        准备上下文文本
        
        Args:
            documents: 文档列表
            max_length: 最大长度
            
        Returns:
            格式化的上下文字符串
        """
        context_parts = []
        current_length = 0

        for i, doc in enumerate(documents):
            doc_text = f"文档 {i+1}:\n{doc.page_content}\n\n"

            if current_length + len(doc_text) > max_length:
                break

            context_parts.append(doc_text)
            current_length += len(doc_text)

        return "".join(context_parts)

    def generate_summary(self, documents: List[Document], query: str = "请总结主要内容") -> Dict[str, Any]:
        """
        生成文档总结
        
        Args:
            documents: 文档列表
            query: 总结查询
            
        Returns:
            总结结果
        """
        context = self._prepare_context(documents, 6000)  # 总结可以使用更多上下文

        try:
            llm_chain = LLMChain(llm=self.llm, prompt=self.prompt_templates["summarize"])
            summary = llm_chain.run(context=context, query=query)

            return {
                "summary": summary,
                "query": query,
                "document_count": len(documents),
                "success": True
            }
        except Exception as e:
            return {
                "summary": f"生成总结时出错: {str(e)}",
                "query": query,
                "document_count": len(documents),
                "success": False,
                "error": str(e)
            }

    def generate_analysis(self, documents: List[Document], query: str) -> Dict[str, Any]:
        """
        生成分析报告
        
        Args:
            documents: 文档列表
            query: 分析查询
            
        Returns:
            分析结果
        """
        context = self._prepare_context(documents, 6000)

        try:
            llm_chain = LLMChain(llm=self.llm, prompt=self.prompt_templates["analysis"])
            analysis = llm_chain.run(context=context, query=query)

            return {
                "analysis": analysis,
                "query": query,
                "document_count": len(documents),
                "success": True
            }
        except Exception as e:
            return {
                "analysis": f"生成分析时出错: {str(e)}",
                "query": query,
                "document_count": len(documents),
                "success": False,
                "error": str(e)
            }

    def get_model_info(self) -> Dict[str, Any]:
        """
        获取模型信息
        
        Returns:
            模型信息字典
        """
        return {
            "model_name": self.model_name,
            "temperature": self.temperature,
            "available_templates": list(self.prompt_templates.keys()),
            "api_base": "https://api.deepseek.com" if "deepseek" in self.model_name.lower() else "https://api.openai.com"
        }
