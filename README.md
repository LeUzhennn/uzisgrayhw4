# 線上籤詩與心靈指引 (Online Fortune & Guidance)

這是一個使用 Streamlit 建構的線上問卜應用程式，它結合了傳統的東方籤詩與西方的塔羅原型占卜，並利用大型語言模型（LLM）為使用者提供個人化的解說。

## 功能

- **雙重風格**: 使用者可以選擇兩種不同的問卜風格：
  - **東方籤詩**: 根據使用者輸入的名字和問題，生成一首七言絕句形式的籤詩，並提供吉凶等級和解說。
  - **西方占卜**: 隨機抽取一張塔羅原型牌（如太陽、月亮、愚者等），並顯示對應的牌義、關鍵詞和指引，同時附上塔羅牌圖片。
- **AI 解說**: 使用 Hugging Face Inference API 驅動的 `meta-llama/Meta-Llama-3-8B-Instruct` 模型，為生成的籤詩或抽到的牌卡提供個人化的解釋。
- **每日固定結果**: 為了增加問卜的儀式感，同一個使用者在同一天針對同一個問題會得到相同的結果。

## 如何執行

1.  **安裝依賴**:
    ```bash
    pip install -r requirements.txt
    ```

2.  **設定 API 金鑰**:
    你需要在 Streamlit 的 secrets 管理中設定你的 Hugging Face API 金鑰。在你的專案底下建立 `.streamlit/secrets.toml` 檔案，並新增以下內容：
    ```toml
    HF_API_KEY = "hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
    ```
    請將 `hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx` 替換成你自己的 Hugging Face API Token。

3.  **執行應用程式**:
    ```bash
    streamlit run app.py
    ```

---

## 更新日誌 (Changelog)

- **版面調整**: 調整了「西方占卜」模式的結果版面，將塔羅牌圖片與詳細內容並排顯示，提升閱讀體驗。
- **新增塔羅牌圖片**: 為「西方占卜」模式增加了對應的塔羅牌卡圖片，提升視覺體驗。
- **移除心靈小語區塊**: 根據使用者回饋，移除了「額外的心靈小語」區塊，使介面更專注於核心的問卜功能。
- **API 問題修復**:
    - 解決了因 Hugging Face API 端點變更 (`api-inference.huggingface.co` -> `router.huggingface.co`) 造成的錯誤。
    - 修正了 API payload 格式以符合新的 OpenAI 相容標準。
    - 更換了數次模型 ID (`Mistral-7B` -> `Mixtral-8x7B` -> `Llama-3-8B`)，最終解決了模型不支援或非聊天模型的錯誤。
- **初始 Bug 修復**: 修復了應用程式一開始因 `generate_fortune` 函式未定義而無法執行的 `NameError`。

## 參考資料

- 本專案的部分概念與實作參考自以下來源：
  - [【Demo06】用 RAG 打造心靈處方籤機器人](https.github.com/yenlung/AI-Demo/blob/master/%E3%80%90Demo06%E3%80%91%E7%94%A8_RAG_%E6%89%93%E9%80%A0%E5%BF%83%E9%9D%88%E8%99%9F%E6%96%B9%E7%B1%A4%E6%A9%9F%E5%99%A8%E4%BA%BA.ipynb)
