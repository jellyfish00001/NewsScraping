import os
import re
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.oxml.ns import qn

def clear_cell_shading_and_highlight(cell):
    """清除儲存格中的所有底色 (w:shd) 與螢光色 (w:highlight)，維持乾淨標準外觀"""
    for shd in cell._tc.xpath('.//w:shd'):
        shd.getparent().remove(shd)
    for hl in cell._tc.xpath('.//w:highlight'):
        hl.getparent().remove(hl)

def set_cell_clean_text(cell, new_text, font_name='Times New Roman', font_size_pt=12, is_bold=False):
    """將文字寫入儲存格，去除特殊顏色與底色，套用標準字型與純黑文字"""
    clear_cell_shading_and_highlight(cell)
    
    t_nodes = cell._tc.xpath('.//w:t')
    if t_nodes:
        t_nodes[0].text = new_text
        for extra in t_nodes[1:]:
            extra.getparent().remove(extra)
        # 設定字型與顏色為純黑
        r_nodes = cell._tc.xpath('.//w:r')
        for r in r_nodes:
            rPr = r.get_or_add_rPr()
            for s in rPr.xpath('.//w:shd'):
                rPr.remove(s)
            for h in rPr.xpath('.//w:highlight'):
                rPr.remove(h)
            color = rPr.find(qn('w:color'))
            if color is not None:
                color.set(qn('w:val'), '000000')
            else:
                new_col = docx.oxml.OxmlElement('w:color')
                new_col.set(qn('w:val'), '000000')
                rPr.append(new_col)
    else:
        for p in list(cell.paragraphs):
            p._p.getparent().remove(p._p)
        p = cell.add_paragraph()
        run = p.add_run(new_text)
        run.font.name = font_name
        run.font.size = Pt(font_size_pt)
        run.font.bold = is_bold
        run.font.color.rgb = RGBColor(0, 0, 0)
        run._r.get_or_add_rPr().get_or_add_rFonts().set(qn('w:eastAsia'), font_name)

def update_hyperlink_cell(cell, doc, target_url):
    """更新相關連結儲存格：同時修正顯示文字與底層 XML 超連結關係 (r:id / rel._target)，並嚴格審核一致性"""
    clear_cell_shading_and_highlight(cell)
    
    # 1. 搜尋 cell 內的 w:hyperlink 元素
    hyperlinks = cell._tc.xpath('.//w:hyperlink')
    if hyperlinks:
        hl_elem = hyperlinks[0]
        r_id = hl_elem.get(qn('r:id'))
        if r_id and r_id in doc.part.rels:
            # 修正底層超連結目標 (Target URL)
            doc.part.rels[r_id]._target = target_url
            
        # 修正可見文字
        t_nodes = hl_elem.xpath('.//w:t')
        if t_nodes:
            t_nodes[0].text = target_url
            for extra in t_nodes[1:]:
                extra.getparent().remove(extra)
        else:
            set_cell_clean_text(cell, target_url, font_name='Times New Roman', font_size_pt=11)
    else:
        # 若無 hyperlink 元素，直接純文字寫入
        set_cell_clean_text(cell, target_url, font_name='Times New Roman', font_size_pt=11)
        
    # 2. 清除儲存格內其他多餘段落與 run 的底色/顏色
    for r in cell._tc.xpath('.//w:r'):
        rPr = r.get_or_add_rPr()
        for s in rPr.xpath('.//w:shd'):
            rPr.remove(s)
        for h in rPr.xpath('.//w:highlight'):
            rPr.remove(h)
        color = rPr.find(qn('w:color'))
        if color is not None:
            color.set(qn('w:val'), '000000')

    # 3. 嚴格審核：確認底層關係已正確更新
    if hyperlinks:
        r_id = hyperlinks[0].get(qn('r:id'))
        if r_id in doc.part.rels:
            actual_rel_target = doc.part.rels[r_id].target_ref
            assert actual_rel_target == target_url, f"審核失敗: 超連結目標 {actual_rel_target} 與網址 {target_url} 不一致！"
            print(f"[審核通過] 超連結底層目標與顯示網址完全一致: {actual_rel_target}")

