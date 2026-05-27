import os
import glob
import json
import csv
from rdflib import Graph, URIRef, Literal, Namespace
from rdflib.namespace import RDFS, OWL

def main():
    
    g = Graph()
    
    # 2. Namespaces 
    namespaces = {}
    print("正在加载命名空间 namespace.json ...")
    with open('namespace.json', 'r', encoding='utf-8') as f:
        ns_dict = json.load(f)
        
    for prefix, uri in ns_dict.items():
        clean_uri = uri.strip('<>')
        ns = Namespace(clean_uri)
        namespaces[prefix] = ns
        g.bind(prefix, ns)

    # Used to correctly parse strings in CSV into RDF nodes (URIRef 或 Literal)
    def resolve_term(term_str):
        term_str = term_str.strip()
        if not term_str:
            return None
            
        # (被 <> 包裹)
        if term_str.startswith('<') and term_str.endswith('>'):
            return URIRef(term_str[1:-1])
            
        # Literal 
        elif term_str.startswith('"'):
            # Strip multiple or single quotes (例 """1987-02-01""")
            clean_str = term_str.strip('"')
            return Literal(clean_str)
            
        # prefix (like: me:item_manifesto)
        elif ':' in term_str:
            prefix, name = term_str.split(':', 1)
            if prefix in namespaces:
                return namespaces[prefix][name]
            else:
                #  URIRef 
                return URIRef(term_str)
                
        # Fallback situation: As a pure text literal processing.
        else:
            return Literal(term_str)

    # 3. (entity_mapping.json)
    print("正在融合实体映射 entity_mapping.json ...")
    with open('entity_mapping.json', 'r', encoding='utf-8') as f:
        entities_data = json.load(f)
        
    # iterate all the major categories in the JSON（如 'items', 'entities', 'concepts' ）
    for category, mapping_dict in entities_data.items():
        for label, mapping in mapping_dict.items():
            # 'items' is a pure string, while the others are dictionaries containing 'local' and 'global'
            if isinstance(mapping, str):
                local_id = mapping
                global_id = ""
            else:
                local_id = mapping.get('local', '')
                global_id = mapping.get('global', '')
                
            if local_id:
                subject_node = resolve_term(local_id)
                # Add human-readable labels to the entities (rdfs:label)
                g.add((subject_node, RDFS.label, Literal(label)))
                
                # If there are global identifiers （如 viaf, wd），添加 owl:sameAs 对齐实体
                if global_id:
                    object_node = resolve_term(global_id)
                    g.add((subject_node, OWL.sameAs, object_node))

    # 4. Automatically capture and process all CSV files
    csv_files = glob.glob('*.csv')
    print(f"找到 {len(csv_files)} 个 CSV 文件，准备解析...")
    
    for file in csv_files:
        print(f"  - 正在解析: {file}")
        with open(file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            # skip (Subject, Predicate, Object)
            header = next(reader, None) 
            
            for row in reader:
                if len(row) >= 3:
                    s_str, p_str, o_str = row[0], row[1], row[2]
                    
                    s = resolve_term(s_str)
                    p = resolve_term(p_str)
                    o = resolve_term(o_str)
                    
                    if s and p and o:
                        g.add((s, p, o))

    # 5. Serialize and export (.ttl)
    output_filename = "cultural_heritage_graph.ttl"
    print(f"数据处理完毕，正在导出至 {output_filename} ...")
    g.serialize(destination=output_filename, format='turtle')
    print("成功！Turtle文件已生成。")

if __name__ == "__main__":
    main()