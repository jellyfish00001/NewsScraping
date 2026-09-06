# AGENT.md - 新住民全球新聞網 AI Agent 專案指引

---

## 一、專案大致用途

本專案為**中華民國政府補助標案**，服務對象為**「新住民全球新聞網」**讀者與在台越南新住民社群。  
專案核心任務在於：
1. 自動化採集與篩選對在台越南新住民具實質益處之越南新聞。
2. 進行客觀、中立之雙語與道地越南文（Tiếng Việt tự nhiên）改寫。
3. 自動產出新聞配圖（516*292 等比例）並填入標準 Word 上稿單文件，供政府標案驗收與對外發布。

---

## 二、唯一權威規則來源 (Single Source of Truth)

> **重大指引規範**  
> **所有審查紅線、選題標準、10大原則、11-Step 編譯 SOP、Word 上稿單排版樣式及目錄管理規範，皆統一記載於以下唯一檔案：**  
> 📖 **[`rules/專案採編與上稿唯一權威規範.md`](./rules/專案採編與上稿唯一權威規範.md)**  
> 
> * 本檔案（`AGENT.md`）及 `README.md` 不重複記載具體規則細節，以維護單一權威來源原則。  
> * 未來任何規則與流程之新增、修改或補充，一律直接在上述唯一權威檔案中進行維護。

---

## 三、專案結構與模組索引

* 📁 **`rules/`**：靜態規範專區，包含唯一權威手冊 [`rules/專案採編與上稿唯一權威規範.md`](./rules/專案採編與上稿唯一權威規範.md)。
* 📁 **`skills/`**（或 **`Skills/`**）：動態工作流專區，包含每日產出作業流程 [`skills/daily-news-workflow/SKILL.md`](./skills/daily-news-workflow/SKILL.md)。
* 📁 **`templates/`**：存放單一 Word 上稿單空白範本（`新住民全球新聞網_上稿單範本.docx`）與放置說明文件（`templates/README.md`）。
* 📁 **`scripts/`**：
  * `crop_news_images.py`：新聞圖片智慧裁切為 516*292 工具。
  * `generate_docx_from_news.py`：Word 上稿單自動生成模組（具備超連結底層目標同步與一致性審核機制）。
* 📁 **`YYYYMMDD/`**（如 `20260906/`）：每日產出目錄（含外層配圖、`AI文字內容/` 純文字稿、`DOC範本/` 正式交付 Word 文件）。
* 📄 **`README.md`**：專案公開說明文件。

---

## 四、專案維護與變更歷史 (Changelog)

* **2026-09-06 (範本目錄清整、圖說語法簡化與超連結底層審核機制)**：
  * **清整 templates/ 目錄**：刪除冗餘之 markdown 範本說明檔，確立 `templates/` 目錄僅保留單一空白 Word 範本（`新住民全球新聞網_上稿單範本.docx`）與放置說明文件（`templates/README.md`）。
  * **簡化圖說命名格式**：去除外層大括號，統一規範為 `主圖說明(Ảnh envato/{圖片名稱})`。同步修正 `rules/`、`skills/`、`templates/README.md` 與今日純文字產出檔。
  * **超連結底層目標審核與同步修復**：修正 `VN20260906_02_海外越語推廣日.docx` 中 Word 底層超連結 Relationship Target 殘留舊連結（vnexpress 菸草報導）之問題，使其與顯示文字 `https://www.vietnamplus.vn/...` 完全一致；並在 `generate_docx_from_news.py`、`rules/` 及 `skills/` 中加入底層超連結嚴格校驗與 Assert 審核機制。
* **2026-09-06 (Rules 與 Skills 職責拆分)**：
  * 依規範與流程分離原則，將每日新聞產生之 7 步作業流程獨立拆分建立成專屬 Skill：[`skills/daily-news-workflow/SKILL.md`](./skills/daily-news-workflow/SKILL.md)。
  * `rules/` 專注於合規紅線、審查標準與交付排版規範（What to comply with）；`skills/` 專注於每日實際執行步驟管線（How to execute）。
  * 同步更新 `rules/專案採編與上稿唯一權威規範.md`、`AGENT.md` 與 `README.md`。
* **2026-09-06 (規則架構精簡與單一權威來源確立)**：
  * 確立「唯一權威來源原則（SSOT）」：整合所有審查紅線、11 步 SOP、Docx 規範與目錄架構至唯一檔案 [`rules/專案採編與上稿唯一權威規範.md`](./rules/專案採編與上稿唯一權威規範.md)。
  * 清理 `rules/` 目錄，刪除分散之舊規則檔（01、02、03）。
  * 精簡 `AGENT.md` 與 `README.md`，去除過多具體規則細節，專注於專案大致用途與權威檔案導引。
* **2026-09-06 (Docx 樣式優化、原始 URL 修正與架構精簡)**：
  * 淘汰舊版 Prompt 範本，優化 Word 範本為純黑無底色，主圖格式統一為 `{主圖說明(Ảnh envato/{圖片名稱})}`。
  * 修正新聞 01 為真實原始 URL（`https://tuoitre.vn/...`），重新產出今日 Word 正式交付文件。
* **2026-09-06 (初期架構與產出建置)**：
  * 專案初始化、建立每日新聞產出與 Word 上稿單自動化生成模組。
