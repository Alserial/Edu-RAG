# RAG系统 (Retrieval-Augmented Generation)

一个基于FastAPI的检索增强生成系统，支持文档处理、向量存储、相似性搜索和智能问答。

## ✨ 功能特性

- 📄 **多格式文档处理**: 支持TXT、PDF、图片文件（PNG、JPG、JPEG、GIF、BMP、TIFF）
- 🔍 **智能OCR识别**: 自动识别PDF和图片中的文字内容
- 🔍 **智能检索**: 基于FAISS的向量相似性搜索
- 🤖 **多模式生成**: 问答、总结、分析三种智能模式
- 🌐 **现代化前端**: 美观的Web界面，支持拖拽上传
- 🌐 **RESTful API**: 完整的FastAPI接口
- 💾 **持久化存储**: 支持向量索引的保存和加载
- 🗄️ **数据库管理**: 完整的数据库备份、恢复、监控和健康检查
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

## 🚀 快速开始

### 方法一：一键启动（推荐）

```bash
# 启动后端服务 + 前端界面
python start_frontend.py
```

这个命令会：
- 自动启动FastAPI后端服务
- 在浏览器中打开前端界面
- 提供详细的使用说明

### 方法二：分别启动

#### 1. 安装依赖

```bash
pip install -r requirements.txt
```

#### 2. 安装OCR依赖（可选，用于处理图片和扫描PDF）

```bash
# 使用安装脚本（推荐）
python install_ocr_deps.py

# 或手动安装
pip install pytesseract Pillow PyMuPDF unstructured
```

#### 3. 配置环境变量

复制环境变量模板文件：

```bash
# 方法1：使用 .env.example（推荐）
cp .env.example .env

# 方法2：使用 env_example.txt
cp env_example.txt .env
```

编辑 `.env` 文件，设置你的API密钥：

```bash
# 必须配置：DeepSeek API密钥
DEEPSEEK_API_KEY=your_deepseek_api_key_here

# 可选配置：其他参数
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
LLM_MODEL=deepseek-chat
VECTOR_STORE_PATH=./vector_store
```

**⚠️ 重要**: `.env` 文件包含敏感信息，已被添加到 `.gitignore` 中，不会被提交到git仓库。

#### 4. 启动后端服务

```bash
# 方法1：使用启动脚本
python start_server.py

# 方法2：直接使用uvicorn
uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

#### 5. 打开前端界面

```bash
# 在浏览器中打开
open frontend.html
# 或直接双击 frontend.html 文件
```

## 🌐 访问地址

- **前端界面**: `frontend.html` (本地文件)
- **后端API**: `http://127.0.0.1:8000`
- **API文档**: `http://127.0.0.1:8000/docs`

## 📚 使用指南

### 前端界面使用

1. **上传文档**:
   - 拖拽文件到上传区域
   - 或点击选择文件
   - 支持多种格式：TXT、PDF、图片

2. **智能查询**:
   - 输入问题
   - 选择模板类型（问答/总结/分析）
   - 调整检索文档数量
   - 点击查询按钮

3. **系统管理**:
   - 保存系统状态
   - 加载已保存的状态
   - 清空系统数据

## 🔌 API接口

### 基础接口

- `GET /` - 系统信息和接口列表
- `GET /health` - 健康检查
- `GET /info` - 详细系统状态

### 文档管理

- `POST /upload` - 上传文档（文件路径）
- `POST /upload-files` - 上传文档（文件内容）
- `POST /save` - 保存系统状态
- `POST /load` - 加载系统状态
- `POST /clear` - 清空系统

### 智能问答

- `POST /query` - 查询文档（问答模式）
- `POST /summary` - 总结文档
- `POST /analysis` - 分析文档

## 💡 使用示例

### 前端使用（推荐）

1. **启动系统**:
   ```bash
   python start_frontend.py
   ```

2. **上传文档**:
   - 拖拽PDF、图片或文本文件到上传区域
   - 点击"上传文档"按钮
   - 等待处理完成

3. **智能查询**:
   - 在查询框输入问题
   - 选择模板类型（问答/总结/分析）
   - 调整检索文档数量
   - 点击"查询"按钮

### API调用示例

#### 1. 上传文档（文件路径）

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

#### 2. 上传文档（文件内容）

```bash
curl -X POST "http://127.0.0.1:8000/upload-files" \
     -F "files=@document.pdf"
```

#### 3. 查询文档

```bash
curl -X POST "http://127.0.0.1:8000/query" \
     -H "Content-Type: application/json" \
     -d '{
       "question": "什么是人工智能？",
       "k": 5,
       "template_type": "qa"
     }'
```

#### 4. 总结文档

```bash
curl -X POST "http://127.0.0.1:8000/summary" \
     -H "Content-Type: application/json" \
     -d '{
       "query": "请总结主要内容"
     }'
```

#### 5. 分析文档

```bash
curl -X POST "http://127.0.0.1:8000/analysis" \
     -H "Content-Type: application/json" \
     -d '{
       "query": "分析技术优势"
     }'
```

### 数据库管理API

#### 1. 数据库统计

```bash
curl -X GET "http://127.0.0.1:8000/db/stats"
```

#### 2. 健康检查

