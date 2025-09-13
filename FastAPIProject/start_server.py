#!/usr/bin/env python3
"""
RAG系统启动脚本
"""
import os
import sys
import subprocess
from pathlib import Path

def check_requirements():
    """检查依赖是否安装"""
    try:
        import fastapi
        import uvicorn
        import openai
        import langchain
        import faiss
        import sentence_transformers
        print("✅ 所有依赖已安装")
        return True
    except ImportError as e:
        print(f"❌ 缺少依赖: {e}")
        print("请运行: pip install -r requirements.txt")
        return False

def check_env_file():
    """检查环境变量文件"""
    env_file = Path(".env")
    if not env_file.exists():
        print("⚠️  未找到 .env 文件")
        print("请复制 env_example.txt 为 .env 并配置API密钥")
        return False
    
    with open(env_file, 'r', encoding='utf-8') as f:
        content = f.read()
        if "your_deepseek_api_key_here" in content:
            print("⚠️  请在 .env 文件中设置正确的API密钥")
            return False
    
    print("✅ 环境变量配置正确")
    return True

def create_directories():
    """创建必要的目录"""
    directories = ["vector_store", "sample_documents"]
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
    print("✅ 目录结构已创建")

def main():
    """主函数"""
    print("🚀 启动RAG系统...")
    print("=" * 50)
    
    # 检查依赖
    if not check_requirements():
        sys.exit(1)
    
    # 检查环境变量
    if not check_env_file():
        sys.exit(1)
    
    # 创建目录
    create_directories()
    
    print("\n🎉 系统检查完成，启动服务器...")
    print("=" * 50)
    
    # 启动服务器
    try:
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "main:app", 
            "--reload", 
            "--host", "0.0.0.0", 
            "--port", "8000"
        ])
    except KeyboardInterrupt:
        print("\n👋 服务器已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
