import os
import re
import json

def parse_abs_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    #delete the first two lines and the last line
    lines = content.splitlines()
    if len(lines) > 3:
        lines = lines[2:] 
    if lines and lines[-1].strip() == '\\\\':
        lines = lines[:-1] 
    content = '\n'.join(lines)

    # Split the content into header and abstract parts
    parts = re.split(r'^\s*\\\\\s*$', content, flags=re.MULTILINE)
    parts = [p.strip() for p in parts if p.strip()]
    header_part = parts[0] if parts else ''
    abstract_part = ' '.join(parts[1:]) if len(parts) > 1 else None

    known_fields = {
        'Paper': 'paper_id',
        'From': 'from',
        'Date': 'submitted',
        'Title': 'title',
        'Authors': 'authors',
        'Author': 'authors',
        'Comments': 'comments',
        'Report-no': 'report_no',
        'Journal-ref': 'journal_ref',
        'Subj-class': 'subject_class',
        'Proxy': 'proxy'
    }

    data = {v: None for v in known_fields.values()}
    data['abstract'] = None

    if abstract_part:
        data['abstract'] = re.sub(r'\s+', ' ', abstract_part)

    lines = header_part.splitlines()
    current_key = None
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
     
        field_match = re.match(r'^([\w\- ]+):\s*(.*)$', stripped)
        if field_match:
            key_part = field_match.group(1).strip()
            value_part = field_match.group(2).strip()

            if key_part in known_fields:
                mapped_key = known_fields[key_part]
                data[mapped_key] = value_part
                current_key = mapped_key
            else:

                if current_key:
                    data[current_key] = (data[current_key] or '') + ' ' + stripped
                else:
                 print(f"[line inidentified] file {os.path.basename(filepath)}: {stripped}")
        else:
            if current_key:
                data[current_key] = (data[current_key] or '') + ' ' + stripped
            else:
                print(f"[line inidentified] file {os.path.basename(filepath)}: {stripped}")


    for key in data:
        if data[key]:
            data[key] = re.sub(r'\s+', ' ', data[key]).strip()

    year = None
    if data['submitted']:
        year_match = re.search(r'\b(19|20)?\d{2}\b', data['submitted'])
        if year_match:
            year = int(year_match.group()[-2:])
            year += 1900 if year < 50 else 2000 if year < 100 else 0
    data['year'] = year

    return data








def process_all_years(base_dir, start_year=1992, end_year=2003):
    all_records = []
    for year in range(start_year, end_year + 1):
        year_dir = os.path.join(base_dir, str(year))
        if not os.path.exists(year_dir):
            print(f"warning:document {year_dir} does not exist.")
            continue

        print(f"working on {year} ...")
        for filename in os.listdir(year_dir):
            if filename.endswith('.abs'):
                filepath = os.path.join(year_dir, filename)
                try:
                    record = parse_abs_file(filepath)
                    record['year'] = year  
                    all_records.append(record)
                except Exception as e:
                    print(f"file {filename} analyse failed: {e}")

    return all_records


base_directory = 'cit-HepTh-abstracts' 

results = process_all_years(base_directory)


with open('output.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

print(f"Finish. In total of {len(results)} records, saved to output.json。")