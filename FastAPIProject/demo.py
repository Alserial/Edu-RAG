#!/usr/bin/env python3
"""
RAG系统演示脚本
"""
import requests
import json
import time
import os
from pathlib import Path

BASE_URL = "http://127.0.0.1:8000"

def wait_for_server():
    """等待服务器启动"""
    print("⏳ 等待服务器启动...")
    for i in range(30):  # 最多等待30秒
        try:
            response = requests.get(f"{BASE_URL}/health", timeout=2)
            if response.status_code == 200:
                print("✅ 服务器已启动")
                return True
        except requests.exceptions.RequestException:
            pass
        time.sleep(1)
        print(f"   等待中... ({i+1}/30)")
    
    print("❌ 服务器启动超时")
    return False

def upload_sample_documents():
    """上传示例文档"""
    print("\n📄 上传示例文档...")
    
    sample_files = [
        "sample_documents/sample1.txt",
        "sample_documents/sample2.txt", 
        "sample_documents/sample3.txt"
    ]
    
    # 检查文件是否存在
    existing_files = [f for f in sample_files if os.path.exists(f)]
    
    if not existing_files:
        print("❌ 未找到示例文档")
        return False
    
    response = requests.post(f"{BASE_URL}/upload", json={"file_paths": existing_files})
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ 成功上传 {result['documents_added']} 个文档")
        print(f"   创建了 {result['chunks_created']} 个文档块")
        return True
    else:
        print(f"❌ 上传失败: {response.text}")
        return False

def demo_queries():
    """演示查询功能"""
    print("\n🔍 演示查询功能...")
    
    queries = [
        "什么是人工智能？",
        "机器学习有哪些类型？",
        "深度学习的应用领域有哪些？",
        "神经网络的基本结构是什么？"
    ]
    
    for i, query in enumerate(queries, 1):
        print(f"\n📝 查询 {i}: {query}")
        
        response = requests.post(f"{BASE_URL}/query", json={
            "question": query,
            "k": 3,
            "template_type": "qa"
        })
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                answer = result["answer"]
                print(f"🤖 回答: {answer[:200]}...")
                print(f"📊 检索到 {result['retrieval_info']['documents_retrieved']} 个相关文档")
            else:
                print(f"❌ 查询失败: {result.get('error', '未知错误')}")
        else:
            print(f"❌ 请求失败: {response.text}")

def demo_summary():
    """演示总结功能"""
    print("\n📋 演示总结功能...")
    
    response = requests.post(f"{BASE_URL}/summary", json={
        "query": "请总结人工智能技术的发展历程"
    })
    
    if response.status_code == 200:
        result = response.json()
        if result.get("success"):
            summary = result["summary"]
            print(f"📄 总结: {summary[:300]}...")
        else:
            print(f"❌ 总结失败: {result.get('error', '未知错误')}")
    else:
        print(f"❌ 请求失败: {response.text}")

def demo_analysis():
    """演示分析功能"""
    print("\n🔬 演示分析功能...")
    
    response = requests.post(f"{BASE_URL}/analysis", json={
        "query": "分析深度学习的优势和挑战"
    })
    
    if response.status_code == 200:
        result = response.json()
        if result.get("success"):
            analysis = result["analysis"]
            print(f"📊 分析: {analysis[:300]}...")
        else:
            print(f"❌ 分析失败: {result.get('error', '未知错误')}")
    else:
        print(f"❌ 请求失败: {response.text}")

def show_system_info():
    """显示系统信息"""
    print("\nℹ️  系统信息...")
    
    response = requests.get(f"{BASE_URL}/info")
    
    if response.status_code == 200:
        result = response.json()
        status = result["system_status"]
        print(f"📊 文档数量: {status['document_count']}")
        print(f"🔧 系统状态: {'已初始化' if status['initialized'] else '未初始化'}")
        print(f"💾 向量存储路径: {status['vector_store_path']}")
    else:
        print(f"❌ 获取系统信息失败: {response.text}")

def main():
    """主函数"""
    print("🎯 RAG系统演示")
    print("=" * 50)
    
    # 等待服务器启动
    if not wait_for_server():
        print("\n请先启动服务器:")
        print("python start_server.py")
        return
    
    # 上传文档
    if not upload_sample_documents():
        return
    
    # 显示系统信息
    show_system_info()
    
    # 演示查询功能
    demo_queries()
    
    # 演示总结功能
    demo_summary()
    
    # 演示分析功能
    demo_analysis()
    
    print("\n🎉 演示完成！")
    print("=" * 50)
    print("💡 提示:")
    print("   - 访问 http://127.0.0.1:8000/docs 查看API文档")
    print("   - 运行 python test_rag.py 进行完整测试")
    print("   - 使用 test_main.http 文件进行API测试")

if __name__ == "__main__":
    main()
