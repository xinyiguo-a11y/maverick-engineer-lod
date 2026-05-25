import json
import csv
import glob
import os
from collections import defaultdict

def generate_modular_ttls():
    # 1. 准备前缀 (Namespaces)
    try:
        with open('namespace.json', 'r', encoding='utf-8') as f:
            namespaces = json.load(f)
    except FileNotFoundError:
        print("错误：找不到 namespace.json 文件。")
        return

    prefixes = []
    for prefix, uri in namespaces.items():
        uri = uri.strip()
        if not (uri.startswith('<') and uri.endswith('>')):
            uri = f"<{uri.strip('<>')}>"
        prefixes.append(f"@prefix {prefix}: {uri} .")
    prefix_header = "\n".join(prefixes) + "\n\n"

    # 2. 构建全局实体知识库 (Entity Knowledge Base)
    # 这个字典将储存所有人物和概念的补充信息 (注释和外部链接)
    entity_kb = defaultdict(list)

    # 2.1 从 entity_mapping.json 抓取注释 (note) 和全局链接 (global)
    if os.path.exists('entity_mapping.json'):
        with open('entity_mapping.json', 'r', encoding='utf-8') as f:
            mapping = json.load(f)
            for key, data in mapping.get('entities', {}).items():
                local = data.get('local')
                if not local: continue
                
                # 抓取 owl:sameAs
                global_id = data.get('global')
                if global_id:
                    entity_kb[local].append(('owl:sameAs', global_id))
                    
                # 抓取刚才写的专属注释，使用 skos:scopeNote
                note = data.get('note')
                if note:
                    entity_kb[local].append(('skos:scopeNote', f'"""{note}"""'))

    # 2.2 从 supplementary CSVs 中抓取任何已有的补充关系
    kb_files = ['entities_sameas_formal.csv', 'additional_formal.csv']
    for kbf in kb_files:
        if os.path.exists(kbf):
            with open(kbf, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    s, p, o = row.get('Subject'), row.get('Predicate'), row.get('Object')
                    if s and p and o:
                        entity_kb[s.strip()].append((p.strip(), o.strip()))

    # 3. 处理每个物品的独立文件 (忽略知识库用的 CSV)
    csv_files = [f for f in glob.glob('*_formal.csv') if f not in kb_files]

    for file in csv_files:
        ttl_filename = file.replace('.csv', '.ttl')
        item_triples = defaultdict(list)
        referenced_entities = set() # 用来记录这个物品引用了哪些人或概念

        # 提取物品本身的三元组
        with open(file, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                s, p, o = row.get('Subject'), row.get('Predicate'), row.get('Object')
                if not (s and p and o): continue
                s, p, o = s.strip(), p.strip(), o.strip()
                
                item_triples[s].append((p, o))
                
                # 如果主语或宾语是项目本地节点 (me:开头)，记录下来
                if s.startswith('me:'): referenced_entities.add(s)
                if o.startswith('me:'): referenced_entities.add(o)

        if not item_triples:
            continue

        # 4. ✨ 核心魔法：将引用实体的知识库信息“融进”当前物品文件
        for ent in referenced_entities:
            if ent in entity_kb:
                for p, o in entity_kb[ent]:
                    # 去重逻辑：防止同一个属性被重复添加
                    if (p, o) not in item_triples[ent]:
                        item_triples[ent].append((p, o))

        # 5. 写入最终的 TTL 文件
        with open(ttl_filename, 'w', encoding='utf-8') as f_out:
            f_out.write(prefix_header)
            
            # 为了排版美观，按 subject 排序 (通常物品本身会排在前面)
            sorted_subjects = sorted(item_triples.keys())
            
            for s in sorted_subjects:
                f_out.write(f"{s}\n")
                po_list = item_triples[s]
                
                for i, (p, o) in enumerate(po_list):
                    end_char = ';' if i < len(po_list) - 1 else '.'
                    f_out.write(f"    {p} {o} {end_char}\n")
                
                f_out.write("\n")

        print(f"✅ 成功生成模块化文档: {ttl_filename}")

if __name__ == "__main__":
    print("开始整合实体属性，生成独立的 TTL 文件...")
    generate_modular_ttls()
    print("全部完成！")