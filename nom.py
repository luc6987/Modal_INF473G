
"""
read authors field from output.json and generate authors.csv
input "O. Aharony, O. Ganor , N. Sochen J. Sonnenschein and S. Yankielowicz"
output "Aharony O, Ganor O, Sochen N, Sonnenschein J, Yankielowicz S"

there are some rules:
1. Remove all institution names and their following content.
2. Remove all email addresses.
3. Remove all single quotes and double quotes.
4. Remove all parentheses and their content.
#         if re.match(r'^[A-Z]{2,}$', part):
5. Remove all non-Latin characters.
# 6. Capitalize the first letter of each name.

"""


import os
import json
import re
import csv

institution_keywords = [
    # 机构
    # institutions
    'university', 'institute', 'dept', 'department', 'college', 'school',
    'laboratory', 'centre', 'cnrs', 'universität', 'universita', 'faculté',
    'academy', 'group', 'team', 'laboratoire', 'division', 'instituto', 'institut',
    'cern', 'mit', 'caltech', 'lptens', 'slac', 'infn', 'inaf','centro'
    # 国家
    # countries
    'usa', 'united states', 'canada', 'china', 'france', 'germany', 'uk', 'united kingdom',
    'italy', 'spain', 'japan', 'australia', 'india', 'russia',
    # 城市/地区（可以持续扩展）
    # cities/regions (can be extended)
    'paris', 'london', 'berlin', 'rome', 'beijing', 'tokyo', 'new york', 'boston',
    'moscow', 'madrid', 'sydney', 'melbourne'
]





def is_institution(name):
    name_lower = name.lower()
    if any(keyword in name_lower for keyword in institution_keywords):
        return True
    # 再加一个规则：如果名字含有 email 地址或 @
    # Add another rule: if the name contains an email address or @
    if '@' in name_lower:
        return True
    # 或者：如果名字看起来像缩写（全大写且长度>3）
    # Or: if the name looks like an abbreviation (all uppercase and length > 3)
    if re.match(r'^[A-Z][A-Z\s.-]{3,}$', name):
        return True
    return False

def extract_author(authors):
    
    # delete all the s
    authors = re.sub(r'\s+', ' ', authors)  
    # 去掉双引号
    # remove double quotes
    authors = re.sub(r'\"', '', authors)  
    # 去掉单引号
    # remove single quotes
    authors = re.sub(r'\'', '', authors)  
    # 去括号内容
    # remove content in parentheses
    while '(' in authors and ')' in authors:
        authors = re.sub(r'\([^()]*\)', '', authors) 
    # 按逗号或"and"分割
    # split by comma or "and"
    authors = re.split(r',| and ', authors)  
    # 去掉多余的空格
    # remove extra spaces
    authors = [a.strip() for a in authors if a.strip()]
    # 只保留拉丁字母
    # keep only Latin letters
    authors = [re.sub(r'[^a-zA-Z .]', '', a) for a in authors]

    authors = [re.sub(r'\s+', ' ', a) for a in authors]
    # 首字母大写
    # capitalize the first letter
    authors = [a.title() for a in authors]  
    authors = [a.replace("Nieegawa", "Niegawa") for a in authors]
    #删除所有university, institute, college, school 及其后面的内容
    # remove all university, institute, college, school and the content after it
    authors = [re.sub(r'\b(?:univ|institute|college|school)\b.*', '', a) for a in authors]
    sorted(authors)
    clean_names = []
    for name in authors:
        if not is_institution(name):
            clean_names.append(name.strip())
    return clean_names



def process_abstracts(path):
    authors_set = set()
    
    # 读取output.json文件中的authors字段
    # Read the authors field from output.json
    with open("temp/output.json", "r", encoding="utf-8") as json_file:
        data = json.load(json_file) 
        for item in data:
            authors = item.get("authors", "")
            if authors:
                authors = extract_author(authors)
                authors_set.update(authors)

    # 将authors按字母排序
    # Sort authors alphabetically
    authors_set = sorted(authors_set)

    # 将结果保存到authors.csv文件中
    # Save the results to authors.csv
    with open("temp/authors.csv", "w", encoding="utf-8", newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["authors"])
        for author in authors_set:
            writer.writerow([author])

    print("Extraction completed. Data saved to temp/output.json and temp/authors.csv")

# 示例调用
# Example call
process_abstracts("temp/output.json")
