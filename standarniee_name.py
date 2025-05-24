import pandas as pd
import re
import json

SUFFIXES = {"jr", "sr", "ii", "iii", "iv", "v"}

#############################################
# 辅助函数
# auxiliary functions
#############################################

def parse_name(full_name):
    """
    输入：任意格式的姓名字符串
    输出：first_names 列表 和 last_name 字符串
    """

    if not isinstance(full_name, str) or not full_name.strip():
        return [], ''

    # 统一格式：去点号，多个空格替换为单个空格，strip首尾空格
    # Normalize the name: remove dots, replace multiple spaces with a single space, and strip leading/trailing spaces
    name = re.sub(r'\s+', ' ', full_name.replace('.', ' ')).strip()

    parts = name.split()

    # 如果是单个词，例如 "JMMaldacena"
    # If it's a single word, e.g., "JMMaldacena"
    if len(parts) == 1:
        compact = parts[0]
        # 尝试匹配类似 JMMaldacena
        # Try to match patterns like JMMaldacena
        match = re.match(r'^(([A-Z]\.? ?)+)([A-Z][a-z]+)$', compact)
        if match:
            initials_part = match.group(1)
            last_name = match.group(3)
            initials = re.findall(r'[A-Z]', initials_part)
            return initials, last_name
        else:
            return [], compact

    # 如果是多个词，展开缩写和名字
    # If it's multiple words, expand abbreviations and names
    expanded_parts = []
    for part in parts:
        # 连写大写字母（例如 JM） 拆开
        # Split compact uppercase letters (e.g., JM)
        if re.fullmatch(r'[A-Z]{2,}', part):
            expanded_parts.extend(list(part))
        else:
            expanded_parts.append(part)

    if not expanded_parts:
        return [], ''

    # 检查 suffix，比如 Jr., Sr.
    # Check for suffixes, e.g., Jr., Sr.
    last = expanded_parts[-1].lower()
    if last in SUFFIXES and len(expanded_parts) >= 2:
        last_name = expanded_parts[-2]
        first_names = expanded_parts[:-2]
    else:
        last_name = expanded_parts[-1]
        first_names = expanded_parts[:-1]

    return first_names, last_name



def generate_variants(first_names, last_name):
    """生成所有可能变体"""
    """Generate all possible variants"""
    variants = set()

    # 完整全名
    # fullname
    full = ' '.join(first_names) + ' ' + last_name
    variants.add(full)

    # 省略中间名
    # omit middle names
    if len(first_names) > 1:
        variants.add(first_names[0] + ' ' + last_name)

    # 首字母缩写
    # initials
    initials = [n[0] for n in first_names]

    # 1. 全首字母缩写（带点、带空格）
    # 1. Full initials (with dots and spaces)
    variants.add('. '.join(initials) + '. ' + last_name)

    # 2. 全首字母缩写（不带空格）
    # 2. Full initials (without spaces)
    variants.add(''.join(initials) + '. ' + last_name)
    variants.add(''.join(initials) + '.' + last_name)

    # 3. 单个名字首字母缩写
    # 3. Single name initials (with dots and spaces)
    for i in initials:
        variants.add(i + '. ' + last_name)
        variants.add(i + ' ' + last_name)

    # 4. 只姓氏
    # 4. Only last name
    variants.add(last_name)

    # 标准化大小写
    # Normalize case
    return set(variant.title() for variant in variants)

def normalize_name(name):
    if not isinstance(name, str):
        return ''
    return re.sub(r'\s+', ' ', name.lower().replace('.', '').strip())


def is_variant(name1, name2):
    fn1, ln1 = parse_name(name1)
    fn2, ln2 = parse_name(name2)

    # 姓氏不同，肯定不是
    # Different last names, definitely not variants
    if ln1.lower() != ln2.lower():
        return False

    # 完整名字相同
    # Full names are the same
    if ' '.join(fn1).lower() == ' '.join(fn2).lower():
        return True

    set1 = set(f.lower() for f in fn1)
    set2 = set(f.lower() for f in fn2)

    # 如果名字完全相同或有交集，可以认为是变体
    # If the names are exactly the same or have an intersection, they can be considered variants
    if set1 & set2:
        return True

    #检查首字母是否有交集
    # Check if the initials have an intersection
    initials1 = set(f[0].lower() for f in fn1 if f)
    initials2 = set(f[0].lower() for f in fn2 if f)

    if initials1 and initials2 and initials1 & initials2:
        return True

    # 否则，不是变体
    # Otherwise, not a variant
    return False




#############################################
# Union-Find 并查集
# Union-Find data structure
#############################################

class UnionFind:
    def __init__(self):
        self.parent = {}

    def find(self, x):
        if x not in self.parent:
            self.parent[x] = x
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]

    def union(self, x, y):
        root_x = self.find(x)
        root_y = self.find(y)
        if root_x != root_y:
            self.parent[root_y] = root_x

#############################################
# 读取数据
# read data
#############################################

df = pd.read_csv('temp/authors.csv')

# 清洗，确保所有名字是字符串
# Clean and ensure all names are strings
df['author_clean'] = df['authors'].fillna('').str.strip().str.title()

names = df['author_clean'].dropna().unique().tolist()

#############################################
# 并查集：合并所有变体
# Union-Find: Merge all variants
#############################################

uf = UnionFind()

# 两两比较，符合 is_variant 的合并
# Compare pairs and merge if they are variants
for i in range(len(names)):
    for j in range(i + 1, len(names)):
        name1 = names[i]
        name2 = names[j]
        if is_variant(name1, name2):
            uf.union(name1, name2)

#############################################
# 生成标准名 -> 变体列表 映射
# Generate standard name -> variant list mapping
#############################################

groups = {}
for name in names:
    root = uf.find(name)
    if root not in groups:
        groups[root] = []
    groups[root].append(name)

# 选择 group 中最长的名字做标准名
# Choose the longest name in the group as the standard name
standard_name_mapping = {}
for group_names in groups.values():
    standard_name = max(group_names, key=lambda n: len(n))
    for var in group_names:
        standard_name_mapping[normalize_name(var)] = standard_name

#############################################
# 替换原数据中的名字
# Replace names in the original data
#############################################

def replace_with_standard(name):
    return standard_name_mapping.get(normalize_name(name), name)

df['standard_author'] = df['author_clean'].apply(replace_with_standard)

#############################################
# 导出 CSV
# Export CSV
#############################################

df[['authors', 'standard_author']].to_csv('temp/authors_standardized.csv', index=False, encoding='utf-8')
print(" all authors standardized and saved to temp/authors_standardized.csv")
#############################################
# 导出 JSON
# Export JSON
#############################################

author_variants = {}
for group_names in groups.values():
    standard_name = max(group_names, key=lambda n: len(n))
    author_variants[standard_name] = sorted(group_names)

with open('temp/author_variants.json', 'w', encoding='utf-8') as f:
    json.dump(author_variants, f, ensure_ascii=False, indent=4)

print("exported author_variants.json")