```bash
curl -X GET "http://127.0.0.1:8000/db/health"
```

#### 3. 创建备份

```bash
curl -X POST "http://127.0.0.1:8000/db/backup" \
     -H "Content-Type: application/json" \
     -d '{
       "name": "backup_name"
     }'
```

#### 4. 恢复备份

```bash
curl -X POST "http://127.0.0.1:8000/db/restore" \
     -H "Content-Type: application/json" \
     -d '{
       "backup_name": "backup_name"
     }'
```

#### 5. 列出备份

```bash
curl -X GET "http://127.0.0.1:8000/db/backups"
```

#### 6. 清理旧备份

```bash
curl -X POST "http://127.0.0.1:8000/db/cleanup" \
     -H "Content-Type: application/json" \
     -d '{
       "keep_count": 5
     }'
```

## 🧪 测试

### 运行测试脚本

```bash
# 基础功能测试
python test_rag.py

# 文件上传测试
python test_upload.py

# 数据库管理测试
python test_db_management.py

# 完整系统测试
python test.py
```

### 使用HTTP文件测试

在VS Code或其他支持HTTP文件的编辑器中打开 `test_main.http`，逐个执行测试请求。

### 前端界面测试

1. 启动前端界面
2. 上传测试文档
3. 尝试不同的问题和模板类型
4. 测试系统管理功能

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

## 📁 项目结构

```text
FastAPIProject/
├── main.py                    # FastAPI应用主文件
├── rag_system.py             # RAG系统主控制器
├── document_processor.py     # 文档处理模块（支持OCR）
├── vector_store.py           # 向量存储模块
├── retriever.py              # 检索模块
├── generator.py              # 生成模块
├── database_manager.py       # 数据库管理模块
├── frontend.html             # 前端界面
├── db_admin.html             # 数据库管理界面
├── start_frontend.py         # 一键启动脚本
├── start_server.py           # 后端启动脚本
├── install_ocr_deps.py       # OCR依赖安装脚本
├── requirements.txt          # 依赖包列表
├── test_rag.py              # 基础功能测试
├── test_upload.py            # 文件上传测试
├── test_db_management.py     # 数据库管理测试
├── test.py                  # 完整系统测试
├── test_main.http           # HTTP测试文件
├── env_example.txt          # 环境变量示例
├── .env.example             # 环境变量模板
├── .gitignore               # Git忽略文件
├── README.md                # 项目说明
├── DB_MANAGEMENT_README.md  # 数据库管理说明
├── FRONTEND_README.md       # 前端使用说明
├── OCR_UPDATE_README.md     # OCR功能说明
├── UPLOAD_FIX_README.md     # 上传功能修复说明
├── vector_store/            # 向量数据库存储
├── backups/                 # 数据库备份存储
└── sample_documents/        # 示例文档
    ├── sample1.txt
    ├── sample2.txt
    └── sample3.txt
```

## ⚠️ 注意事项

1. **API密钥**: 确保设置正确的DeepSeek API密钥
2. **OCR依赖**: 如需处理图片和扫描PDF，需安装OCR相关依赖
3. **内存使用**: 大文档和大量向量会消耗较多内存
4. **模型下载**: 首次运行会自动下载嵌入模型
5. **文件格式**: 支持TXT、PDF、图片文件（PNG、JPG、JPEG、GIF、BMP、TIFF）
6. **中文支持**: 系统对中文文档有良好的支持
7. **文件大小**: 建议单个文件不超过50MB

## 🔧 故障排除

### 常见问题

1. **API密钥错误**: 检查 `.env` 文件中的API密钥是否正确
2. **OCR功能不可用**: 运行 `python install_ocr_deps.py` 安装OCR依赖
3. **文件上传失败**: 检查文件格式和大小，确保网络连接正常
4. **模型下载失败**: 检查网络连接，可能需要代理
5. **内存不足**: 减少文档大小或分块大小
6. **文件路径错误**: 确保文档路径正确且文件存在

### 快速诊断

```bash
# 检查系统状态
curl http://127.0.0.1:8000/health

# 测试文件上传
python test_upload.py

# 检查OCR依赖
python -c "import pytesseract, PIL, fitz; print('OCR依赖正常')"
```

### 日志查看

启动服务时会显示详细的日志信息，包括：

- 模型加载状态
- 文档处理进度
- OCR处理状态
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

## 🎯 快速开始总结

### 最简单的启动方式

```bash
# 1. 克隆项目
git clone <your-repo-url>
cd FastAPIProject

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置API密钥
cp env_example.txt .env
# 编辑 .env 文件，设置 DEEPSEEK_API_KEY

# 4. 一键启动（推荐）
python start_frontend.py
```

### 处理图片和扫描PDF

```bash
# 安装OCR依赖
python install_ocr_deps.py

# 然后正常启动即可
python start_frontend.py
```

### 使用步骤

1. **启动系统**: `python start_frontend.py`
2. **上传文档**: 拖拽文件到上传区域
3. **智能查询**: 输入问题，选择模板类型
4. **查看结果**: 在结果区域查看AI回答

## 🤝 贡献

欢迎提交Issue和Pull Request来改进这个项目！

## 📄 许可证

MIT License
