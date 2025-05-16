import json
from tqdm import tqdm
from sentence_transformers import SentenceTransformer
from sklearn.decomposition import PCA
from collections import defaultdict
import numpy as np
import hdbscan
import gc


# ======== 加载数据 ==========
with open("keywords_extracted.json", "r") as f:
    data = json.load(f)

# ======== 提取所有关键词短语 ==========
all_keywords = set()
for paper in data:
    all_keywords.update(paper["keywords"])
all_keywords = sorted(all_keywords)



# ======== 编码关键词短语 ==========
model = SentenceTransformer("all-MiniLM-L6-v2")
embeddings = model.encode(all_keywords, show_progress_bar=True)



# ======== 释放模型减少内存 ==========
del model
gc.collect()

# ======== 降维处理 ==========

pca = PCA(n_components=50)
reduced_embeddings = pca.fit_transform(embeddings.astype(np.float32))



# ======== 聚类合并相似关键词 ==========

clusterer = hdbscan.HDBSCAN(min_cluster_size=3)
labels = clusterer.fit_predict(reduced_embeddings)



# ======== 构建关键词合并映射 ==========
clusters = defaultdict(list)
for kw, label in zip(all_keywords, labels):
    if label == -1:
        clusters[kw].append(kw)  # 独立关键词自己归类
    else:
        clusters[label].append(kw)

merge_dict = {}
for group in clusters.values():
    sorted_group = sorted(group)
    rep = min(sorted_group, key=len)
    for var in sorted_group:
        merge_dict[var] = rep

# ======== 替换每篇文章中的关键词 ==========
result = []
for paper in tqdm(data, desc="🧹 替换合并关键词"):
    new_keywords = [merge_dict.get(kw, kw) for kw in paper["keywords"]]
    deduped = sorted(set(new_keywords))
    result.append({
        "paper_id": paper["paper_id"],
        "title": paper["title"],
        "keywords": deduped
    })

# ======== 保存文件 ==========
output_path = "./keywords_merged.json"
with open(output_path, "w") as f:
    json.dump(result, f, indent=2)



# ======== 反向映射：代表词 ➝ 同义词列表 ==========
from collections import defaultdict

reverse_merge_dict = defaultdict(list)
for variant, rep in merge_dict.items():
    reverse_merge_dict[rep].append(variant)

# 按代表词排序，组内排序
cluster_dict = {
    rep: sorted(variants)
    for rep, variants in sorted(reverse_merge_dict.items())
    if len(variants) > 1  # 只显示发生了合并的
}

# 保存为 JSON 文件
with open("keyword_clusters.json", "w") as f:
    json.dump(cluster_dict, f, indent=4, ensure_ascii=False)


