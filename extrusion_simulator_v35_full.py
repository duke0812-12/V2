
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
from fpdf import FPDF

st.set_page_config(page_title="雙螺桿擠壓模擬器 v3.5", layout="centered")
st.title("📦 雙螺桿擠壓模擬器 v3.5")

# ====== 參數輸入區 ======
st.sidebar.header("基本操作參數設定")
temp = st.sidebar.slider("筒溫（℃）", 60, 180, 140)
rpm = st.sidebar.slider("螺桿轉速（rpm）", 100, 600, 300)
moisture = st.sidebar.slider("水含量（%）", 10, 25, 15)
fat = st.sidebar.slider("油脂含量（%）", 0, 15, 5)
feed_rate = st.sidebar.slider("喂料速率（kg/h）", 10, 100, 50)
die_diameter = st.sidebar.slider("模口孔徑（mm）", 1, 10, 4)

# 原料比例輸入
st.sidebar.header("原料比例設定（總和 = 100%）")
corn = st.sidebar.slider("玉米粉（%）", 0, 100, 60)
wheat = st.sidebar.slider("小麥粉（%）", 0, 100 - corn, 30)
soy = 100 - corn - wheat
st.sidebar.text(f"高蛋白粉（自動計算）: {soy}%")

if corn + wheat + soy != 100:
    st.warning("⚠️ 原料比例總和需為 100%")

# ====== 模擬邏輯（簡化版） ======
expansion = round(1.5 + (temp - 100) * 0.005 - moisture * 0.01 + fat * 0.008 + (100 - feed_rate) * 0.003, 2)
crispiness = round(4.5 + (rpm - 300) * 0.005 - fat * 0.1 + moisture * 0.05, 2)
stickiness = round(1 + fat * 0.1 + moisture * 0.1 - rpm * 0.002, 2)
bulk_density = round(0.6 - expansion * 0.1 + feed_rate * 0.002 - die_diameter * 0.02, 2)
pressure = round(2.5 + rpm * 0.005 + feed_rate * 0.01 - die_diameter * 0.1, 2)

# 感官風味模擬（比例簡化估算）
sweet = round((corn * 0.6 + wheat * 0.2 + soy * 0.1) * fat * 0.05, 1)
grain = round((corn * 0.3 + wheat * 0.6 + soy * 0.1) * temp * 0.01, 1)
oily = round(fat * 8 + soy * 0.2, 1)

# ====== 顯示結果 ======
st.subheader("📊 模擬預測結果")

col1, col2 = st.columns(2)
with col1:
    st.write(f"**膨發指數**：{expansion}")
    st.write(f"**酥脆度**：{crispiness}")
    st.write(f"**黏性**：{stickiness}")
    st.write(f"**體積密度**：{bulk_density} g/cm³")
with col2:
    st.write(f"**預估筒內壓力**：{pressure} bar")
    st.write(f"**甜香強度**：{sweet} %")
    st.write(f"**穀香強度**：{grain} %")
    st.write(f"**油香強度**：{oily} %")

# 圖表視覺化
st.subheader("📈 指標圖表")
fig, ax = plt.subplots()
metrics = ["膨發", "酥脆", "黏性", "密度", "甜香", "穀香", "油香"]
values = [expansion, crispiness, stickiness, bulk_density, sweet, grain, oily]
ax.bar(metrics, values)
st.pyplot(fig)

# 說明區
st.markdown("---")
st.markdown("""
🧾 **模擬結果參數說明：**

- **膨發指數**：產品膨脹程度，數值高表示更鬆脆。
- **酥脆度**：咬碎容易程度，數值高表示更脆。
- **黏性**：加工時的黏著感，數值越高表示越容易黏壁。
- **體積密度**：產品紮實程度，數值越高表示更密實。
- **預估筒內壓力**：系統估算的擠壓壓力（bar）。
- **甜香 / 穀香 / 油香強度**：由原料與加工條件預測的風味強度（%）。

以上數值為模擬預估，實際仍需搭配感官品評與物理量測進一步驗證。
""")

# ====== PDF 報告匯出 ======
if st.button("📄 匯出模擬報告 PDF"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, "雙螺桿擠壓模擬報告 v3.5", ln=True, align="C")
    pdf.set_font("Arial", "", 12)
    pdf.ln(8)
    pdf.multi_cell(0, 8, f"操作參數：
筒溫：{temp}°C，轉速：{rpm} rpm，水含量：{moisture}%，油脂：{fat}%，
喂料速率：{feed_rate} kg/h，模口孔徑：{die_diameter} mm")
    pdf.ln(4)
    pdf.multi_cell(0, 8, f"原料比例：玉米粉 {corn}%，小麥粉 {wheat}%，高蛋白粉 {soy} %")
    pdf.ln(6)
    pdf.multi_cell(0, 8, f"模擬結果：
膨發指數：{expansion}、酥脆度：{crispiness}、黏性：{stickiness}
體積密度：{bulk_density} g/cm³、筒內壓力：{pressure} bar
甜香：{sweet}%、穀香：{grain}%、油香：{oily}%")
    pdf.ln(4)
    pdf.set_font("Arial", "I", 11)
    pdf.multi_cell(0, 6, "※ 本報告為模擬預估，僅供研發參考使用")
    buffer = BytesIO()
    pdf.output(buffer)
    st.download_button("⬇️ 下載 PDF 報告", data=buffer.getvalue(), file_name="extrusion_v35_report.pdf")
