import json
import os
import pickle
from keyphrase_vectorizers import KeyphraseCountVectorizer

# 文件路径
input_path = "papers_standardized.json"
cache_path = "keyphrases_cache.pkl"
output_txt = "keyphrases_unique.txt"

# 加载数据
with open(input_path, "r") as f:
    data = json.load(f)
print(f"数据集大小: {len(data)}")

# 提取摘要
all_abstracts = [paper["abstract"] for paper in data if paper.get("abstract")]
print(f"摘要数量: {len(all_abstracts)}")

# 去重
unique_abstracts = sorted(set(all_abstracts))
print(f"去重后的摘要数量: {len(unique_abstracts)}")

# 检查缓存
if os.path.exists(cache_path):
    with open(cache_path, "rb") as f:
        keyphrases = pickle.load(f)
    print(f"缓存文件已加载: {cache_path}")
else:
    vectorizer = KeyphraseCountVectorizer(
        pos_pattern='<N.*|PROPN>+',
        spacy_pipeline='en_core_web_sm',
        stop_words='english',
        workers=-1
    )
    vectorizer.fit(unique_abstracts)
    keyphrases = vectorizer.get_feature_names_out()
    with open(cache_path, "wb") as f:
        pickle.dump(keyphrases, f)
    print(f"缓存文件已创建: {cache_path}")

# 保存候选短语清单
with open(output_txt, "w") as f:
    for phrase in sorted(keyphrases):
        f.write(phrase + "\n")
print(f"候选短语已保存到: {output_txt}")

keyphrases[:10]  # 显示前10个候选短语作为样本输出
