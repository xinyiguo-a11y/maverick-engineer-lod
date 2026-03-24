from bs4 import BeautifulSoup
from rdflib import Graph, URIRef, Literal, Namespace, RDF, OWL
from rdflib.namespace import SKOS, FOAF

def generate_rdf(xml_file, output_rdf):
    # 读取 XML 文件
    with open(xml_file, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'xml')

    # 初始化 RDF 图和命名空间
    g = Graph()
    SCHEMA = Namespace("http://schema.org/")
    EX = Namespace("http://example.org/project/edward_yang/") # 你的项目本地前缀
    
    g.bind("schema", SCHEMA)
    g.bind("owl", OWL)
    g.bind("skos", SKOS)
    g.bind("ex", EX)

    # 1. 解析人物 (Persons)
    for person in soup.find_all('person'):
        if not person.has_attr('xml:id'): continue
        uri = EX[person['xml:id']]
        g.add((uri, RDF.type, SCHEMA.Person))
        
        # 名字
        name_tag = person.find('persName', lang='en') or person.find('persName')
        if name_tag: g.add((uri, SCHEMA.name, Literal(name_tag.text.strip())))
        
        # 外部链接
        if person.has_attr('sameAs'):
            g.add((uri, OWL.sameAs, URIRef(person['sameAs'])))

        # 职业
        occ_tag = person.find('occupation')
        if occ_tag: g.add((uri, SCHEMA.jobTitle, Literal(occ_tag.text.strip())))

    # 2. 解析电影作品 (Movies/Bibl)
    for bibl in soup.find_all('bibl'):
        if not bibl.has_attr('xml:id'): continue
        uri = EX[bibl['xml:id']]
        g.add((uri, RDF.type, SCHEMA.Movie))
        
        # 片名
        title_tag = bibl.find('title', lang='en') or bibl.find('title')
        if title_tag: g.add((uri, SCHEMA.name, Literal(title_tag.text.strip())))
        
        # 年份
        date_tag = bibl.find('date')
        if date_tag: g.add((uri, SCHEMA.datePublished, Literal(date_tag.text.strip())))

        # Wikidata 和 IMDb 链接
        if bibl.has_attr('sameAs'):
            g.add((uri, OWL.sameAs, URIRef(bibl['sameAs'])))
        imdb_tag = bibl.find('idno', type='IMDb')
        if imdb_tag:
            g.add((uri, SCHEMA.sameAs, URIRef(imdb_tag.text.strip())))

    # 3. 解析概念/术语 (Concepts/Terms)
    for term in soup.find_all('term'):
        if not term.has_attr('xml:id'): continue
        uri = EX[term['xml:id']]
        g.add((uri, RDF.type, SKOS.Concept))
        
        label_tag = term.find('term', lang='en') or term
        g.add((uri, SKOS.prefLabel, Literal(label_tag.text.strip().split('\n')[0].strip())))

        if term.has_attr('sameAs'):
            g.add((uri, OWL.sameAs, URIRef(term['sameAs'])))

        note_tag = term.find('note')
        if note_tag: g.add((uri, SKOS.definition, Literal(note_tag.text.strip())))

    # 4. 解析机构与地点 (Organizations and Places)
    for org in soup.find_all('org'):
        if not org.has_attr('xml:id'): continue
        uri = EX[org['xml:id']]
        g.add((uri, RDF.type, SCHEMA.Organization))
        g.add((uri, SCHEMA.name, Literal(org.find('orgName').text.strip())))
        if org.has_attr('sameAs'): g.add((uri, OWL.sameAs, URIRef(org['sameAs'])))

    for place in soup.find_all('place'):
        if not place.has_attr('xml:id'): continue
        uri = EX[place['xml:id']]
        g.add((uri, RDF.type, SCHEMA.Place))
        g.add((uri, SCHEMA.name, Literal(place.find('placeName').text.strip())))
        if place.has_attr('sameAs'): g.add((uri, OWL.sameAs, URIRef(place['sameAs'])))

    # 保存为标准的 RDF/XML 格式
    g.serialize(destination=output_rdf, format='xml')
    print(f"🌍 RDF 知识图谱已成功提取并保存至：{output_rdf}")

# 运行脚本
generate_rdf('Fulltext.xml', 'text.rdf')