# HF Paper Translator - 中文学术论文翻译器

## 项目简介

这是一个基于 Hugging Face Inference API 的学术论文翻译工具，能够批量将英文论文的标题和摘要翻译成中文。项目已修复所有依赖冲突和代码问题，支持断点续传和进度显示。

## 主要特性

- **批量翻译**: 自动处理 CSV 文件中的论文数据
- **断点续传**: 程序中断后可从上次位置继续
- **进度显示**: 实时显示翻译进度条
- **错误重试**: 自动重试失败的翻译请求
- **Token 安全**: 通过环境变量管理 API Token
- **工程化**: 完整的异常处理和日志记录

## 环境要求

- Python 3.8+
- Hugging Face Access Token

## 安装步骤

### 1. 克隆项目
```bash
git clone <your-repo-url>
cd BuggyPaperTranslator-main
```

### 2. 创建虚拟环境
```bash
python -m venv translator_env
translator_env\Scripts\activate  # Windows
# 或
source translator_env/bin/activate  # Linux/Mac
```

### 3. 安装依赖
```bash
pip install -r requirements_fixed.txt
```

### 4. 配置环境变量
创建 `.env` 文件并添加你的 Hugging Face Token：
```
HF_TOKEN=your_actual_hugging_face_token_here
```

> 获取 Token: 访问 [Hugging Face Settings](https://huggingface.co/settings/tokens)

## 使用方法

### 1. 准备数据
将论文数据保存为 `iccv2025.csv` 格式，包含以下列：
- `title`: 论文标题
- `authors`: 作者
- `abstract`: 摘要
- `date`: 日期
- `paper_url`: 论文链接
- `score`: 评分

### 2. 运行翻译
```bash
python translator_legacy.py
```

### 3. 查看结果
翻译完成后，结果将保存到 `result.csv` 文件中，包含原始数据和中文翻译。

## 技术栈

- **API**: Hugging Face Inference API (OpenAI 兼容接口)
- **模型**: `meta-llama/Llama-3.1-8B-Instruct:fastest`
- **核心库**:
  - `openai==1.1.0`
  - `pandas==1.5.3`
  - `numpy==1.23.5`
  - `tenacity==8.2.3` (重试机制)
  - `tqdm` (进度条)

## 配置说明

### 翻译参数
- **Temperature**: 0.3 (平衡翻译的准确性和流畅性)
- **Max Tokens**: 2048 (支持长文本翻译)
- **重试机制**: 最多重试3次，指数退避延迟
- **请求间隔**: 1秒 (避免 API 限制)

### 断点续传
- 程序每处理5篇论文自动保存进度到 `progress.json`
- 中断后重启会自动从上次位置继续
- 完成后自动删除进度文件

## 故障排除

### 常见问题

1. **FileNotFoundError**: 确保在正确的目录运行脚本
2. **API 连接错误**: 检查网络连接和 Token 有效性
3. **依赖冲突**: 使用提供的 `requirements_fixed.txt`

### 清理缓存
```bash
# 清除 Python 缓存
del /s /q *.pyc
rmdir /s /q __pycache__
```

## 项目结构

```
BuggyPaperTranslator-main/
├── translator_legacy.py    # 主程序
├── requirements_fixed.txt  # 依赖包列表
├── iccv2025.csv           # 输入数据
├── result.csv             # 输出结果 (运行后生成)
├── progress.json          # 进度文件 (运行时生成)
├── .env                   # 环境变量配置
├── FIX_LOG.md             # 修复记录
└── README.md              # 项目说明
```

## 注意事项

- 请勿在代码中硬编码 API Token
- 建议使用虚拟环境隔离依赖
- 翻译大量论文时注意 API 使用限制
- 确保 `.env` 文件不被提交到版本控制
