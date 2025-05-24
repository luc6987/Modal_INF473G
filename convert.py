import json
from nom import extract_author  

"""
This script standardizes author names in scientific papers by mapping variants to a standard name.
input: a JSON file containing papers with author names.
output: a new JSON file with standardized author names and cleaned paper IDs.

The script does the following:
1. Loads author variants from a JSON file.
2. Maps author name variants to their standard names.
3. Reads the original JSON file containing papers.
4. Extracts author names using the `extract_author` function from `nom.py`.
5. Standardizes the extracted names using the mapping.
"""

# 加载变体
# load author variants from JSON file
with open('author_variants.json', 'r') as f:
    author_variants = json.load(f)

# 反向映射：变体 -> 标准名字
# mapping from variant to standard name
variant_to_standard = {}
for standard_name, variants in author_variants.items():
    for variant in variants:
        if variant.strip():
            variant_to_standard[variant.strip()] = standard_name.strip()

def standardize_name(name):
    name = name.strip()
    return variant_to_standard.get(name, name)

# 读取原始 JSON（你之前从 .abs 提取的）
# Read the original JSON file (extracted from .abs files)
with open('temp/output.json', 'r') as f:
    papers = json.load(f)

for paper in papers:
    author_str = paper.get('authors', '')
    # 用 nom.py 的规则提取名字
    # Extract names using the rules from nom.py
    author_names = extract_author(author_str)
    standardized = []
    for name in author_names:
        standardized.append(standardize_name(name))
    paper['authors'] = standardized
    # 将"paper_id": "hep-th/9211077" 改为"paper_id": "9211077"
    # Change "paper_id": "hep-th/9211077" to "paper_id": "9211077"
    if 'paper_id' in paper:
        paper['paper_id'] = paper['paper_id'].split('/')[-1]

# 保存
# Save the standardized papers to a new JSON file
with open('temp/papers_standardized.json', 'w') as f:
    json.dump(papers, f, indent=2)

print("Standardized author names and saved to temp/papers_standardized.json")
