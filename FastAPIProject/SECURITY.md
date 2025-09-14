# 🔒 安全说明

## 环境变量安全

### ✅ 已保护的文件
以下文件包含敏感信息，已被添加到 `.gitignore` 中：

- `.env` - 包含API密钥和敏感配置
- `.env.local` - 本地环境变量
- `.env.production` - 生产环境变量
- `.env.staging` - 测试环境变量

### 📋 环境变量模板
使用以下模板文件配置环境变量：

- `.env.example` - 推荐使用（标准格式）
- `env_example.txt` - 备用模板

### 🔑 敏感信息
以下信息不应提交到git仓库：

- API密钥（DeepSeek、OpenAI等）
- 数据库连接字符串
- 密码和令牌
- 生产环境配置

## 配置步骤

### 1. 复制模板文件
```bash
cp .env.example .env
```

### 2. 编辑环境变量
```bash
# 编辑 .env 文件
nano .env
# 或
vim .env
```

### 3. 设置API密钥
```bash
DEEPSEEK_API_KEY=your_actual_api_key_here
```

### 4. 验证配置
```bash
# 检查环境变量是否正确加载
python -c "import os; print('API Key loaded:', bool(os.getenv('DEEPSEEK_API_KEY')))"
```

## 安全检查

### 验证.gitignore
```bash
# 检查 .env 文件是否被忽略
git status --ignored | grep .env
```

### 检查已跟踪文件
```bash
# 确保敏感文件未被跟踪
git ls-files | grep -E "\.(env|key|secret)"
```

## 最佳实践

### ✅ 推荐做法
1. **使用模板文件** - 提供 `.env.example` 作为参考
2. **本地配置** - 每个开发者创建自己的 `.env` 文件
3. **文档说明** - 在README中说明如何配置
4. **定期检查** - 确保敏感文件未被意外提交

### ❌ 避免做法
1. **不要提交** - 包含真实API密钥的文件
2. **不要硬编码** - 在代码中直接写入密钥
3. **不要分享** - 通过聊天工具分享敏感信息
4. **不要忽略** - 安全检查和代码审查

## 故障排除

### 问题1: 环境变量未加载
```bash
# 检查文件是否存在
ls -la .env

# 检查文件内容
cat .env

# 检查Python加载
python -c "from dotenv import load_dotenv; load_dotenv(); import os; print(os.getenv('DEEPSEEK_API_KEY'))"
```

### 问题2: API密钥无效
```bash
# 验证API密钥格式
python -c "import os; key=os.getenv('DEEPSEEK_API_KEY'); print('Key length:', len(key) if key else 0)"
```

### 问题3: 配置不生效
```bash
# 重启服务
python start_frontend.py
```

## 紧急情况

### 如果敏感信息被意外提交
1. **立即撤销**:
   ```bash
   git reset HEAD~1
   git push --force-with-lease
   ```

2. **更新密钥**:
   - 在服务提供商处重新生成API密钥
   - 更新本地 `.env` 文件

3. **清理历史**:
   ```bash
   git filter-branch --force --index-filter 'git rm --cached --ignore-unmatch .env' --prune-empty --tag-name-filter cat -- --all
   ```

## 联系支持

如果遇到安全问题，请：
1. 立即撤销相关提交
2. 更新所有敏感信息
3. 联系项目维护者

---

**记住**: 安全是每个人的责任！🔒
