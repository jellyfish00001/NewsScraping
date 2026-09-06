# 新住民全球新聞網 越南新聞採編專案 (NewsScraping)

本專案為中華民國政府補助標案，旨在協助「新住民全球新聞網」進行越南新聞之過濾採集、客觀編譯改寫，並自動化排版產出標準 Word 上稿單與 516*292 配圖，作為政府履約驗收與對外發布使用。

---

## 📖 專案唯一權威規則來源 (Single Source of Truth)

本專案所有審查紅線（零政治、零涉中、零腥羶色）、正向選題領域、十大改寫原則、11-Step 編譯 SOP、Word 上稿單排版樣式及檔案目錄管理標準，**皆集中由 `rules/` 目錄依專業面向分工管轄，嚴禁跨檔重複記載**：

👉 **[rules/README.md](./rules/README.md)**（規則體系總覽導覽）
* 總綱與目錄管理：[`rules/00_規則體系總綱與目錄管理規範.md`](./rules/00_規則體系總綱與目錄管理規範.md)
* 選題與審查紅線：[`rules/01_新聞選題與審查紅線規範.md`](./rules/01_新聞選題與審查紅線規範.md)
* 改寫與 11 步 SOP：[`rules/02_新聞改寫與11步SOP規範.md`](./rules/02_新聞改寫與11步SOP規範.md)
* Word 排版與超連結：[`rules/03_Word上稿單排版與超連結規範.md`](./rules/03_Word上稿單排版與超連結規範.md)

*任何規則異動，皆在對應單一管轄檔案進行修訂，其他檔案一律不重複贅述。*

---

## 專案結構簡介

* 📁 **`rules/`**：靜態規範專區，由 4 份各司其職、零重複記載之專業權威規則與導覽索引組成（詳見 [`rules/README.md`](./rules/README.md)）。
* 📁 **`skills/`**（或 **`Skills/`**）：動態工作流專區，包含每日新聞產出標準作業流程 [`skills/daily-news-workflow/SKILL.md`](./skills/daily-news-workflow/SKILL.md)。
* 📁 **`templates/`**：存放單一 Word 上稿單空白範本（`新住民全球新聞網_上稿單範本.docx`）與範本說明（`README.md`）。
* 📁 **`scripts/`**：
  * `crop_news_images.py`：新聞圖片智慧等比例裁切模組（516*292）。
  * `generate_docx_from_news.py`：Word 上稿單自動填入與文件產出模組。
* 📁 **`YYYYMMDD/`**（如 `20260906/`）：每日成果目錄，包含外層 516*292 配圖、`AI文字內容/` 純文字稿與 `DOC範本/` 正式交付 Word 文件。
* 🤖 **`AGENT.md`**：AI Agent 與專案維護運作指引及變更紀錄。
