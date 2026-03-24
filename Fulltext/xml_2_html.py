from bs4 import BeautifulSoup

def generate_html_optimized(xml_file, output_html):
    # 读取 XML 文件
    with open(xml_file, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'xml')

    # --- 1. 提取元数据 (Metadata Extraction) ---
    metadata = {
        'book': {},
        'project': {}
    }

    # 1a. 提取书籍信息 (Source Desc -> Bibl)
    bibl = soup.find('sourceDesc').find('bibl')
    metadata['book']['chap_title'] = bibl.find('title', level='a').text.strip()
    metadata['book']['book_title'] = bibl.find('title', level='m').text.strip()
    metadata['book']['author'] = bibl.find('author').text.strip()
    metadata['book']['publisher'] = bibl.find('publisher').text.strip()
    metadata['book']['date'] = bibl.find('date').text.strip()
    metadata['book']['isbn'] = bibl.find('idno', type='ISBN').text.strip()

    # 1b. 提取项目信息 (TitleStmt + PublicationStmt)
    respStmt = soup.find('teiHeader').find('respStmt')
    metadata['project']['editor'] = respStmt.find('forename').text.strip() + ' ' + respStmt.find('surname').text.strip()
    metadata['project']['institution'] = soup.find('teiHeader').find('publicationStmt').find('publisher').text.strip()
    metadata['project']['date'] = soup.find('teiHeader').find('publicationStmt').find('date').text.strip()


    # 2. 建立 ID 到 外部链接的映射字典
    link_mapping = {}
    
    # 遍历 Header 中所有带 xml:id 的标签
    for element in soup.find_all(attrs={"xml:id": True}):
        element_id = "#" + element['xml:id']
        # 优先寻找 sameAs 属性 (Wikidata 等)
        if element.has_attr('sameAs'):
            link_mapping[element_id] = element['sameAs']
        # 如果是电影，并且有 IMDb 链接，优先使用 IMDb
        idno = element.find('idno', type='IMDb')
        if idno:
            link_mapping[element_id] = idno.text.strip()

    # 3. 提取正文主体部分
    body = soup.find('body')

    # 4. 转换 TEI 标签为 HTML 标签 (Simplified colors)
    # 处理各种实体标签
    tags_to_convert = {
        'persName': 'person', # 蓝色
        'title': 'movie',     # 紫色
        'placeName': 'misc',  # 灰色
        'orgName': 'misc',    # 灰色
        'term': 'misc',       # 灰色
        'name': 'misc'        # 灰色
    }

    for tag_name, css_class in tags_to_convert.items():
        for tag in body.find_all(tag_name):
            html_a = soup.new_tag('a', attrs={'class': f'entity {css_class}'})
            
            # 获取链接 URL
            if tag.has_attr('ref') and tag['ref'] in link_mapping:
                html_a['href'] = link_mapping[tag['ref']]
                html_a['target'] = '_blank'
                html_a['title'] = "View Authority Record"
            elif tag.has_attr('sameAs'):
                html_a['href'] = tag['sameAs']
                html_a['target'] = '_blank'
            else:
                html_a['href'] = '#'

            # 插入图标和原始文本
            html_a.string = tag.text
            tag.replace_with(html_a)

    # 处理引用语 <q> 转换为 <span> 并保留你喜欢的样式
    for q_tag in body.find_all('q'):
        span = soup.new_tag('span', attrs={'class': 'quote'})
        span.string = q_tag.text
        q_tag.replace_with(span)

    # 处理 <lb/> 换行
    for lb in body.find_all('lb'):
        lb.replace_with(' ')

    # 5. 生成新的、包含自适应元数据的 HTML 结构
    html_template = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Edward Yang: Digital Edition</title>
        <style>
            body {{ font-family: 'Georgia', serif; line-height: 1.8; color: #333; background-color: #f4f6f7; padding: 20px; }}
            .container {{ max-width: 900px; margin: 0 auto; background: #fff; padding: 40px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); border-top: 5px solid #2c3e50; }}
            
            /* Metadata Section Styling (Responsive) */
            .metadata-box {{ display: flex; flex-wrap: wrap; background-color: #fafbfc; border: 1px solid #eee; border-radius: 8px; padding: 20px; margin-bottom: 30px; }}
            .metadata-item {{ flex: 1; min-width: 250px; padding: 10px 20px; }}
            .metadata-item h2 {{ font-size: 1.2em; color: #2c3e50; border-bottom: 2px solid #ddd; padding-bottom: 5px; margin-top: 0; }}
            .metadata-item ul {{ list-style: none; padding: 0; margin: 0; }}
            .metadata-item li {{ margin-bottom: 8px; font-size: 0.9em; }}
            .metadata-label {{ font-weight: bold; color: #555; }}

            h1 {{ text-align: center; color: #2c3e50; margin-top: 0; }}
            
            /* 2. 文字自适应对齐 */
            p {{ margin-bottom: 20px; text-align: justify; }}
            
            a.entity {{ text-decoration: none; font-weight: bold; padding: 2px 4px; border-radius: 3px; transition: background-color 0.3s; }}
            
            /* 3. 人物保留蓝色 */
            .person {{ color: #2980b9; }} .person:hover {{ background-color: #ebf5fb; }}
            
            /* 3. 电影保留紫色斜体 */
            .movie {{ color: #8e44ad; font-style: italic; }} .movie:hover {{ background-color: #f4ecf7; }}
            
            /* 3. 其他所有misc实体（地名、机构、概念）统一灰色并使用虚线下划线 */
            .misc {{ color: #7f8c8d; border-bottom: 1px dashed #7f8c8d; }} .misc:hover {{ background-color: #f4f6f7; }} 

            /* 4. 保留引用样式 */
            .quote {{ font-style: italic; color: #555; background-color: #f9f9f9; padding: 2px 6px; border-radius: 4px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="metadata-box">
                <div class="metadata-item">
                    <h2>Source Document Info</h2>
                    <ul>
                        <li><span class="metadata-label">Chapter Title:</span> {metadata['book']['chap_title']}</li>
                        <li><span class="metadata-label">Book Title:</span> {metadata['book']['book_title']}</li>
                        <li><span class="metadata-label">Author:</span> {metadata['book']['author']}</li>
                        <li><span class="metadata-label">Publisher:</span> {metadata['book']['publisher']}, {metadata['book']['date']}</li>
                        <li><span class="metadata-label">ISBN:</span> {metadata['book']['isbn']}</li>
                    </ul>
                </div>
                <div class="metadata-item">
                    <h2>DH Project Info</h2>
                    <ul>
                        <li><span class="metadata-label">Project Name:</span> {metadata['project']['institution']}</li>
                        <li><span class="metadata-label">Digital Editor:</span> {metadata['project']['editor']}</li>
                        <li><span class="metadata-label">Publication Date:</span> {metadata['project']['date']}</li>
                        <li><span class="metadata-label">Institution:</span> {metadata['project']['institution']}</li>
                    </ul>
                </div>
            </div>

            <h1>Edward Yang: Poetry and Motion</h1>
            <p style="text-align: center; color: #7f8c8d; font-style: italic; margin-top: -10px;">A Digital TEI Edition extracted from John Anderson (2005)</p>
            {body.decode_contents()}
        </div>
    </body>
    </html>
    """

    with open(output_html, 'w', encoding='utf-8') as f:
        f.write(html_template)
    print(f"🎉 优化的前端网页已成功生成：{output_html}")

# 运行脚本（确保目录下有 Fulltext.xml）
try:
    generate_html_optimized('Fulltext.xml', 'text.html')
except FileNotFoundError:
    print("错误：未找到 'Fulltext.xml' 文件，请确保该文件在同一目录下。")