import csv
import json
import os
import glob

# ==========================================
# 1. 动词字典 (Predicate Mapping) - 终极完全版
# ==========================================
PREDICATE_MAPPING = {
   
    "has source": "schema:url",
    "has primary source": "schema:url",
    "has archival source": "schema:archivedAt",
    "has bibliographic source": "schema:citation",
    "has identifier": "schema:identifier",
    "has digital identifier": "schema:identifier",
    "is part of collection": "schema:isPartOf",
    "has archive date": "dcterms:available",
    "has type": "rdf:type",
    
    "has creator": "schema:creator",
    "has director": "schema:director",
    "has author": "schema:author",
    "has translator": "schema:translator",
    "has maker": "schema:creator",
    "has cataloger": "schema:contributor",
    "has scanner": "schema:instrument",
    "is about": "schema:keywords",
  
    "has date": "schema:datePublished",
    "has publication date": "schema:datePublished",
    "has release date": "schema:datePublished",
    "has cataloging date": "schema:dateCreated",
    "has year built": "schema:dateCreated",
    "has year description": "schema:temporalCoverage",
    "has historical context": "schema:temporalCoverage",
    "reflects context": "skos:scopeNote",
    "has definition": "skos:definition",
    "opposes": "schema:isRelatedTo",      
    "is rooted in": "schema:isBasedOn",
    
    "has location": "schema:location",
    "has campus location": "schema:location",
    "has filming location": "schema:location",
    "located in": "schema:location",
    "has origin": "schema:locationCreated",
    "has place of publication": "schema:locationCreated",
    "has spatial coverage": "schema:spatialCoverage",
    "has address": "schema:address",
    
    "has subject": "dcterms:subject",
    "reflects": "schema:about",
    "has category": "schema:genre",
    "has genre": "schema:genre",
    "has format": "schema:fileFormat",
    "has language": "schema:inLanguage",
    "has material": "schema:material",
    "has duration": "schema:duration",
    "depicts": "schema:depicts",

    "has publisher": "schema:publisher",
    "has original publisher": "schema:publisher",
    "is archived at": "schema:archivedAt",
    "has production country": "schema:countryOfOrigin",
    "has production company": "schema:productionCompany",
    "has studio": "schema:productionCompany",
    "has registration status": "schema:status",
    "has capital in ntd": "schema:capital",
   
    "has festival edition": "schema:event",
    "has award": "schema:award",
    "is part of": "schema:isPartOf",
    "has department": "schema:department",
    "is influenced by": "schema:isBasedOn",
    "is inspired by": "schema:isBasedOn",
    
    "has chinese name": "schema:alternateName",
    "has chinese translation": "schema:alternateName",
    "has alternate name": "schema:alternateName",
    "has profession": "schema:hasOccupation",
    "colleague of": "schema:colleague",
    "graduated from": "schema:alumniOf",
    
    "has number of levels": "schema:value",
    "has number of rooms": "schema:value",
    "has gross square foot": "schema:value"
}

def load_entity_mapping(json_file):
    """读取 JSON 并将 Name 映射到 Local ID"""
    name_to_local = {}
    if not os.path.exists(json_file):
        print(f"⚠️ 警告: 找不到 {json_file}，请确保它在同级目录下！")
        return name_to_local

    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        for name, local_id in data.get('items', {}).items():
            name_to_local[name] = local_id
        for name, entity_info in data.get('entities', {}).items():
            name_to_local[name] = entity_info['local']
            
    return name_to_local

def format_node(text, name_to_local):
    """格式化节点：判断是实体、URL 还是普通文本"""
    text = text.strip()
    if text in name_to_local:
        return name_to_local[text]
    if ":" in text and not text.startswith("http"):
        return text
    if text.startswith("http"):
        return f"<{text}>"
    if text.startswith('"') and ('"@' in text or text.endswith('"')):
        return text
    # 纯净的 3 引号处理
    return f'"""{text}"""'

def process_csv(input_csv, output_csv, name_to_local):
    """处理单个 CSV 文件（直接拼接，避免自带 csv 库的连环转义乱码）"""
    with open(input_csv, 'r', encoding='utf-8-sig') as infile, \
         open(output_csv, 'w', encoding='utf-8-sig') as outfile:
        
        reader = csv.reader(infile)
        header = next(reader, None)
        if header:
            outfile.write("Subject,Predicate,Object\n")
            
        row_count = 0
        for row in reader:
            if len(row) < 3:
                continue
            
            sub = format_node(row[0], name_to_local)
            pred = PREDICATE_MAPPING.get(row[1].strip().lower(), row[1].strip())
            obj = format_node(row[2], name_to_local)
            
            # 手动写入，绝对干净
            outfile.write(f'{sub},{pred},{obj}\n')
            row_count += 1
            
    print(f"  ✅ 转换成功: {output_csv} ({row_count} 行)")

def generate_sameas_csv(json_file, output_csv):
    """【新功能】提取 JSON 中的 global ID，生成 owl:sameAs 关系表"""
    if not os.path.exists(json_file):
        return
        
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    entities = data.get('entities', {})
    
    count = 0
    with open(output_csv, 'w', encoding='utf-8-sig') as f:
        f.write("Subject,Predicate,Object\n")
        
        for name, info in entities.items():
            local_id = info.get('local', '').strip()
            global_id = info.get('global', '').strip()
            
            # 如果配置了 global id，才生成 sameAs 连线
            if local_id and global_id:
                # 智能判断：如果是完整的 http 链接（比如 Instagram），套上尖括号
                if global_id.startswith('http'):
                    global_id = f"<{global_id}>"
                
                f.write(f"{local_id},owl:sameAs,{global_id}\n")
                count += 1
                
    print(f"\n🌐 自动生成全局对齐表: {output_csv} (提取了 {count} 条 owl:sameAs 数据)")

def main():
    print("🚀 开始批量转换数据管道...\n")
    
    # 1. 加载字典
    name_to_local = load_entity_mapping('entity_mapping.json')
    
    # 2. 找到所有自然语言表
    natural_files = glob.glob('*_natural.csv')
    if not natural_files:
        print("❌ 找不到 *_natural.csv 文件，请检查路径。")
        return
        
    print(f"📂 找到 {len(natural_files)} 个业务数据文件，开始处理：")
    
    # 3. 逐个转换 (带防崩溃保护)
    success_count = 0
    for in_file in natural_files:
        out_file = in_file.replace('_natural.csv', '_formal.csv')
        try:
            process_csv(in_file, out_file, name_to_local)
            success_count += 1
        except UnicodeDecodeError:
            print(f"  ❌ [编码错误] {in_file} 不是 UTF-8 编码，请用 VSCode 另存为 UTF-8。")
        except Exception as e:
            print(f"  ❌ [未知错误] {in_file} 崩溃: {e}")
            
    # 4. 【新功能】独立生成 sameAs 关系表
    generate_sameas_csv('entity_mapping.json', 'entities_sameAs_formal.csv')
            
    print(f"\n🎉 恭喜！全部流水线执行完毕 (转换成功: {success_count}/{len(natural_files)})。")

if __name__ == "__main__":
    main()