import json
from tqdm import tqdm
from sentence_transformers import SentenceTransformer
from sklearn.decomposition import PCA
from collections import defaultdict
import numpy as np
import hdbscan
import gc

"""
this script is to merge similar keywords extracted from scientific papers.
Input: a JSONL file with each line containing a paper's ID, title, and keywords.
Output: a JSON file with merged keywords, and a JSON file with clusters of synonyms.

The alogorithm works as follows:
1. Load the keywords from the JSONL file.
2. Preprocess the keywords to remove unnecessary prefixes and symbols.
3. Encode the keywords using a SentenceTransformer model.
4. Reduce the dimensionality of the embeddings using PCA.
5. Cluster the reduced embeddings using HDBSCAN.
6. Create a mapping of keywords to their representative terms based on clustering.
"""


# ======== loading data ==========
with open("temp/keywords_extracted.jsonl", "r") as f:
    data = [json.loads(line) for line in f]

# ======== extracting all keyword phrases ==========
all_keywords = set()
for paper in data:
    all_keywords.update(paper["keywords"])
all_keywords = sorted(all_keywords)

#========= preprocessing ==========

# delete the spaces around hyphens
all_keywords = [kw.replace(" - ", "-") for kw in all_keywords]
# delete the title as prefix
all_keywords = [kw.replace("title:", "") for kw in all_keywords]
# 3. delete the "abstract:" prefix
all_keywords = [kw.replace("abstract:", "") for kw in all_keywords]
# 4. delete the "$" symbol
all_keywords = [kw.replace("$", "") for kw in all_keywords]


# ======== encoding keyword phrases ==========
model = SentenceTransformer("all-MiniLM-L6-v2")
embeddings = model.encode(all_keywords, show_progress_bar=True)



# ======== releasing model memory ==========
del model
gc.collect()

# ======== dimensionality reduction ==========

pca = PCA(n_components=50)
reduced_embeddings = pca.fit_transform(embeddings.astype(np.float32))



# ======== clustering similar keywords ==========
clusterer = hdbscan.HDBSCAN(min_cluster_size=3)
labels = clusterer.fit_predict(reduced_embeddings)



# ======== constructing keyword merge mapping ==========
clusters = defaultdict(list)
for kw, label in zip(all_keywords, labels):
    if label == -1:
        clusters[kw].append(kw)  # for noise points, keep them as their own cluster
    else:
        clusters[label].append(kw)

merge_dict = {}
for group in clusters.values():
    sorted_group = sorted(group)
    rep = sorted_group[0]  # representative term
    for var in sorted_group:
        merge_dict[var] = rep

# ======== replacing keywords in each paper ==========
result = []
for paper in tqdm(data, desc="Replacing keywords"):
    new_keywords = [merge_dict.get(kw, kw) for kw in paper["keywords"]]
    deduped = sorted(set(new_keywords))
    result.append({
        "paper_id": paper["paper_id"],
        "title": paper["title"],
        "keywords": deduped
    })

# ======== saving file ==========
output_path = "./temp/keywords_merged.json"
with open(output_path, "w") as f:
    json.dump(result, f, indent=2)



# ======== reverse mapping: representative term ➝ synonym list ==========
from collections import defaultdict

reverse_merge_dict = defaultdict(list)
for variant, rep in merge_dict.items():
    reverse_merge_dict[rep].append(variant)

# ordering the synonyms in each cluster
cluster_dict = {
    rep: sorted(variants)
    for rep, variants in sorted(reverse_merge_dict.items())
    if len(variants) > 1  # only keep clusters with more than one variant
}

# saving the clusters to a JSON file
with open("temp/keyword_clusters.json", "w") as f:
    json.dump(cluster_dict, f, indent=4, ensure_ascii=False)


