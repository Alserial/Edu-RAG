"""
RAG系统测试脚本
"""
import requests
import json
import time
import os
from typing import Dict, Any

# API基础URL
BASE_URL = "http://127.0.0.1:8000"

def test_api_endpoint(endpoint: str, method: str = "GET", data: Dict = None) -> Dict[str, Any]:
    """测试API端点"""
    url = f"{BASE_URL}{endpoint}"
    
    try:
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data)
        else:
            raise ValueError(f"不支持的HTTP方法: {method}")
        
        response.raise_for_status()
        return {
            "success": True,
            "status_code": response.status_code,
            "data": response.json()
        }
    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "error": str(e),
            "status_code": getattr(e.response, 'status_code', None) if hasattr(e, 'response') else None
        }

def test_rag_system():
    """测试RAG系统完整流程"""
    print("🚀 开始测试RAG系统...")
    
    # 1. 测试根路径
    print("\n1. 测试根路径...")
    result = test_api_endpoint("/")
    if result["success"]:
        print("✅ 根路径测试成功")
        print(f"   响应: {result['data']['message']}")
    else:
        print(f"❌ 根路径测试失败: {result['error']}")
        return
    
    # 2. 测试健康检查
    print("\n2. 测试健康检查...")
    result = test_api_endpoint("/health")
    if result["success"]:
        print("✅ 健康检查成功")
        print(f"   系统状态: {result['data']}")
    else:
        print(f"❌ 健康检查失败: {result['error']}")
    
    # 3. 测试系统信息
    print("\n3. 测试系统信息...")
    result = test_api_endpoint("/info")
    if result["success"]:
        print("✅ 系统信息获取成功")
        print(f"   文档数量: {result['data']['system_status']['document_count']}")
    else:
        print(f"❌ 系统信息获取失败: {result['error']}")
    
    # 4. 测试文档上传
    print("\n4. 测试文档上传...")
    sample_files = [
        "sample_documents/sample1.txt",
        "sample_documents/sample2.txt",
        "sample_documents/sample3.txt"
    ]
    
    # 检查示例文件是否存在
    existing_files = []
    for file_path in sample_files:
        if os.path.exists(file_path):
            existing_files.append(file_path)
        else:
            print(f"⚠️  示例文件不存在: {file_path}")
    
    if existing_files:
        upload_data = {"file_paths": existing_files}
        result = test_api_endpoint("/upload", "POST", upload_data)
        if result["success"]:
            print("✅ 文档上传成功")
            print(f"   添加文档数: {result['data']['documents_added']}")
            print(f"   创建块数: {result['data']['chunks_created']}")
        else:
            print(f"❌ 文档上传失败: {result['error']}")
            return
    else:
        print("❌ 没有可用的示例文件")
        return
    
    # 5. 测试查询功能
    print("\n5. 测试查询功能...")
    test_queries = [
        "什么是人工智能？",
        "机器学习有哪些类型？",
        "深度学习的主要应用领域是什么？",
        "神经网络的基本结构是什么？"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n   查询 {i}: {query}")
        query_data = {
            "question": query,
            "k": 3,
            "template_type": "qa"
        }
        result = test_api_endpoint("/query", "POST", query_data)
        if result["success"]:
            print(f"   ✅ 查询成功")
            print(f"   答案: {result['data']['answer'][:200]}...")
            print(f"   检索文档数: {result['data']['retrieval_info']['documents_retrieved']}")
        else:
            print(f"   ❌ 查询失败: {result['error']}")
    
    # 6. 测试总结功能
    print("\n6. 测试总结功能...")
    summary_data = {"query": "请总结人工智能技术的发展历程"}
    result = test_api_endpoint("/summary", "POST", summary_data)
    if result["success"]:
        print("✅ 总结功能成功")
        print(f"   总结: {result['data']['summary'][:300]}...")
    else:
        print(f"❌ 总结功能失败: {result['error']}")
    
    # 7. 测试分析功能
    print("\n7. 测试分析功能...")
    analysis_data = {"query": "分析深度学习的优势和挑战"}
    result = test_api_endpoint("/analysis", "POST", analysis_data)
    if result["success"]:
        print("✅ 分析功能成功")
        print(f"   分析: {result['data']['analysis'][:300]}...")
    else:
        print(f"❌ 分析功能失败: {result['error']}")
    
    # 8. 测试保存系统
    print("\n8. 测试保存系统...")
    result = test_api_endpoint("/save", "POST")
    if result["success"]:
        print("✅ 系统保存成功")
        print(f"   消息: {result['data']['message']}")
    else:
        print(f"❌ 系统保存失败: {result['error']}")
    
    print("\n🎉 RAG系统测试完成！")

def test_error_cases():
    """测试错误情况"""
    print("\n🔍 测试错误情况...")
    
    # 测试查询空系统
    print("\n1. 测试查询空系统...")
    query_data = {"question": "测试问题"}
    result = test_api_endpoint("/query", "POST", query_data)
    if not result["success"]:
        print("✅ 空系统查询正确返回错误")
    else:
        print("❌ 空系统查询应该返回错误")
    
    # 测试上传不存在的文件
    print("\n2. 测试上传不存在的文件...")
    upload_data = {"file_paths": ["不存在的文件.txt"]}
    result = test_api_endpoint("/upload", "POST", upload_data)
    if not result["success"]:
        print("✅ 不存在文件上传正确返回错误")
    else:
        print("❌ 不存在文件上传应该返回错误")

def main():
    """主函数"""
    print("=" * 50)
    print("RAG系统API测试")
    print("=" * 50)
    
    # 检查服务器是否运行
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        print("✅ 服务器正在运行")
    except requests.exceptions.RequestException:
        print("❌ 服务器未运行，请先启动服务器：")
        print("   uvicorn main:app --reload")
        return
    
    # 运行测试
    test_rag_system()
    test_error_cases()
    
    print("\n" + "=" * 50)
    print("测试完成")
    print("=" * 50)

if __name__ == "__main__":
    main()