def build_template_doc(source_docx):
    """建立乾淨無特殊顏色之標準 Docx Document 物件"""
    doc = docx.Document(source_docx)
    t = doc.tables[0]
    
    # 動態調整欄位替換為占位符號 (Placeholder)
    set_cell_clean_text(t.rows[0].cells[1], '{{中文標題}}', font_name='微軟正黑體', font_size_pt=12)
    set_cell_clean_text(t.rows[1].cells[1], '{{外文標題}}', font_name='Times New Roman', font_size_pt=12)
    # 主圖格式調整為：主圖說明(Ảnh envato/{圖片名稱})，不帶最外層大括號
    set_cell_clean_text(t.rows[8].cells[4], '主圖說明(Ảnh envato/{圖片名稱})', font_name='Times New Roman', font_size_pt=11)
    set_cell_clean_text(t.rows[12].cells[1], '{{關鍵字}}', font_name='Times New Roman', font_size_pt=11)
    
    # 範本相關連結占位符 (若有 hyperlink 則更新文字)
    update_hyperlink_cell(t.rows[13].cells[1], doc, '{{相關連結URL}}')
    
    # 替換內文段落為標準占位符
    for p in list(doc.paragraphs)[2:]:
        p._p.getparent().remove(p._p)
        
    placeholders = [
        '{{第一段：導言（50~70字，回答發生什麼事、在哪裡、為什麼重要）}}',
        '{{第二段：事件內容（事件經過、關鍵數據、官方說法）}}',
        '{{第三段：影響（對民眾、新住民、社會之可能影響）}}',
        '{{第四段：後續措施（政府措施、進度、政策規劃）}}',
        '{{第五段：背景（歷史背景、補充資訊）}}'
    ]
    for ph in placeholders:
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(12)
        p.paragraph_format.space_after = Pt(12)
        p.paragraph_format.line_spacing = 1.15
        run = p.add_run(ph)
        run.font.name = 'Times New Roman'
        run.font.size = Pt(12)
        run.font.color.rgb = RGBColor(0, 0, 0)
        run._r.get_or_add_rPr().get_or_add_rFonts().set(qn('w:eastAsia'), 'Times New Roman')
        
    return doc

