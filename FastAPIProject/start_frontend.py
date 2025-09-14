#!/usr/bin/env python3
"""
启动RAG系统前端测试界面
"""
import webbrowser
import time
import subprocess
import sys
import os
from pathlib import Path

def start_backend():
    """启动后端服务"""
    print("🚀 启动RAG系统后端服务...")
    try:
        # 启动FastAPI服务器
        subprocess.Popen([
            sys.executable, "-m", "uvicorn", 
            "main:app", 
            "--host", "127.0.0.1", 
            "--port", "8000", 
            "--reload"
        ], cwd=os.path.dirname(os.path.abspath(__file__)))
        print("✅ 后端服务已启动: http://127.0.0.1:8000")
        return True
    except Exception as e:
        print(f"❌ 启动后端服务失败: {e}")
        return False

def start_frontend():
    """启动前端界面"""
    print("🌐 启动前端界面...")
    try:
        # 获取前端文件路径
        frontend_path = Path(__file__).parent / "frontend.html"
        frontend_url = f"file://{frontend_path.absolute()}"
        
        # 等待后端启动
        print("⏳ 等待后端服务启动...")
        time.sleep(3)
        
        # 打开浏览器
        webbrowser.open(frontend_url)
        print(f"✅ 前端界面已打开: {frontend_url}")
        print("\n📋 使用说明:")
        print("1. 首先点击'加载示例文档'来加载测试文档")
        print("2. 在查询框中输入问题，点击'查询'按钮")
        print("3. 可以尝试不同的模板类型：问答、总结、分析")
        print("4. 使用系统管理功能保存/加载/清空系统")
        print("\n💡 提示: 后端API文档可在 http://127.0.0.1:8000/docs 查看")
        return True
    except Exception as e:
        print(f"❌ 启动前端界面失败: {e}")
        return False

def main():
    """主函数"""
    print("=" * 50)
    print("🤖 RAG系统前端测试界面启动器")
    print("=" * 50)
    
    # 检查依赖
    try:
        import uvicorn
        import fastapi
    except ImportError:
        print("❌ 缺少必要依赖，请先安装:")
        print("pip install fastapi uvicorn")
        return
    
    # 启动后端
    if not start_backend():
        return
    
    # 启动前端
    if not start_frontend():
        return
    
    print("\n🎉 系统启动完成！")
    print("按 Ctrl+C 停止服务")
    
    try:
        # 保持程序运行
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n👋 正在关闭服务...")

if __name__ == "__main__":
    main()
