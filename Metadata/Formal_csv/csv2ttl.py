import os
import glob
import json
import csv
from rdflib import Graph, URIRef, Literal, Namespace
from rdflib.namespace import RDFS, OWL

def main():
    print("开始构建文化遗产知识图谱...")
    
    # 1. 初始化 RDF 图
    g = Graph()
    
    # 2. 加载并绑定 Namespaces (命名空间)
    namespaces = {}
    print("正在加载命名空间 namespace.json ...")
    with open('namespace.json', 'r', encoding='utf-8') as f:
        ns_dict = json.load(f)
        
    for prefix, uri in ns_dict.items():
        # 清除部分URI可能带有的尖括号（例如 "<http://vocab.getty.edu/aat/>"）
        clean_uri = uri.strip('<>')
        ns = Namespace(clean_uri)
        namespaces[prefix] = ns
        g.bind(prefix, ns)

    # 定义一个辅助函数，用于将CSV中的字符串正确解析为 RDF 节点 (URIRef 或 Literal)
    def resolve_term(term_str):
        term_str = term_str.strip()
        if not term_str:
            return None
            
        # 如果是完整的URI (被 <> 包裹)
        if term_str.startswith('<') and term_str.endswith('>'):
            return URIRef(term_str[1:-1])
            
        # 如果是字面量 Literal (被引号包裹)
        elif term_str.startswith('"'):
            # 剥离多重或单重引号 (例如 """1987-02-01""")
            clean_str = term_str.strip('"')
            return Literal(clean_str)
            
        # 如果是带有前缀的缩写 (例如 me:item_manifesto)
        elif ':' in term_str:
            prefix, name = term_str.split(':', 1)
            if prefix in namespaces:
                return namespaces[prefix][name]
            else:
                # 如果前缀未定义，退化为完整的 URIRef (容错处理)
                return URIRef(term_str)
                
        # 兜底情况：作为纯文本字面量处理
        else:
            return Literal(term_str)

    # 3. 处理实体映射 (entity_mapping.json)
    print("正在融合实体映射 entity_mapping.json ...")
    with open('entity_mapping.json', 'r', encoding='utf-8') as f:
        entities_data = json.load(f)
        
    # 遍历 JSON 中的所有大类（如 'items', 'entities', 'concepts' 等）
    for category, mapping_dict in entities_data.items():
        for label, mapping in mapping_dict.items():
            # 应对结构差异：'items' 是纯字符串，其他是字典包含 local 和 global
            if isinstance(mapping, str):
                local_id = mapping
                global_id = ""
            else:
                local_id = mapping.get('local', '')
                global_id = mapping.get('global', '')
                
            if local_id:
                subject_node = resolve_term(local_id)
                # 为实体添加人类可读的标签 (rdfs:label)
                g.add((subject_node, RDFS.label, Literal(label)))
                
                # 如果同时存在全局标识符（如 viaf, wd），添加 owl:sameAs 对齐实体
                if global_id:
                    object_node = resolve_term(global_id)
                    g.add((subject_node, OWL.sameAs, object_node))

    # 4. 自动抓取并处理所有 CSV 文件
    csv_files = glob.glob('*.csv')
    print(f"找到 {len(csv_files)} 个 CSV 文件，准备解析...")
    
    for file in csv_files:
        print(f"  - 正在解析: {file}")
        with open(file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            # 跳过表头 (Subject, Predicate, Object)
            header = next(reader, None) 
            
            for row in reader:
                if len(row) >= 3:
                    s_str, p_str, o_str = row[0], row[1], row[2]
                    
                    s = resolve_term(s_str)
                    p = resolve_term(p_str)
                    o = resolve_term(o_str)
                    
                    if s and p and o:
                        g.add((s, p, o))

    # 5. 序列化导出为 Turtle 格式 (.ttl)
    output_filename = "cultural_heritage_graph.ttl"
    print(f"数据处理完毕，正在导出至 {output_filename} ...")
    g.serialize(destination=output_filename, format='turtle')
    print("成功！Turtle文件已生成。")

if __name__ == "__main__":
    main()