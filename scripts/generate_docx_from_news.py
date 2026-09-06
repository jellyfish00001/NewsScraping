import os
import re
import docx
from docx.shared import Inches, Pt
from docx.oxml.ns import qn

def set_cell_text_preserve_style(cell, new_text):
    """保留儲存格原有樣式 (字體、大小、顏色、底色、控制標記)，替換其中的文字內容"""
    t_nodes = cell._tc.xpath('.//w:t')
    if t_nodes:
        t_nodes[0].text = new_text
        for extra in t_nodes[1:]:
            extra.getparent().remove(extra)
    else:
        cell.text = new_text

def create_template_docx(source_docx, out_template_path):
    """以使用者的 VN090602.docx 為基礎，產生乾淨的標準 Docx 範本檔案"""
    doc = docx.Document(source_docx)
    t = doc.tables[0]
    
    # 動態調整欄位替換為占位符號 (Placeholder)
    set_cell_text_preserve_style(t.rows[0].cells[1], '{{中文標題}}')
    set_cell_text_preserve_style(t.rows[1].cells[1], '{{外文標題}}')
    set_cell_text_preserve_style(t.rows[8].cells[4], '{{主圖說明與版權來源}}')
    set_cell_text_preserve_style(t.rows[12].cells[1], '{{關鍵字}}')
    set_cell_text_preserve_style(t.rows[13].cells[1], '{{相關連結}}')
    
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
        run._r.get_or_add_rPr().get_or_add_rFonts().set(qn('w:eastAsia'), 'Times New Roman')
        
    os.makedirs(os.path.dirname(out_template_path), exist_ok=True)
    doc.save(out_template_path)
    print(f'[成功] 已產生 Docx 範本檔案: {out_template_path}')

def parse_news_txt(txt_path):
    """解析每日新聞文字檔案中的各欄位資訊"""
    with open(txt_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # 中文標題
    zh_match = re.search(r'【中文標題 \(Rewrite\)】\s*\n([^\n]+)', content)
    zh_title = zh_match.group(1).strip() if zh_match else ''
    
    # 越文標題
    vi_match = re.search(r'【越南文標題 \(Rewrite\)】\s*\n([^\n]+)', content)
    vi_title = vi_match.group(1).strip() if vi_match else ''
    
    # 相關連結
    url_match = re.search(r'原始來源參考：([^\n]+)', content)
    if not url_match:
        url_match = re.search(r'原始出處連結：([^\n]+)', content)
    source_url = url_match.group(1).strip() if url_match else ''
    
    # 關鍵字 (Tiếng Việt)
    kw_match = re.search(r'Tiếng Việt：([^\n]+)', content)
    keywords = kw_match.group(1).strip() if kw_match else ''
    
    # 圖說 (Tiếng Việt)
    caption_match = re.search(r'STEP 9｜五語圖說\s*=+\s*\n(?:Tiếng Việt:\s*)?([^\n]+)', content)
    caption = caption_match.group(1).strip() if caption_match else ''
    # 如果有完整的事件說明，可與圖說組合
    
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
        'caption': caption,
        'paragraphs': paragraphs
    }

def fill_news_to_docx(template_docx, news_data, image_path, out_docx_path):
    """將新聞資料與 516*292 配圖精確填入 Docx 上稿單"""
    doc = docx.Document(template_docx)
    t = doc.tables[0]
    
    # 1. 填入標題
    set_cell_text_preserve_style(t.rows[0].cells[1], news_data['zh_title'])
    set_cell_text_preserve_style(t.rows[1].cells[1], news_data['vi_title'])
    
    # 2. 替換主圖 (Row 8, Cell 1)
    r8_c1 = t.rows[8].cells[1]
    for p in list(r8_c1.paragraphs):
        p._p.getparent().remove(p._p)
    new_img_p = r8_c1.add_paragraph()
    img_run = new_img_p.add_run()
    if os.path.exists(image_path):
        # 依 516*292 等比例插入，寬度設定為 2.135 英吋 (對應原始 Word 樣式)
        img_run.add_picture(image_path, width=Inches(2.135))
    
    # 3. 填入圖說 (Row 8, Cell 4)
    # 圖說組合：越文標題或首段精簡描述 + 圖說標記
    full_caption = f"{news_data['vi_title']}. {news_data['caption']}"
    set_cell_text_preserve_style(t.rows[8].cells[4], full_caption)
    
    # 4. 填入關鍵字與相關連結
    set_cell_text_preserve_style(t.rows[12].cells[1], news_data['keywords'])
    set_cell_text_preserve_style(t.rows[13].cells[1], news_data['source_url'])
    
    # 5. 填入內文段落 (表格後方的內文)
    for p in list(doc.paragraphs)[2:]:
        p._p.getparent().remove(p._p)
        
    for para_text in news_data['paragraphs']:
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(12)
        p.paragraph_format.space_after = Pt(12)
        p.paragraph_format.line_spacing = 1.15
        run = p.add_run(para_text)
        run.font.name = 'Times New Roman'
        run.font.size = Pt(12)
        run._r.get_or_add_rPr().get_or_add_rFonts().set(qn('w:eastAsia'), 'Times New Roman')
        
    os.makedirs(os.path.dirname(out_docx_path), exist_ok=True)
    doc.save(out_docx_path)
    print(f'[成功] 已產生填寫完成之上稿單: {out_docx_path}')

if __name__ == '__main__':
    base_docx = r'D:\越南新聞稿\VN090602.docx'
    template_out = r'D:\越南新聞稿\templates\新住民全球新聞網_上稿單範本.docx'
    
    # 1. 建立標準範本
    create_template_docx(base_docx, template_out)
    
    # 同步複製一份至 20260906/DOC範本/
    import shutil
    shutil.copyfile(template_out, r'D:\越南新聞稿\20260906\DOC範本\新住民全球新聞網_上稿單範本.docx')
    
    # 2. 自動填入今日兩篇新聞稿
    news1_txt = r'D:\越南新聞稿\20260906\AI文字內容\20260906_新聞稿01_越南新身分法海外僑民換證指南.txt'
    news1_img = r'D:\越南新聞稿\20260906\20260906_新聞01_越南新身分法換證配圖.jpg'
    news1_out = r'D:\越南新聞稿\20260906\DOC範本\VN20260906_01_越南新身分法.docx'
    
    data1 = parse_news_txt(news1_txt)
    fill_news_to_docx(template_out, data1, news1_img, news1_out)
    
    news2_txt = r'D:\越南新聞稿\20260906\AI文字內容\20260906_新聞稿02_海外越語推廣日贈書與二代雙語計畫.txt'
    news2_img = r'D:\越南新聞稿\20260906\20260906_新聞02_海外越語推廣日教育配圖.jpg'
    news2_out = r'D:\越南新聞稿\20260906\DOC範本\VN20260906_02_海外越語推廣日.docx'
    
    data2 = parse_news_txt(news2_txt)
    fill_news_to_docx(template_out, data2, news2_img, news2_out)
