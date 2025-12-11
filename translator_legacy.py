import os
import time
import requests
import pandas as pd
from openai import OpenAI
from tqdm import tqdm
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential
import json

# 从环境变量读取 Hugging Face Token
load_dotenv()
HF_TOKEN = os.getenv("HF_TOKEN")

# 检查是否成功读取 token
if not HF_TOKEN:
    raise ValueError("错误：请在 .env 文件中设置 HF_TOKEN，或设置系统环境变量")
elif HF_TOKEN == "your_actual_hf_token_here":
    raise ValueError("错误：请在 .env 文件中将 your_actual_hf_token_here 替换为你的真实 Hugging Face token")

client = OpenAI(
    api_key=HF_TOKEN,
    base_url="https://router.huggingface.co/hf-inference/v1/openai"
)

def save_progress(index, results):
    """保存当前进度到文件"""
    progress = {
        "last_index": index,
        "results": results
    }
    with open("progress.json", "w", encoding='utf-8') as f:
        json.dump(progress, f, ensure_ascii=False, indent=2)

def load_progress():
    """从文件读取上次进度"""
    if os.path.exists("progress.json"):
        try:
            with open("progress.json", "r", encoding='utf-8') as f:
                return json.load(f)
        except:
            return {"last_index": 0, "results": []}
    return {"last_index": 0, "results": []}

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def translate_text(text):  # 用来调用API翻译传入的文本
    model_name = "meta-llama/Llama-3.1-8B-Instruct:fastest"

    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": "你是一个专业的学术论文翻译专家。请将英文论文准确翻译成中文，保持学术语气和专业性。"},
                {"role": "user", "content": f"请翻译以下论文摘要：\n\n{text}"}
            ],
            temperature=0.3,
            max_tokens=2048,
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error: {e}")
        return None


def main():
    # 获取脚本所在目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)  # 切换到脚本所在目录
    
    # 读取进度
    progress = load_progress()
    start_index = progress["last_index"]
    results = progress["results"]
    
    # 读取正确的数据文件
    df = pd.read_csv("iccv2025.csv")
    
    if start_index > 0:
        print(f"检测到进度文件，从第 {start_index + 1} 篇论文继续处理...")
    
    # 使用 tqdm 显示进度条，从断点开始
    for index, row in tqdm(df.iterrows(), total=len(df), desc="翻译进度"):
        # 跳过已处理的论文
        if index < start_index:
            continue

        # 获取所有原始数据    
        title = row['title']
        authors = row['authors']
        abstract = row['abstract']
        date = row['date']
        paper_url = row['paper_url']
        score = row['score']
        
        # 显示当前处理的论文信息
        print(f"正在翻译论文 {index + 1}/{len(df)}: {title[:50]}...")
        
        # 翻译摘要和标题
        cn_abstract = translate_text(abstract)
        cn_title = translate_text(title) if title else ""
        
        # 将结果添加到列表中（而不是直接写入文件）
        results.append({
            'title': title,
            'authors': authors,
            'abstract': abstract,
            'date': date,
            'paper_url': paper_url,
            'score': score,
            'title_cn': cn_title,
            'abstract_cn': cn_abstract
        })
        
        # 每处理5篇论文就保存一次进度
        if (index + 1) % 5 == 0:
            save_progress(index + 1, results)
            print(f"进度已保存：已处理 {index + 1} 篇论文")
        
        # 合理的延迟时间（1秒而不是1000秒）
        time.sleep(1)
    
    # 删除进度文件（表示已完成）
    if os.path.exists("progress.json"):
        os.remove("progress.json")
        print("翻译完成，已删除进度文件")
    
    #  循环结束后一次性保存所有结果
    result_df = pd.DataFrame(results)
    result_df.to_csv("result.csv", index=False, encoding='utf-8')
    
    # 显示完成信息
    print(f"翻译完成！共处理 {len(results)} 篇论文，结果已保存到 result.csv")

if __name__ == "__main__":
    main()
