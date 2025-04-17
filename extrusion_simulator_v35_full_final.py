
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF
from io import BytesIO

st.set_page_config(page_title="雙螺桿擠壓模擬器 v3.5", layout="centered")
st.title("⚙️ 雙螺桿擠壓模擬器 v3.5（含能耗預測）")

# 原料資料
def get_flavor_profiles():
    return {
        "玉米粉": {"expansion": 2.0, "crisp": 6.0, "flavor": "甜香"},
        "小麥粉": {"expansion": 1.8, "crisp": 5.5, "flavor": "穀香"},
        "裸麥粉": {"expansion": 1.5, "crisp": 5.0, "flavor": "堅果風"},
        "高蛋白粉": {"expansion": 1.2, "crisp": 4.0, "flavor": "麥皮香"},
        "馬鈴薯澱粉": {"expansion": 2.2, "crisp": 6.5, "flavor": "黏Q感"},
        "全麥粉": {"expansion": 1.3, "crisp": 4.5, "flavor": "纖維感"}
    }

# 側邊參數設定
st.sidebar.header("參數設定")
temp = st.sidebar.slider("筒溫（°C）", 60, 180, 140)
rpm = st.sidebar.slider("轉速（rpm）", 100, 600, 300)
moisture = st.sidebar.slider("水含量（%）", 10, 25, 15)
fat = st.sidebar.slider("油脂含量（%）", 0, 15, 5)
screw_diameter = st.sidebar.slider("螺桿直徑（mm）", 20, 60, 30)
screw_length = st.sidebar.slider("螺桿長度（mm）", 500, 1500, 850)
feed_rate = st.sidebar.slider("喂料速率（kg/h）", 10, 100, 30)
die_diameter = st.sidebar.slider("模口孔徑（mm）", 2, 10, 4)

st.subheader("🔢 混合原料設定（總和需為100%）")
material_options = list(get_flavor_profiles().keys())
blend_dict = {}
total_ratio = 0
for mat in material_options:
    ratio = st.number_input(f"{mat} 比例（%）", min_value=0, max_value=100, value=0, step=5)
    if ratio > 0:
        blend_dict[mat] = ratio
        total_ratio += ratio

# 模擬邏輯
def simulate_blended_formula(temp, rpm, moisture, fat, screw_diameter, screw_length, feed_rate, die_diameter, blend_dict):
    flavor_profiles = get_flavor_profiles()
    total_ratio = sum(blend_dict.values())
    expansion = 0
    crisp = 0
    stickiness = 0
    aw = round(moisture / 25, 2)
    flavors = []

    for mat, ratio in blend_dict.items():
        weight = ratio / total_ratio
        profile = flavor_profiles[mat]
        expansion += profile["expansion"] * weight
        crisp += profile["crisp"] * weight
        stickiness += (6 - profile["crisp"]) * weight
        flavors.append(profile["flavor"])

    density = round(0.5 + (25 - moisture) * 0.02 - fat * 0.015, 2)
    pressure = round((temp * rpm * feed_rate) / (screw_diameter * screw_length * 100000), 3)
    energy = round((rpm * temp * (1 + fat/100 + moisture/100)) / 1000000, 3)

    return {
        "膨發指數": round(expansion, 2),
        "酥脆度": round(crisp, 2),
        "水活性": aw,
        "黏性": round(stickiness, 2),
        "體積密度": density,
        "感官風味": "、".join(set(flavors)),
        "螺桿直徑": screw_diameter,
        "螺桿長度": screw_length,
        "預估能耗": energy,
        "筒內壓力": pressure
    }

# 執行模擬
if total_ratio == 100:
    if st.button("🚀 執行模擬"):
        results = simulate_blended_formula(temp, rpm, moisture, fat, screw_diameter, screw_length, feed_rate, die_diameter, blend_dict)
        st.subheader("📊 模擬結果")
        for k, v in results.items():
            st.write(f"{k}：{v}")

        st.markdown("#### 各項參數說明")
        st.markdown(
            "- **膨發指數**：擠壓後產品膨大的程度，數值越高表示膨化越明顯。
"
            "- **酥脆度**：咀嚼時的酥脆感，越高越酥脆。
"
            "- **水活性（aw）**：越接近 1 越容易受微生物影響，需注意保存。
"
            "- **黏性**：口感黏性指標，數值越高代表越黏牙。
"
            "- **體積密度**：產品質地密實程度，值越高代表越紮實。
"
            "- **感官風味**：模擬配方綜合風味特性（來源於原料）。"
        )

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(200, 10, "雙螺桿擠壓模擬報告（含能耗）", ln=True, align="C")
        pdf.set_font("Arial", "", 12)
        pdf.ln(5)
        pdf.multi_cell(0, 8, f"操作參數：
筒溫: {temp} °C，轉速: {rpm} rpm，水含量: {moisture}% ，油脂: {fat}%，喂料速率: {feed_rate} kg/h，模口孔徑: {die_diameter} mm")
        pdf.cell(0, 10, f"螺桿直徑：{screw_diameter} mm，螺桿長度：{screw_length} mm", ln=True)
        pdf.ln(5)
        for k, v in results.items():
            pdf.cell(0, 10, f"{k}：{v}", ln=True)
        pdf_buffer = BytesIO()
        pdf.output(pdf_buffer)
        st.download_button("⬇️ 下載報告", data=pdf_buffer.getvalue(), file_name="extrusion_energy_report.pdf")
else:
    st.warning(f"⚠️ 原料總比例需為 100%，目前為 {total_ratio}%。")
