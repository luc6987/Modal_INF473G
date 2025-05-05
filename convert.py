import json
from nom import extract_author  # 用你自己的 nom.py 中的名字拆分函数

# 加载变体
with open('author_variants.json', 'r') as f:
    author_variants = json.load(f)

# 反向映射：变体 -> 标准名字
variant_to_standard = {}
for standard_name, variants in author_variants.items():
    for variant in variants:
        if variant.strip():
            variant_to_standard[variant.strip()] = standard_name.strip()

def standardize_name(name):
    name = name.strip()
    return variant_to_standard.get(name, name)

# 读取原始 JSON（你之前从 .abs 提取的）
with open('output.json', 'r') as f:
    papers = json.load(f)

for paper in papers:
    author_str = paper.get('authors', '')
    # 用 nom.py 的规则提取名字
    author_names = extract_author(author_str)
    standardized = []
    for name in author_names:
        standardized.append(standardize_name(name))
    paper['authors'] = standardized
    # 将"paper_id": "hep-th/9211077" 改为"paper_id": "9211077"
    if 'paper_id' in paper:
        paper['paper_id'] = paper['paper_id'].split('/')[-1]

# 保存
with open('papers_standardized.json', 'w') as f:
    json.dump(papers, f, indent=2)

print("完成：所有 authors 已标准化")
