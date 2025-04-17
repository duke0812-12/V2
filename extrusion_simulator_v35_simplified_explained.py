import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF
from io import BytesIO

st.set_page_config(page_title="雙螺桿擠壓模擬器 v35", layout="centered")
st.title("⚙️ 雙螺桿擠壓模擬器 v35（簡潔版）")

def get_flavor_profiles():
    return {
        "玉米粉":     {"expansion": 2.0, "crisp": 6.0, "flavor": "甜香"},
        "小麥粉":     {"expansion": 1.8, "crisp": 5.5, "flavor": "穀香"},
        "裸麥粉":     {"expansion": 1.5, "crisp": 5.0, "flavor": "堅果風"},
        "高蛋白粉":  {"expansion": 1.2, "crisp": 4.0, "flavor": "豆粉味"},
        "馬鈴薯澱粉": {"expansion": 2.2, "crisp": 6.5, "flavor": "脆口澱粉香"},
        "全麥粉":     {"expansion": 1.6, "crisp": 5.2, "flavor": "麩皮香、纖維感"}
    }

material_options = list(get_flavor_profiles().keys())

st.sidebar.header("參數設定")
temp = st.sidebar.slider("筒溫（℃）", 60, 180, 140)
rpm = st.sidebar.slider("轉速（rpm）", 100, 600, 300)
moisture = st.sidebar.slider("水含量（%）", 10, 25, 15)
fat = st.sidebar.slider("油脂含量（%）", 0, 15, 5)
screw_diameter = st.sidebar.slider("螺桿直徑（mm）", 20, 60, 30)
screw_length = st.sidebar.slider("螺桿長度（mm）", 600, 1600, 1000)
feed_rate = st.sidebar.slider("喂料速率（kg/h）", 10, 100, 40)
die_diameter = st.sidebar.slider("模口孔徑（mm）", 2, 12, 6)

st.subheader("🔢 混合原料設定（總和需為100%）")
blend_dict = {}
total_ratio = 0
for mat in material_options:
    ratio = st.number_input(f"{mat} 比例（%）", min_value=0, max_value=100, value=0, step=5)
    if ratio > 0:
        blend_dict[mat] = ratio
        total_ratio += ratio

def simulate(temp, rpm, moisture, fat, screw_diameter, screw_length, blend_dict):
    profiles = get_flavor_profiles()
    total = sum(blend_dict.values())
    expansion = crisp = 0
    flavors = []
    for mat, ratio in blend_dict.items():
        w = ratio / total
        p = profiles[mat]
        expansion += p["expansion"] * w
        crisp += p["crisp"] * w
        flavors.append((p["flavor"], w))
    aw = round(0.6 + moisture * 0.01 - temp * 0.001, 2)
    sticky = round(1 + fat * 0.1 + moisture * 0.1 - rpm * 0.002, 2)
    density = round(1.2 / (expansion + 0.1), 2)
    pressure = round((temp * rpm * (1 - moisture / 100)) / 10000, 2)
    energy = round((temp * rpm * feed_rate * (1 - moisture / 100)) / 10000000, 3)
    return {
        "膨發指數": round(expansion, 2),
        "酥脆度": round(crisp, 2),
        "水活性": aw,
        "黏性": sticky,
        "體積密度": density,
        "桶內壓力（bar）": pressure,
        "預估能耗（kWh/kg）": energy,
        "風味描述": "、".join([f"{f[0]}（{int(f[1]*100)}%）" for f in flavors])
    }

if total_ratio == 100:
    if st.button("🚀 執行模擬"):
        results = simulate(temp, rpm, moisture, fat, screw_diameter, screw_length, blend_dict)
        st.subheader("📊 模擬結果")
        for k, v in results.items():
            st.write(f"{k}：{v}")

        
        st.markdown("#### 📘 指標說明")
        st.markdown("""
        - **膨發指數**：產品膨脹程度，數值越高代表越蓬鬆。
        - **酥脆度**：模擬咬下時的脆感，數值越高代表越酥脆。
        - **黏性**：產品的濕潤與黏牙程度，數值越高代表越黏。
        - **體積密度**：每立方公分的重量，數值越高代表產品較紮實。
        - **感官風味強度**：依原料組合推估的香氣特徵（如穀香、麥皮香等）。
        """)
st.subheader("📈 數值圖表")
        keys = ["膨發指數", "酥脆度", "水活性", "黏性", "體積密度", "桶內壓力（bar）", "預估能耗（kWh/kg）"]
        vals = [results[k] for k in keys]
        fig, ax = plt.subplots()
        ax.bar(keys, vals)
        st.pyplot(fig)

        if st.button("📄 匯出 PDF 報告"):
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", "B", 16)
            pdf.cell(200, 10, "雙螺桿擠壓模擬報告 v35", ln=True, align="C")
            pdf.set_font("Arial", "", 12)
            pdf.ln(5)
            pdf.multi_cell(0, 8, f"原料組合：{', '.join([f'{k} {v}%' for k,v in blend_dict.items()])}")
            pdf.cell(0, 10, f"筒溫：{temp}°C，轉速：{rpm} rpm，水：{moisture}%，油：{fat}%", ln=True)
            pdf.cell(0, 10, f"螺桿直徑：{screw_diameter} mm，螺桿長度：{screw_length} mm", ln=True)
            pdf.ln(5)
            for k, v in results.items():
                pdf.cell(0, 10, f"{k}：{v}", ln=True)
            buffer = BytesIO()
            pdf.output(buffer)
            st.download_button("⬇️ 下載報告", data=buffer.getvalue(), file_name="extrusion_v35_report.pdf")
else:
    st.warning(f"⚠️ 原料總比例需為 100%，目前為 {total_ratio}%")