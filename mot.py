from sentence_transformers import SentenceTransformer
from keybert import KeyBERT
import torch
import json

# 判断是否有 GPU
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Using device: {device}")

# 加载模型到 GPU 或 CPU
model = SentenceTransformer("all-MiniLM-L6-v2", device=device)
kw_model = KeyBERT(model)

# 加载数据
with open("papers_standardized.json", "r") as f:
    data = json.load(f)

abstracts = [item["abstract"] for item in data[:10] if item.get("abstract")]

# 拼成整体语境
text = " ".join(abstracts)

# 提取关键词
keywords = kw_model.extract_keywords(
    text,
    top_n=20,
    stop_words="english",
    use_maxsum=True,
    nr_candidates=50
)

print("\nTop keywords:")
for word, score in keywords:
    print(f"{word} ({score:.4f})")
