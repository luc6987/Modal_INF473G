from sentence_transformers import SentenceTransformer
from keyphrase_vectorizers import KeyphraseCountVectorizer
from keybert import KeyBERT
from tqdm import tqdm
import json
import os

# This script extracts keywords from the abstracts of scientific papers using KeyBERT.
# It loads a pre-trained SentenceTransformer model and uses it to extract keywords from the abstracts.
# The extracted keywords are then saved to a JSON file.

# On the computer of Salle d'info, the GPU is a NVIDIA GeForce RTX 3090
# it takes usually 3 hours to extract all keywords from 29555 abstracts

# 初始化模型（使用 GPU）
model = SentenceTransformer("all-MiniLM-L6-v2", device="cuda")
kw_model = KeyBERT(model)
vectorizer = KeyphraseCountVectorizer()

# 加载论文数据
with open("papers_standardized.json") as f:
    data = json.load(f)

# 结果文件路径
output_path = "keywords_extracted.jsonl"

# 如果文件存在，收集已处理的 paper_id
processed_ids = set()
if os.path.exists(output_path):
    with open(output_path, "r") as f:
        for line in f:
            try:
                entry = json.loads(line)
                processed_ids.add(entry["paper_id"])
            except json.JSONDecodeError:
                continue  # 忽略损坏的行（例如意外中断）

# 处理数据并实时写入
with open(output_path, "a") as f_out:
    with tqdm(total=len(data)) as pbar:
        pbar.update(len(processed_ids))
        for paper in data:
            paper_id = paper.get("paper_id", "")
            if paper_id in processed_ids:
                continue

            text = paper.get("abstract", "")
            title = paper.get("title", "")
            if title:
                text = "Title:" + title + ". Abstract:" + text
            if len(text.strip()) == 0:
                continue

            keywords = kw_model.extract_keywords(
                text,
                keyphrase_ngram_range=(1, 2),
                top_n=3,
                stop_words='english',
                use_mmr=True,
                diversity=0.5,
                nr_candidates=30,
                vectorizer=vectorizer
            )

            result_entry = {
                "paper_id": paper_id,
                "title": title,
                "keywords": [kw[0] for kw in keywords]
            }

            f_out.write(json.dumps(result_entry) + "\n")
            f_out.flush()  # 强制写盘，防止中途丢失

            processed_ids.add(paper_id)
            pbar.update(1)
