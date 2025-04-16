
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF
from io import BytesIO
import os

st.set_page_config(page_title="雙螺桿擠壓模擬器 v3", layout="centered")

st.title("⚙️ 雙螺桿擠壓模擬器 v3（含能耗預測）")

# --------- 原料資料 ---------
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
target_options = ["膨發零食", "酥餅", "夾心餅體"]

# --------- 使用者參數輸入 ---------
st.sidebar.header("參數設定")
temp = st.sidebar.slider("筒溫（℃）", 60, 180, 140)
rpm = st.sidebar.slider("轉速（rpm）", 100, 600, 300)
moisture = st.sidebar.slider("水含量（%）", 10, 25, 15)
fat = st.sidebar.slider("油脂含量（%）", 0, 15, 5)
screw_diameter = st.sidebar.slider("螺桿直徑（mm）", 20, 60, 30)
screw_length = st.sidebar.slider("螺桿長度（mm）", 600, 1600, 1000)
target_product = st.sidebar.selectbox("產品目標", target_options)

# --------- 混合原料比例輸入 ---------
st.subheader("🔢 混合原料設定（總和需為100%）")
blend_dict = {}
total_ratio = 0
for mat in material_options:
    ratio = st.number_input(f"{mat} 比例（%）", min_value=0, max_value=100, value=0, step=5)
    if ratio > 0:
        blend_dict[mat] = ratio
        total_ratio += ratio

# --------- 模擬計算 ---------
def simulate_blended_formula(temp, rpm, moisture, fat, blend_dict):
    flavor_profiles = get_flavor_profiles()
    total_ratio = sum(blend_dict.values())
    expansion = 0
    crisp = 0
    flavors = []
    for mat, ratio in blend_dict.items():
        weight = ratio / total_ratio
        expansion += flavor_profiles[mat]["expansion"] * weight
        crisp += flavor_profiles[mat]["crisp"] * weight
        flavors.append((flavor_profiles[mat]["flavor"], weight))
    expansion = round(expansion + (temp - 100) * 0.005 - moisture * 0.01 + fat * 0.01, 2)
    crisp = round(crisp + (rpm - 300) * 0.005 - fat * 0.1 + moisture * 0.05, 2)
    water_aw = round(0.6 + moisture * 0.01 - temp * 0.001, 2)
    stickiness = round(1 + fat * 0.1 + moisture * 0.1 - rpm * 0.002, 2)
    appearance = "膨鬆偏亮" if expansion > 2 else "偏密實"
    color = "金黃色" if temp >= 140 else "淺黃"
    flavor_desc = "、".join([f"{f[0]}（{int(f[1]*100)}%）" for f in flavors])
    return {
        "膨發指數": expansion,
        "酥脆度": crisp,
        "水活性": water_aw,
        "黏性": stickiness,
        "外觀": appearance,
        "色澤": color,
        "風味描述": f"綜合風味：{flavor_desc}"
    }

def estimate_energy_consumption(temp, rpm, moisture, fat, screw_diameter_mm, screw_length_mm):
    base_energy = 0.12
    energy = (
        base_energy
        + (temp - 100) * 0.0008
        + (rpm - 300) * 0.0005
        + screw_length_mm / 1000 * 0.05
        - moisture * 0.002
        - fat * 0.003
        + (screw_diameter_mm / 100) * 0.02
    )
    return round(max(energy, 0.05), 3)

def simulate_with_energy(temp, rpm, moisture, fat, blend_dict, screw_diameter, screw_length):
    result = simulate_blended_formula(temp, rpm, moisture, fat, blend_dict)
    result["螺桿直徑（mm）"] = screw_diameter
    result["螺桿長度（mm）"] = screw_length
    result["預估能耗（kWh/kg）"] = estimate_energy_consumption(
        temp, rpm, moisture, fat, screw_diameter, screw_length
    )
    return result

# --------- 執行模擬 ---------
if total_ratio == 100:
    if st.button("🚀 執行模擬"):
        results = simulate_with_energy(temp, rpm, moisture, fat, blend_dict, screw_diameter, screw_length)
        st.subheader("📊 模擬結果")
        for k, v in results.items():
            st.write(f"**{k}**：{v}")

        st.subheader("📈 數值圖表")
        fig, ax = plt.subplots()
        keys = ["膨發指數", "酥脆度", "水活性", "黏性", "預估能耗（kWh/kg）"]
        vals = [results[k] for k in keys]
        ax.bar(keys, vals)
        st.pyplot(fig)

        # PDF 匯出
        if st.button("📄 匯出 PDF 報告"):
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", "B", 16)
            pdf.cell(200, 10, "雙螺桿擠壓模擬報告（含能耗）", ln=True, align="C")
            pdf.set_font("Arial", "", 12)
            pdf.ln(5)
            pdf.multi_cell(0, 8, f"原料組合：{', '.join([f'{k} {v}%' for k,v in blend_dict.items()])}")
            pdf.cell(0, 10, f"筒溫：{temp}°C，轉速：{rpm} rpm，水：{moisture}%，油：{fat}%", ln=True)
            pdf.cell(0, 10, f"螺桿直徑：{screw_diameter} mm，螺桿長度：{screw_length} mm", ln=True)
            pdf.ln(5)
            for k, v in results.items():
                pdf.cell(0, 10, f"{k}：{v}", ln=True)
            pdf_buffer = BytesIO()
            pdf.output(pdf_buffer)
            st.download_button("⬇️ 下載報告", data=pdf_buffer.getvalue(), file_name="extrusion_energy_report.pdf")
else:
    st.warning("⚠️ 原料總比例需為 100%，目前為 {}%".format(total_ratio))