def parse_news_txt(txt_path):
    """精準解析每日新聞文字檔案中的各欄位資訊，提取原始真實 URL 連結與圖說"""
    with open(txt_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # 中文標題
    zh_match = re.search(r'【中文標題 \(Rewrite\)】\s*\n([^\n]+)', content)
    zh_title = zh_match.group(1).strip() if zh_match else ''
    
    # 越文標題
    vi_match = re.search(r'【越南文標題 \(Rewrite\)】\s*\n([^\n]+)', content)
    vi_title = vi_match.group(1).strip() if vi_match else ''
    
    # 原始 URL 連結 (嚴格提取 http:// 或 https:// 網址)
    url_match = re.search(r'原始來源連結：\s*(https?://[^\s\n]+)', content)
    if not url_match:
        url_match = re.search(r'https?://[^\s\n]+', content)
    source_url = url_match.group(1).strip() if url_match else ''
    
    # 關鍵字 (Tiếng Việt)
    kw_match = re.search(r'Tiếng Việt：([^\n]+)', content)
    keywords = kw_match.group(1).strip() if kw_match else ''
    
    # 圖說 (格式：主圖說明(Ảnh envato/{圖片名稱}))
    # 移除可能殘留的最外層大括號
    caption_match = re.search(r'STEP 9｜五語圖說\s*=+\s*\n(?:Tiếng Việt:\s*)?([^\n]+)', content)
    caption_raw = caption_match.group(1).strip() if caption_match else ''
    if caption_raw.startswith('{') and caption_raw.endswith('}'):
        caption_raw = caption_raw[1:-1].strip()
    
    # 越南文內文段落
    body_match = re.search(r'【越南文內文 \(Rewrite\)】\s*\n(.*?)(?=\n={10,}|\nSTEP 6|$)', content, re.DOTALL)
    body_text = body_match.group(1).strip() if body_match else ''
    
    paragraphs = [p.strip() for p in body_text.split('\n\n') if p.strip()]
    if not paragraphs:
        paragraphs = [p.strip() for p in body_text.split('\n') if p.strip()]
        
    return {
        'zh_title': zh_title,
        'vi_title': vi_title,
        'source_url': source_url,
        'keywords': keywords,
        'caption': caption_raw,
        'paragraphs': paragraphs
    }

def fill_news_from_doc(template_doc, news_data, image_path, out_docx_path):
    """將新聞資料、原始 URL 連結與 516*292 配圖精確填入 Docx 上稿單"""
    t = template_doc.tables[0]
    
    # 1. 填入標題 (無特殊背景色與反白)
    set_cell_clean_text(t.rows[0].cells[1], news_data['zh_title'], font_name='微軟正黑體', font_size_pt=12)
    set_cell_clean_text(t.rows[1].cells[1], news_data['vi_title'], font_name='Times New Roman', font_size_pt=12)
    
    # 2. 替換主圖 (Row 8, Cell 1)
    r8_c1 = t.rows[8].cells[1]
    clear_cell_shading_and_highlight(r8_c1)
    for p in list(r8_c1.paragraphs):
        p._p.getparent().remove(p._p)
    new_img_p = r8_c1.add_paragraph()
    img_run = new_img_p.add_run()
    if os.path.exists(image_path):
        img_run.add_picture(image_path, width=Inches(2.135))
    
    # 3. 填入圖說 (Row 8, Cell 4) - 格式為 主圖說明(Ảnh envato/{圖片名稱})
    set_cell_clean_text(t.rows[8].cells[4], news_data['caption'], font_name='Times New Roman', font_size_pt=11)
    
    # 4. 填入關鍵字與原始真實 URL 連結 (含底層超連結審核)
    set_cell_clean_text(t.rows[12].cells[1], news_data['keywords'], font_name='Times New Roman', font_size_pt=11)
    update_hyperlink_cell(t.rows[13].cells[1], template_doc, news_data['source_url'])
    
    # 5. 填入內文段落 (表格後方的內文)
    for p in list(template_doc.paragraphs)[2:]:
        p._p.getparent().remove(p._p)
        
    for para_text in news_data['paragraphs']:
        p = template_doc.add_paragraph()
        p.paragraph_format.space_before = Pt(12)
        p.paragraph_format.space_after = Pt(12)
        p.paragraph_format.line_spacing = 1.15
        run = p.add_run(para_text)
        run.font.name = 'Times New Roman'
        run.font.size = Pt(12)
        run.font.color.rgb = RGBColor(0, 0, 0)
        run._r.get_or_add_rPr().get_or_add_rFonts().set(qn('w:eastAsia'), 'Times New Roman')
        
    os.makedirs(os.path.dirname(out_docx_path), exist_ok=True)
    template_doc.save(out_docx_path)
    print(f'[成功] 已產生正式上稿單文件: {out_docx_path}')

if __name__ == '__main__':
    base_docx = r'D:\越南新聞稿\VN090602.docx'
    template_out = r'D:\越南新聞稿\templates\新住民全球新聞網_上稿單範本.docx'
    
    # 1. 產生標準單一 Docx 範本
    tmpl = build_template_doc(base_docx)
    tmpl.save(template_out)
    print(f'[成功] 已更新單一標準 Docx 範本檔案: {template_out}')

    # 2. 自動填入今日兩篇新聞稿 (使用原始 URL 連結與 主圖說明(Ảnh envato/{圖片名稱}) 圖說)
    news1_txt = r'D:\越南新聞稿\20260906\AI文字內容\20260906_新聞稿01_越南新身分法海外僑民換證指南.txt'
    news1_img = r'D:\越南新聞稿\20260906\20260906_新聞01_越南新身分法換證配圖.jpg'
    news1_out = r'D:\越南新聞稿\20260906\DOC範本\VN20260906_01_越南新身分法.docx'
    
    data1 = parse_news_txt(news1_txt)
    doc1 = build_template_doc(base_docx)
    fill_news_from_doc(doc1, data1, news1_img, news1_out)
    
    news2_txt = r'D:\越南新聞稿\20260906\AI文字內容\20260906_新聞稿02_海外越語推廣日贈書與二代雙語計畫.txt'
    news2_img = r'D:\越南新聞稿\20260906\20260906_新聞02_海外越語推廣日教育配圖.jpg'
    news2_out = r'D:\越南新聞稿\20260906\DOC範本\VN20260906_02_海外越語推廣日.docx'
    
    data2 = parse_news_txt(news2_txt)
    doc2 = build_template_doc(base_docx)
    fill_news_from_doc(doc2, data2, news2_img, news2_out)
