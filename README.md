# 雙螺桿擠壓模擬器 v2

這是一個使用 Python + Streamlit 製作的擠壓加工模擬工具，支援食品研發中常見的參數模擬與風味推估，適合應用於：

- 膨發程度預估
- 酥脆度／黏性評估
- 原料混合比例模擬（最多支援 5 種）
- 批次 CSV 匯入模擬
- PDF 模擬報告匯出

## 執行方式

```bash
streamlit run extrusion_simulator_v2.py
```

## 預測輸出項目

- 膨發指數
- 酥脆度
- 水活性
- 黏性
- 外觀與色澤
- 風味描述（根據原料組合）

---

如果你想部署到 [Streamlit Cloud](https://streamlit.io/cloud)，請確保本 repo 包含：
- extrusion_simulator_v2.py
- requirements.txt
- （選填）README.md

部署後即可取得一組公開網址供同仁／業界使用。