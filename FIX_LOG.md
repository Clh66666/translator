# 修复记录 (FIX_LOG)

### 1. 依赖包问题
**静态分析**
- **问题**: requirements.txt 中包名错误
  - `request` → 应该是 `requests`
  - `tdqm` → 应该是 `tqdm`
  - `huggingface` → 应该是 `huggingface_hub`
- **问题**: 版本过旧
  - `openai==0.27.0` → API 接口已过时
  - `python-dotenv==0.1.0` → 版本太旧
- **问题**: 不必要的依赖
  - `tensorflow==1.15.0` → 翻译任务不需要
**初步更改**
pandas==2.0.0
numpy
requests==2.25.0
openai==1.0.0
tqdm
huggingface_hub=0.20.0
python-dotenv==0.19.0
tenacity  # 用于重试机制
**实际验证更改是否正确**
新创建python环境translator_env，安装改后的依赖文件，全部正确安装，无冲突
**运行时的验证**
报错 pandas 和 numpy 版本不兼容
**再次更改**
pandas==1.5.3
numpy==1.23.5
requests==2.31.0
openai==1.1.0
tqdm
huggingface_hub==0.17.3
python-dotenv==1.0.0
tenacity==8.2.3

### 2.代码问题
- **问题1**：头文件导入问题，导入错误的依赖文件
  - `import request``import qtmd`改为`import requests``import tqdm`
- **问题2**：假token、硬编码问题
  - 修改translator_legacy.py，使其能从环境变量里读取token
  - 配置.env文件，导入自己的token
  - 安全保护：.gitignore 已更新，确保 token 不会被意外提交
- **问题3**：base_url 已经过时
  - 改成`https://router.huggingface.co/hf-inference/v1/openai`，且使用httpx客户端
- **问题4**：模型修正
  - 改成`model_name = "meta-llama/Llama-3.1-8B-Instruct:fastest"`
- **问题5**：Prompt 优化
  - 改为：
  ```python
  messages=[
                {"role": "system", "content": "你是一个专业的学术论文翻译专家。请将英文论文准确翻译成中文，保持学术语气和专业性。"},
                {"role": "user", "content": f"请翻译以下论文摘要：\n\n{text}"}
            ],
  ```
- **问题6**：参数修正
  - `temperature=100`:temperature 应该在 0-1 之间,来控制输出随机性，越接近1越随机。修正为0.3，保证一定的随机性。
  - `max_tokens=20`:20个token约为10中文字符，不够翻译论文摘要，改为2048。
- **异常处理**：添加 tenacity 重试机制
  - 在头文件添加`from tenacity import retry, stop_after_attempt, wait_exponential`
  - def translate_text(text)函数前添加装饰器：@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
  - 最多重试3次，每次失败后分别等待4\8\10秒
- **main函数**：需修改延迟时间和文件处理逻辑、引入进度显示
  - 用 tqdm 显示进度条
  - 删除错误的文件写入，改为读取iccv2025.csv
  - 添加正确的结果保存，将结果添加到列表中，而不是直接写入文件
  - 设置合理的延迟时间，1秒而不是1000秒
  - 设置正确的读取和结果显示格式
  - 其他操作是为了增强程序的可调试性
- **断点续传逻辑**：
  - 在头文件添加`import json`
  - `translate_text`函数前添加进度管理函数`save_progress`，`load_progress`
  - 修改main函数使其能从断点处读取论文

- **3.运行时出现的问题**
- **库依赖冲突**
  - 返回问题1重新更改并重装依赖
- **httpx版本错误问题**：报错argument `proxies`
  - 卸载0.28.1版本的httpx，重装0.27.2版本的