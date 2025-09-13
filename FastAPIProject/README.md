# RAG系统 (Retrieval-Augmented Generation)

一个基于FastAPI的检索增强生成系统，支持文档处理、向量存储、相似性搜索和智能问答。

## 功能特性

- 📄 **文档处理**: 支持TXT和PDF文档的加载、分块和向量化
- 🔍 **智能检索**: 基于FAISS的向量相似性搜索
- 🤖 **智能生成**: 集成DeepSeek等大语言模型
- 🌐 **RESTful API**: 完整的FastAPI接口
- 💾 **持久化存储**: 支持向量索引的保存和加载
- 🔧 **灵活配置**: 可自定义分块大小、模型等参数

## 系统架构

```text
RAG系统
├── 文档处理模块 (document_processor.py)
│   ├── 文档加载 (TXT, PDF)
│   ├── 文本分块
│   └── 向量化 (sentence-transformers)
├── 向量存储模块 (vector_store.py)
│   ├── FAISS索引
│   ├── 向量存储
│   └── 持久化
├── 检索模块 (retriever.py)
│   ├── 相似性搜索
│   ├── 混合搜索
│   └── 上下文检索
├── 生成模块 (generator.py)
│   ├── LLM集成
│   ├── 提示模板
│   └── 答案生成
└── 主控制器 (rag_system.py)
    ├── 系统集成
    ├── 流程控制
    └── 状态管理
```

## 安装和配置

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

复制 `env_example.txt` 为 `.env` 并配置API密钥：

```bash
cp env_example.txt .env
```

编辑 `.env` 文件，设置你的DeepSeek API密钥：

```bash
DEEPSEEK_API_KEY=your_deepseek_api_key_here
```

### 3. 启动服务

```bash
uvicorn main:app --reload
```

服务将在 `http://127.0.0.1:8000` 启动。

## API接口

### 基础接口

- `GET /` - 系统信息
- `GET /health` - 健康检查
- `GET /info` - 系统状态

### 文档管理

- `POST /upload` - 上传文档
- `POST /save` - 保存系统状态
- `POST /load` - 加载系统状态
- `POST /clear` - 清空系统

### 智能问答

- `POST /query` - 查询文档
- `POST /summary` - 总结文档
- `POST /analysis` - 分析文档

## 使用示例

### 1. 上传文档

```bash
curl -X POST "http://127.0.0.1:8000/upload" \
     -H "Content-Type: application/json" \
     -d '{
       "file_paths": [
         "sample_documents/sample1.txt",
         "sample_documents/sample2.txt"
       ]
     }'
```

### 2. 查询文档

```bash
curl -X POST "http://127.0.0.1:8000/query" \
     -H "Content-Type: application/json" \
     -d '{
       "question": "什么是人工智能？",
       "k": 5,
       "template_type": "qa"
     }'
```

### 3. 总结文档

```bash
curl -X POST "http://127.0.0.1:8000/summary" \
     -H "Content-Type: application/json" \
     -d '{
       "query": "请总结主要内容"
     }'
```

## 测试

### 运行测试脚本

```bash
python test_rag.py
```

### 使用HTTP文件测试

在VS Code或其他支持HTTP文件的编辑器中打开 `test_main.http`，逐个执行测试请求。

## 配置参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| CHUNK_SIZE | 1000 | 文档分块大小 |
| CHUNK_OVERLAP | 200 | 分块重叠大小 |
| EMBEDDING_MODEL | sentence-transformers/all-MiniLM-L6-v2 | 嵌入模型 |
| LLM_MODEL | deepseek-chat | 大语言模型 |
| VECTOR_STORE_PATH | ./vector_store | 向量存储路径 |

## 支持的模型

### 嵌入模型

- sentence-transformers/all-MiniLM-L6-v2 (默认)
- 其他sentence-transformers模型

### 大语言模型

- DeepSeek Chat (默认)
- OpenAI GPT系列
- 其他兼容OpenAI API的模型

## 项目结构

```text
FastAPIProject/
├── main.py                 # FastAPI应用主文件
├── rag_system.py          # RAG系统主控制器
├── document_processor.py  # 文档处理模块
├── vector_store.py        # 向量存储模块
├── retriever.py           # 检索模块
├── generator.py           # 生成模块
├── requirements.txt       # 依赖包列表
├── test_rag.py           # 测试脚本
├── test_main.http        # HTTP测试文件
├── env_example.txt       # 环境变量示例
├── README.md             # 项目说明
└── sample_documents/     # 示例文档
    ├── sample1.txt
    ├── sample2.txt
    └── sample3.txt
```

## 注意事项

1. **API密钥**: 确保设置正确的DeepSeek API密钥
2. **内存使用**: 大文档和大量向量会消耗较多内存
3. **模型下载**: 首次运行会自动下载嵌入模型
4. **文件格式**: 目前支持TXT和PDF格式
5. **中文支持**: 系统对中文文档有良好的支持

## 故障排除

### 常见问题

1. **API密钥错误**: 检查 `.env` 文件中的API密钥是否正确
2. **模型下载失败**: 检查网络连接，可能需要代理
3. **内存不足**: 减少文档大小或分块大小
4. **文件路径错误**: 确保文档路径正确且文件存在

### 日志查看

启动服务时会显示详细的日志信息，包括：

- 模型加载状态
- 文档处理进度
- API请求日志
- 错误信息

## 扩展功能

系统设计为模块化架构，可以轻松扩展：

1. **添加新的文档格式**: 在 `document_processor.py` 中添加新的加载器
2. **集成新的嵌入模型**: 修改 `DocumentProcessor` 类
3. **添加新的检索策略**: 在 `retriever.py` 中实现新的检索方法
4. **支持新的LLM**: 在 `generator.py` 中添加新的模型支持

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request来改进这个项目！
